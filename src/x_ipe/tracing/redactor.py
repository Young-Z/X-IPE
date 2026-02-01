"""
FEATURE-023: Application Action Tracing - Core

Redactor module for sensitive data redaction in trace logs.

This module provides automatic redaction of sensitive data before logging,
including passwords, tokens, API keys, and credit card numbers.
"""
import re
from typing import Any, Dict, List, Set, Optional

REDACTED = "[REDACTED]"

# Sensitive key patterns (case-insensitive matching)
SENSITIVE_KEY_PATTERNS = {
    "password",
    "secret",
    "token",
    "api_key",
    "apikey",
    "authorization",
    "auth",
    "credential",
    "private_key",
    "privatekey",
}

# Value patterns
CREDIT_CARD_PATTERN = re.compile(r"^\d{16}$")
JWT_PREFIX = "eyJ"


class Redactor:
    """
    Sensitive data redactor for trace logs.
    
    Automatically redacts:
    - Fields containing sensitive key patterns (password, secret, token, etc.)
    - Credit card numbers (16-digit patterns)
    - JWT tokens (values starting with 'eyJ')
    - Custom fields specified via constructor
    
    Usage:
        redactor = Redactor(custom_fields=["ssn", "dob"])
        safe_data = redactor.redact({"password": "secret", "name": "John"})
        # Result: {"password": "[REDACTED]", "name": "John"}
    """
    
    def __init__(self, custom_fields: Optional[List[str]] = None):
        """
        Initialize Redactor with optional custom fields.
        
        Args:
            custom_fields: Additional field names to redact (case-insensitive)
        """
        self.custom_fields: Set[str] = set(
            f.lower() for f in (custom_fields or [])
        )
    
    def redact(self, data: Any) -> Any:
        """
        Recursively redact sensitive data.
        
        Args:
            data: Data to redact (dict, list, or primitive)
            
        Returns:
            Data with sensitive values replaced with '[REDACTED]'
        """
        if isinstance(data, dict):
            return {k: self._redact_value(k, v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.redact(item) for item in data]
        elif isinstance(data, tuple):
            return tuple(self.redact(item) for item in data)
        return data
    
    def _redact_value(self, key: str, value: Any) -> Any:
        """
        Redact a single value based on key name and value patterns.
        
        Args:
            key: Field name
            value: Field value
            
        Returns:
            Redacted value or original value if not sensitive
        """
        key_lower = key.lower()
        
        # Check field name against sensitive patterns
        for pattern in SENSITIVE_KEY_PATTERNS:
            if pattern in key_lower:
                return REDACTED
        
        # Check custom fields
        if key_lower in self.custom_fields:
            return REDACTED
        
        # Check value patterns for strings
        if isinstance(value, str):
            # Credit card pattern (16 digits)
            if CREDIT_CARD_PATTERN.match(value):
                return REDACTED
            
            # JWT pattern (starts with eyJ)
            if value.startswith(JWT_PREFIX):
                return REDACTED
        
        # Recurse for nested structures
        return self.redact(value)
