"""
FEATURE-058-E/F: Ontology Graph Viewer — Service Layer

Reads ontology graph data from knowledge-base/.ontology/ directory,
transforms JSONL event-sourced records to Cytoscape.js-compatible JSON,
provides text search and BFS graph traversal across entities.
"""
import importlib.util
import json
import math
import os
from pathlib import Path
from typing import Any

from x_ipe.tracing import x_ipe_tracing

ONTOLOGY_DIR = '.ontology'
GRAPH_INDEX_FILE = '.graph-index.json'


def _import_ontology_search():
    """Dynamically import search module from ontology tool skill."""
    # __file__ = src/x_ipe/services/ontology_graph_service.py
    # Need 4 dirname calls: services/ → x_ipe/ → src/ → project root
    project_root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    )
    # ontology.py must be importable first (search.py depends on it)
    ontology_path = os.path.join(
        project_root, '.github', 'skills', 'x-ipe-tool-ontology', 'scripts', 'ontology.py'
    )
    ont_spec = importlib.util.spec_from_file_location('ontology', ontology_path)
    ont_mod = importlib.util.module_from_spec(ont_spec)
    import sys
    sys.modules['ontology'] = ont_mod
    ont_spec.loader.exec_module(ont_mod)

    search_path = os.path.join(
        project_root, '.github', 'skills', 'x-ipe-tool-ontology', 'scripts', 'search.py'
    )
    spec = importlib.util.spec_from_file_location('ontology_search', search_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# Cache the module at import time
_search_module = None


def _get_search_module():
    global _search_module
    if _search_module is None:
        _search_module = _import_ontology_search()
    return _search_module


class OntologyGraphService:
    """Service for reading and transforming ontology graph data."""

    def __init__(self, kb_root: str):
        self._kb_root = Path(kb_root)
        self._ontology_dir = self._kb_root / ONTOLOGY_DIR

    @property
    def ontology_dir(self) -> Path:
        return self._ontology_dir

    @property
    def has_ontology(self) -> bool:
        return self._ontology_dir.is_dir()

    @x_ipe_tracing()
    def list_graphs(self) -> list[dict]:
        """List available graphs from .graph-index.json.

        Returns list of dicts with name, file_path, node_count, edge_count,
        dominant_type for each graph.
        """
        if not self.has_ontology:
            return []

        index = self._read_graph_index()
        if not index:
            return []

        result = []
        for g in index.get('graphs', []):
            result.append({
                'name': g.get('name', ''),
                'file_path': f'{ONTOLOGY_DIR}/{g.get("file", "")}',
                'node_count': g.get('entity_count', 0),
                'edge_count': g.get('relation_count', 0),
                'dominant_type': self._compute_dominant_type_from_index(g),
            })
        return result

    @x_ipe_tracing()
    def get_graph(self, name: str) -> dict | None:
        """Get Cytoscape.js-formatted elements for a named graph.

        Returns dict with 'name' and 'elements' (nodes + edges),
        or None if the graph doesn't exist.
        """
        graph_path = self._ontology_dir / f'{name}.jsonl'
        if not graph_path.is_file():
            return None

        entities, relations = self._parse_graph_jsonl(graph_path)

        nodes = [self._entity_to_cytoscape_node(e) for e in entities]
        edges = [self._relation_to_cytoscape_edge(r) for r in relations]

        return {
            'name': name,
            'elements': {
                'nodes': nodes,
                'edges': edges,
            },
        }

    @x_ipe_tracing()
    def search(self, query: str, graph_names: list[str] | None = None) -> list[dict]:
        """Search nodes across graphs with case-insensitive text matching.

        Matches against entity label and description fields.
        If graph_names is provided, only searches those graphs.
        """
        if not self.has_ontology or not query:
            return []

        q = query.lower()
        targets = self._resolve_target_graphs(graph_names)

        results = []
        for graph_name, graph_path in targets:
            entities, _ = self._parse_graph_jsonl(graph_path)
            for entity in entities:
                props = entity.get('properties', {})
                relevance = self._compute_relevance(props, q)
                if relevance > 0:
                    results.append({
                        'node_id': entity.get('id', ''),
                        'label': props.get('label', ''),
                        'graph': graph_name,
                        'relevance': relevance,
                    })

        results.sort(key=lambda r: r['relevance'], reverse=True)
        return results

    @x_ipe_tracing()
    def search_bfs(
        self,
        query: str,
        graph_names: list[str] | None = None,
        depth: int = 3,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        """BFS graph search via ontology tool's search.py module.

        Finds text matches then expands via BFS traversal to discover
        the knowledge neighborhood. Returns results + subgraph + pagination.
        """
        if not self.has_ontology or not query:
            return {
                'results': [],
                'subgraph': {'nodes': [], 'edges': []},
                'pagination': {'page': page, 'page_size': page_size, 'total': 0, 'total_pages': 0},
            }

        # Clamp parameters
        depth = max(1, min(5, depth))
        page = max(1, page)
        page_size = max(1, min(100, page_size))

        # Build scope string for search.py
        if graph_names:
            scope = ','.join(f'{n}.jsonl' for n in graph_names)
        else:
            scope = 'all'

        search_mod = _get_search_module()
        raw = search_mod.search(
            query=query,
            scope=scope,
            ontology_dir=str(self._ontology_dir),
            depth=depth,
            page_size=page_size,
            page=page,
        )

        # Transform matches to API format
        results = []
        for m in raw.get('matches', []):
            entity = m.get('entity', {})
            props = entity.get('properties', {})
            provenance = m.get('provenance', '')
            graph_name = provenance.replace('.jsonl', '') if provenance else ''
            results.append({
                'node_id': entity.get('id', ''),
                'label': props.get('label', ''),
                'node_type': props.get('node_type', 'entity'),
                'graph': graph_name,
                'relevance': m.get('score', 0),
                'match_fields': m.get('match_fields', []),
            })

        subgraph = raw.get('subgraph', {'nodes': [], 'edges': []})
        total = raw.get('total_count', 0)
        total_pages = max(1, math.ceil(total / page_size)) if total > 0 else 0

        return {
            'results': results,
            'subgraph': subgraph,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': total,
                'total_pages': total_pages,
            },
        }

    # --- Private helpers ---

    def _read_graph_index(self) -> dict | None:
        index_path = self._ontology_dir / GRAPH_INDEX_FILE
        if not index_path.is_file():
            return None
        try:
            with open(index_path) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return None

    def _parse_graph_jsonl(self, path: Path) -> tuple[list[dict], list[dict]]:
        """Parse a graph JSONL file into entities and relations.

        Each line is a JSON record with 'op' field:
        - 'create': entity record with 'entity' dict
        - 'relate': relation record with 'from', 'rel', 'to' fields
        Malformed lines are skipped.
        """
        entities: list[dict] = []
        relations: list[dict] = []

        try:
            with open(path) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        record = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    op = record.get('op')
                    if op == 'create' and 'entity' in record:
                        entities.append(record['entity'])
                    elif op == 'relate':
                        relations.append({
                            'from': record.get('from', ''),
                            'rel': record.get('rel', ''),
                            'to': record.get('to', ''),
                            'properties': record.get('properties', {}),
                        })
        except OSError:
            pass

        return entities, relations

    def _entity_to_cytoscape_node(self, entity: dict) -> dict:
        """Transform an ontology entity to Cytoscape.js node format."""
        props = entity.get('properties', {})
        eid = entity.get('id', '')

        return {
            'data': {
                'id': eid,
                'label': props.get('label', eid),
                'node_type': props.get('node_type', 'entity'),
                'weight': props.get('weight', 1),
                'description': props.get('description', ''),
                'dimensions': props.get('dimensions', {}),
                'source_files': props.get('source_files', []),
                'metadata': {
                    'connections': 0,  # Will be set by frontend from edge count
                    'created': entity.get('created', ''),
                    'updated': entity.get('updated', ''),
                },
            },
        }

    def _relation_to_cytoscape_edge(self, relation: dict) -> dict:
        """Transform an ontology relation to Cytoscape.js edge format."""
        source = relation.get('from', '')
        target = relation.get('to', '')
        rel_type = relation.get('rel', 'related_to')

        return {
            'data': {
                'id': f'e_{source}_{target}',
                'source': source,
                'target': target,
                'relation_type': rel_type,
                'label': rel_type,
            },
        }

    def _resolve_target_graphs(
        self, graph_names: list[str] | None,
    ) -> list[tuple[str, Path]]:
        """Resolve which graph files to search."""
        if graph_names:
            targets = []
            for name in graph_names:
                p = self._ontology_dir / f'{name}.jsonl'
                if p.is_file():
                    targets.append((name, p))
            return targets

        # Search all JSONL files except _entities.jsonl
        targets = []
        if self._ontology_dir.is_dir():
            for p in sorted(self._ontology_dir.glob('*.jsonl')):
                if p.name.startswith('_'):
                    continue
                targets.append((p.stem, p))
        return targets

    @staticmethod
    def _compute_relevance(props: dict, query_lower: str) -> float:
        """Compute relevance score for an entity against a search query."""
        score = 0.0
        label = props.get('label', '')
        if isinstance(label, str) and query_lower in label.lower():
            score += 1.0
            if label.lower() == query_lower:
                score += 0.5  # Exact match bonus

        desc = props.get('description', '')
        if isinstance(desc, str) and query_lower in desc.lower():
            score += 0.5

        dims = props.get('dimensions', {})
        if isinstance(dims, dict):
            for dim_vals in dims.values():
                if isinstance(dim_vals, list):
                    for v in dim_vals:
                        if isinstance(v, str) and query_lower in v.lower():
                            score += 0.25
                            break
                elif isinstance(dim_vals, str) and query_lower in dim_vals.lower():
                    score += 0.25

        return score

    @staticmethod
    def _compute_dominant_type_from_index(graph_info: dict) -> str:
        """Determine dominant node type. Falls back to 'concept'."""
        # graph-index.json doesn't directly store type distribution,
        # so we use root_label heuristic or default to 'concept'
        return 'concept'
