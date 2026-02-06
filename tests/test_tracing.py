"""
Tests for FEATURE-023: Application Action Tracing - Core

TDD test suite for the tracing decorator, context management, buffer,
log writer, redactor, service, and API endpoints.

Run with: pytest tests/test_tracing.py -v
"""
import pytest
import json
import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os


# =============================================================================
# UNIT TESTS: Redactor
# =============================================================================

class TestRedactor:
    """Unit tests for sensitive data redaction."""
    
    def test_redact_password_field(self):
        """AC-5.1: Fields containing 'password' should be redacted."""
        from x_ipe.tracing.redactor import Redactor
        
        redactor = Redactor()
        data = {"username": "john", "password": "secret123"}
        result = redactor.redact(data)
        
        assert result["username"] == "john"
        assert result["password"] == "[REDACTED]"
    
    def test_redact_password_case_insensitive(self):
        """AC-5.1: Password redaction should be case-insensitive."""
        from x_ipe.tracing.redactor import Redactor
        
        redactor = Redactor()
        data = {"PASSWORD": "secret", "userPassword": "hidden"}
        result = redactor.redact(data)
        
        assert result["PASSWORD"] == "[REDACTED]"
        assert result["userPassword"] == "[REDACTED]"
    
    def test_redact_secret_field(self):
        """AC-5.2: Fields containing 'secret' should be redacted."""
        from x_ipe.tracing.redactor import Redactor
        
        redactor = Redactor()
        data = {"client_secret": "abc123", "name": "test"}
        result = redactor.redact(data)
        
        assert result["client_secret"] == "[REDACTED]"
        assert result["name"] == "test"
    
    def test_redact_token_field(self):
        """AC-5.3: Fields containing 'token' should be redacted."""
        from x_ipe.tracing.redactor import Redactor
        
        redactor = Redactor()
        data = {"access_token": "tok_123", "refresh_token": "ref_456"}
        result = redactor.redact(data)
        
        assert result["access_token"] == "[REDACTED]"
        assert result["refresh_token"] == "[REDACTED]"
    
    def test_redact_api_key_field(self):
        """AC-5.4: Fields containing 'api_key' or 'apiKey' should be redacted."""
        from x_ipe.tracing.redactor import Redactor
        
        redactor = Redactor()
        data = {"api_key": "sk_live_xxx", "apiKey": "pk_test_yyy"}
        result = redactor.redact(data)
        
        assert result["api_key"] == "[REDACTED]"
        assert result["apiKey"] == "[REDACTED]"
    
    def test_redact_credit_card_pattern(self):
        """AC-5.5: 16-digit numbers (credit cards) should be redacted."""
        from x_ipe.tracing.redactor import Redactor
        
        redactor = Redactor()
        data = {"card_number": "4111111111111111", "cvv": "123"}
        result = redactor.redact(data)
        
        assert result["card_number"] == "[REDACTED]"
        assert result["cvv"] == "123"  # Not 16 digits
    
    def test_redact_jwt_pattern(self):
        """AC-5.6: JWT tokens (starting with eyJ) should be redacted."""
        from x_ipe.tracing.redactor import Redactor
        
        redactor = Redactor()
        jwt = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.dozjg"
        data = {"auth": jwt, "name": "test"}
        result = redactor.redact(data)
        
        assert result["auth"] == "[REDACTED]"
        assert result["name"] == "test"
    
    def test_redact_replacement_text(self):
        """AC-5.7: Redacted values should be replaced with '[REDACTED]'."""
        from x_ipe.tracing.redactor import Redactor
        
        redactor = Redactor()
        data = {"password": "anything"}
        result = redactor.redact(data)
        
        assert result["password"] == "[REDACTED]"
    
    def test_redact_custom_fields(self):
        """AC-5.8: Custom redact fields from decorator should be honored."""
        from x_ipe.tracing.redactor import Redactor
        
        redactor = Redactor(custom_fields=["ssn", "dob"])
        data = {"ssn": "123-45-6789", "dob": "1990-01-01", "name": "John"}
        result = redactor.redact(data)
        
        assert result["ssn"] == "[REDACTED]"
        assert result["dob"] == "[REDACTED]"
        assert result["name"] == "John"
    
    def test_redact_nested_dict(self):
        """Redaction should work on nested dictionaries."""
        from x_ipe.tracing.redactor import Redactor
        
        redactor = Redactor()
        data = {
            "user": {
                "email": "test@example.com",
                "password": "secret"
            }
        }
        result = redactor.redact(data)
        
        assert result["user"]["email"] == "test@example.com"
        assert result["user"]["password"] == "[REDACTED]"
    
    def test_redact_list_of_dicts(self):
        """Redaction should work on lists of dictionaries."""
        from x_ipe.tracing.redactor import Redactor
        
        redactor = Redactor()
        data = [
            {"username": "user1", "password": "pass1"},
            {"username": "user2", "password": "pass2"}
        ]
        result = redactor.redact(data)
        
        assert result[0]["password"] == "[REDACTED]"
        assert result[1]["password"] == "[REDACTED]"
    
    def test_redact_preserves_non_sensitive_data(self):
        """Non-sensitive data should be preserved unchanged."""
        from x_ipe.tracing.redactor import Redactor
        
        redactor = Redactor()
        data = {"id": 123, "name": "test", "active": True, "count": 0}
        result = redactor.redact(data)
        
        assert result == data


# =============================================================================
# UNIT TESTS: TraceBuffer
# =============================================================================

class TestTraceBuffer:
    """Unit tests for in-memory trace buffer."""
    
    def test_buffer_creation(self):
        """Buffer should initialize with trace_id and root_api."""
        from x_ipe.tracing.buffer import TraceBuffer
        
        buffer = TraceBuffer("abc-123", "POST /api/orders")
        
        assert buffer.trace_id == "abc-123"
        assert buffer.root_api == "POST /api/orders"
        assert buffer.entries == []
    
    def test_buffer_add_entry(self):
        """Buffer should accept trace entries."""
        from x_ipe.tracing.buffer import TraceBuffer, TraceEntry
        
        buffer = TraceBuffer("abc-123", "POST /api/orders")
        entry = TraceEntry(
            timestamp=datetime.now(timezone.utc),
            trace_id="abc-123",
            level="INFO",
            direction="→",
            event_type="start_function",
            function_name="process_order",
            data={"order_id": "O001"},
            depth=0
        )
        
        buffer.add(entry)
        
        assert len(buffer.entries) == 1
        assert buffer.entries[0].function_name == "process_order"
    
    def test_buffer_max_size_limit(self):
        """Buffer should not exceed 10MB limit."""
        from x_ipe.tracing.buffer import TraceBuffer, TraceEntry
        
        buffer = TraceBuffer("abc-123", "POST /api/orders")
        buffer.MAX_SIZE = 1000  # Set small limit for testing
        
        # Add entries until limit reached
        large_data = {"data": "x" * 500}
        for i in range(10):
            entry = TraceEntry(
                timestamp=datetime.now(timezone.utc),
                trace_id="abc-123",
                level="INFO",
                direction="→",
                event_type="start_function",
                function_name=f"func_{i}",
                data=large_data,
                depth=0
            )
            buffer.add(entry)
        
        # Buffer should have stopped accepting entries
        assert buffer._size <= buffer.MAX_SIZE + 500  # Some tolerance
    
    def test_buffer_to_log_string_format(self):
        """Buffer should produce correctly formatted log string."""
        from x_ipe.tracing.buffer import TraceBuffer, TraceEntry
        
        buffer = TraceBuffer("abc-123", "POST /api/orders")
        buffer.add(TraceEntry(
            timestamp=datetime.now(timezone.utc),
            trace_id="abc-123",
            level="INFO",
            direction="→",
            event_type="start_function",
            function_name="process_order",
            data={"order_id": "O001"},
            depth=0
        ))
        
        log_str = buffer.to_log_string("SUCCESS", 100.0)
        
        assert "[TRACE-START] abc-123" in log_str
        assert "[TRACE-END] abc-123" in log_str
        assert "100ms" in log_str
        assert "SUCCESS" in log_str
    
    def test_buffer_indentation_by_depth(self):
        """Log output should indent based on call depth."""
        from x_ipe.tracing.buffer import TraceBuffer, TraceEntry
        
        buffer = TraceBuffer("abc-123", "POST /api/orders")
        buffer.add(TraceEntry(
            timestamp=datetime.now(timezone.utc),
            trace_id="abc-123",
            level="INFO",
            direction="→",
            event_type="start_function",
            function_name="outer",
            data={},
            depth=0
        ))
        buffer.add(TraceEntry(
            timestamp=datetime.now(timezone.utc),
            trace_id="abc-123",
            level="DEBUG",
            direction="→",
            event_type="start_function",
            function_name="inner",
            data={},
            depth=1
        ))
        
        log_str = buffer.to_log_string("SUCCESS", 50.0)
        lines = log_str.split("\n")
        
        # Nested call should have more indentation
        outer_line = [l for l in lines if "outer" in l][0]
        inner_line = [l for l in lines if "inner" in l][0]
        
        assert inner_line.startswith("    ")  # More indented


# =============================================================================
# UNIT TESTS: TraceContext
# =============================================================================

class TestTraceContext:
    """Unit tests for trace context management."""
    
    def test_start_trace_generates_uuid(self):
        """AC-3.1: start_trace should generate unique UUID trace ID."""
        from x_ipe.tracing.context import TraceContext
        
        ctx = TraceContext.start_trace("POST /api/orders")
        
        assert ctx.trace_id is not None
        assert len(ctx.trace_id) > 0
        
        # Cleanup
        TraceContext.end_trace()
    
    def test_start_trace_creates_buffer(self):
        """start_trace should create in-memory buffer."""
        from x_ipe.tracing.context import TraceContext
        
        ctx = TraceContext.start_trace("POST /api/orders")
        
        assert ctx.buffer is not None
        assert ctx.buffer.root_api == "POST /api/orders"
        
        TraceContext.end_trace()
    
    def test_get_current_returns_active_context(self):
        """get_current should return the active trace context."""
        from x_ipe.tracing.context import TraceContext
        
        ctx1 = TraceContext.start_trace("GET /api/users")
        ctx2 = TraceContext.get_current()
        
        assert ctx1 is ctx2
        
        TraceContext.end_trace()
    
    def test_get_current_returns_none_when_inactive(self):
        """get_current should return None when no active trace."""
        from x_ipe.tracing.context import TraceContext
        
        # Ensure no active context
        TraceContext.end_trace()
        
        ctx = TraceContext.get_current()
        
        assert ctx is None
    
    def test_end_trace_returns_buffer(self):
        """AC-3.6: end_trace should return the trace buffer."""
        from x_ipe.tracing.context import TraceContext
        
        ctx = TraceContext.start_trace("POST /api/orders")
        buffer = TraceContext.end_trace()
        
        assert buffer is not None
        assert buffer.trace_id == ctx.trace_id
    
    def test_end_trace_clears_context(self):
        """end_trace should clear the active context."""
        from x_ipe.tracing.context import TraceContext
        
        TraceContext.start_trace("POST /api/orders")
        TraceContext.end_trace()
        
        assert TraceContext.get_current() is None
    
    def test_push_call_increments_depth(self):
        """AC-3.4: push_call should increment nesting depth."""
        from x_ipe.tracing.context import TraceContext
        
        ctx = TraceContext.start_trace("POST /api/orders")
        
        assert ctx.depth == 0
        ctx.push_call("func1")
        assert ctx.depth == 1
        ctx.push_call("func2")
        assert ctx.depth == 2
        
        TraceContext.end_trace()
    
    def test_pop_call_decrements_depth(self):
        """pop_call should decrement nesting depth."""
        from x_ipe.tracing.context import TraceContext
        
        ctx = TraceContext.start_trace("POST /api/orders")
        ctx.push_call("func1")
        ctx.push_call("func2")
        
        ctx.pop_call()
        assert ctx.depth == 1
        ctx.pop_call()
        assert ctx.depth == 0
        
        TraceContext.end_trace()
    
    def test_trace_id_propagates_to_nested_calls(self):
        """AC-3.2: Trace ID should propagate to nested function calls."""
        from x_ipe.tracing.context import TraceContext
        
        ctx = TraceContext.start_trace("POST /api/orders")
        original_id = ctx.trace_id
        
        ctx.push_call("nested_func")
        nested_ctx = TraceContext.get_current()
        
        assert nested_ctx.trace_id == original_id
        
        TraceContext.end_trace()


# =============================================================================
# UNIT TESTS: Decorator
# =============================================================================

class TestTracingDecorator:
    """Unit tests for @x_ipe_tracing decorator."""
    
    def test_decorator_with_skip_level(self):
        """Decorator with level='SKIP' should be no-op."""
        from x_ipe.tracing.decorator import x_ipe_tracing
        
        @x_ipe_tracing(level="SKIP")
        def my_func():
            return "result"
        
        result = my_func()
        assert result == "result"
    
    def test_decorator_preserves_function_name(self):
        """Decorator should preserve original function metadata."""
        from x_ipe.tracing.decorator import x_ipe_tracing
        
        @x_ipe_tracing(level="INFO")
        def my_special_func():
            """My docstring."""
            return 42
        
        assert my_special_func.__name__ == "my_special_func"
        assert "My docstring" in my_special_func.__doc__
    
    def test_decorator_returns_original_value(self):
        """Decorator should return the original function's return value."""
        from x_ipe.tracing.decorator import x_ipe_tracing
        from x_ipe.tracing.context import TraceContext
        
        @x_ipe_tracing(level="INFO")
        def add(a, b):
            return a + b
        
        TraceContext.start_trace("TEST")
        result = add(2, 3)
        TraceContext.end_trace()
        
        assert result == 5
    
    def test_decorator_logs_entry(self):
        """AC-1.4: Decorator should log function entry with parameters."""
        from x_ipe.tracing.decorator import x_ipe_tracing
        from x_ipe.tracing.context import TraceContext
        
        @x_ipe_tracing(level="INFO")
        def greet(name):
            return f"Hello, {name}"
        
        TraceContext.start_trace("TEST")
        greet("Alice")
        buffer = TraceContext.end_trace()
        
        entry_logs = [e for e in buffer.entries if e.direction == "→"]
        assert len(entry_logs) >= 1
        assert entry_logs[0].function_name == "greet"
    
    def test_decorator_logs_exit_with_duration(self):
        """AC-1.5: Decorator should log function exit with execution time."""
        from x_ipe.tracing.decorator import x_ipe_tracing
        from x_ipe.tracing.context import TraceContext
        
        @x_ipe_tracing(level="INFO")
        def slow_func():
            import time
            time.sleep(0.01)
            return "done"
        
        TraceContext.start_trace("TEST")
        slow_func()
        buffer = TraceContext.end_trace()
        
        exit_logs = [e for e in buffer.entries if e.direction == "←"]
        assert len(exit_logs) >= 1
        assert exit_logs[0].duration_ms is not None
        assert exit_logs[0].duration_ms >= 10  # At least 10ms
    
    def test_decorator_logs_exception(self):
        """AC-1.6: Decorator should log exceptions with type and message."""
        from x_ipe.tracing.decorator import x_ipe_tracing
        from x_ipe.tracing.context import TraceContext
        
        @x_ipe_tracing(level="INFO")
        def failing_func():
            raise ValueError("Something went wrong")
        
        TraceContext.start_trace("TEST")
        with pytest.raises(ValueError):
            failing_func()
        buffer = TraceContext.end_trace()
        
        error_logs = [e for e in buffer.entries if e.level == "ERROR"]
        assert len(error_logs) >= 1
        assert "ValueError" in str(error_logs[0].data)
    
    def test_decorator_propagates_exception(self):
        """Decorator should propagate exceptions (not swallow them)."""
        from x_ipe.tracing.decorator import x_ipe_tracing
        from x_ipe.tracing.context import TraceContext
        
        @x_ipe_tracing(level="INFO")
        def raise_error():
            raise RuntimeError("Test error")
        
        TraceContext.start_trace("TEST")
        with pytest.raises(RuntimeError, match="Test error"):
            raise_error()
        TraceContext.end_trace()
    
    def test_decorator_with_no_active_trace(self):
        """Decorator should work when no active trace (no-op)."""
        from x_ipe.tracing.decorator import x_ipe_tracing
        from x_ipe.tracing.context import TraceContext
        
        TraceContext.end_trace()  # Ensure no active trace
        
        @x_ipe_tracing(level="INFO")
        def my_func():
            return "result"
        
        result = my_func()
        assert result == "result"
    
    def test_decorator_redacts_specified_fields(self):
        """AC-1.3: Decorator should redact specified fields."""
        from x_ipe.tracing.decorator import x_ipe_tracing
        from x_ipe.tracing.context import TraceContext
        
        @x_ipe_tracing(level="INFO", redact=["password"])
        def create_user(email, password):
            return {"id": 1, "email": email}
        
        TraceContext.start_trace("TEST")
        create_user("test@example.com", "secret123")
        buffer = TraceContext.end_trace()
        
        entry_log = buffer.entries[0]
        assert "[REDACTED]" in str(entry_log.data) or "password" not in str(entry_log.data).lower()
    
    def test_decorator_with_async_function(self):
        """AC-1.7: Decorator should work with async functions."""
        from x_ipe.tracing.decorator import x_ipe_tracing
        from x_ipe.tracing.context import TraceContext
        
        @x_ipe_tracing(level="INFO")
        async def async_func():
            await asyncio.sleep(0.01)
            return "async result"
        
        async def run_test():
            TraceContext.start_trace("TEST")
            result = await async_func()
            buffer = TraceContext.end_trace()
            return result, buffer
        
        result, buffer = asyncio.run(run_test())
        
        assert result == "async result"
        assert len(buffer.entries) >= 2  # Entry and exit


# =============================================================================
# UNIT TESTS: TraceLogWriter
# =============================================================================

class TestTraceLogWriter:
    """Unit tests for log file writing."""
    
    def test_writer_creates_directory(self):
        """AC-4.3: Writer should create log directory if it doesn't exist."""
        from x_ipe.tracing.writer import TraceLogWriter
        from x_ipe.tracing.buffer import TraceBuffer
        
        with tempfile.TemporaryDirectory() as tmpdir:
            log_path = os.path.join(tmpdir, "traces", "nested")
            writer = TraceLogWriter(log_path)
            
            buffer = TraceBuffer("abc-123", "POST /api/test")
            writer.write(buffer, "SUCCESS")
            
            assert os.path.exists(log_path)
    
    def test_writer_creates_log_file(self):
        """Writer should create log file with correct naming."""
        from x_ipe.tracing.writer import TraceLogWriter
        from x_ipe.tracing.buffer import TraceBuffer
        
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = TraceLogWriter(tmpdir)
            buffer = TraceBuffer("abc-123", "POST /api/orders")
            
            filepath = writer.write(buffer, "SUCCESS")
            
            assert filepath is not None
            assert os.path.exists(filepath)
            assert "abc-123" in filepath
            assert filepath.endswith(".log")
    
    def test_writer_log_filename_format(self):
        """AC-4.1: Log filename should be {timestamp}-{api}-{trace_id}.log."""
        from x_ipe.tracing.writer import TraceLogWriter
        from x_ipe.tracing.buffer import TraceBuffer
        import re
        
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = TraceLogWriter(tmpdir)
            buffer = TraceBuffer("abc-123", "POST /api/orders")
            
            filepath = writer.write(buffer, "SUCCESS")
            filename = os.path.basename(filepath)
            
            # Pattern: YYYYMMDD-HHMMSS-post--api-orders-abc-123.log
            pattern = r"\d{8}-\d{6}-.+-abc-123\.log"
            assert re.match(pattern, filename)
    
    def test_writer_file_permissions(self):
        """Log file should have restricted permissions (owner read/write only)."""
        from x_ipe.tracing.writer import TraceLogWriter
        from x_ipe.tracing.buffer import TraceBuffer
        
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = TraceLogWriter(tmpdir)
            buffer = TraceBuffer("abc-123", "POST /api/test")
            
            filepath = writer.write(buffer, "SUCCESS")
            
            # Check file permissions (0o600 = owner read/write)
            mode = os.stat(filepath).st_mode & 0o777
            assert mode == 0o600
    
    def test_writer_cleanup_old_files(self):
        """AC-4.7: Cleanup should delete files older than retention period."""
        from x_ipe.tracing.writer import TraceLogWriter
        
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = TraceLogWriter(tmpdir)
            
            # Create old file
            old_file = os.path.join(tmpdir, "old-trace.log")
            with open(old_file, "w") as f:
                f.write("old trace")
            
            # Make it old
            old_time = datetime.now().timestamp() - (48 * 3600)  # 48 hours ago
            os.utime(old_file, (old_time, old_time))
            
            # Create new file
            new_file = os.path.join(tmpdir, "new-trace.log")
            with open(new_file, "w") as f:
                f.write("new trace")
            
            deleted = writer.cleanup(retention_hours=24)
            
            assert deleted == 1
            assert not os.path.exists(old_file)
            assert os.path.exists(new_file)
    
    def test_writer_handles_write_error(self):
        """EC-7: Writer should handle disk write errors gracefully."""
        from x_ipe.tracing.writer import TraceLogWriter
        from x_ipe.tracing.buffer import TraceBuffer
        
        # Use an invalid path
        writer = TraceLogWriter("/nonexistent/path/that/should/fail")
        buffer = TraceBuffer("abc-123", "POST /api/test")
        
        # Should not raise, just return None
        result = writer.write(buffer, "SUCCESS")
        assert result is None


# =============================================================================
# UNIT TESTS: TracingService
# =============================================================================

class TestTracingService:
    """Unit tests for TracingService."""
    
    def test_get_config_returns_defaults(self):
        """get_config should return default values when not configured."""
        from x_ipe.services.tracing_service import TracingService
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create minimal tools.json
            config_dir = os.path.join(tmpdir, "x-ipe-docs", "config")
            os.makedirs(config_dir)
            with open(os.path.join(config_dir, "tools.json"), "w") as f:
                json.dump({"version": "2.0"}, f)
            
            service = TracingService(tmpdir)
            config = service.get_config()
            
            assert config["enabled"] == False
            assert config["retention_hours"] == 24
            assert "instance/traces" in config["log_path"]
    
    def test_is_active_false_by_default(self):
        """is_active should return False when tracing not enabled."""
        from x_ipe.services.tracing_service import TracingService
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = os.path.join(tmpdir, "x-ipe-docs", "config")
            os.makedirs(config_dir)
            with open(os.path.join(config_dir, "tools.json"), "w") as f:
                json.dump({"version": "2.0"}, f)
            
            service = TracingService(tmpdir)
            
            assert service.is_active() == False
    
    def test_is_active_when_enabled(self):
        """is_active should return True when tracing_enabled is True."""
        from x_ipe.services.tracing_service import TracingService
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = os.path.join(tmpdir, "x-ipe-docs", "config")
            os.makedirs(config_dir)
            with open(os.path.join(config_dir, "tools.json"), "w") as f:
                json.dump({"version": "2.0", "tracing_enabled": True}, f)
            
            service = TracingService(tmpdir)
            
            assert service.is_active() == True
    
    def test_is_active_when_stop_at_future(self):
        """AC-6.6: is_active should return True when stop_at is in the future."""
        from x_ipe.services.tracing_service import TracingService
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = os.path.join(tmpdir, "x-ipe-docs", "config")
            os.makedirs(config_dir)
            
            future_time = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat().replace("+00:00", "Z")
            with open(os.path.join(config_dir, "tools.json"), "w") as f:
                json.dump({"version": "2.0", "tracing_stop_at": future_time}, f)
            
            service = TracingService(tmpdir)
            
            assert service.is_active() == True
    
    def test_is_active_when_stop_at_past(self):
        """is_active should return False when stop_at is in the past."""
        from x_ipe.services.tracing_service import TracingService
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = os.path.join(tmpdir, "x-ipe-docs", "config")
            os.makedirs(config_dir)
            
            past_time = (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat().replace("+00:00", "Z")
            with open(os.path.join(config_dir, "tools.json"), "w") as f:
                json.dump({"version": "2.0", "tracing_stop_at": past_time}, f)
            
            service = TracingService(tmpdir)
            
            assert service.is_active() == False
    
    def test_start_with_valid_duration(self):
        """AC-7.2: start should accept 3, 15, or 30 minutes."""
        from x_ipe.services.tracing_service import TracingService
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = os.path.join(tmpdir, "x-ipe-docs", "config")
            os.makedirs(config_dir)
            with open(os.path.join(config_dir, "tools.json"), "w") as f:
                json.dump({"version": "2.0"}, f)
            
            service = TracingService(tmpdir)
            
            result = service.start(3)
            
            assert result["success"] == True
            assert "stop_at" in result
    
    def test_start_with_invalid_duration(self):
        """start should reject invalid duration values."""
        from x_ipe.services.tracing_service import TracingService
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = os.path.join(tmpdir, "x-ipe-docs", "config")
            os.makedirs(config_dir)
            with open(os.path.join(config_dir, "tools.json"), "w") as f:
                json.dump({"version": "2.0"}, f)
            
            service = TracingService(tmpdir)
            
            with pytest.raises(ValueError):
                service.start(5)  # Invalid duration
    
    def test_stop_clears_stop_at(self):
        """AC-7.3: stop should clear tracing_stop_at."""
        from x_ipe.services.tracing_service import TracingService
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = os.path.join(tmpdir, "x-ipe-docs", "config")
            os.makedirs(config_dir)
            
            future_time = (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat().replace("+00:00", "Z")
            with open(os.path.join(config_dir, "tools.json"), "w") as f:
                json.dump({"version": "2.0", "tracing_stop_at": future_time}, f)
            
            service = TracingService(tmpdir)
            service.stop()
            
            assert service.is_active() == False
    
    def test_list_logs_returns_empty_when_no_logs(self):
        """list_logs should return empty list when no logs exist."""
        from x_ipe.services.tracing_service import TracingService
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = os.path.join(tmpdir, "x-ipe-docs", "config")
            os.makedirs(config_dir)
            with open(os.path.join(config_dir, "tools.json"), "w") as f:
                json.dump({"version": "2.0"}, f)
            
            service = TracingService(tmpdir)
            logs = service.list_logs()
            
            assert logs == []
    
    def test_list_logs_returns_log_files(self):
        """AC-7.4: list_logs should return list of trace log files."""
        from x_ipe.services.tracing_service import TracingService
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = os.path.join(tmpdir, "x-ipe-docs", "config")
            os.makedirs(config_dir)
            with open(os.path.join(config_dir, "tools.json"), "w") as f:
                json.dump({"version": "2.0", "tracing_log_path": "traces/"}, f)
            
            # Create log files
            traces_dir = os.path.join(tmpdir, "traces")
            os.makedirs(traces_dir)
            with open(os.path.join(traces_dir, "test-trace.log"), "w") as f:
                f.write("test log content")
            
            service = TracingService(tmpdir)
            logs = service.list_logs()
            
            assert len(logs) == 1
            assert "test-trace" in logs[0]["trace_id"] or "test-trace" in logs[0]["filename"]

    def test_list_logs_extracts_api_and_trace_id(self):
        """list_logs should extract API and full trace_id from filename."""
        from x_ipe.services.tracing_service import TracingService
        
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = os.path.join(tmpdir, "x-ipe-docs", "config")
            os.makedirs(config_dir)
            with open(os.path.join(config_dir, "tools.json"), "w") as f:
                json.dump({"version": "2.0", "tracing_log_path": "traces/"}, f)
            
            # Create log file with proper naming format
            traces_dir = os.path.join(tmpdir, "traces")
            os.makedirs(traces_dir)
            filename = "20260202-072505-get-api-project-structure-a649c048-3d73.log"
            with open(os.path.join(traces_dir, filename), "w") as f:
                f.write("[TRACE-START] a649c048-3d73 | GET /api/project/structure | 2026-02-02T07:25:05Z\n")
            
            service = TracingService(tmpdir)
            logs = service.list_logs()
            
            assert len(logs) == 1
            # Should extract full trace_id (last 2 UUID segments)
            assert logs[0]["trace_id"] == "a649c048-3d73"
            # Should extract and convert API name
            assert logs[0]["api"] == "GET /api/project/structure"
            assert logs[0]["filename"] == filename


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestTracingIntegration:
    """Integration tests for complete tracing flow."""
    
    def test_full_trace_lifecycle(self):
        """Test complete trace from start to log file."""
        from x_ipe.tracing.decorator import x_ipe_tracing
        from x_ipe.tracing.context import TraceContext
        from x_ipe.tracing.writer import TraceLogWriter
        
        @x_ipe_tracing(level="INFO")
        def outer_func(x):
            return inner_func(x * 2)
        
        @x_ipe_tracing(level="DEBUG")
        def inner_func(y):
            return y + 1
        
        with tempfile.TemporaryDirectory() as tmpdir:
            writer = TraceLogWriter(tmpdir)
            
            # Execute traced functions
            TraceContext.start_trace("POST /api/test")
            result = outer_func(5)
            buffer = TraceContext.end_trace()
            
            # Write to file
            filepath = writer.write(buffer, "SUCCESS")
            
            # Verify
            assert result == 11
            assert os.path.exists(filepath)
            
            with open(filepath) as f:
                content = f.read()
            
            assert "[TRACE-START]" in content
            assert "[TRACE-END]" in content
            assert "outer_func" in content
            assert "inner_func" in content
    
    def test_error_trace_includes_stack(self):
        """Error traces should include exception details."""
        from x_ipe.tracing.decorator import x_ipe_tracing
        from x_ipe.tracing.context import TraceContext
        
        @x_ipe_tracing(level="INFO")
        def failing_func():
            raise ValueError("Test failure")
        
        TraceContext.start_trace("POST /api/test")
        try:
            failing_func()
        except ValueError:
            pass
        buffer = TraceContext.end_trace()
        
        log_str = buffer.to_log_string("ERROR", 50.0)
        
        assert "ERROR" in log_str
        assert "ValueError" in log_str
    
    def test_nested_async_calls(self):
        """EC-1: Nested async calls should share trace context."""
        from x_ipe.tracing.decorator import x_ipe_tracing
        from x_ipe.tracing.context import TraceContext
        
        @x_ipe_tracing(level="INFO")
        async def async_outer():
            return await async_inner()
        
        @x_ipe_tracing(level="DEBUG")
        async def async_inner():
            return "done"
        
        async def run():
            TraceContext.start_trace("POST /api/async")
            result = await async_outer()
            buffer = TraceContext.end_trace()
            return result, buffer
        
        result, buffer = asyncio.run(run())
        
        assert result == "done"
        # Both functions should be in the same trace
        func_names = [e.function_name for e in buffer.entries]
        assert "async_outer" in func_names
        assert "async_inner" in func_names


# =============================================================================
# API TESTS
# =============================================================================

class TestTracingAPI:
    """API tests for tracing endpoints."""
    
    @pytest.fixture
    def client(self, tmp_path):
        """Create test client with temp project root."""
        from x_ipe.app import create_app
        
        # Create tools.json in temp directory
        config_dir = tmp_path / "x-ipe-docs" / "config"
        config_dir.mkdir(parents=True)
        (config_dir / "tools.json").write_text('{}')
        
        app = create_app()
        app.config['TESTING'] = True
        app.config['PROJECT_ROOT'] = str(tmp_path)
        with app.test_client() as client:
            yield client
    
    def test_get_status_endpoint(self, client):
        """AC-7.1: GET /api/tracing/status should return tracing state."""
        response = client.get('/api/tracing/status')
        
        assert response.status_code == 200
        data = response.get_json()
        assert "enabled" in data
        assert "stop_at" in data
        assert "retention_hours" in data
    
    def test_start_tracing_endpoint(self, client):
        """AC-7.2: POST /api/tracing/start should start tracing."""
        response = client.post('/api/tracing/start', 
                               json={"duration_minutes": 3},
                               content_type='application/json')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] == True
        assert "stop_at" in data
    
    def test_start_tracing_invalid_duration(self, client):
        """start should reject invalid duration."""
        response = client.post('/api/tracing/start',
                               json={"duration_minutes": 5},
                               content_type='application/json')
        
        assert response.status_code == 400
    
    def test_stop_tracing_endpoint(self, client):
        """AC-7.3: POST /api/tracing/stop should stop tracing."""
        response = client.post('/api/tracing/stop')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] == True
    
    def test_list_logs_endpoint(self, client):
        """AC-7.4: GET /api/tracing/logs should return log list."""
        response = client.get('/api/tracing/logs')
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
    
    def test_delete_logs_endpoint(self, client):
        """AC-7.6: DELETE /api/tracing/logs should delete all logs."""
        response = client.delete('/api/tracing/logs')
        
        assert response.status_code == 200
        data = response.get_json()
        assert "deleted" in data


# =============================================================================
# MIDDLEWARE TESTS
# =============================================================================

class TestTracingMiddleware:
    """Tests for tracing middleware that creates TraceContext per request."""
    
    @pytest.fixture
    def client_with_tracing(self, tmp_path):
        """Create test client with tracing enabled."""
        from x_ipe.app import create_app
        
        # Create tools.json with tracing enabled
        config_dir = tmp_path / "x-ipe-docs" / "config"
        config_dir.mkdir(parents=True)
        
        # Set tracing to be active (stop_at in future)
        stop_at = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat().replace("+00:00", "Z")
        tools_config = {"tracing_stop_at": stop_at}
        (config_dir / "tools.json").write_text(json.dumps(tools_config))
        
        # Create traces directory
        traces_dir = tmp_path / "instance" / "traces"
        traces_dir.mkdir(parents=True)
        
        app = create_app()
        app.config['TESTING'] = True
        app.config['PROJECT_ROOT'] = str(tmp_path)
        
        with app.test_client() as client:
            yield client, tmp_path
    
    def test_middleware_creates_trace_file_when_active(self, client_with_tracing):
        """BUG FIX: When tracing is active, API calls should create trace log files."""
        client, tmp_path = client_with_tracing
        traces_dir = tmp_path / "instance" / "traces"
        
        # Verify no traces initially
        initial_logs = list(traces_dir.glob("*.log"))
        initial_count = len(initial_logs)
        
        # Make an API call that should be traced
        response = client.get('/api/settings/all')
        
        # The middleware should have created a trace file
        final_logs = list(traces_dir.glob("*.log"))
        
        assert len(final_logs) > initial_count, \
            f"Expected trace log file to be created. Initial: {initial_count}, Final: {len(final_logs)}"
    
    def test_middleware_ignores_tracing_apis(self, client_with_tracing):
        """Tracing API endpoints should not create their own trace files (avoid loops)."""
        client, tmp_path = client_with_tracing
        traces_dir = tmp_path / "instance" / "traces"
        
        # Get initial count
        initial_logs = list(traces_dir.glob("*.log"))
        initial_count = len(initial_logs)
        
        # Call the tracing status endpoint - should be ignored
        response = client.get('/api/tracing/status')
        
        # The trace file count should remain the same
        final_logs = list(traces_dir.glob("*.log"))
        
        assert len(final_logs) == initial_count, \
            f"Tracing APIs should not create trace files. Initial: {initial_count}, Final: {len(final_logs)}"
    
    def test_middleware_ignores_user_configured_apis(self, tmp_path):
        """BUG FIX: APIs in tracing_ignored_apis config should not be traced."""
        from x_ipe.app import create_app
        
        # Create tools.json with tracing enabled AND custom ignored API
        config_dir = tmp_path / "x-ipe-docs" / "config"
        config_dir.mkdir(parents=True)
        
        stop_at = (datetime.now(timezone.utc) + timedelta(minutes=5)).isoformat().replace("+00:00", "Z")
        tools_config = {
            "tracing_stop_at": stop_at,
            "tracing_ignored_apis": ["/api/project/structure"]
        }
        (config_dir / "tools.json").write_text(json.dumps(tools_config))
        
        # Create traces directory
        traces_dir = tmp_path / "instance" / "traces"
        traces_dir.mkdir(parents=True)
        
        app = create_app()
        app.config['TESTING'] = True
        app.config['PROJECT_ROOT'] = str(tmp_path)
        
        with app.test_client() as client:
            # Get initial count
            initial_logs = list(traces_dir.glob("*.log"))
            initial_count = len(initial_logs)
            
            # Call the ignored API endpoint
            response = client.get('/api/project/structure')
            
            # The trace file count should remain the same - API is ignored
            final_logs = list(traces_dir.glob("*.log"))
            
            assert len(final_logs) == initial_count, \
                f"User-configured ignored APIs should not create trace files. Initial: {initial_count}, Final: {len(final_logs)}"
    
    def test_middleware_does_not_trace_when_inactive(self, tmp_path):
        """When tracing is not active, no trace files should be created."""
        from x_ipe.app import create_app
        
        # Create tools.json with tracing disabled
        config_dir = tmp_path / "x-ipe-docs" / "config"
        config_dir.mkdir(parents=True)
        (config_dir / "tools.json").write_text('{"tracing_enabled": false}')
        
        # Create traces directory
        traces_dir = tmp_path / "instance" / "traces"
        traces_dir.mkdir(parents=True)
        
        app = create_app()
        app.config['TESTING'] = True
        app.config['PROJECT_ROOT'] = str(tmp_path)
        
        with app.test_client() as client:
            # Make API call
            response = client.get('/api/settings/all')
            
            # No trace file should be created
            logs = list(traces_dir.glob("*.log"))
            assert len(logs) == 0, \
                f"No trace files should be created when tracing is inactive. Found: {len(logs)}"


# =============================================================================
# TEST SUMMARY
# =============================================================================
# 
# Total Tests: 65
# - Unit Tests (Redactor): 14
# - Unit Tests (TraceBuffer): 5
# - Unit Tests (TraceContext): 9
# - Unit Tests (Decorator): 11
# - Unit Tests (TraceLogWriter): 6
# - Unit Tests (TracingService): 11
# - Integration Tests: 3
# - API Tests: 6
# - Middleware Tests: 3
#
# Expected: ALL tests pass after middleware implementation
# =============================================================================
