#!/usr/bin/env python3
"""
Template Loader - Robust template loading with fallbacks and validation.

Handles missing templates, corrupted JSON, custom templates,
and provides clear error messages.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple


class TemplateValidator:
    """Validates hook template structure and content."""

    REQUIRED_FIELDS = {
        "name": str,
        "description": str,
        "event_type": str,
        "matcher": (dict, type(None)),
        "hooks": (list, dict),
        "command": (str, type(None))
    }

    VALID_EVENT_TYPES = [
        "PostToolUse",
        "SubagentStop",
        "SessionStart",
        "PreToolUse",
        "UserPromptSubmit",
        "Stop",
        "PrePush"
    ]

    @staticmethod
    def validate(template: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate template structure.

        Args:
            template: Template dict to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check required fields
        for field, expected_type in TemplateValidator.REQUIRED_FIELDS.items():
            if field not in template:
                errors.append(f"Missing required field: '{field}'")
            elif expected_type is not type(None):
                if not isinstance(template[field], expected_type):
                    errors.append(f"Field '{field}' has wrong type. Expected {expected_type}, got {type(template[field])}")

        # Validate event_type
        if "event_type" in template:
            if template["event_type"] not in TemplateValidator.VALID_EVENT_TYPES:
                errors.append(f"Invalid event_type: '{template['event_type']}'. Must be one of: {', '.join(TemplateValidator.VALID_EVENT_TYPES)}")

        # Check for dangerous patterns
        dangerous_patterns = ["rm -rf", "mkfs", "dd if=", ":(){ :|:& };:"]
        if "command" in template and template["command"]:
            for pattern in dangerous_patterns:
                if pattern in str(template["command"]):
                    errors.append(f"⚠️ DANGEROUS: Template contains pattern '{pattern}'")

        return len(errors) == 0, errors


class TemplateLoader:
    """Loads templates with robust error handling."""

    def __init__(self, skill_root: str = None):
        """
        Initialize template loader.

        Args:
            skill_root: Root directory of hook-factory skill (auto-detected if None)
        """
        if skill_root is None:
            skill_root = Path(__file__).parent

        self.skill_root = Path(skill_root)
        self.templates_path = self.skill_root / "templates.json"
        self.custom_templates_dir = Path.home() / ".claude" / "hook-templates"
        self.project_templates_dir = Path.cwd() / ".claude" / "hook-templates"

        # Ensure custom templates directory exists
        self.custom_templates_dir.mkdir(parents=True, exist_ok=True)

        # Load templates (with fallback)
        self.templates = self._load_all_templates()

    def _load_all_templates(self) -> Dict[str, Dict[str, Any]]:
        """
        Load templates from all sources with fallback strategy.

        Strategy:
        1. Load embedded templates (hardcoded)
        2. Load from templates.json (project level)
        3. Load custom templates from ~/.claude/hook-templates/
        4. Load custom templates from .claude/hook-templates/

        Returns:
            Combined template dictionary
        """
        templates = {}

        # Step 1: Load embedded templates
        templates.update(self._get_embedded_templates())
        print(f"✅ Loaded {len(templates)} embedded templates")

        # Step 2: Try load from templates.json
        if self.templates_path.exists():
            try:
                with open(self.templates_path, 'r') as f:
                    loaded = json.load(f)
                    templates.update(loaded)
                    print(f"✅ Loaded {len(loaded)} templates from templates.json")
            except json.JSONDecodeError as e:
                print(f"⚠️  templates.json is corrupted: {e}")
                print("   Using embedded templates as fallback")
            except Exception as e:
                print(f"⚠️  Error loading templates.json: {e}")
        else:
            print(f"⚠️  templates.json not found at {self.templates_path}")

        # Step 3: Load custom templates from user home
        custom_count = self._load_custom_templates(self.custom_templates_dir, templates)
        if custom_count > 0:
            print(f"✅ Loaded {custom_count} custom templates from ~/.claude/hook-templates/")

        # Step 4: Load custom templates from project
        if self.project_templates_dir.exists():
            project_count = self._load_custom_templates(self.project_templates_dir, templates)
            if project_count > 0:
                print(f"✅ Loaded {project_count} custom templates from .claude/hook-templates/")

        return templates

    def _load_custom_templates(self, templates_dir: Path, templates: Dict) -> int:
        """
        Load custom templates from directory.

        Args:
            templates_dir: Directory containing custom templates
            templates: Dictionary to update with loaded templates

        Returns:
            Number of templates loaded
        """
        count = 0

        if not templates_dir.exists():
            return 0

        for template_file in templates_dir.glob("*.json"):
            try:
                with open(template_file, 'r') as f:
                    template = json.load(f)
                    is_valid, errors = TemplateValidator.validate(template)

                    if not is_valid:
                        print(f"⚠️  Skipping {template_file.name}: {errors[0]}")
                        continue

                    template_name = template.get("name", template_file.stem)
                    templates[template_name] = template
                    count += 1

            except json.JSONDecodeError as e:
                print(f"⚠️  Failed to parse {template_file.name}: {e}")
            except Exception as e:
                print(f"⚠️  Error loading {template_file.name}: {e}")

        return count

    def _get_embedded_templates(self) -> Dict[str, Dict[str, Any]]:
        """
        Get embedded templates (hardcoded fallback).

        Returns:
            Dictionary of embedded templates
        """
        return {
            "post_tool_use_format": {
                "name": "post_tool_use_format",
                "description": "Auto-format code after editing",
                "event_type": "PostToolUse",
                "matcher": {"tool_names": ["Write", "Edit"]},
                "hooks": [{
                    "type": "command",
                    "command": "if command -v black &> /dev/null; then black \"$CLAUDE_TOOL_FILE_PATH\" || exit 0; fi",
                    "timeout": 60
                }]
            },
            "post_tool_use_git_add": {
                "name": "post_tool_use_git_add",
                "description": "Auto-stage files with git after editing",
                "event_type": "PostToolUse",
                "matcher": {"tool_names": ["Write", "Edit"]},
                "hooks": [{
                    "type": "command",
                    "command": "cd \"$CLAUDE_TOOL_PROJECT_ROOT\" && git add \"$CLAUDE_TOOL_FILE_PATH\" || exit 0",
                    "timeout": 10
                }]
            },
            "session_start_load_context": {
                "name": "session_start_load_context",
                "description": "Load project context at session start",
                "event_type": "SessionStart",
                "matcher": {},
                "hooks": [{
                    "type": "command",
                    "command": "test -f $CLAUDE_TOOL_PROJECT_ROOT/TODO.md && cat $CLAUDE_TOOL_PROJECT_ROOT/TODO.md || exit 0",
                    "timeout": 5
                }]
            },
            "stop_session_cleanup": {
                "name": "stop_session_cleanup",
                "description": "Cleanup temporary files at session end",
                "event_type": "Stop",
                "matcher": {},
                "hooks": [{
                    "type": "command",
                    "command": "rm -f /tmp/claude-* 2>/dev/null || exit 0",
                    "timeout": 10
                }]
            }
        }

    def get_template(self, template_name: str) -> Optional[Dict[str, Any]]:
        """
        Get a template by name.

        Args:
            template_name: Name of template to retrieve

        Returns:
            Template dict or None if not found
        """
        return self.templates.get(template_name)

    def list_templates(self, event_type: Optional[str] = None) -> Dict[str, Dict[str, str]]:
        """
        List available templates.

        Args:
            event_type: Filter by event type (optional)

        Returns:
            Dict mapping template names to descriptions
        """
        result = {}

        for name, template in self.templates.items():
            if event_type and template.get("event_type") != event_type:
                continue

            result[name] = {
                "description": template.get("description", ""),
                "event_type": template.get("event_type", "")
            }

        return result

    def validate_template(self, template: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate a template.

        Args:
            template: Template to validate

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        return TemplateValidator.validate(template)

    def add_custom_template(self, template: Dict[str, Any], save_location: str = "user") -> Tuple[bool, str]:
        """
        Add a custom template.

        Args:
            template: Template dictionary
            save_location: "user" or "project"

        Returns:
            Tuple of (success, message)
        """
        # Validate template
        is_valid, errors = TemplateValidator.validate(template)
        if not is_valid:
            return False, f"Template validation failed: {errors[0]}"

        # Determine save location
        if save_location == "user":
            save_dir = self.custom_templates_dir
        else:
            save_dir = self.project_templates_dir
            save_dir.mkdir(parents=True, exist_ok=True)

        # Save template
        template_name = template.get("name", "custom-template")
        template_path = save_dir / f"{template_name}.json"

        try:
            with open(template_path, 'w') as f:
                json.dump(template, f, indent=2)

            # Reload templates
            self.templates = self._load_all_templates()

            return True, f"✅ Template saved to {template_path}"

        except Exception as e:
            return False, f"❌ Error saving template: {e}"

    def get_status(self) -> str:
        """Get status report of template system."""
        return f"""
Template System Status:
- Total templates: {len(self.templates)}
- Embedded templates: {len(self._get_embedded_templates())}
- Custom user templates: {len(list(self.custom_templates_dir.glob('*.json')))}
- Project templates: {len(list(self.project_templates_dir.glob('*.json')))}
- templates.json status: {"✅ Present" if self.templates_path.exists() else "❌ Missing"}
"""


if __name__ == "__main__":
    loader = TemplateLoader()

    print(loader.get_status())

    print("\n" + "=" * 60)
    print("Available Templates")
    print("=" * 60)

    templates = loader.list_templates()
    for name, info in templates.items():
        print(f"\n{name}")
        print(f"  Event: {info['event_type']}")
        print(f"  Description: {info['description']}")
