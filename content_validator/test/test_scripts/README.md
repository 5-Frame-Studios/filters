# Content Validator Test System

This directory contains individual test scripts for the modular content validator system.

## Overview

The content validator has been refactored to use a modular test system where each validation type is its own test class with a standard API. This provides several benefits:

- **Modularity**: Each test can be run independently
- **Maintainability**: Easier to debug, modify, and extend individual tests
- **Reusability**: Tests can be composed into different validation suites
- **Standard API**: Consistent interface across all tests

## Test Structure

### Base Test Class
All tests inherit from `BaseValidatorTest` which provides:
- Standard `validate()` method interface
- Helper methods for adding results and logging
- Consistent error handling

### Test Registry
The `TestRegistry` manages:
- Test discovery and registration
- Execution order management
- Test instance creation

### Individual Test Classes
Each validation type is now its own test class:
- `PackStructureTest` - Validates BP/RP directory structure
- `ManifestTest` - Validates manifest requirements
- `NamespaceTest` - Validates namespace usage
- `FileStructureTest` - Validates file structure and organization
- `NamingTest` - Validates naming conventions
- `TechnicalTest` - Validates technical restrictions
- `DebugTest` - Validates debug statement removal
- `TranslatableTest` - Validates translatable text
- `ContentGuidelinesTest` - Validates Add-On guidelines
- `MCTTest` - Validates with Minecraft Creator Tools
- `OrganizationTest` - Validates organization-specific requirements

## Usage

### Running Individual Tests

#### Via Main Script
```bash
# Run a specific test
python main.py --test "Pack Structure"

# List all available tests
python main.py --list-tests

# Show execution order
python main.py --execution-order
```

#### Via Individual Test Scripts
```bash
# Run pack structure test
python test_scripts/test_pack_structure.py

# Run namespace test
python test_scripts/test_namespace.py

# Run all individual tests
python test_scripts/run_all_tests.py
```

### Test Execution Order

Tests are executed in dependency order:
1. **PackStructureTest** - Must run first to detect pack structure
2. **ManifestTest** - Early validation
3. **NamespaceTest** - Namespace info needed by other tests
4. **FileStructureTest** - File structure validation
5. **NamingTest** - Naming conventions
6. **TechnicalTest** - Technical restrictions
7. **DebugTest** - Debug statements
8. **TranslatableTest** - Translatable text
9. **OrganizationTest** - Organization requirements
10. **ContentGuidelinesTest** - Content guidelines
11. **MCTTest** - MCT validation (last)

## Creating New Tests

To add a new test:

1. Create a new test class in `src/tests/`:
```python
from .base_test import BaseValidatorTest

class MyNewTest(BaseValidatorTest):
    def get_test_name(self) -> str:
        return "My New Test"
    
    def get_test_description(self) -> str:
        return "Description of what this test validates"
    
    def validate(self, pack_paths: Dict[str, str]) -> ValidationReport:
        # Your validation logic here
        return self.report
```

2. Register the test in `test_registry.py`:
```python
from .my_new_test import MyNewTest

# In _register_default_tests method:
self.register_test(MyNewTest, 5)  # Specify execution order
```

3. Create an individual test script (optional):
```python
#!/usr/bin/env python3
import sys
sys.path.insert(0, '../../src')

from tests.my_new_test import MyNewTest
# ... rest of script
```

## Benefits of the New System

1. **Targeted Validation**: Run only the tests you need
2. **Faster Development**: Debug specific validation issues
3. **Better Organization**: Clear separation of concerns
4. **Extensibility**: Easy to add new validation types
5. **Composability**: Create custom validation profiles
6. **Maintainability**: Smaller, focused test classes

## Migration Notes

The main validator still works exactly as before for Regolith integration. The new modular system is an enhancement that provides additional capabilities while maintaining backward compatibility.
