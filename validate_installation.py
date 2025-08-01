#!/usr/bin/env python3
"""Validation script for Paw Control installation."""
import json
import sys
from pathlib import Path


def validate_manifest() -> list[str]:
    """Validate manifest.json structure."""
    errors = []
    manifest_path = Path("custom_components/pawcontrol/manifest.json")
    if not manifest_path.exists():
        return ["❌ manifest.json not found"]

    try:
        with open(manifest_path) as f:
            manifest = json.load(f)
    except json.JSONDecodeError as e:
        return [f"❌ manifest.json is invalid JSON: {e}"]

    required_fields = [
        "domain", "name", "version", "documentation",
        "issue_tracker", "codeowners", "requirements"
    ]

    for field in required_fields:
        if field not in manifest:
            errors.append(f"❌ Missing required field: {field}")

    # Validate version format
    version = manifest.get("version", "")
    if not version or not version.replace(".", "").replace("-", "").replace("beta", "").replace("alpha", "").isalnum():
        errors.append(f"❌ Invalid version format: {version}")

    # Check Home Assistant version
    if "homeassistant" not in manifest:
        errors.append("❌ Missing homeassistant version requirement")

    return errors


def validate_services() -> list[str]:
    """Validate services.yaml structure."""
    errors = []
    services_path = Path("custom_components/pawcontrol/services.yaml")
    if not services_path.exists():
        return ["⚠️ services.yaml not found (optional)"]

    try:
        import yaml
        with open(services_path) as f:
            services = yaml.safe_load(f)
    except yaml.YAMLError as e:
        return [f"❌ services.yaml is invalid YAML: {e}"]
    except ImportError:
        return ["⚠️ PyYAML not available, skipping services validation"]

    if not isinstance(services, dict):
        errors.append("❌ services.yaml must be a dictionary")

    return errors


def validate_strings() -> list[str]:
    """Validate strings.json structure."""
    errors = []
    strings_path = Path("custom_components/pawcontrol/strings.json")
    if not strings_path.exists():
        return ["⚠️ strings.json not found (optional)"]

    try:
        with open(strings_path) as f:
            strings = json.load(f)
    except json.JSONDecodeError as e:
        return [f"❌ strings.json is invalid JSON: {e}"]

    required_sections = ["config"]
    for section in required_sections:
        if section not in strings:
            errors.append(f"❌ Missing strings section: {section}")

    return errors


def validate_python_files() -> list[str]:
    """Validate Python files for syntax errors."""
    errors = []
    python_files = list(Path("custom_components/pawcontrol").glob("*.py"))
    if not python_files:
        return ["❌ No Python files found in integration"]

    for file_path in python_files:
        try:
            with open(file_path) as f:
                compile(f.read(), file_path, "exec")
        except SyntaxError as e:
            errors.append(f"❌ Syntax error in {file_path.name}: {e}")
        except Exception as e:
            errors.append(f"❌ Error compiling {file_path.name}: {e}")

    return errors


def validate_required_files() -> list[str]:
    """Check for required files."""
    errors = []
    required_files = [
        "custom_components/pawcontrol/__init__.py",
        "custom_components/pawcontrol/manifest.json",
        "README.md",
        "CHANGELOG.md",
    ]

    for file_path in required_files:
        if not Path(file_path).exists():
            errors.append(f"❌ Required file missing: {file_path}")

    return errors


def main():
    """Run all validations."""
    print("🔍 Validating Paw Control installation...\n")

    all_errors = []

    # Run all validations
    validations = [
        ("Required Files", validate_required_files),
        ("Manifest", validate_manifest),
        ("Services", validate_services),
        ("Strings", validate_strings),
        ("Python Syntax", validate_python_files),
    ]

    for name, validator in validations:
        print(f"📋 Checking {name}...")
        errors = validator()
        if errors:
            all_errors.extend(errors)
            for error in errors:
                print(f"  {error}")
        else:
            print(f"  ✅ {name} validation passed")
        print()

    # Summary
    if all_errors:
        print(f"❌ Validation failed with {len(all_errors)} errors:")
        for error in all_errors:
            print(f"  {error}")
        sys.exit(1)
    else:
        print("✅ All validations passed! Installation is ready.")
        sys.exit(0)


if __name__ == "__main__":
    main()
