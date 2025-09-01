# Content Validator Test Environment

This directory contains a test environment for the Content Validator filter following the [Regolith testing guidelines](https://regolith-docs.readthedocs.io/en/latest/developing-filters/testing-filters/).

## Test Structure

```
test/
├── config.json              # Regolith configuration
├── .gitignore               # Git ignore file (includes /build)
├── run_test.py              # Test runner script
├── README.md                # This file
└── packs/
    ├── BP/                  # Behavior Pack
    │   ├── manifest.json    # BP manifest
    │   └── entities/         # Test entities
    │       ├── test_entity.json      # Valid entity
    │       └── bad_entity/           # Invalid entity (minecraft namespace)
    │           └── minecraft_entity.json
    ├── RP/                  # Resource Pack
    │   └── manifest.json    # RP manifest
    └── data/                # Output directory (created by Regolith)
```

## Test Cases

### ✅ Valid Content
- **test_entity.json**: Uses proper namespace (`test:test_entity`)
- **Manifests**: Include required fields (`pack_scope`, `metadata.product_type`, dependencies)

### ❌ Invalid Content (Should Fail Validation)
- **minecraft_entity.json**: Uses forbidden `minecraft:` namespace
- This should trigger a validation error

## Running Tests

### Method 1: Using the Test Script
```bash
cd content_validator/test
python run_test.py
```

### Method 2: Using Regolith Directly
```bash
cd content_validator/test
regolith run
```

### Method 3: Using Regolith with Profile
```bash
cd content_validator/test
regolith run --profile default
```

## Expected Results

The test should:
1. ✅ Detect the valid entity (`test:test_entity`)
2. ❌ Detect the invalid entity (`minecraft:bad_entity`)
3. 📊 Generate a validation report in `packs/data/content_validator_report.json`
4. 📋 Show validation summary with errors and warnings

## Adding Your Own Test Content

To test your own BP and RP content:

1. **Replace the test content**: Replace the files in `packs/BP/` and `packs/RP/` with your own content
2. **Run the test**: Execute `python run_test.py` or `regolith run`
3. **Check results**: Review the validation report in `packs/data/content_validator_report.json`

## Test Configuration

The `config.json` is configured with:
- **Export target**: `"local"` (prevents export to `com.mojang`)
- **Filter definition**: Points to `../main.py` (the content validator)
- **Build output**: Goes to `./build` (ignored by git)

## Troubleshooting

### "Regolith not found"
Make sure Regolith is installed and in your PATH:
```bash
npm install -g @bedrock-oss/regolith
```

### "Python dependencies missing"
Install the required Python packages:
```bash
pip install jsonschema PyYAML dpath reticulator rich colorama
```

### "Minecraft Creator Tools not found" (Optional)
For full validation including MCT:
```bash
npm install -g @minecraft/creator-tools
```

## Validation Report

After running the test, check `packs/data/content_validator_report.json` for detailed validation results:

```json
{
  "summary": {
    "total_files_checked": 4,
    "total_errors": 1,
    "total_warnings": 0,
    "total_info": 2,
    "is_valid": false
  },
  "results": [
    {
      "level": "error",
      "message": "Forbidden namespace 'minecraft' used in description.identifier",
      "file_path": "packs/BP/entities/bad_entity/minecraft_entity.json",
      "context": {
        "value": "minecraft:bad_entity",
        "path": "description.identifier"
      }
    }
  ],
  "namespace_info": {
    "namespace": "test",
    "studio_name": "test",
    "pack_name": null
  }
}
```

## Next Steps

1. **Add your content**: Replace the test files with your actual BP/RP content
2. **Run validation**: Execute the test to check for issues
3. **Fix issues**: Address any validation errors or warnings
4. **Iterate**: Repeat until validation passes

This test environment helps ensure your Add-On content meets all marketplace requirements before submission.
