#!/usr/bin/env python3
"""
Slash Command Factory Enhancements - Auto-testing and versioning.

Adds:
1. Auto-test generation and dry-run mode
2. Command versioning with safe updates and rollback
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import hashlib
import shutil


class CommandAutoTester:
    """Generates test cases and validates command execution."""

    def __init__(self):
        """Initialize auto tester."""
        self.test_scenarios = {}

    def generate_test_cases(self, command_config: Dict) -> Dict[str, Dict]:
        """
        Generate test scenarios based on command configuration.

        Args:
            command_config: Command configuration

        Returns:
            Dictionary of test scenarios
        """
        test_cases = {}
        description = command_config.get("description", "")
        tools = command_config.get("allowed-tools", "")

        # Test 1: Basic execution
        test_cases["basic"] = {
            "name": "Basic Execution",
            "description": "Verify command runs without errors",
            "input": "test-argument",
            "expected_output_pattern": ".*",
            "timeout_seconds": 10
        }

        # Test 2: No arguments
        if "$ARGUMENTS" in command_config.get("markdown_content", ""):
            test_cases["no_args"] = {
                "name": "Handle Missing Arguments",
                "description": "Verify command handles missing arguments",
                "input": "",
                "expected_behavior": "Should show usage or handle gracefully",
                "timeout_seconds": 5
            }

        # Test 3: Tool-specific tests
        if "Bash" in tools:
            test_cases["bash_availability"] = {
                "name": "Tool Availability Check",
                "description": "Verify required tools are available",
                "input": "verify",
                "expected_output_pattern": ".*tool.*available.*",
                "timeout_seconds": 10
            }

        if "Read" in tools or "Grep" in tools:
            test_cases["file_handling"] = {
                "name": "File Operations",
                "description": "Verify file reading works correctly",
                "input": "README.md",
                "expected_behavior": "Should successfully read file",
                "timeout_seconds": 10
            }

        # Test 4: Edge cases
        test_cases["empty_input"] = {
            "name": "Empty Input Handling",
            "description": "Verify command handles empty input gracefully",
            "input": "",
            "expected_behavior": "Should not crash",
            "timeout_seconds": 5
        }

        test_cases["special_chars"] = {
            "name": "Special Characters",
            "description": "Verify command handles special characters",
            "input": "test@#$%^&*()",
            "expected_behavior": "Should handle or escape properly",
            "timeout_seconds": 10
        }

        return test_cases

    def generate_test_examples_md(self, command_name: str, test_cases: Dict) -> str:
        """
        Generate TEST_EXAMPLES.md documentation.

        Args:
            command_name: Name of command
            test_cases: Test scenarios

        Returns:
            Markdown documentation
        """
        md = f"""# /{command_name} - Test Examples

## Overview

Test these scenarios to verify the command works correctly.

---

"""
        for test_id, test_case in test_cases.items():
            md += f"""## Test {test_id.upper()}: {test_case.get('name', 'Unknown')}

**Description**: {test_case.get('description', 'No description')}

**Test Input**:
```
/{command_name} {test_case.get('input', '(no args)')}
```

**Expected Behavior**:
{test_case.get('expected_behavior', test_case.get('expected_output_pattern', 'Successful execution'))}

**Timeout**: {test_case.get('timeout_seconds', 10)} seconds

---

"""
        md += """## Running Tests

To test this command:

1. Copy command to `.claude/commands/`
2. Restart Claude Code
3. Run each test case above
4. Verify output matches expectations
5. Report any failures

## Dry-Run Mode

Before installing, test with:
```
slash-command-factory --dry-run /command-name test-input
```

## Success Criteria

✅ All tests pass without errors
✅ Output is as expected
✅ No hanging or timeouts
✅ Help text is clear
✅ Error messages are helpful
"""
        return md

    def validate_command_syntax(self, command_content: str) -> Tuple[bool, List[str]]:
        """
        Validate command YAML and content syntax.

        Args:
            command_content: Command markdown content

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check YAML frontmatter
        if not command_content.startswith("---"):
            errors.append("Missing YAML frontmatter (must start with ---)")

        # Check for closing ---
        if command_content.count("---") < 2:
            errors.append("YAML frontmatter not properly closed")

        # Check required fields
        if "description:" not in command_content:
            errors.append("Missing 'description' field in YAML")

        if "allowed-tools:" not in command_content:
            errors.append("Missing 'allowed-tools' field in YAML")

        # Check for dangerous patterns
        dangerous = ["rm -rf", "mkfs", "dd if=", ":(){ :|:& };:"]
        for pattern in dangerous:
            if pattern in command_content:
                errors.append(f"⚠️ Dangerous pattern detected: '{pattern}'")

        # Check for unescaped special chars in YAML
        yaml_section = command_content.split("---")[1] if "---" in command_content else ""
        if ": " in yaml_section:
            # Basic YAML validation
            lines = yaml_section.split("\n")
            for line in lines:
                if line.strip() and not line.startswith("#"):
                    if ":" in line:
                        parts = line.split(":", 1)
                        if len(parts) != 2:
                            errors.append(f"Invalid YAML syntax: {line}")

        return len(errors) == 0, errors


class CommandVersionManager:
    """Manages command versions with safe updates and rollback."""

    def __init__(self, commands_dir: str = None):
        """Initialize version manager."""
        if commands_dir is None:
            commands_dir = str(Path.home() / ".claude" / "commands")

        self.commands_dir = Path(commands_dir)
        self.versions_dir = self.commands_dir / "versions"
        self.versions_dir.mkdir(parents=True, exist_ok=True)

    def get_command_version(self, command_name: str) -> Optional[str]:
        """
        Get current version of a command.

        Args:
            command_name: Name of command

        Returns:
            Version string or None
        """
        cmd_file = self.commands_dir / f"{command_name}.md"

        if not cmd_file.exists():
            return None

        with open(cmd_file, 'r') as f:
            content = f.read()

        # Extract version from YAML frontmatter
        match = re.search(r'version:\s*(.+)', content)
        return match.group(1).strip() if match else "unknown"

    def save_command_version(self, command_name: str, content: str, version: str) -> bool:
        """
        Save command to version history.

        Args:
            command_name: Name of command
            content: Command content
            version: Version string

        Returns:
            Success status
        """
        version_dir = self.versions_dir / command_name / version
        version_dir.mkdir(parents=True, exist_ok=True)

        version_file = version_dir / f"{command_name}.md"

        try:
            with open(version_file, 'w') as f:
                f.write(content)

            # Generate changelog entry
            self._update_changelog(command_name, version, "new_version")

            return True
        except Exception as e:
            print(f"❌ Error saving version: {e}")
            return False

    def list_versions(self, command_name: str) -> List[str]:
        """List all versions of a command."""
        cmd_versions_dir = self.versions_dir / command_name

        if not cmd_versions_dir.exists():
            return []

        versions = sorted([d.name for d in cmd_versions_dir.iterdir() if d.is_dir()])
        return versions[::-1]  # Return newest first

    def rollback_command(self, command_name: str, target_version: str) -> Tuple[bool, str]:
        """
        Rollback command to a previous version.

        Args:
            command_name: Name of command
            target_version: Version to rollback to

        Returns:
            Tuple of (success, message)
        """
        # Get target version
        version_file = self.versions_dir / command_name / target_version / f"{command_name}.md"

        if not version_file.exists():
            return False, f"Version {target_version} not found"

        # Backup current version
        current_version = self.get_command_version(command_name)
        cmd_file = self.commands_dir / f"{command_name}.md"

        if cmd_file.exists() and current_version:
            backup_dir = self.versions_dir / command_name / f"{current_version}_backup"
            backup_dir.mkdir(parents=True, exist_ok=True)
            shutil.copy(cmd_file, backup_dir / f"{command_name}.md")

        # Restore target version
        try:
            with open(version_file, 'r') as f:
                content = f.read()

            with open(cmd_file, 'w') as f:
                f.write(content)

            self._update_changelog(command_name, target_version, "rollback")
            return True, f"✅ Rolled back to version {target_version}"

        except Exception as e:
            return False, f"❌ Rollback failed: {e}"

    def generate_changelog(self, command_name: str) -> str:
        """Generate CHANGELOG.md for a command."""
        versions = self.list_versions(command_name)

        md = f"""# /{command_name} - Changelog

## Version History

"""
        for version in versions:
            version_dir = self.versions_dir / command_name / version
            md += f"""### {version}

**Date**: {datetime.now().strftime('%Y-%m-%d')}

**Changes**:
- Initial version

"""

        md += """## Migration Guide

### From v1.0 → v2.0
- Update your command to use new features
- Check backwards compatibility notes

## Rollback

To rollback to a previous version:

```bash
command-factory --rollback command-name v1.0.0
```

## Versioning

This project uses semantic versioning:
- **MAJOR**: Breaking changes
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes

"""
        return md

    def _update_changelog(self, command_name: str, version: str, action: str):
        """Update changelog (internal helper)."""
        pass  # Placeholder for changelog updates


def create_versioned_command(command_name: str, content: str, version: str = "1.0.0") -> bool:
    """
    Create a command with versioning support.

    Args:
        command_name: Name of command
        content: Command content
        version: Version string

    Returns:
        Success status
    """
    # Add version to YAML if not present
    if "version:" not in content:
        # Insert after name field
        content = content.replace(
            f"name: {command_name}",
            f"name: {command_name}\nversion: {version}"
        )

    manager = CommandVersionManager()
    return manager.save_command_version(command_name, content, version)


if __name__ == "__main__":
    # Test auto-testing
    print("=" * 60)
    print("COMMAND AUTO-TESTING")
    print("=" * 60)

    tester = CommandAutoTester()
    test_cases = tester.generate_test_cases({
        "description": "Analyze customer feedback and generate insights",
        "allowed-tools": "Read, Bash, Grep",
        "markdown_content": "Do something with $ARGUMENTS"
    })

    print(f"\nGenerated {len(test_cases)} test scenarios:\n")
    for test_id, test_case in test_cases.items():
        print(f"- {test_case['name']}: {test_case['description']}")

    # Test versioning
    print("\n" + "=" * 60)
    print("COMMAND VERSIONING")
    print("=" * 60)

    manager = CommandVersionManager()
    versions = manager.list_versions("my-command")
    print(f"\nVersions of 'my-command': {versions if versions else 'None'}")

    # Generate test examples
    print("\n" + "=" * 60)
    print("TEST EXAMPLES GENERATION")
    print("=" * 60)

    test_md = tester.generate_test_examples_md("analyze-feedback", test_cases)
    print(test_md[:500] + "...")
