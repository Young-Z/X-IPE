"""
Tests for FEATURE-023-C: Trace Viewer & DAG Visualization

TDD test suite for the trace log parser, get_trace service method,
and /api/tracing/logs/{trace_id} endpoint.

Run with: pytest tests/test_tracing_graph.py -v
"""
import pytest
import json
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os


# =============================================================================
# UNIT TESTS: TraceLogParser
# =============================================================================

class TestTraceLogParser:
    """Unit tests for trace log file parsing."""
    
    @pytest.fixture
    def sample_trace_log(self, tmp_path):
        """Create a sample trace log file for testing."""
        log_content = """[TRACE-START] 550e8400-e29b-41d4-a716-446655440000 | POST /api/orders | 2026-02-01T04:15:30Z
  [INFO] → start_function: validate_order | {"order_id": "O001", "items": [{"id": "I1"}]}
  [DEBUG] → start_function: check_inventory | {"item_ids": ["I1"]}
  [DEBUG] ← return_function: check_inventory | {"available": true} | 12ms
  [INFO] ← return_function: validate_order | {"valid": true} | 45ms
  [INFO] → start_function: process_payment | {"amount": 99.99}
  [INFO] ← return_function: process_payment | {"status": "success"} | 230ms
[TRACE-END] 550e8400-e29b-41d4-a716-446655440000 | 287ms | SUCCESS
"""
        log_file = tmp_path / "20260201-041530-post-api-orders-550e8400.log"
        log_file.write_text(log_content)
        return log_file
    
    @pytest.fixture
    def error_trace_log(self, tmp_path):
        """Create a trace log with error for testing."""
        log_content = """[TRACE-START] abc12345-def6-7890 | POST /api/payments | 2026-02-01T05:00:00Z
  [INFO] → start_function: charge_card | {"amount": 50.00, "card": "[REDACTED]"}
  [ERROR] ← exception: charge_card | PaymentError: Card declined | 150ms
    at charge_card (payment.py:42)
    at process_order (orders.py:15)
[TRACE-END] abc12345-def6-7890 | 150ms | ERROR
"""
        log_file = tmp_path / "20260201-050000-post-api-payments-abc12345.log"
        log_file.write_text(log_content)
        return log_file
    
    def test_parser_returns_trace_id(self, sample_trace_log):
        """Parser should extract trace_id from log."""
        from x_ipe.tracing.parser import TraceLogParser
        
        parser = TraceLogParser()
        result = parser.parse(sample_trace_log)
        
        assert result["trace_id"] == "550e8400-e29b-41d4-a716-446655440000"
    
    def test_parser_returns_api_name(self, sample_trace_log):
        """Parser should extract API name from TRACE-START."""
        from x_ipe.tracing.parser import TraceLogParser
        
        parser = TraceLogParser()
        result = parser.parse(sample_trace_log)
        
        assert result["api"] == "POST /api/orders"
    
    def test_parser_returns_timestamp(self, sample_trace_log):
        """Parser should extract timestamp from TRACE-START."""
        from x_ipe.tracing.parser import TraceLogParser
        
        parser = TraceLogParser()
        result = parser.parse(sample_trace_log)
        
        assert result["timestamp"] == "2026-02-01T04:15:30Z"
    
    def test_parser_returns_total_time(self, sample_trace_log):
        """Parser should extract total execution time from TRACE-END."""
        from x_ipe.tracing.parser import TraceLogParser
        
        parser = TraceLogParser()
        result = parser.parse(sample_trace_log)
        
        assert result["total_time_ms"] == 287
    
    def test_parser_returns_status_success(self, sample_trace_log):
        """Parser should return 'success' status for successful traces."""
        from x_ipe.tracing.parser import TraceLogParser
        
        parser = TraceLogParser()
        result = parser.parse(sample_trace_log)
        
        assert result["status"] == "success"
    
    def test_parser_returns_status_error(self, error_trace_log):
        """Parser should return 'error' status for traces with errors."""
        from x_ipe.tracing.parser import TraceLogParser
        
        parser = TraceLogParser()
        result = parser.parse(error_trace_log)
        
        assert result["status"] == "error"
    
    def test_parser_creates_nodes_list(self, sample_trace_log):
        """Parser should create nodes list from function calls."""
        from x_ipe.tracing.parser import TraceLogParser
        
        parser = TraceLogParser()
        result = parser.parse(sample_trace_log)
        
        assert "nodes" in result
        assert isinstance(result["nodes"], list)
        assert len(result["nodes"]) == 4  # API + 3 functions
    
    def test_parser_node_has_required_fields(self, sample_trace_log):
        """Each node should have id, label, timing, status, level, input, output."""
        from x_ipe.tracing.parser import TraceLogParser
        
        parser = TraceLogParser()
        result = parser.parse(sample_trace_log)
        
        node = result["nodes"][0]
        assert "id" in node
        assert "label" in node
        assert "timing" in node
        assert "status" in node
        assert "level" in node
        assert "input" in node
        assert "output" in node
    
    def test_parser_root_node_is_api(self, sample_trace_log):
        """First node should be the API entry point with level='API'."""
        from x_ipe.tracing.parser import TraceLogParser
        
        parser = TraceLogParser()
        result = parser.parse(sample_trace_log)
        
        root = result["nodes"][0]
        assert root["label"] == "POST /api/orders"
        assert root["level"] == "API"
        assert root["timing"] == "287ms"
    
    def test_parser_function_node_has_correct_level(self, sample_trace_log):
        """Function nodes should have INFO or DEBUG level."""
        from x_ipe.tracing.parser import TraceLogParser
        
        parser = TraceLogParser()
        result = parser.parse(sample_trace_log)
        
        # validate_order should be INFO
        validate_node = next(n for n in result["nodes"] if n["label"] == "validate_order")
        assert validate_node["level"] == "INFO"
        
        # check_inventory should be DEBUG
        inventory_node = next(n for n in result["nodes"] if n["label"] == "check_inventory")
        assert inventory_node["level"] == "DEBUG"
    
    def test_parser_function_node_has_timing(self, sample_trace_log):
        """Function nodes should have execution timing."""
        from x_ipe.tracing.parser import TraceLogParser
        
        parser = TraceLogParser()
        result = parser.parse(sample_trace_log)
        
        validate_node = next(n for n in result["nodes"] if n["label"] == "validate_order")
        assert validate_node["timing"] == "45ms"
    
    def test_parser_function_node_has_input_output(self, sample_trace_log):
        """Function nodes should have input and output JSON."""
        from x_ipe.tracing.parser import TraceLogParser
        
        parser = TraceLogParser()
        result = parser.parse(sample_trace_log)
        
        validate_node = next(n for n in result["nodes"] if n["label"] == "validate_order")
        assert validate_node["input"] is not None
        assert validate_node["output"] is not None
        assert "order_id" in validate_node["input"]
        assert "valid" in validate_node["output"]
    
    def test_parser_creates_edges_list(self, sample_trace_log):
        """Parser should create edges list for call relationships."""
        from x_ipe.tracing.parser import TraceLogParser
        
        parser = TraceLogParser()
        result = parser.parse(sample_trace_log)
        
        assert "edges" in result
        assert isinstance(result["edges"], list)
        assert len(result["edges"]) >= 2  # API->validate, validate->inventory, etc.
    
    def test_parser_edge_has_source_target(self, sample_trace_log):
        """Each edge should have source and target node IDs."""
        from x_ipe.tracing.parser import TraceLogParser
        
        parser = TraceLogParser()
        result = parser.parse(sample_trace_log)
        
        for edge in result["edges"]:
            assert "source" in edge
            assert "target" in edge
    
    def test_parser_edges_connect_parent_child(self, sample_trace_log):
        """Edges should connect parent function to child function."""
        from x_ipe.tracing.parser import TraceLogParser
        
        parser = TraceLogParser()
        result = parser.parse(sample_trace_log)
        
        # Find node IDs
        nodes_by_label = {n["label"]: n["id"] for n in result["nodes"]}
        
        # API should connect to validate_order
        api_to_validate = next(
            (e for e in result["edges"] 
             if e["source"] == nodes_by_label["POST /api/orders"] 
             and e["target"] == nodes_by_label["validate_order"]),
            None
        )
        assert api_to_validate is not None
    
    def test_parser_error_node_has_error_info(self, error_trace_log):
        """Error nodes should have error field with type, message, stack."""
        from x_ipe.tracing.parser import TraceLogParser
        
        parser = TraceLogParser()
        result = parser.parse(error_trace_log)
        
        # Find the node with error details (not just status=error)
        error_node = next(n for n in result["nodes"] if n["error"] is not None)
        assert error_node["status"] == "error"
        assert error_node["error"]["type"] == "PaymentError"
        assert "Card declined" in error_node["error"]["message"]
    
    def test_parser_error_node_has_stack_trace(self, error_trace_log):
        """Error nodes should have stack trace with func, file, line."""
        from x_ipe.tracing.parser import TraceLogParser
        
        parser = TraceLogParser()
        result = parser.parse(error_trace_log)
        
        # Find the node with error details
        error_node = next(n for n in result["nodes"] if n["error"] is not None)
        assert "stack" in error_node["error"]
        assert len(error_node["error"]["stack"]) >= 1
        
        stack_line = error_node["error"]["stack"][0]
        assert "func" in stack_line
        assert "file" in stack_line
    
    def test_parser_handles_empty_file(self, tmp_path):
        """Parser should handle empty log file gracefully."""
        from x_ipe.tracing.parser import TraceLogParser
        
        log_file = tmp_path / "empty.log"
        log_file.write_text("")
        
        parser = TraceLogParser()
        result = parser.parse(log_file)
        
        assert result["nodes"] == []
        assert result["edges"] == []
    
    def test_parser_handles_malformed_line(self, tmp_path):
        """Parser should skip malformed lines and continue parsing."""
        from x_ipe.tracing.parser import TraceLogParser
        
        log_content = """[TRACE-START] abc-123 | GET /api/test | 2026-02-01T00:00:00Z
  [INFO] → this is a malformed line without proper format
  [INFO] → start_function: valid_func | {"key": "value"}
  [INFO] ← return_function: valid_func | {"result": true} | 10ms
[TRACE-END] abc-123 | 10ms | SUCCESS
"""
        log_file = tmp_path / "malformed.log"
        log_file.write_text(log_content)
        
        parser = TraceLogParser()
        result = parser.parse(log_file)
        
        # Should still parse the valid function
        assert len(result["nodes"]) >= 1


# =============================================================================
# UNIT TESTS: TracingService.get_trace
# =============================================================================

class TestTracingServiceGetTrace:
    """Unit tests for TracingService.get_trace method."""
    
    @pytest.fixture
    def service_with_logs(self, tmp_path):
        """Create TracingService with sample log files."""
        from x_ipe.services.tracing_service import TracingService
        
        # Create traces directory
        traces_dir = tmp_path / "instance" / "traces"
        traces_dir.mkdir(parents=True)
        
        # Create sample log file
        log_content = """[TRACE-START] test-trace-id-123 | GET /api/users | 2026-02-01T12:00:00Z
  [INFO] → start_function: get_user | {"user_id": "U001"}
  [INFO] ← return_function: get_user | {"name": "John"} | 50ms
[TRACE-END] test-trace-id-123 | 50ms | SUCCESS
"""
        log_file = traces_dir / "20260201-120000-get-api-users-test-trace-id-123.log"
        log_file.write_text(log_content)
        
        # Create tools.json
        tools_json = tmp_path / "tools.json"
        tools_json.write_text(json.dumps({
            "tracing_log_path": "instance/traces/"
        }))
        
        return TracingService(str(tmp_path))
    
    def test_get_trace_returns_parsed_data(self, service_with_logs):
        """get_trace should return parsed trace data."""
        result = service_with_logs.get_trace("test-trace-id-123")
        
        assert result is not None
        assert "trace_id" in result
        assert "nodes" in result
        assert "edges" in result
    
    def test_get_trace_not_found_returns_none(self, service_with_logs):
        """get_trace should return None for non-existent trace."""
        result = service_with_logs.get_trace("nonexistent-trace-id")
        
        assert result is None
    
    def test_get_trace_matches_partial_id(self, service_with_logs):
        """get_trace should match partial trace IDs."""
        result = service_with_logs.get_trace("test-trace-id")
        
        assert result is not None
        assert result["trace_id"] == "test-trace-id-123"


# =============================================================================
# API TESTS: GET /api/tracing/logs/{trace_id}
# =============================================================================

class TestGetTraceEndpoint:
    """API tests for GET /api/tracing/logs/{trace_id} endpoint."""
    
    @pytest.fixture
    def client(self, tmp_path):
        """Create Flask test client with tracing routes."""
        from x_ipe.app import create_app
        
        # Create traces directory with sample log
        traces_dir = tmp_path / "instance" / "traces"
        traces_dir.mkdir(parents=True)
        
        log_content = """[TRACE-START] api-test-trace-001 | POST /api/orders | 2026-02-01T10:00:00Z
  [INFO] → start_function: create_order | {"item": "Widget"}
  [INFO] ← return_function: create_order | {"order_id": "ORD-123"} | 100ms
[TRACE-END] api-test-trace-001 | 100ms | SUCCESS
"""
        log_file = traces_dir / "20260201-100000-post-api-orders-api-test-trace-001.log"
        log_file.write_text(log_content)
        
        # Create tools.json
        tools_json = tmp_path / "tools.json"
        tools_json.write_text(json.dumps({
            "tracing_enabled": False,
            "tracing_log_path": "instance/traces/"
        }))
        
        app = create_app({
            'PROJECT_ROOT': str(tmp_path),
            'TESTING': True
        })
        
        with app.test_client() as client:
            yield client
    
    def test_get_trace_endpoint_returns_200(self, client):
        """GET /api/tracing/logs/{trace_id} should return 200 for valid trace."""
        response = client.get('/api/tracing/logs/api-test-trace-001')
        
        assert response.status_code == 200
    
    def test_get_trace_endpoint_returns_json(self, client):
        """GET /api/tracing/logs/{trace_id} should return JSON."""
        response = client.get('/api/tracing/logs/api-test-trace-001')
        
        data = response.get_json()
        assert data is not None
        assert "trace_id" in data
        assert "nodes" in data
        assert "edges" in data
    
    def test_get_trace_endpoint_returns_404_not_found(self, client):
        """GET /api/tracing/logs/{trace_id} should return 404 for missing trace."""
        response = client.get('/api/tracing/logs/nonexistent-id')
        
        assert response.status_code == 404
        data = response.get_json()
        assert "error" in data
    
    def test_get_trace_endpoint_returns_nodes_with_structure(self, client):
        """Nodes should have required structure for graph visualization."""
        response = client.get('/api/tracing/logs/api-test-trace-001')
        data = response.get_json()
        
        assert len(data["nodes"]) >= 1
        node = data["nodes"][0]
        assert "id" in node
        assert "label" in node
        assert "timing" in node
        assert "status" in node
        assert "level" in node
    
    def test_get_trace_endpoint_returns_edges_with_structure(self, client):
        """Edges should have source and target for graph visualization."""
        response = client.get('/api/tracing/logs/api-test-trace-001')
        data = response.get_json()
        
        for edge in data["edges"]:
            assert "source" in edge
            assert "target" in edge


# =============================================================================
# INTEGRATION TESTS: Parser + Service + API
# =============================================================================

class TestTracingGraphIntegration:
    """Integration tests for trace graph pipeline."""
    
    @pytest.fixture
    def full_trace_setup(self, tmp_path):
        """Create complete tracing setup with complex trace."""
        from x_ipe.app import create_app
        
        traces_dir = tmp_path / "instance" / "traces"
        traces_dir.mkdir(parents=True)
        
        # Complex multi-level trace
        log_content = """[TRACE-START] complex-trace-xyz | POST /api/checkout | 2026-02-01T14:00:00Z
  [INFO] → start_function: validate_cart | {"cart_id": "C001"}
  [DEBUG] → start_function: check_items | {"items": ["I1", "I2"]}
  [DEBUG] ← return_function: check_items | {"valid": true} | 15ms
  [INFO] ← return_function: validate_cart | {"ok": true} | 25ms
  [INFO] → start_function: process_payment | {"amount": 150.00}
  [INFO] ← return_function: process_payment | {"txn_id": "TXN-456"} | 200ms
  [INFO] → start_function: send_confirmation | {"email": "test@test.com"}
  [INFO] ← return_function: send_confirmation | {"sent": true} | 50ms
[TRACE-END] complex-trace-xyz | 275ms | SUCCESS
"""
        log_file = traces_dir / "20260201-140000-post-api-checkout-complex-trace-xyz.log"
        log_file.write_text(log_content)
        
        tools_json = tmp_path / "tools.json"
        tools_json.write_text(json.dumps({
            "tracing_log_path": "instance/traces/"
        }))
        
        app = create_app({
            'PROJECT_ROOT': str(tmp_path),
            'TESTING': True
        })
        
        with app.test_client() as client:
            yield client
    
    def test_complex_trace_has_correct_node_count(self, full_trace_setup):
        """Complex trace should have all nodes parsed."""
        response = full_trace_setup.get('/api/tracing/logs/complex-trace-xyz')
        data = response.get_json()
        
        # API + validate_cart + check_items + process_payment + send_confirmation = 5
        assert len(data["nodes"]) == 5
    
    def test_complex_trace_has_correct_edge_count(self, full_trace_setup):
        """Complex trace should have correct parent-child edges."""
        response = full_trace_setup.get('/api/tracing/logs/complex-trace-xyz')
        data = response.get_json()
        
        # API->validate, validate->check_items, API->process, API->send = 4
        assert len(data["edges"]) >= 3
    
    def test_complex_trace_nested_functions(self, full_trace_setup):
        """Nested functions should be connected properly."""
        response = full_trace_setup.get('/api/tracing/logs/complex-trace-xyz')
        data = response.get_json()
        
        nodes_by_label = {n["label"]: n["id"] for n in data["nodes"]}
        
        # check_items should be child of validate_cart
        validate_id = nodes_by_label["validate_cart"]
        check_id = nodes_by_label["check_items"]
        
        parent_child_edge = next(
            (e for e in data["edges"] if e["source"] == validate_id and e["target"] == check_id),
            None
        )
        assert parent_child_edge is not None


# =============================================================================
# FRONTEND TESTS (JavaScript mocks for documentation)
# =============================================================================

class TestFrontendContracts:
    """Document expected frontend behavior for manual testing."""
    
    def test_graph_api_response_format(self):
        """Document the expected API response format for frontend."""
        expected_response = {
            "trace_id": "string - UUID",
            "api": "string - HTTP method + path",
            "timestamp": "string - ISO 8601",
            "total_time_ms": "number - milliseconds",
            "status": "string - 'success' or 'error'",
            "nodes": [
                {
                    "id": "string - unique node ID",
                    "label": "string - function name",
                    "timing": "string - e.g. '45ms'",
                    "status": "string - 'success' or 'error'",
                    "level": "string - 'API', 'INFO', or 'DEBUG'",
                    "input": "string - JSON",
                    "output": "string - JSON or null",
                    "error": "object or null - {type, message, stack}"
                }
            ],
            "edges": [
                {
                    "source": "string - parent node ID",
                    "target": "string - child node ID"
                }
            ]
        }
        
        # This test documents the contract
        assert "trace_id" in expected_response
        assert "nodes" in expected_response
        assert "edges" in expected_response
    
    def test_error_node_structure(self):
        """Document error node structure for frontend modal."""
        expected_error = {
            "type": "string - exception class name",
            "message": "string - error message",
            "stack": [
                {
                    "func": "string - function name",
                    "file": "string - file path",
                    "line": "number - line number (optional)"
                }
            ]
        }
        
        assert "type" in expected_error
        assert "message" in expected_error
        assert "stack" in expected_error
