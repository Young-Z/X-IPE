# Test Generation Patterns Reference

## Test Case Templates

### Unit Test Template (Arrange-Act-Assert)

```python
def test_<function>_<scenario>_<expected_result>(self):
    """AC: <Acceptance Criteria being tested>"""
    # ARRANGE (Given)
    # Set up test data and dependencies
    email = "user@test.com"
    password = "ValidPass123"
    
    # ACT (When)
    # Execute the function under test
    result = auth_service.authenticate(email, password)
    
    # ASSERT (Then)
    # Verify expected outcomes
    assert result.access_token is not None
    assert result.token_type == "Bearer"
```

### Integration Test Template

```python
class TestAuthIntegration:
    """Integration tests for authentication flow."""
    
    @pytest.fixture
    def setup_db(self):
        """Set up test database with fixtures."""
        db = create_test_database()
        yield db
        db.cleanup()
    
    def test_full_auth_flow_success(self, setup_db):
        """Test complete authentication from request to token storage."""
        # Test end-to-end flow
        user = create_test_user(setup_db)
        result = auth_service.authenticate(user.email, "password")
        stored_token = token_repo.get_by_user(user.id)
        
        assert result.success
        assert stored_token is not None
```

### API Test Template

```python
class TestAuthAPI:
    """API tests for authentication endpoints."""
    
    def test_login_endpoint_success(self, client):
        """POST /api/auth/login returns 200 with valid credentials."""
        response = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "ValidPass123"
        })
        
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert response.json()["token_type"] == "Bearer"
    
    def test_login_endpoint_invalid_credentials(self, client):
        """POST /api/auth/login returns 401 with invalid credentials."""
        response = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "WrongPassword"
        })
        
        assert response.status_code == 401
        assert "error" in response.json()
```

### Parameterized Test Template

```python
@pytest.mark.parametrize("input_data,expected", [
    ({"email": "valid@test.com", "name": "Test"}, True),
    ({"email": "invalid-email", "name": "Test"}, False),
    ({"email": "", "name": "Test"}, False),
    ({"email": "valid@test.com", "name": ""}, False),
])
def test_user_validation(input_data, expected):
    """Test user data validation with various inputs."""
    result = validate_user(input_data)
    assert result.is_valid == expected
```

---

## Test Naming Conventions

### Pattern
```
test_<function>_<scenario>_<expected_result>
```

### Examples by Category

| Category | Example Name |
|----------|--------------|
| Happy path | `test_authenticate_valid_credentials_returns_token` |
| Invalid input | `test_authenticate_invalid_email_raises_error` |
| Edge case | `test_authenticate_expired_token_returns_401` |
| Boundary | `test_password_minimum_length_accepted` |
| Error handling | `test_database_connection_failure_handled_gracefully` |
| State | `test_logout_clears_session_data` |

### Language-Specific Conventions

**Python (pytest):**
```python
def test_function_scenario_expected():
    pass

class TestClassName:
    def test_method_scenario_expected(self):
        pass
```

**JavaScript (Jest):**
```javascript
describe('ClassName', () => {
  describe('methodName', () => {
    it('should return expected when scenario', () => {});
    it('should throw error when invalid input', () => {});
  });
});
```

**Go:**
```go
func TestFunctionName_Scenario_ExpectedResult(t *testing.T) {}
```

---

## Mock and Stub Examples

### Python (pytest-mock)

```python
def test_service_calls_repository(mocker):
    """Verify service delegates to repository."""
    # Create mock
    mock_repo = mocker.Mock()
    mock_repo.find_by_id.return_value = User(id=1, name="Test")
    
    # Inject mock
    service = UserService(repository=mock_repo)
    
    # Execute
    result = service.get_user(1)
    
    # Verify
    mock_repo.find_by_id.assert_called_once_with(1)
    assert result.name == "Test"

def test_external_api_mocked(mocker):
    """Mock external API calls."""
    mocker.patch(
        'services.external_api.fetch_data',
        return_value={"status": "success"}
    )
    
    result = my_service.process()
    assert result.success
```

### Stub for Database

```python
@pytest.fixture
def stub_repository():
    """Stub repository with predefined responses."""
    class StubRepository:
        def find_by_id(self, id):
            return {"1": User(id=1, name="Alice")}.get(str(id))
        
        def save(self, entity):
            entity.id = 999  # Simulate generated ID
            return entity
    
    return StubRepository()
```

### Mock for HTTP Responses

```python
@pytest.fixture
def mock_http_client(mocker):
    """Mock HTTP client for external service calls."""
    mock = mocker.patch('httpx.Client')
    mock.return_value.__enter__ = mocker.Mock(return_value=mock)
    mock.return_value.__exit__ = mocker.Mock(return_value=False)
    
    # Configure responses
    mock.get.return_value = mocker.Mock(
        status_code=200,
        json=lambda: {"data": "mocked"}
    )
    return mock
```

### JavaScript Mocks (Jest)

```javascript
// Mock module
jest.mock('./database', () => ({
  findUser: jest.fn().mockResolvedValue({ id: 1, name: 'Test' }),
  saveUser: jest.fn().mockResolvedValue({ id: 1 }),
}));

// Spy on method
const spy = jest.spyOn(userService, 'validate');
await userService.create(userData);
expect(spy).toHaveBeenCalledWith(userData);
```

---

## Coverage Requirements

### Coverage Thresholds by Test Type

| Test Level | Minimum Coverage | Target Coverage |
|------------|------------------|-----------------|
| Unit Tests | 80% | 90%+ |
| Integration Tests | 60% | 75%+ |
| API Tests | 100% endpoints | 100% endpoints |
| Overall | 75% | 85%+ |

### What Must Be Covered

| Component Type | Coverage Requirement |
|----------------|---------------------|
| Public methods | 100% |
| Data models | All field validations |
| API endpoints | All success + error responses |
| Error handlers | All error paths |
| Business rules | All conditions |

### What Can Be Excluded

- Private helper methods (covered via public interface)
- Boilerplate code (getters/setters)
- Configuration files
- Third-party library code

### Coverage Documentation Template

```markdown
| Component | Unit Tests | Integration | API Tests | Coverage |
|-----------|------------|-------------|-----------|----------|
| AuthService | 8 | 2 | - | 92% |
| TokenManager | 5 | - | - | 88% |
| UserRepository | 4 | 3 | - | 85% |
| /login endpoint | - | - | 4 | 100% |
| /logout endpoint | - | - | 3 | 100% |
| **TOTAL** | **17** | **5** | **7** | **89%** |
```

---

## Test Data Strategies

### Fixtures vs Factories

**Use Fixtures when:**
- Static test data that doesn't change
- Shared across multiple tests
- Database seeding

**Use Factories when:**
- Need dynamic/unique data
- Tests require variations
- Complex object creation

### Factory Pattern Example

```python
class UserFactory:
    _counter = 0
    
    @classmethod
    def create(cls, **overrides):
        cls._counter += 1
        defaults = {
            "id": cls._counter,
            "email": f"user{cls._counter}@test.com",
            "name": f"Test User {cls._counter}",
            "active": True,
        }
        defaults.update(overrides)
        return User(**defaults)

# Usage
user1 = UserFactory.create()
user2 = UserFactory.create(name="Custom Name")
inactive_user = UserFactory.create(active=False)
```

---

## Tracing Test Patterns

### Decorator Presence Test

```python
def test_service_functions_have_tracing():
    """Verify service functions have @x_ipe_tracing decorators."""
    import inspect
    from x_ipe.services.my_service import MyService
    
    traced_functions = ['create', 'update', 'delete', 'get']
    for func_name in traced_functions:
        func = getattr(MyService, func_name, None)
        if func:
            source = inspect.getsource(func)
            assert "@x_ipe_tracing" in source, f"{func_name} missing tracing"
```

### Sensitive Data Redaction Test

```python
def test_password_redacted_in_traces(mocker, captured_logs):
    """Verify password is not logged in trace output."""
    service.login(email="test@test.com", password="secret123")
    for log in captured_logs:
        assert "secret123" not in log
        assert "[REDACTED]" in log or "password" not in log.lower()
```

### Trace Context Propagation Test

```python
def test_trace_context_propagates():
    """Verify trace_id propagates through nested calls."""
    from x_ipe.tracing import get_current_trace_id
    with trace_context("test-trace-123"):
        result = service.nested_operation()
        assert result.trace_id == "test-trace-123"
```

---

## Test File Structure

```
tests/
├── unit/                    # Unit tests (isolated)
│   ├── services/
│   │   └── auth_service_test.py
│   ├── models/
│   │   └── user_test.py
│   └── utils/
│       └── token_utils_test.py
├── integration/             # Integration tests
│   └── auth_flow_test.py
├── api/                     # API tests
│   └── auth_api_test.py
├── fixtures/                # Shared test data
│   └── users.py
└── conftest.py              # Test configuration
```
