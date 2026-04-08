"""Tests for x-ipe-tool-ontology scripts (FEATURE-058-A).

Covers: ontology.py, dimension_registry.py, graph_ops.py, search.py.
Entity CRUD, relations, cycle detection, validation, registry, clusters, search.
"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

_SCRIPTS_DIR = str(
    Path(__file__).resolve().parent.parent
    / ".github"
    / "skills"
    / "x-ipe-tool-ontology"
    / "scripts"
)
sys.path.insert(0, _SCRIPTS_DIR)

import ontology  # noqa: E402
import dimension_registry  # noqa: E402
import graph_ops  # noqa: E402
import search  # noqa: E402


# ──────────────────── Fixtures ────────────────────


@pytest.fixture()
def tmp_graph(tmp_path):
    """Return path to a temporary graph JSONL file."""
    return str(tmp_path / "test_graph.jsonl")


@pytest.fixture()
def tmp_registry(tmp_path):
    """Return path to a temporary dimension registry JSON file."""
    return str(tmp_path / ".dimension-registry.json")


@pytest.fixture()
def sample_props():
    """Valid KnowledgeNode properties."""
    return {
        "label": "JWT Authentication",
        "node_type": "concept",
        "description": "Token-based auth mechanism",
        "dimensions": {"technology": ["JWT", "OAuth2"], "domain": "security"},
        "source_files": ["src/auth/jwt.py"],
    }


@pytest.fixture()
def two_entities(tmp_graph, sample_props):
    """Create two entities and return their IDs."""
    e1 = ontology.create_entity("KnowledgeNode", dict(sample_props), tmp_graph)
    props2 = dict(sample_props)
    props2["label"] = "Password Hashing"
    props2["source_files"] = ["src/auth/hash.py"]
    e2 = ontology.create_entity("KnowledgeNode", props2, tmp_graph)
    return e1["id"], e2["id"]


# ══════════════════════════════════════════════════
#  ontology.py
# ══════════════════════════════════════════════════


class TestGenerateId:
    def test_default_prefix(self):
        eid = ontology.generate_id()
        assert eid.startswith("know_")
        assert len(eid) == 13  # know_ + 8 hex chars

    def test_custom_prefix(self):
        eid = ontology.generate_id("test")
        assert eid.startswith("test_")

    def test_unique(self):
        ids = {ontology.generate_id() for _ in range(100)}
        assert len(ids) == 100


class TestResolveSafePath:
    def test_valid_child_path(self, tmp_path):
        child = tmp_path / "subdir" / "file.txt"
        result = ontology.resolve_safe_path(
            "subdir/file.txt", root=str(tmp_path)
        )
        assert result == child

    def test_rejects_traversal(self, tmp_path):
        with pytest.raises(ValueError, match="must stay within root"):
            ontology.resolve_safe_path(
                "../../etc/passwd", root=str(tmp_path)
            )

    def test_rejects_empty(self):
        with pytest.raises(ValueError, match="empty path"):
            ontology.resolve_safe_path("")

    def test_must_exist_missing(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            ontology.resolve_safe_path(
                "nonexistent.txt", root=str(tmp_path), must_exist=True
            )


class TestLoadGraphEmpty:
    def test_missing_file(self, tmp_graph):
        entities, relations = ontology.load_graph(tmp_graph)
        assert entities == {}
        assert relations == []


class TestCreateEntity:
    def test_basic_create(self, tmp_graph, sample_props):
        entity = ontology.create_entity("KnowledgeNode", sample_props, tmp_graph)
        assert entity["id"].startswith("know_")
        assert entity["type"] == "KnowledgeNode"
        assert entity["properties"]["label"] == "JWT Authentication"
        assert entity["properties"]["weight"] == 5  # default

    def test_custom_id(self, tmp_graph, sample_props):
        entity = ontology.create_entity(
            "KnowledgeNode", sample_props, tmp_graph, entity_id="know_custom01"
        )
        assert entity["id"] == "know_custom01"

    def test_missing_required_prop(self, tmp_graph):
        with pytest.raises(ValueError, match="Missing required property"):
            ontology.create_entity("KnowledgeNode", {"label": "Test"}, tmp_graph)

    def test_invalid_node_type(self, tmp_graph):
        props = {
            "label": "Test",
            "node_type": "invalid",
            "source_files": ["a.py"],
        }
        with pytest.raises(ValueError, match="Invalid node_type"):
            ontology.create_entity("KnowledgeNode", props, tmp_graph)

    def test_invalid_weight(self, tmp_graph, sample_props):
        sample_props["weight"] = 11
        with pytest.raises(ValueError, match="weight"):
            ontology.create_entity("KnowledgeNode", sample_props, tmp_graph)

    def test_persisted_to_file(self, tmp_graph, sample_props):
        ontology.create_entity("KnowledgeNode", sample_props, tmp_graph)
        assert Path(tmp_graph).exists()
        with open(tmp_graph) as f:
            record = json.loads(f.readline())
        assert record["op"] == "create"


class TestGetEntity:
    def test_get_existing(self, tmp_graph, sample_props):
        created = ontology.create_entity("KnowledgeNode", sample_props, tmp_graph)
        found = ontology.get_entity(created["id"], tmp_graph)
        assert found is not None
        assert found["id"] == created["id"]

    def test_get_missing(self, tmp_graph):
        assert ontology.get_entity("know_missing0", tmp_graph) is None


class TestUpdateEntity:
    def test_update_existing(self, tmp_graph, sample_props):
        created = ontology.create_entity("KnowledgeNode", sample_props, tmp_graph)
        updated = ontology.update_entity(
            created["id"], {"weight": 8, "description": "Updated"}, tmp_graph
        )
        assert updated is not None
        assert updated["properties"]["weight"] == 8
        assert updated["properties"]["description"] == "Updated"

    def test_update_missing(self, tmp_graph):
        assert ontology.update_entity("know_missing0", {"weight": 3}, tmp_graph) is None

    def test_update_invalid_node_type(self, tmp_graph, sample_props):
        created = ontology.create_entity("KnowledgeNode", sample_props, tmp_graph)
        with pytest.raises(ValueError, match="Invalid node_type"):
            ontology.update_entity(created["id"], {"node_type": "bad"}, tmp_graph)


class TestDeleteEntity:
    def test_delete_existing(self, tmp_graph, sample_props):
        created = ontology.create_entity("KnowledgeNode", sample_props, tmp_graph)
        assert ontology.delete_entity(created["id"], tmp_graph) is True
        assert ontology.get_entity(created["id"], tmp_graph) is None

    def test_delete_missing(self, tmp_graph):
        assert ontology.delete_entity("know_missing0", tmp_graph) is False


class TestListEntities:
    def test_list_all(self, tmp_graph, sample_props):
        ontology.create_entity("KnowledgeNode", sample_props, tmp_graph)
        entities = ontology.list_entities(None, tmp_graph)
        assert len(entities) == 1

    def test_list_by_type(self, tmp_graph, sample_props):
        ontology.create_entity("KnowledgeNode", sample_props, tmp_graph)
        assert len(ontology.list_entities("KnowledgeNode", tmp_graph)) == 1
        assert len(ontology.list_entities("Other", tmp_graph)) == 0


class TestQueryEntities:
    def test_query_by_property(self, tmp_graph, sample_props):
        ontology.create_entity("KnowledgeNode", sample_props, tmp_graph)
        results = ontology.query_entities(
            "KnowledgeNode", {"node_type": "concept"}, tmp_graph
        )
        assert len(results) == 1

    def test_query_nested_dimension(self, tmp_graph, sample_props):
        ontology.create_entity("KnowledgeNode", sample_props, tmp_graph)
        results = ontology.query_entities(
            None, {"dimensions.domain": "security"}, tmp_graph
        )
        assert len(results) == 1

    def test_query_list_value(self, tmp_graph, sample_props):
        ontology.create_entity("KnowledgeNode", sample_props, tmp_graph)
        results = ontology.query_entities(
            None, {"dimensions.technology": "JWT"}, tmp_graph
        )
        assert len(results) == 1

    def test_query_no_match(self, tmp_graph, sample_props):
        ontology.create_entity("KnowledgeNode", sample_props, tmp_graph)
        results = ontology.query_entities(
            None, {"node_type": "document"}, tmp_graph
        )
        assert len(results) == 0


class TestRelations:
    def test_create_relation(self, tmp_graph, two_entities):
        id1, id2 = two_entities
        rel = ontology.create_relation(id1, "depends_on", id2, None, tmp_graph)
        assert rel["from"] == id1
        assert rel["rel"] == "depends_on"

    def test_invalid_relation_type(self, tmp_graph, two_entities):
        id1, id2 = two_entities
        with pytest.raises(ValueError, match="Invalid relation type"):
            ontology.create_relation(id1, "invalid_rel", id2, None, tmp_graph)

    def test_missing_entity(self, tmp_graph, two_entities):
        id1, _ = two_entities
        with pytest.raises(ValueError, match="not found"):
            ontology.create_relation(id1, "related_to", "know_missing0", None, tmp_graph)

    def test_cycle_detection(self, tmp_graph, sample_props):
        e1 = ontology.create_entity("KnowledgeNode", dict(sample_props), tmp_graph)
        p2 = dict(sample_props)
        p2["label"] = "B"
        p2["source_files"] = ["b.py"]
        e2 = ontology.create_entity("KnowledgeNode", p2, tmp_graph)
        p3 = dict(sample_props)
        p3["label"] = "C"
        p3["source_files"] = ["c.py"]
        e3 = ontology.create_entity("KnowledgeNode", p3, tmp_graph)

        ontology.create_relation(e1["id"], "depends_on", e2["id"], None, tmp_graph)
        ontology.create_relation(e2["id"], "depends_on", e3["id"], None, tmp_graph)
        with pytest.raises(ValueError, match="Cycle detected"):
            ontology.create_relation(e3["id"], "depends_on", e1["id"], None, tmp_graph)

    def test_non_acyclic_allows_cycle(self, tmp_graph, two_entities):
        id1, id2 = two_entities
        ontology.create_relation(id1, "related_to", id2, None, tmp_graph)
        ontology.create_relation(id2, "related_to", id1, None, tmp_graph)


class TestGetRelated:
    def test_outgoing(self, tmp_graph, two_entities):
        id1, id2 = two_entities
        ontology.create_relation(id1, "depends_on", id2, None, tmp_graph)
        results = ontology.get_related(id1, None, tmp_graph, "outgoing")
        assert len(results) == 1
        assert results[0]["entity"]["id"] == id2

    def test_incoming(self, tmp_graph, two_entities):
        id1, id2 = two_entities
        ontology.create_relation(id1, "depends_on", id2, None, tmp_graph)
        results = ontology.get_related(id2, None, tmp_graph, "incoming")
        assert len(results) == 1
        assert results[0]["entity"]["id"] == id1

    def test_both(self, tmp_graph, two_entities):
        id1, id2 = two_entities
        ontology.create_relation(id1, "depends_on", id2, None, tmp_graph)
        results = ontology.get_related(id1, None, tmp_graph, "both")
        assert len(results) == 1
        assert "direction" in results[0]


class TestFindPath:
    def test_direct(self, tmp_graph, two_entities):
        id1, id2 = two_entities
        ontology.create_relation(id1, "related_to", id2, None, tmp_graph)
        path = ontology.find_path(id1, id2, tmp_graph)
        assert path == [id1, id2]

    def test_no_path(self, tmp_graph, two_entities):
        id1, id2 = two_entities
        assert ontology.find_path(id1, id2, tmp_graph) == []

    def test_self_path(self, tmp_graph, two_entities):
        id1, _ = two_entities
        assert ontology.find_path(id1, id1, tmp_graph) == [id1]


class TestValidateGraph:
    def test_valid_graph(self, tmp_graph, sample_props):
        ontology.create_entity("KnowledgeNode", sample_props, tmp_graph)
        errors = ontology.validate_graph(tmp_graph)
        assert errors == []

    def test_detects_issues(self, tmp_graph):
        # Manually write an invalid entity
        record = {
            "op": "create",
            "entity": {
                "id": "know_bad00001",
                "type": "KnowledgeNode",
                "properties": {"label": "Missing fields"},
                "created": "2026-01-01T00:00:00+00:00",
                "updated": "2026-01-01T00:00:00+00:00",
            },
            "timestamp": "2026-01-01T00:00:00+00:00",
        }
        ontology.append_op(tmp_graph, record)
        errors = ontology.validate_graph(tmp_graph)
        assert len(errors) > 0
        assert any("missing required" in e for e in errors)


class TestMergeSchema:
    def test_basic_merge(self):
        base = {"a": 1, "b": {"c": 2}}
        incoming = {"b": {"d": 3}, "e": 4}
        result = ontology.merge_schema(base, incoming)
        assert result == {"a": 1, "b": {"c": 2, "d": 3}, "e": 4}

    def test_list_dedup(self):
        base = {"items": [1, 2, 3]}
        incoming = {"items": [2, 3, 4]}
        result = ontology.merge_schema(base, incoming)
        assert result["items"] == [1, 2, 3, 4]


class TestCorruptedLineRecovery:
    def test_skips_bad_json(self, tmp_graph, sample_props):
        ontology.create_entity("KnowledgeNode", sample_props, tmp_graph)
        # Append corrupted line
        with open(tmp_graph, "a") as f:
            f.write("this is not json\n")
        entities, _ = ontology.load_graph(tmp_graph)
        assert len(entities) == 1  # valid entity still loaded


# ══════════════════════════════════════════════════
#  dimension_registry.py
# ══════════════════════════════════════════════════


class TestDimensionResolve:
    def test_canonical_match(self, tmp_registry):
        dim = {"name": "technology", "type": "multi-value", "examples": ["Python"]}
        dimension_registry.register(dim, tmp_registry)
        result = dimension_registry.resolve("technology", tmp_registry)
        assert result["canonical"] == "technology"

    def test_alias_match(self, tmp_registry):
        dim = {
            "name": "technology",
            "type": "multi-value",
            "aliases": ["tech", "tech-stack"],
        }
        dimension_registry.register(dim, tmp_registry)
        result = dimension_registry.resolve("tech", tmp_registry)
        assert result["canonical"] == "technology"

    def test_no_match(self, tmp_registry):
        result = dimension_registry.resolve("unknown", tmp_registry)
        assert result["canonical"] is None


class TestDimensionRegister:
    def test_register_new(self, tmp_registry):
        dim = {"name": "domain", "type": "multi-value", "examples": ["security"]}
        result = dimension_registry.register(dim, tmp_registry)
        assert result["registered"] == "domain"

    def test_register_merge(self, tmp_registry):
        dim1 = {"name": "tech", "examples": ["Python"]}
        dim2 = {"name": "tech", "examples": ["JavaScript"]}
        dimension_registry.register(dim1, tmp_registry)
        result = dimension_registry.register(dim2, tmp_registry)
        assert "Python" in result["dimension"]["examples"]
        assert "JavaScript" in result["dimension"]["examples"]

    def test_no_name_raises(self, tmp_registry):
        with pytest.raises(ValueError, match="'name'"):
            dimension_registry.register({}, tmp_registry)


class TestDimensionList:
    def test_list_empty(self, tmp_registry):
        result = dimension_registry.list_dimensions(tmp_registry)
        assert result["dimensions"] == {}

    def test_list_after_register(self, tmp_registry):
        dimension_registry.register({"name": "domain"}, tmp_registry)
        result = dimension_registry.list_dimensions(tmp_registry)
        assert "domain" in result["dimensions"]


class TestDimensionRebuild:
    def test_rebuild_from_entities(self, tmp_path):
        entities_path = str(tmp_path / "_entities.jsonl")
        registry_path = str(tmp_path / ".dimension-registry.json")

        props = {
            "label": "Test",
            "node_type": "concept",
            "source_files": ["test.py"],
            "dimensions": {"technology": ["Python", "Flask"], "domain": "backend"},
        }
        ontology.create_entity("KnowledgeNode", props, entities_path)

        result = dimension_registry.rebuild(entities_path, registry_path)
        assert result["rebuilt"] is True
        assert "technology" in result["dimensions"]
        assert "domain" in result["dimensions"]


# ══════════════════════════════════════════════════
#  graph_ops.py
# ══════════════════════════════════════════════════


class TestUnionFind:
    def test_basic_union(self):
        uf = graph_ops.UnionFind()
        uf.union("a", "b")
        uf.union("b", "c")
        assert uf.find("a") == uf.find("c")

    def test_disjoint(self):
        uf = graph_ops.UnionFind()
        uf.find("a")
        uf.find("b")
        assert uf.find("a") != uf.find("b")


class TestDetectClusters:
    def test_single_cluster(self):
        entities = {"a": {}, "b": {}, "c": {}}
        relations = [
            {"from": "a", "rel": "related_to", "to": "b"},
            {"from": "b", "rel": "related_to", "to": "c"},
        ]
        clusters = graph_ops.detect_clusters(entities, relations)
        assert len(clusters) == 1

    def test_two_clusters(self):
        entities = {"a": {}, "b": {}, "c": {}, "d": {}}
        relations = [
            {"from": "a", "rel": "related_to", "to": "b"},
            {"from": "c", "rel": "related_to", "to": "d"},
        ]
        clusters = graph_ops.detect_clusters(entities, relations)
        assert len(clusters) == 2


class TestPruneStale:
    def test_prune_missing_files(self, tmp_path):
        entities_path = str(tmp_path / "_entities.jsonl")
        props = {
            "label": "Test",
            "node_type": "concept",
            "source_files": ["/nonexistent/file.py"],
        }
        ontology.create_entity("KnowledgeNode", props, entities_path)

        result = graph_ops.prune_stale(entities_path)
        assert len(result["pruned"]) == 1

    def test_keep_existing_files(self, tmp_path):
        entities_path = str(tmp_path / "_entities.jsonl")
        real_file = tmp_path / "real.py"
        real_file.write_text("# real file")
        props = {
            "label": "Test",
            "node_type": "concept",
            "source_files": [str(real_file)],
        }
        ontology.create_entity("KnowledgeNode", props, entities_path)

        result = graph_ops.prune_stale(entities_path)
        assert result["pruned"] == []
        assert result["updated"] == []


class TestBuild:
    def test_build_empty(self, tmp_path):
        entities_path = str(tmp_path / "_entities.jsonl")
        output_path = str(tmp_path / "output")
        result = graph_ops.build(str(tmp_path), output_path, entities_path)
        assert result["clusters"] == 0

    def test_build_with_entities(self, tmp_path):
        entities_path = str(tmp_path / "_entities.jsonl")
        output_path = str(tmp_path / "output")

        src_file = tmp_path / "src" / "auth.py"
        src_file.parent.mkdir(parents=True)
        src_file.write_text("# auth module")

        props = {
            "label": "Auth Module",
            "node_type": "concept",
            "source_files": [str(src_file)],
        }
        ontology.create_entity("KnowledgeNode", props, entities_path)

        result = graph_ops.build(str(tmp_path), output_path, entities_path)
        assert result["clusters"] >= 1
        assert result["entities_in_scope"] == 1

        # Check that output file was created
        output_files = list(Path(output_path).glob("*.jsonl"))
        assert len(output_files) == 1


class TestSlugify:
    def test_basic(self):
        assert graph_ops._slugify("JWT Authentication") == "jwt-authentication"

    def test_special_chars(self):
        assert graph_ops._slugify("Hello World!!!") == "hello-world"


# ══════════════════════════════════════════════════
#  search.py
# ══════════════════════════════════════════════════


@pytest.fixture()
def search_setup(tmp_path):
    """Create ontology dir with a graph file containing searchable entities."""
    ont_dir = tmp_path / ".ontology"
    ont_dir.mkdir()
    graph_file = str(ont_dir / "auth.jsonl")

    props1 = {
        "label": "JWT Authentication",
        "node_type": "concept",
        "description": "Token-based auth using JSON Web Tokens",
        "dimensions": {"technology": ["JWT", "OAuth2"]},
        "source_files": ["src/auth.py"],
    }
    props2 = {
        "label": "Password Hashing",
        "node_type": "concept",
        "description": "Secure password storage with bcrypt",
        "dimensions": {"technology": ["bcrypt"]},
        "source_files": ["src/hash.py"],
    }
    e1 = ontology.create_entity("KnowledgeNode", props1, graph_file)
    e2 = ontology.create_entity("KnowledgeNode", props2, graph_file)
    ontology.create_relation(e1["id"], "related_to", e2["id"], None, graph_file)

    return str(ont_dir), e1["id"], e2["id"]


class TestTextMatch:
    def test_label_match(self):
        entity = {"properties": {"label": "JWT Auth", "description": "", "dimensions": {}}}
        fields = search._text_match(entity, "jwt")
        assert "label" in fields

    def test_description_match(self):
        entity = {"properties": {"label": "", "description": "Token auth", "dimensions": {}}}
        fields = search._text_match(entity, "token")
        assert "description" in fields

    def test_dimension_match(self):
        entity = {
            "properties": {
                "label": "",
                "description": "",
                "dimensions": {"tech": ["Python", "Flask"]},
            }
        }
        fields = search._text_match(entity, "flask")
        assert "dimensions.tech" in fields

    def test_no_match(self):
        entity = {"properties": {"label": "X", "description": "Y", "dimensions": {}}}
        assert search._text_match(entity, "zzz") == []


class TestSearch:
    def test_search_by_label(self, search_setup):
        ont_dir, _, _ = search_setup
        result = search.search("JWT", "all", ont_dir)
        assert result["total_count"] >= 1
        assert any("label" in m["match_fields"] for m in result["matches"])

    def test_search_no_results(self, search_setup):
        ont_dir, _, _ = search_setup
        result = search.search("nonexistent_term_xyz", "all", ont_dir)
        assert result["total_count"] == 0

    def test_subgraph_included(self, search_setup):
        ont_dir, id1, id2 = search_setup
        result = search.search("JWT", "all", ont_dir, depth=1)
        assert len(result["subgraph"]["nodes"]) >= 1

    def test_pagination(self, search_setup):
        ont_dir, _, _ = search_setup
        result = search.search("auth", "all", ont_dir, page_size=1, page=1)
        assert len(result["matches"]) <= 1
        assert result["page"] == 1

    def test_specific_scope(self, search_setup):
        ont_dir, _, _ = search_setup
        result = search.search("JWT", "auth.jsonl", ont_dir)
        assert result["total_count"] >= 1


class TestBFSSubgraph:
    def test_bfs_reaches_neighbors(self, search_setup):
        ont_dir, id1, id2 = search_setup
        graph_file = str(Path(ont_dir) / "auth.jsonl")
        entities, relations = ontology.load_graph(graph_file)

        nodes, edges = search._bfs_subgraph({id1}, entities, relations, depth=1)
        assert id1 in nodes
        assert id2 in nodes
        assert len(edges) >= 1

    def test_bfs_zero_depth(self, search_setup):
        ont_dir, id1, id2 = search_setup
        graph_file = str(Path(ont_dir) / "auth.jsonl")
        entities, relations = ontology.load_graph(graph_file)

        nodes, edges = search._bfs_subgraph({id1}, entities, relations, depth=0)
        assert nodes == {id1}


# ══════════════════════════════════════════════════
#  CLI smoke tests
# ══════════════════════════════════════════════════


class TestOntologyCLI:
    """CLI tests calling main() in-process for coverage."""

    def _run_main(self, module, argv: list[str], capsys):
        """Call module.main() with patched sys.argv. Returns (exit_code, stdout)."""
        import unittest.mock

        with unittest.mock.patch("sys.argv", [module.__name__] + argv):
            try:
                module.main()
                code = 0
            except SystemExit as exc:
                code = exc.code if exc.code is not None else 0
        captured = capsys.readouterr()
        return code, captured.out

    # -- ontology.py CLI --

    def test_create_cli(self, tmp_graph, capsys):
        props = json.dumps({"label": "CLI", "node_type": "concept", "source_files": ["t.py"]})
        rc, out = self._run_main(ontology, ["create", "--type", "KnowledgeNode", "--props", props, "--graph", tmp_graph], capsys)
        assert rc == 0
        assert json.loads(out)["id"].startswith("know_")

    def test_get_cli(self, tmp_graph, sample_props, capsys):
        e = ontology.create_entity("KnowledgeNode", sample_props, tmp_graph)
        rc, out = self._run_main(ontology, ["get", "--id", e["id"], "--graph", tmp_graph], capsys)
        assert rc == 0
        assert json.loads(out)["id"] == e["id"]

    def test_get_missing_cli(self, tmp_graph, capsys):
        rc, out = self._run_main(ontology, ["get", "--id", "know_missing0", "--graph", tmp_graph], capsys)
        assert rc == 1

    def test_update_cli(self, tmp_graph, sample_props, capsys):
        e = ontology.create_entity("KnowledgeNode", sample_props, tmp_graph)
        rc, out = self._run_main(ontology, ["update", "--id", e["id"], "--props", '{"weight":9}', "--graph", tmp_graph], capsys)
        assert rc == 0
        assert json.loads(out)["properties"]["weight"] == 9

    def test_update_missing_cli(self, tmp_graph, capsys):
        rc, _ = self._run_main(ontology, ["update", "--id", "know_missing0", "--props", '{"weight":1}', "--graph", tmp_graph], capsys)
        assert rc == 1

    def test_delete_cli(self, tmp_graph, sample_props, capsys):
        e = ontology.create_entity("KnowledgeNode", sample_props, tmp_graph)
        rc, out = self._run_main(ontology, ["delete", "--id", e["id"], "--graph", tmp_graph], capsys)
        assert rc == 0
        assert json.loads(out)["deleted"] == e["id"]

    def test_delete_missing_cli(self, tmp_graph, capsys):
        rc, _ = self._run_main(ontology, ["delete", "--id", "know_missing0", "--graph", tmp_graph], capsys)
        assert rc == 1

    def test_list_cli(self, tmp_graph, sample_props, capsys):
        ontology.create_entity("KnowledgeNode", sample_props, tmp_graph)
        rc, out = self._run_main(ontology, ["list", "--graph", tmp_graph], capsys)
        assert rc == 0
        assert len(json.loads(out)) == 1

    def test_list_typed_cli(self, tmp_graph, sample_props, capsys):
        ontology.create_entity("KnowledgeNode", sample_props, tmp_graph)
        rc, out = self._run_main(ontology, ["list", "--type", "KnowledgeNode", "--graph", tmp_graph], capsys)
        assert rc == 0
        assert len(json.loads(out)) == 1

    def test_query_cli(self, tmp_graph, sample_props, capsys):
        ontology.create_entity("KnowledgeNode", sample_props, tmp_graph)
        rc, out = self._run_main(ontology, ["query", "--type", "KnowledgeNode", "--where", '{"node_type":"concept"}', "--graph", tmp_graph], capsys)
        assert rc == 0
        assert len(json.loads(out)) == 1

    def test_relate_cli(self, tmp_graph, two_entities, capsys):
        id1, id2 = two_entities
        rc, out = self._run_main(ontology, ["relate", "--from", id1, "--rel", "related_to", "--to", id2, "--graph", tmp_graph], capsys)
        assert rc == 0
        assert json.loads(out)["rel"] == "related_to"

    def test_related_cli(self, tmp_graph, two_entities, capsys):
        id1, id2 = two_entities
        ontology.create_relation(id1, "related_to", id2, None, tmp_graph)
        rc, out = self._run_main(ontology, ["related", "--id", id1, "--graph", tmp_graph], capsys)
        assert rc == 0
        assert len(json.loads(out)) == 1

    def test_find_path_cli(self, tmp_graph, two_entities, capsys):
        id1, id2 = two_entities
        ontology.create_relation(id1, "related_to", id2, None, tmp_graph)
        rc, out = self._run_main(ontology, ["find-path", "--from", id1, "--to", id2, "--graph", tmp_graph], capsys)
        assert rc == 0
        assert json.loads(out)["length"] == 2

    def test_validate_cli(self, tmp_graph, sample_props, capsys):
        ontology.create_entity("KnowledgeNode", sample_props, tmp_graph)
        rc, out = self._run_main(ontology, ["validate", "--graph", tmp_graph], capsys)
        assert rc == 0
        assert json.loads(out)["valid"] is True

    def test_load_cli(self, tmp_graph, sample_props, capsys):
        ontology.create_entity("KnowledgeNode", sample_props, tmp_graph)
        rc, out = self._run_main(ontology, ["load", "--graph", tmp_graph], capsys)
        assert rc == 0
        assert json.loads(out)["entity_count"] == 1

    def test_create_validation_error_cli(self, tmp_graph, capsys):
        rc, out = self._run_main(ontology, ["create", "--type", "KnowledgeNode", "--props", '{"label":"X"}', "--graph", tmp_graph], capsys)
        assert rc == 1
        assert "error" in json.loads(out)

    # -- dimension_registry.py CLI --

    def test_dim_resolve_cli(self, tmp_path, capsys):
        reg = str(tmp_path / "reg.json")
        dimension_registry.register({"name": "tech", "aliases": ["technology"]}, reg)
        rc, out = self._run_main(dimension_registry, ["resolve", "--name", "technology", "--registry", reg], capsys)
        assert rc == 0
        assert json.loads(out)["canonical"] == "tech"

    def test_dim_register_cli(self, tmp_path, capsys):
        reg = str(tmp_path / "reg.json")
        dim = json.dumps({"name": "domain", "examples": ["security"]})
        rc, out = self._run_main(dimension_registry, ["register", "--dimension", dim, "--registry", reg], capsys)
        assert rc == 0
        assert json.loads(out)["registered"] == "domain"

    def test_dim_list_cli(self, tmp_path, capsys):
        reg = str(tmp_path / "reg.json")
        rc, out = self._run_main(dimension_registry, ["list", "--registry", reg], capsys)
        assert rc == 0

    def test_dim_rebuild_cli(self, tmp_path, capsys):
        ents = str(tmp_path / "ents.jsonl")
        reg = str(tmp_path / "reg.json")
        props = {"label": "T", "node_type": "concept", "source_files": ["a.py"], "dimensions": {"tech": ["Py"]}}
        ontology.create_entity("KnowledgeNode", props, ents)
        rc, out = self._run_main(dimension_registry, ["rebuild", "--entities", ents, "--registry", reg], capsys)
        assert rc == 0
        assert json.loads(out)["rebuilt"] is True

    # -- graph_ops.py CLI --

    def test_build_main_cli(self, tmp_path, capsys):
        ents = str(tmp_path / "_entities.jsonl")
        output = str(tmp_path / "out")
        src = tmp_path / "src" / "main.py"
        src.parent.mkdir()
        src.write_text("# code")
        props = {"label": "Main", "node_type": "concept", "source_files": [str(src)]}
        ontology.create_entity("KnowledgeNode", props, ents)
        rc, out = self._run_main(graph_ops, ["build", "--scope", str(tmp_path), "--output", output, "--entities", ents], capsys)
        assert rc == 0
        assert json.loads(out)["clusters"] >= 1

    def test_prune_main_cli(self, tmp_path, capsys):
        ents = str(tmp_path / "_entities.jsonl")
        props = {"label": "X", "node_type": "concept", "source_files": ["/no/exist.py"]}
        ontology.create_entity("KnowledgeNode", props, ents)
        rc, out = self._run_main(graph_ops, ["prune", "--entities", ents], capsys)
        assert rc == 0
        assert len(json.loads(out)["pruned"]) == 1

    # -- search.py CLI --

    def test_search_main_cli(self, search_setup, capsys):
        ont_dir, _, _ = search_setup
        rc, out = self._run_main(search, ["--query", "JWT", "--scope", "all", "--ontology-dir", ont_dir], capsys)
        assert rc == 0
        assert json.loads(out)["total_count"] >= 1


# ══════════════════════════════════════════════════
#  FEATURE-058-D Tests: .graph-index.json & retag
# ══════════════════════════════════════════════════


class TestGraphIndex:
    """Tests for .graph-index.json manifest generation in graph_ops.build()."""

    def test_build_generates_graph_index_file(self, tmp_path):
        """Build should create .graph-index.json in the output dir."""
        scope = tmp_path / "kb"
        scope.mkdir()
        (scope / "doc.md").write_text("test")
        ont_dir = tmp_path / ".ontology"
        ont_dir.mkdir()
        ents = str(ont_dir / "_entities.jsonl")
        ontology.create_entity(
            "KnowledgeNode",
            {"label": "Test Doc", "node_type": "document", "source_files": [str(scope / "doc.md")]},
            ents,
        )
        result = graph_ops.build(str(scope), str(ont_dir), ents)
        index_path = ont_dir / ".graph-index.json"
        assert index_path.exists()
        manifest = json.loads(index_path.read_text())
        assert manifest["version"] == "1.0"
        assert len(manifest["graphs"]) == 1
        assert "graph_index" in result

    def test_graph_index_has_correct_fields(self, tmp_path):
        """Each graph entry should have name, file, entity_count, etc."""
        scope = tmp_path / "kb"
        scope.mkdir()
        (scope / "a.py").write_text("code")
        ont_dir = tmp_path / ".ontology"
        ont_dir.mkdir()
        ents = str(ont_dir / "_entities.jsonl")
        ontology.create_entity(
            "KnowledgeNode",
            {"label": "Module A", "node_type": "concept", "source_files": [str(scope / "a.py")],
             "dimensions": {"technology": "Python"}},
            ents,
        )
        result = graph_ops.build(str(scope), str(ont_dir), ents)
        gi = result["graph_index"]
        graph_entry = gi["graphs"][0]
        assert "name" in graph_entry
        assert "file" in graph_entry
        assert "description" in graph_entry
        assert "entity_count" in graph_entry
        assert "relation_count" in graph_entry
        assert "dimensions" in graph_entry
        assert "root_entity_id" in graph_entry
        assert "root_label" in graph_entry
        assert graph_entry["root_label"] == "Module A"
        assert graph_entry["entity_count"] == 1

    def test_graph_index_multiple_clusters(self, tmp_path):
        """Multiple clusters should produce multiple entries in graph index."""
        scope = tmp_path / "kb"
        scope.mkdir()
        (scope / "a.py").write_text("code a")
        (scope / "b.py").write_text("code b")
        ont_dir = tmp_path / ".ontology"
        ont_dir.mkdir()
        ents = str(ont_dir / "_entities.jsonl")
        # Two unrelated entities => two clusters
        ontology.create_entity(
            "KnowledgeNode",
            {"label": "Alpha", "node_type": "concept", "source_files": [str(scope / "a.py")]},
            ents,
        )
        ontology.create_entity(
            "KnowledgeNode",
            {"label": "Beta", "node_type": "concept", "source_files": [str(scope / "b.py")]},
            ents,
        )
        result = graph_ops.build(str(scope), str(ont_dir), ents)
        gi = result["graph_index"]
        assert len(gi["graphs"]) == 2

    def test_graph_index_empty_build(self, tmp_path):
        """Build with no entities should produce empty graphs list."""
        scope = tmp_path / "kb"
        scope.mkdir()
        ont_dir = tmp_path / ".ontology"
        ont_dir.mkdir()
        ents = str(ont_dir / "_entities.jsonl")
        Path(ents).touch()
        result = graph_ops.build(str(scope), str(ont_dir), ents)
        gi = result["graph_index"]
        assert gi["graphs"] == []
        assert (ont_dir / ".graph-index.json").exists()

    def test_graph_index_dimensions_collected(self, tmp_path):
        """Dimensions from entities should appear in graph index entries."""
        scope = tmp_path / "kb"
        scope.mkdir()
        (scope / "doc.md").write_text("test")
        ont_dir = tmp_path / ".ontology"
        ont_dir.mkdir()
        ents = str(ont_dir / "_entities.jsonl")
        ontology.create_entity(
            "KnowledgeNode",
            {
                "label": "Auth Module",
                "node_type": "concept",
                "source_files": [str(scope / "doc.md")],
                "dimensions": {"technology": "Python", "domain": "Security"},
            },
            ents,
        )
        result = graph_ops.build(str(scope), str(ont_dir), ents)
        dims = result["graph_index"]["graphs"][0]["dimensions"]
        assert "technology" in dims
        assert "domain" in dims

    def test_graph_index_atomic_write(self, tmp_path):
        """No .json.tmp file should remain after build."""
        scope = tmp_path / "kb"
        scope.mkdir()
        (scope / "f.py").write_text("x")
        ont_dir = tmp_path / ".ontology"
        ont_dir.mkdir()
        ents = str(ont_dir / "_entities.jsonl")
        ontology.create_entity(
            "KnowledgeNode",
            {"label": "F", "node_type": "concept", "source_files": [str(scope / "f.py")]},
            ents,
        )
        graph_ops.build(str(scope), str(ont_dir), ents)
        assert not (ont_dir / ".graph-index.json.tmp").exists()
        assert (ont_dir / ".graph-index.json").exists()

    def test_rebuild_replaces_old_index(self, tmp_path):
        """Rebuilding should replace the old .graph-index.json."""
        scope = tmp_path / "kb"
        scope.mkdir()
        (scope / "doc.md").write_text("test")
        ont_dir = tmp_path / ".ontology"
        ont_dir.mkdir()
        ents = str(ont_dir / "_entities.jsonl")
        ontology.create_entity(
            "KnowledgeNode",
            {"label": "First", "node_type": "concept", "source_files": [str(scope / "doc.md")]},
            ents,
        )
        graph_ops.build(str(scope), str(ont_dir), ents)
        old_content = (ont_dir / ".graph-index.json").read_text()
        # Add another entity and rebuild
        (scope / "doc2.md").write_text("test2")
        ontology.create_entity(
            "KnowledgeNode",
            {"label": "Second", "node_type": "concept", "source_files": [str(scope / "doc2.md")]},
            ents,
        )
        graph_ops.build(str(scope), str(ont_dir), ents)
        new_content = (ont_dir / ".graph-index.json").read_text()
        assert old_content != new_content
        assert len(json.loads(new_content)["graphs"]) == 2


class TestRetag:
    """Tests for ontology.py retag_files() function."""

    def _setup_intake(self, tmp_path, files_config):
        """Helper: set up a scope dir, ontology dir, and intake-status.json."""
        scope = tmp_path / "kb"
        scope.mkdir(parents=True, exist_ok=True)
        ont_dir = tmp_path / ".ontology"
        ont_dir.mkdir(exist_ok=True)
        ents = str(ont_dir / "_entities.jsonl")
        Path(ents).touch()

        status = {}
        for fname, dest_rel, file_status in files_config:
            dest = scope / dest_rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(f"content of {fname}")
            status[fname] = {"status": file_status, "destination": str(dest)}

        status_path = tmp_path / ".intake-status.json"
        status_path.write_text(json.dumps(status))
        return str(scope), str(ont_dir), str(status_path), ents

    def test_retag_happy_path(self, tmp_path):
        """Retag filed-untagged files creates entities and updates status."""
        scope, ont_dir, status_path, ents = self._setup_intake(tmp_path, [
            ("readme.md", "docs/readme.md", "filed-untagged"),
        ])
        result = ontology.retag_files(scope, ont_dir, status_path)
        assert result["retagged"] == 1
        assert result["failed"] == 0
        assert result["files"][0]["status"] == "tagged"
        assert result["files"][0]["entity_id"].startswith("know_")
        # Check status file updated
        with open(status_path) as f:
            updated = json.load(f)
        assert updated["readme.md"]["status"] == "filed"

    def test_retag_no_untagged_files(self, tmp_path):
        """Retag with no filed-untagged entries returns zeros."""
        scope, ont_dir, status_path, _ = self._setup_intake(tmp_path, [
            ("readme.md", "docs/readme.md", "filed"),
        ])
        result = ontology.retag_files(scope, ont_dir, status_path)
        assert result["retagged"] == 0
        assert result["failed"] == 0
        assert result["files"] == []

    def test_retag_file_not_found(self, tmp_path):
        """Retag fails gracefully when destination file is missing."""
        scope = tmp_path / "kb"
        scope.mkdir()
        ont_dir = tmp_path / ".ontology"
        ont_dir.mkdir()
        Path(ont_dir / "_entities.jsonl").touch()
        # Point to non-existent file
        missing = scope / "gone" / "missing.md"
        status = {"missing.md": {"status": "filed-untagged", "destination": str(missing)}}
        status_path = tmp_path / ".intake-status.json"
        status_path.write_text(json.dumps(status))
        result = ontology.retag_files(str(scope), str(ont_dir), str(status_path))
        assert result["retagged"] == 0
        assert result["failed"] == 1
        assert "not found" in result["files"][0]["error"].lower()

    def test_retag_mixed_statuses(self, tmp_path):
        """Only filed-untagged files are processed; filed and pending are skipped."""
        scope, ont_dir, status_path, _ = self._setup_intake(tmp_path, [
            ("a.md", "docs/a.md", "filed-untagged"),
            ("b.md", "docs/b.md", "filed"),
            ("c.md", "docs/c.md", "pending"),
        ])
        result = ontology.retag_files(scope, ont_dir, status_path)
        assert result["retagged"] == 1
        assert result["failed"] == 0
        assert len(result["files"]) == 1
        assert result["files"][0]["file"] == "a.md"

    def test_retag_out_of_scope(self, tmp_path):
        """Files outside scope are not processed even if filed-untagged."""
        scope = tmp_path / "kb"
        scope.mkdir()
        other = tmp_path / "other"
        other.mkdir()
        (other / "external.md").write_text("content")
        ont_dir = tmp_path / ".ontology"
        ont_dir.mkdir()
        Path(ont_dir / "_entities.jsonl").touch()
        status = {"external.md": {"status": "filed-untagged", "destination": str(other / "external.md")}}
        status_path = tmp_path / ".intake-status.json"
        status_path.write_text(json.dumps(status))
        result = ontology.retag_files(str(scope), str(ont_dir), str(status_path))
        assert result["retagged"] == 0

    def test_retag_updates_existing_entity(self, tmp_path):
        """Retag finds existing entity for same source file and updates instead of creating."""
        scope = tmp_path / "kb"
        scope.mkdir()
        doc = scope / "doc.md"
        doc.write_text("content")
        ont_dir = tmp_path / ".ontology"
        ont_dir.mkdir()
        ents = str(ont_dir / "_entities.jsonl")
        # Pre-create entity
        existing = ontology.create_entity(
            "KnowledgeNode",
            {"label": "Doc", "node_type": "document", "source_files": [str(doc)]},
            ents,
        )
        status = {"doc.md": {"status": "filed-untagged", "destination": str(doc)}}
        status_path = tmp_path / ".intake-status.json"
        status_path.write_text(json.dumps(status))
        result = ontology.retag_files(str(scope), str(ont_dir), str(status_path))
        assert result["retagged"] == 1
        assert result["files"][0]["entity_id"] == existing["id"]

    def test_retag_intake_status_not_found(self, tmp_path):
        """Retag raises ValueError when intake status file doesn't exist."""
        with pytest.raises(ValueError, match="not found"):
            ontology.retag_files(
                str(tmp_path), str(tmp_path), str(tmp_path / "nonexistent.json")
            )

    def test_retag_cli_happy_path(self, tmp_path, capsys):
        """Test retag via CLI main()."""
        scope = tmp_path / "kb"
        scope.mkdir()
        doc = scope / "doc.md"
        doc.write_text("content")
        ont_dir = tmp_path / ".ontology"
        ont_dir.mkdir()
        Path(ont_dir / "_entities.jsonl").touch()
        status = {"doc.md": {"status": "filed-untagged", "destination": str(doc)}}
        status_path = tmp_path / ".intake-status.json"
        status_path.write_text(json.dumps(status))
        sys.argv = [
            "ontology.py", "retag",
            "--scope", str(scope),
            "--ontology-dir", str(ont_dir),
            "--intake-status", str(status_path),
        ]
        try:
            ontology.main()
        except SystemExit:
            pass
        captured = capsys.readouterr()
        result = json.loads(captured.out)
        assert result["retagged"] == 1
