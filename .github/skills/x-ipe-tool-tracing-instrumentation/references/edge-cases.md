# Tracing Instrumentation - Edge Cases & Anti-Patterns

## Edge Cases

### EC-1: Already Traced Function
```python
# Input
@x_ipe_tracing(level="DEBUG")
def my_function():
    pass

# Action: SKIP
# Report: "already traced"
```

### EC-2: Multiple Decorators
```python
# Input
@validate_input
@authorize
def my_function():
    pass

# Output (add tracing first)
@x_ipe_tracing(level="INFO")
@validate_input
@authorize
def my_function():
    pass
```

### EC-3: Class with Methods
```python
# Input
class MyService:
    def process(self, data):
        pass

# Output
class MyService:
    @x_ipe_tracing(level="INFO")
    def process(self, data):
        pass
```

### EC-4: Empty File / No Functions
```
Report: "No traceable functions found in {filepath}"
```

### EC-5: Syntax Error in File
```
Report: "Error parsing {filepath}: {error}"
Skip file, continue with others
```

---

## Anti-Patterns

| Anti-Pattern | Why Bad | Do Instead |
|--------------|---------|------------|
| Trace `__init__` | Noisy, rarely useful | Skip all dunder methods |
| Trace test files | Tests should not be traced | Exclude `test_*.py` |
| Force all INFO | DEBUG floods production logs | Use auto level assignment |
| Skip redaction check | Security risk | Always detect sensitive params |
| Modify without approval | Unexpected changes | Always show proposal first |

---

## Sensitive Parameter Patterns

**Exact matches (case-insensitive):**
```
password, pwd, passwd, pass
secret, secret_key, secretkey
token, auth_token, api_token, access_token, refresh_token
key, api_key, apikey, private_key, privatekey
auth, authorization
credential, cred, credentials
ssn, social_security
pin, cvv, card_number
```

**Suffix patterns:**
```
*_password, *_pwd
*_secret, *_key
*_token, *_auth
*_credential
```
