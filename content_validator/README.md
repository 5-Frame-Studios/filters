# Content Validator Filter

A comprehensive validation filter for Minecraft Bedrock Add-Ons that ensures compliance with marketplace guidelines and best practices.

## Overview

This filter validates Minecraft Bedrock Add-Ons for compliance with marketplace guidelines, including:

- **Namespace Requirements**: Validates proper namespace usage and prevents conflicts
- **File Structure**: Ensures proper pack organization and file structure
- **Manifest Validation**: Checks manifest requirements and format
- **Naming Conventions**: Validates naming patterns for various asset types
- **Technical Restrictions**: Checks for forbidden features and API usage
- **Size Limits**: Validates file size and count restrictions
- **Content Guidelines**: Ensures compliance with Add-On marketplace policies

## Features

### Modular Test System
- **11 Individual Test Classes**: Each validation type is its own focused test
- **Standard API**: Consistent interface across all validation tests
- **Test Registry**: Centralized management of test execution order
- **Individual Execution**: Run specific tests or the full validation suite

### Regolith Integration
- **Non-destructive**: Only reports issues, doesn't modify content
- **Temporary Directory Support**: Works with Regolith's temporary file structure
- **Comprehensive Reporting**: Generates detailed validation reports
- **Exit Codes**: Proper exit codes for CI/CD integration

## Installation

1. Clone or download this filter
2. Ensure you have Python 3.7+ installed
3. Install required dependencies (see `requirements.txt`)

## Usage

### Regolith Integration

Add to your Regolith config:

   ```json
   {
  "regolith": {
    "filterDefinitions": {
      "content_validator": {
        "runWith": "python",
        "script": "path/to/content_validator/filter.py"
      }
    },
    "profiles": {
      "default": {
     "filters": [
       {
            "filter": "content_validator"
          }
        ]
      }
    }
  }
}
```

### Command Line Usage

```bash
# Run all validation tests
python filter.py

# List available tests
python filter.py --list-tests

# Show test execution order
python filter.py --execution-order

# Run specific test
python filter.py --test "Pack Structure"

# Enable verbose logging
python filter.py --verbose
```

### Individual Test Scripts

```bash
# Run pack structure test
python test/test_scripts/test_pack_structure.py

# Run namespace test
python test/test_scripts/test_namespace.py

# Run all individual tests
python test/test_scripts/run_all_tests.py
```

## Test Categories

### 1. Pack Structure Test
Validates that BP and RP directories exist and are properly structured.

### 2. Manifest Test
Validates manifest requirements and format compliance.

### 3. Namespace Test
Validates namespace usage across all files and checks for forbidden namespaces.

### 4. File Structure Test
Validates file structure, size limits, and organization requirements.

### 5. Naming Test
Validates naming conventions for geometry, animations, and render controllers.

### 6. Technical Test
Validates technical restrictions like runtime_identifier, experimental features, vanilla overrides.

### 7. Debug Test
Validates that debug statements are removed from final content.

### 8. Translatable Test
Validates that user-facing text is translatable and not hardcoded.

### 9. Organization Test
Validates organization-specific requirements like namespace prefix.

### 10. Content Guidelines Test
Validates Add-On guidelines compliance.

### 11. MCT Test
Validates content using Minecraft Creator Tools.

## Test Execution Order

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

## Configuration

The filter can be configured through settings. Default settings are used if none provided:

```json
{
    "log_level": "INFO",
    "generate_report": true,
  "forbidden_namespaces": ["minecraft"],
  "naming_patterns": {
    "geometry": "geometry.{namespace}.",
    "animation": "animation.{namespace}.",
    "render_controller": "controller.render.{namespace}."
  },
  "organization_specific": {
    "debug_statement_patterns": ["console.log", "debug", "TODO"],
    "forbidden_text_patterns": ["sword", "weapon"]
  }
}
```

## Output

### Validation Report
The filter generates a comprehensive JSON report at `data/content_validator_report.json`:

```json
{
  "summary": {
    "total_files_checked": 42,
    "total_errors": 0,
    "total_warnings": 2,
    "total_info": 0,
    "is_valid": true
  },
  "results": [
    {
      "level": "warning",
      "message": "Geometry identifier should start with 'geometry.test.'",
      "file_path": "RP/models/entity/test_entity.json",
      "context": {"current_id": "geometry.test_entity"}
    }
  ],
  "namespace_info": {
    "namespace": "test",
    "studio_name": "TestStudio",
    "pack_name": "TestPack"
  }
}
```

### Console Output
The filter provides detailed console output with validation results and summary information.

## Testing

### Running Tests
```bash
# Run the Regolith integration test
cd test
python run_test.py

# Run individual test scripts
python test_scripts/test_pack_structure.py
python test_scripts/test_namespace.py
python test_scripts/run_all_tests.py
```

### Test Data
The `test/` directory contains sample pack data for testing:
- Valid pack structure in `packs/BP/` and `packs/RP/`
- Invalid examples for testing error detection
- Expected validation results

## Development

### Adding New Tests

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

2. Register the test in `src/tests/test_registry.py`:
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

### Project Structure
```
content_validator/
├── filter.py                 # Main filter entry point
├── main.py                   # Legacy entry point (maintained for compatibility)
├── requirements.txt          # Python dependencies
├── README.md                 # This file
├── src/                      # Source code
│   ├── __init__.py
│   ├── validator.py          # Main validator orchestrator
│   ├── models.py             # Data models and enums
│   ├── utils.py              # Utility functions
│   ├── namespace_extractor.py # Namespace extraction
│   ├── manifest_validator.py # Manifest validation
│   ├── file_validator.py     # File structure validation
│   ├── content_validator.py  # Content guidelines validation
│   ├── mct_validator.py      # MCT integration
│   ├── report_generator.py   # Report generation
│   └── tests/                # Test modules
│       ├── __init__.py
│       ├── base_test.py      # Base test class
│       ├── test_registry.py  # Test registry
│       ├── pack_structure_test.py
│       ├── manifest_test.py
│       ├── namespace_test.py
│       ├── file_structure_test.py
│       ├── naming_test.py
│       ├── technical_test.py
│       ├── debug_test.py
│       ├── translatable_test.py
│       ├── content_guidelines_test.py
│       ├── mct_test.py
│       └── organization_test.py
└── test/                     # Test data and scripts
    ├── config.json           # Regolith test config
    ├── run_test.py           # Regolith integration test
    ├── data/                 # Generated test reports
    ├── packs/                # Test pack data
    │   ├── BP/
    │   └── RP/
    └── test_scripts/         # Individual test scripts
        ├── README.md
        ├── test_pack_structure.py
        ├── test_namespace.py
        └── run_all_tests.py
```

## Dependencies

- Python 3.7+
- Regolith (for integration)
- Optional: Rich (for enhanced console output)
- Optional: PyYAML (for YAML validation)
- Optional: jsonschema (for JSON validation)

## License

This filter is provided as-is for Minecraft Bedrock Add-On validation.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## Support

For issues and questions:
1. Check the test output for detailed error information
2. Review the validation report for specific issues
3. Run individual tests to isolate problems
4. Check the Regolith documentation for integration issues
