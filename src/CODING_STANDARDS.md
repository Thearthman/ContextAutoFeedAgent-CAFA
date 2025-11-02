# CAFA Coding Standards

## 📋 Overview

This document defines the coding standards for the CAFA (Context Auto Feed Agent) project. All contributors must follow these guidelines to maintain code quality and consistency.

## 🌍 Language Requirements

### Code Language: English Only

**All code MUST be written in English, including:**

✅ **Required in English:**
- Variable names
- Function names
- Class names
- Method names
- Comments
- Docstrings
- Error messages
- Log messages
- UI text (for developer-facing UIs)
- Configuration keys
- Documentation

❌ **NOT Allowed:**
- Chinese characters in code
- Other non-English languages in code
- Mixed language identifiers (e.g., `用户_name`)

### Exceptions

The ONLY exception is **user-facing text** in the UI layer, which can be:
- Translated at runtime using i18n/l10n
- Stored in separate language files
- Defined as constants with clear English keys

**Example:**
```python
# ❌ BAD - Chinese in code
def 获取用户信息(用户名):
    """获取用户的详细信息"""
    pass

# ✅ GOOD - English only
def get_user_info(username):
    """Get detailed user information"""
    pass

# ✅ GOOD - User-facing text separated
MESSAGES = {
    "welcome": "Welcome to CAFA",
    "error": "An error occurred"
}
```

## 📝 Naming Conventions

### General Rules

1. **Use descriptive, meaningful names**
   ```python
   # ❌ BAD
   x = get_data()
   temp = process(x)
   
   # ✅ GOOD
   user_data = get_user_data()
   processed_results = process_user_data(user_data)
   ```

2. **Follow Python PEP 8 naming conventions**
   - `snake_case` for functions and variables
   - `PascalCase` for classes
   - `UPPER_CASE` for constants
   - `_leading_underscore` for internal/private

### Specific Guidelines

**Functions:**
```python
def calculate_similarity_score(text1, text2):
    """Calculate semantic similarity between two texts."""
    pass
```

**Classes:**
```python
class MemoryStore:
    """Store and retrieve semantic memories."""
    pass
```

**Constants:**
```python
MAX_RETRY_ATTEMPTS = 3
DEFAULT_TIMEOUT_SECONDS = 30
API_BASE_URL = "https://api.example.com"
```

**Private Methods:**
```python
class APIClient:
    def _validate_response(self, response):
        """Internal method to validate API response."""
        pass
```

## 📚 Documentation Standards

### Docstrings

All public functions, classes, and methods MUST have docstrings in English.

**Format:**
```python
def process_request(data: Dict, timeout: int = 30) -> Dict:
    """
    Process an API request with timeout handling.
    
    Args:
        data: Request data dictionary
        timeout: Timeout in seconds (default: 30)
    
    Returns:
        Response data dictionary
    
    Raises:
        APITimeoutError: If request times out
        ValidationError: If data validation fails
    
    Example:
        >>> result = process_request({"query": "test"})
        >>> print(result["status"])
        "success"
    """
    pass
```

### Comments

**Guidelines:**
- Write clear, concise comments in English
- Explain WHY, not WHAT (code should be self-explanatory)
- Update comments when code changes
- Avoid obvious comments

```python
# ❌ BAD - Obvious comment
x = x + 1  # Increment x by 1

# ✅ GOOD - Explains reasoning
x = x + 1  # Account for zero-based indexing

# ✅ GOOD - Explains complex logic
# Use exponential backoff to avoid overwhelming the API
# during high-traffic periods
delay = base_delay * (2 ** attempt_count)
```

## 🏗️ Code Structure

### Import Organization

```python
# 1. Standard library imports
import os
import sys
from typing import Dict, List, Optional

# 2. Third-party imports
import requests
import numpy as np
from flask import Flask, request

# 3. Local imports
from src.utils import calculate_hash
from src.exceptions import APIError
```

### Function Organization

```python
class MyClass:
    # 1. Class variables
    DEFAULT_VALUE = 100
    
    # 2. __init__ method
    def __init__(self):
        pass
    
    # 3. Public methods
    def public_method(self):
        pass
    
    # 4. Private methods
    def _private_method(self):
        pass
    
    # 5. Static methods
    @staticmethod
    def utility_method():
        pass
    
    # 6. Class methods
    @classmethod
    def from_config(cls, config):
        pass
```

## ⚠️ Error Handling

### Exception Messages

All exception messages MUST be in English:

```python
# ❌ BAD
raise ValueError("参数不能为空")

# ✅ GOOD
raise ValueError("Parameter cannot be empty")

# ✅ BETTER - Use custom exceptions
raise MissingParameterError("api_key")
```

### Logging

All log messages MUST be in English:

```python
# ❌ BAD
logger.info("用户登录成功")

# ✅ GOOD
logger.info("User logged in successfully")

# ✅ BETTER - Include context
logger.info(f"User {username} logged in successfully from {ip_address}")
```

## 🎨 UI Text Guidelines

### Separation of Concerns

User-facing text should be separated from code logic:

```python
# ❌ BAD - Mixed UI text in code
def greet_user(name):
    print("欢迎")  # Chinese hardcoded
    return f"你好, {name}"

# ✅ GOOD - Separate UI text
UI_TEXT = {
    "welcome": "Welcome",
    "greeting": "Hello, {name}"
}

def greet_user(name):
    print(UI_TEXT["welcome"])
    return UI_TEXT["greeting"].format(name=name)
```

### UI Constants File

For GUI applications, create a separate file:

```python
# ui_constants.py
class UIText:
    """User interface text constants."""
    
    # English (default)
    WELCOME = "Welcome to CAFA"
    SELECT_MODEL = "Select Model"
    SET_API_KEY = "Set API Key"
    
    # Can be extended for i18n
    @classmethod
    def get_text(cls, key, lang="en"):
        """Get localized text."""
        pass
```

## 🧪 Testing Standards

### Test Names

```python
# ✅ GOOD - Clear, descriptive test names
def test_api_key_detector_recognizes_openai_format():
    pass

def test_memory_store_raises_error_on_empty_text():
    pass

def test_llm_client_retries_on_timeout():
    pass
```

### Test Documentation

```python
def test_complex_scenario():
    """
    Test that the system correctly handles multiple
    concurrent API requests with rate limiting.
    
    Given:
        - Multiple API keys with different rate limits
        - Concurrent requests exceeding the limit
    
    When:
        - Requests are sent simultaneously
    
    Then:
        - Requests are queued and retried
        - No requests are lost
        - Rate limits are respected
    """
    pass
```

## 🔍 Code Review Checklist

Before submitting code, verify:

- [ ] All variable/function/class names are in English
- [ ] All comments are in English
- [ ] All docstrings are in English
- [ ] All error messages are in English
- [ ] All log messages are in English
- [ ] No Chinese characters in code (except UI text constants)
- [ ] Code follows PEP 8 style guide
- [ ] Functions have appropriate docstrings
- [ ] Complex logic has explanatory comments
- [ ] Tests are included for new features

## 📦 File Organization

### Module Structure

```
src/
├── __init__.py          # Module initialization
├── config_manager.py    # Configuration management
├── logger.py            # Logging utilities
├── utils.py            # General utilities
├── exceptions.py        # Custom exceptions
├── validators.py        # Input validation
└── module_name/        # Sub-modules
    ├── __init__.py
    ├── core.py
    └── helpers.py
```

### File Headers

Each file should start with:

```python
#!/usr/bin/env python3
"""
Module name and brief description.

This module provides functionality for...
More detailed description if needed.
"""

# Standard library imports
import os
```

## 🚀 Performance Guidelines

### Optimization

```python
# ✅ GOOD - Use list comprehension
squares = [x**2 for x in range(1000)]

# ✅ GOOD - Use generators for large datasets
def read_large_file(filepath):
    with open(filepath) as f:
        for line in f:
            yield line.strip()

# ✅ GOOD - Cache expensive operations
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_computation(x):
    pass
```

## 🔒 Security Guidelines

### API Keys

```python
# ❌ BAD
API_KEY = "sk-1234567890abcdef"  # Hardcoded

# ✅ GOOD
API_KEY = os.getenv("OPENAI_API_KEY")

# ✅ BETTER
from src.config_manager import get_config
api_key = get_config().get("api_keys.openai")
```

### Input Validation

```python
# ✅ GOOD - Always validate user input
from src.validators import LLMRequestValidator

def process_request(data):
    LLMRequestValidator.validate_chat_request(data)
    # Process validated data
```

## 📈 Git Commit Messages

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```
feat(api): add automatic API key detection

Implement intelligent API key recognition that automatically
detects the provider based on key format. Supports OpenAI,
Anthropic, Google, and other major providers.

Closes #123
```

## 🎯 Summary

**Golden Rules:**
1. ✅ **English only** for all code elements
2. ✅ **Clear, descriptive names** 
3. ✅ **Comprehensive documentation**
4. ✅ **Consistent style** (PEP 8)
5. ✅ **Separation of concerns** (UI text vs logic)

**When in doubt, ask:**
- Would a non-Chinese developer understand this code?
- Are the names clear and self-explanatory?
- Is the documentation complete and helpful?

---

**Version**: 1.0  
**Last Updated**: 2025-10-27  
**Maintained by**: CAFA Development Team

