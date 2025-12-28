#!/usr/bin/env python3
"""
Slash Command Factory CLI - Interactive interface for generating slash commands.

Provides guided 5-7 question flow with smart tool picker, validation,
and command generation.
"""

import argparse
import sys
import json
import re
from pathlib import Path
from typing import Optional, Dict, Any, List

from command_generator import SlashCommandGenerator


class SlashCommandFactoryCLI:
    """CLI interface for Slash Command Factory."""

    # Tool picker options
    AVAILABLE_TOOLS = {
        "Read": "Read and analyze files",
        "Write": "Create new files",
        "Edit": "Modify existing files",
        "Bash": "Execute shell commands",
        "Grep": "Search code content",
        "Glob": "Find files by pattern",
        "Task": "Launch agents"
    }

    # Tool combinations (for easy selection)
    TOOL_PRESETS = {
        "git": ["Read", "Bash(git status:*, git diff:*, git log:*, git branch:*, git add:*, git commit:*)"],
        "discovery": ["Bash(find:*, tree:*, ls:*)", "Grep", "Glob"],
        "content_analysis": ["Read", "Bash(grep:*, wc:*, head:*, tail:*, cat:*)", "Grep"],
        "code_generation": ["Read", "Write", "Edit"],
        "testing": ["Read", "Write", "Edit", "Bash(pytest:*, npm:*)"],
        "comprehensive": ["Read", "Write", "Edit", "Bash(git:*, find:*, grep:*)", "Grep", "Glob", "Task"]
    }

    def __init__(self):
        """Initialize CLI."""
        self.generator = SlashCommandGenerator()
        self.output_base = Path.cwd() / "generated-commands"
        self.output_base.mkdir(parents=True, exist_ok=True)

    def run_interactive(self):
        """Run 5-7 question interactive flow."""
        print("\n" + "=" * 70)
        print("⚡ SLASH COMMAND FACTORY - Interactive Mode")
        print("=" * 70 + "\n")

        # Q1: Command Purpose
        purpose = self._ask_question(
            "Q1: What should this slash command do?",
            "Examples: 'Analyze customer feedback', 'Generate API docs', 'Run tests'"
        )

        # Q2: Arguments (auto-detect)
        needs_args = self._auto_detect_arguments(purpose)
        if needs_args:
            arg_hint = self._ask_question(
                "Q2: Argument format? (e.g., [filename] [test-type])",
                "Press Enter for auto-detected format"
            )
        else:
            arg_hint = None
            print("   ℹ️ No arguments needed for this command")

        # Q3: Tools Selection
        tools = self._ask_tools()

        # Q4: Agent Integration
        uses_agents = self._ask_yes_no("Q4: Should this command launch agents?")
        agents = []
        if uses_agents:
            agents = self._ask_agents()

        # Q5: Output Type
        output_type = self._ask_output_type()

        # Q6: Model Preference
        model = self._ask_model()

        # Q7: Additional Features
        features = self._ask_features()

        # Generate command
        answers = {
            "purpose": purpose,
            "argument_hint": arg_hint,
            "tools": tools,
            "agents": agents,
            "output_type": output_type,
            "model": model,
            "features": features
        }

        # Show summary
        self._show_summary(answers)

        if self._ask_yes_no("\nConfirm and generate command?"):
            return self._generate_and_save(answers)
        else:
            print("❌ Cancelled.")
            return False

    def run_preset(self, preset_name: str):
        """Generate command from preset."""
        print(f"\n⚡ Generating command from preset: {preset_name}")

        try:
            result = self.generator.generate_from_preset(preset_name)
            return self._save_command(result)
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

    def _ask_question(self, question: str, hint: str = "") -> str:
        """Ask a question and get response."""
        print(f"\n{question}")
        if hint:
            print(f"   {hint}")
        response = input("   Your answer: ").strip()

        if not response:
            if hint:
                return hint
            return ""

        return response

    def _ask_yes_no(self, question: str) -> bool:
        """Ask yes/no question."""
        print(f"\n{question}")
        response = input("   (y/n): ").strip().lower()
        return response in ['y', 'yes']

    def _auto_detect_arguments(self, purpose: str) -> bool:
        """Auto-detect if command needs arguments."""
        argument_triggers = ["analyze", "process", "generate", "create", "build", "test", "check", "validate"]
        return any(trigger in purpose.lower() for trigger in argument_triggers)

    def _ask_tools(self) -> str:
        """Interactive tool selection with checkbox UI."""
        print("\nQ3: Which tools does this command need?")
        print("   (Use space to toggle, Enter when done)\n")

        selected = []
        tool_list = list(self.AVAILABLE_TOOLS.keys())

        # Show tool presets
        print("   Quick Selections (or pick manually):")
        for preset_name, preset_tools in self.TOOL_PRESETS.items():
            print(f"     - {preset_name}")

        # Ask if user wants preset
        preset_choice = input("\n   Choose preset (or press Enter for manual): ").strip().lower()
        if preset_choice in self.TOOL_PRESETS:
            return ",".join(self.TOOL_PRESETS[preset_choice])

        # Manual selection
        print("\n   Available tools:")
        for i, tool in enumerate(tool_list, 1):
            desc = self.AVAILABLE_TOOLS[tool]
            print(f"   {i}. [{' '  }] {tool:10} - {desc}")

        print("\n   Select tools (comma-separated numbers, e.g., 1,3,6):")
        choices = input("   Your selection: ").strip()

        try:
            indices = [int(x.strip()) - 1 for x in choices.split(",")]
            selected = [tool_list[i] for i in indices if 0 <= i < len(tool_list)]
        except ValueError:
            print("   ⚠️ Invalid selection. Using default: Read, Write, Edit")
            selected = ["Read", "Write", "Edit"]

        return ",".join(selected)

    def _ask_agents(self) -> List[str]:
        """Ask which agents to launch."""
        print("\n   Available agents:")
        agents = ["code-reviewer", "test-runner", "security-auditor", "documentation-generator"]

        for i, agent in enumerate(agents, 1):
            print(f"   {i}. {agent}")

        print("\n   Select agents (comma-separated numbers, e.g., 1,3):")
        choices = input("   Your selection: ").strip()

        try:
            indices = [int(x.strip()) - 1 for x in choices.split(",")]
            selected = [agents[i] for i in indices if 0 <= i < len(agents)]
            return selected
        except ValueError:
            return []

    def _ask_output_type(self) -> str:
        """Ask for output type."""
        print("\nQ5: What type of output should this command produce?")
        output_types = {
            "1": "Analysis - Research report, insights, recommendations",
            "2": "Files - Generated code, documentation, configs",
            "3": "Action - Execute tasks, run workflows",
            "4": "Report - Structured report with findings"
        }

        for key, desc in output_types.items():
            print(f"   {key}. {desc}")

        choice = input("   Your choice (1-4): ").strip()
        type_map = {"1": "analysis", "2": "files", "3": "action", "4": "report"}
        return type_map.get(choice, "analysis")

    def _ask_model(self) -> Optional[str]:
        """Ask for model preference."""
        print("\nQ6: Which Claude model should this use?")
        print("   1. Default (inherit from conversation)")
        print("   2. Sonnet (best for complex tasks)")
        print("   3. Haiku (fastest, cheapest)")
        print("   4. Opus (maximum capability)")

        choice = input("   Your choice (1-4) or press Enter for default: ").strip()
        model_map = {"1": None, "2": "sonnet", "3": "haiku", "4": "opus"}
        return model_map.get(choice, None)

    def _ask_features(self) -> List[str]:
        """Ask for additional features."""
        print("\nQ7: Any special features?")
        print("   1. Bash execution (!`command`) - Run shell commands in prompt")
        print("   2. File references (@file.txt) - Include file contents")
        print("   3. Context gathering - Read project files for context")

        print("\n   Select features (comma-separated, e.g., 1,3) or press Enter:")
        choice = input("   Your selection: ").strip()

        features = []
        if "1" in choice:
            features.append("bash_execution")
        if "2" in choice:
            features.append("file_references")
        if "3" in choice:
            features.append("context_gathering")

        return features

    def _show_summary(self, answers: Dict[str, Any]):
        """Show summary of answers for confirmation."""
        print("\n" + "=" * 70)
        print("📋 COMMAND CONFIGURATION SUMMARY")
        print("=" * 70)
        print(f"\nPurpose:        {answers['purpose']}")
        print(f"Arguments:      {answers['argument_hint'] or '(none)'}")
        print(f"Tools:          {answers['tools']}")
        print(f"Agents:         {', '.join(answers['agents']) if answers['agents'] else '(none)'}")
        print(f"Output Type:    {answers['output_type']}")
        print(f"Model:          {answers['model'] or 'Default'}")
        print(f"Features:       {', '.join(answers['features']) if answers['features'] else '(none)'}")
        print("\n" + "=" * 70)

    def _generate_and_save(self, answers: Dict[str, Any]) -> bool:
        """Generate and save command."""
        try:
            result = self.generator.generate_custom(answers)
            return self._save_command(result)
        except Exception as e:
            print(f"❌ Error generating command: {e}")
            return False

    def _save_command(self, result: Dict[str, Any]) -> bool:
        """Save generated command to disk."""
        try:
            command_name = result["command_name"]
            command_path = self.output_base / command_name

            # Create directory
            command_path.mkdir(parents=True, exist_ok=True)

            # Write command file
            cmd_file = command_path / f"{command_name}.md"
            with open(cmd_file, 'w') as f:
                f.write(result["command_content"])

            # Write README
            readme_file = command_path / "README.md"
            readme_content = self._generate_readme(command_name)
            with open(readme_file, 'w') as f:
                f.write(readme_content)

            print(f"\n✅ Command created successfully!")
            print(f"\n📁 Location: {command_path}")
            print(f"   - {cmd_file.name}")
            print(f"   - {readme_file.name}")

            print(f"\n📋 Next steps:")
            print(f"   1. Review the command: less {cmd_file}")
            print(f"   2. Copy to Claude Code:")
            print(f"      cp {cmd_file} .claude/commands/")
            print(f"   3. Restart Claude Code")
            print(f"   4. Test: /{command_name}")

            return True

        except Exception as e:
            print(f"❌ Error saving command: {e}")
            return False

    def _generate_readme(self, command_name: str) -> str:
        """Generate README for command."""
        return f"""# /{command_name}

## Installation

Copy the command file to your Claude Code commands directory:

```bash
cp {command_name}.md ~/.claude/commands/
# or for project-level:
cp {command_name}.md .claude/commands/
```

Then restart Claude Code.

## Usage

```
/{command_name} [arguments]
```

## Testing

Try the command with test arguments to verify it works:

```
/{command_name} test-argument
```

## Customization

Edit the command file to:
- Change behavior
- Adjust tools and permissions
- Modify success criteria
- Update documentation

## Troubleshooting

If the command doesn't work:
1. Check Claude Code logs: `tail -f ~/.claude/logs/`
2. Verify tools are installed and available
3. Check file paths are correct
4. Review the command's allowed-tools
"""


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Slash Command Factory - Generate Claude Code slash commands",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (5-7 question flow)
  slash-command-factory-cli.py -i

  # Generate from preset
  slash-command-factory-cli.py --preset research-business

  # List all presets
  slash-command-factory-cli.py --list-presets
        """
    )

    parser.add_argument("-i", "--interactive", action="store_true",
                       help="Interactive mode (guided 5-7 question flow)")
    parser.add_argument("--preset", help="Generate from preset")
    parser.add_argument("--list-presets", action="store_true",
                       help="List available presets")
    parser.add_argument("--output", type=Path,
                       help="Output directory (default: ./generated-commands/)")

    args = parser.parse_args()

    cli = SlashCommandFactoryCLI()

    if args.output:
        cli.output_base = args.output
        cli.output_base.mkdir(parents=True, exist_ok=True)

    # Execute mode
    if args.interactive:
        success = cli.run_interactive()
    elif args.preset:
        success = cli.run_preset(args.preset)
    elif args.list_presets:
        try:
            presets = cli.generator.presets
            print("\n" + "=" * 70)
            print("⚡ AVAILABLE SLASH COMMAND PRESETS")
            print("=" * 70 + "\n")

            for name, preset in presets.items():
                print(f"  {name}")
                print(f"    Description: {preset.get('description', 'N/A')}")
                print()

            print(f"Total: {len(presets)} presets available")
            success = True
        except Exception as e:
            print(f"❌ Error listing presets: {e}")
            success = False
    else:
        parser.print_help()
        return

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
