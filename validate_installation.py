#!/usr/bin/env python3
"""Validation script for Paw Control installation."""
from __future__ import annotations

import json
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

_LOGGER = logging.getLogger(__name__)


def validate_manifest() -> list[str]:
    """Validate manifest.json structure."""
    errors: list[str] = []
    manifest_path = Path("custom_components/pawcontrol/manifest.json")
    if not manifest_path.exists():
        return ["❌ manifest.json not found"]

    try:
        with manifest_path.open() as file:
            manifest = json.load(file)
    except json.JSONDecodeError as e:
        return [f"❌ manifest.json is invalid JSON: {e}"]

    required_fields = [
        "domain",
        "name",
        "version",
        "documentation",
        "issue_tracker",
        "codeowners",
        "requirements",
    ]

    for field in required_fields:
        if field not in manifest:
            errors.append(f"❌ Missing required field: {field}")

    # Validate version format
    version = manifest.get("version", "")
    if (
        not version
        or not version.replace(".", "")
        .replace("-", "")
        .replace("beta", "")
        .replace("alpha", "")
        .isalnum()
    ):
        errors.append(f"❌ Invalid version format: {version}")

    # Check Home Assistant version
    if "homeassistant" not in manifest:
        errors.append("❌ Missing homeassistant version requirement")

    return errors


def validate_services() -> list[str]:
    """Validate services.yaml structure."""
    errors: list[str] = []
    services_path = Path("custom_components/pawcontrol/services.yaml")
    if not services_path.exists():
        return ["⚠️ services.yaml not found (optional)"]

    try:
        import yaml

        with services_path.open() as file:
            services = yaml.safe_load(file)
    except yaml.YAMLError as e:
        return [f"❌ services.yaml is invalid YAML: {e}"]
    except ImportError:
        return ["⚠️ PyYAML not available, skipping services validation"]

    if not isinstance(services, dict):
        errors.append("❌ services.yaml must be a dictionary")

    return errors


def validate_strings() -> list[str]:
    """Validate strings.json structure."""
    errors: list[str] = []
    strings_path = Path("custom_components/pawcontrol/strings.json")
    if not strings_path.exists():
        return ["⚠️ strings.json not found (optional)"]

    try:
        with strings_path.open() as file:
            strings = json.load(file)
    except json.JSONDecodeError as e:
        return [f"❌ strings.json is invalid JSON: {e}"]

    required_sections = ["config"]
    for section in required_sections:
        if section not in strings:
            errors.append(f"❌ Missing strings section: {section}")

    return errors


def validate_python_files() -> list[str]:
    """Validate Python files for syntax errors."""
    errors: list[str] = []
    python_files = list(Path("custom_components/pawcontrol").glob("*.py"))
    if not python_files:
        return ["❌ No Python files found in integration"]

    for file_path in python_files:
        try:
            compile(file_path.read_text(), file_path, "exec")
        except SyntaxError as e:
            errors.append(f"❌ Syntax error in {file_path.name}: {e}")
        except OSError as e:
            errors.append(f"❌ Error reading {file_path.name}: {e}")

    return errors


def validate_required_files() -> list[str]:
    """Check for required files."""
    errors: list[str] = []
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


@dataclass
class Validation:
    """Single validation step."""

    name: str
    func: Callable[[], list[str]]


VALIDATIONS: list[Validation] = [
    Validation("Required Files", validate_required_files),
    Validation("Manifest", validate_manifest),
    Validation("Services", validate_services),
    Validation("Strings", validate_strings),
    Validation("Python Syntax", validate_python_files),
]


def main() -> None:
    """Run all validations."""
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    _LOGGER.info("🔍 Validating Paw Control installation...\n")

    all_errors: list[str] = []

    for validation in VALIDATIONS:
        _LOGGER.info("📋 Checking %s...", validation.name)
        errors = validation.func()
        if errors:
            all_errors.extend(errors)
            for error in errors:
                _LOGGER.error("  %s", error)
        else:
            _LOGGER.info("  ✅ %s validation passed", validation.name)
        _LOGGER.info("")

    if all_errors:
        _LOGGER.error("❌ Validation failed with %d errors:", len(all_errors))
        for error in all_errors:
            _LOGGER.error("  %s", error)
        sys.exit(1)

    _LOGGER.info("✅ All validations passed! Installation is ready.")
    sys.exit(0)


if __name__ == "__main__":
    main()
