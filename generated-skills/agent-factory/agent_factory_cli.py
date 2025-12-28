#!/usr/bin/env python3
"""
Agent Factory CLI - Command-line interface for generating Claude Code agents.

Provides interactive and batch modes for creating production-ready agents
with proper YAML frontmatter, system prompts, and validation.
"""

import argparse
import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any

from agent_generator import AgentGenerator, generate_agent_file
from agent_prompt_synthesizer import PromptSynthesizer


class AgentFactoryCLI:
    """CLI interface for Agent Factory."""

    def __init__(self):
        """Initialize CLI."""
        self.generator = AgentGenerator()
        self.synthesizer = PromptSynthesizer()
        self.output_base = Path.home() / ".claude" / "agents"
        self.output_base.mkdir(parents=True, exist_ok=True)

    def interactive_mode(self):
        """Run interactive 5-question flow."""
        print("\n" + "=" * 60)
        print("🤖 AGENT FACTORY - Interactive Mode")
        print("=" * 60 + "\n")

        # Q1: Agent Name
        while True:
            agent_name = input("Q1: Agent name (kebab-case, e.g., my-agent): ").strip().lower()
            if self._validate_kebab_case(agent_name):
                break
            print("❌ Invalid. Use lowercase letters and hyphens only.")

        # Q2: Agent Type
        agent_types = ["Strategic", "Implementation", "Quality", "Coordination"]
        print(f"\nQ2: Agent type?")
        for i, t in enumerate(agent_types, 1):
            print(f"   {i}. {t}")
        type_choice = input("Enter choice (1-4): ").strip()
        agent_type = agent_types[int(type_choice) - 1] if type_choice.isdigit() else "Implementation"

        # Q3: Description
        description = input("\nQ3: What does this agent do? (brief description): ").strip()
        if not description:
            description = f"{agent_type} agent for specialized tasks"

        # Q4: Domain
        domains = ["frontend", "backend", "fullstack", "mobile", "devops", "testing", "security", "data", "ai", "general"]
        print(f"\nQ4: Primary domain?")
        for i, d in enumerate(domains, 1):
            print(f"   {i}. {d}")
        domain_choice = input("Enter choice (1-10) or custom domain: ").strip()
        if domain_choice.isdigit():
            domain = domains[int(domain_choice) - 1]
        else:
            domain = domain_choice if domain_choice else "general"

        # Q5: MCP Servers
        mcp_tools = input("\nQ5: MCP servers needed? (e.g., mcp__github, mcp__playwright) or press Enter: ").strip()

        # Generate agent
        config = {
            "agent_name": agent_name,
            "description": description,
            "agent_type": agent_type,
            "field": domain,
            "mcp_tools": mcp_tools.split(",") if mcp_tools else None
        }

        return self._generate_and_save(config)

    def preset_mode(self, agent_type: str, domain: str):
        """Generate agent from preset configuration."""
        print(f"\n🤖 Generating {agent_type} agent for {domain}...")

        # Create valid agent name from type + domain
        agent_name = f"{domain}-{agent_type.lower().replace(' ', '-')}"

        config = {
            "agent_name": agent_name,
            "description": f"{agent_type} agent specializing in {domain}",
            "agent_type": agent_type,
            "field": domain
        }

        return self._generate_and_save(config)

    def batch_mode(self, config_file: str):
        """Generate multiple agents from JSON config."""
        try:
            with open(config_file, 'r') as f:
                configs = json.load(f)

            results = []
            for config in configs:
                result = self._generate_and_save(config)
                results.append(result)

            print(f"\n✅ Generated {len(results)} agents successfully")
            return True

        except Exception as e:
            print(f"❌ Error in batch mode: {e}")
            return False

    def _generate_and_save(self, config: Dict[str, Any]) -> bool:
        """Generate agent file and save to disk."""
        try:
            # Validate configuration
            self.generator._validate_config(config)

            # Synthesize system prompt
            system_prompt = self.synthesizer.generate_prompt(
                agent_type=config.get("agent_type", "Implementation"),
                agent_name=config["agent_name"],
                domain=config.get("field", "general"),
                tools=config.get("tools"),
                mcp_tools=config.get("mcp_tools")
            )

            # Add system prompt to config
            config["system_prompt"] = system_prompt

            # Generate complete agent file
            agent_content = self.generator.generate_agent(config)

            # Determine output path
            agent_name = config["agent_name"]
            output_path = self.output_base / f"{agent_name}.md"

            # Check if exists
            if output_path.exists():
                response = input(f"\n⚠️  {agent_name}.md already exists. Overwrite? (y/n): ").strip().lower()
                if response != 'y':
                    print("❌ Cancelled.")
                    return False

            # Write file
            with open(output_path, 'w') as f:
                f.write(agent_content)

            # Validate generated file
            validation = self.generator.validate_yaml_format(agent_content.split('\n\n')[0])
            if not validation["valid"]:
                print(f"⚠️  Validation warnings:")
                for error in validation["errors"]:
                    print(f"   - {error}")

            print(f"\n✅ Agent created: {output_path}")
            print(f"   Name: {agent_name}")
            print(f"   Type: {config.get('agent_type', 'Implementation')}")
            print(f"   Domain: {config.get('field', 'general')}")
            print(f"\n📋 Next steps:")
            print(f"   1. Review: {output_path}")
            print(f"   2. Copy to project if needed: cp {output_path} .claude/agents/")
            print(f"   3. Restart Claude Code for agent discovery")

            return True

        except ValueError as e:
            print(f"❌ Error: {e}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            return False

    def _validate_kebab_case(self, name: str) -> bool:
        """Validate kebab-case naming."""
        import re
        return bool(re.match(r'^[a-z]+(-[a-z]+)*$', name))


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Agent Factory - Generate Claude Code agents",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (guided 5-question flow)
  agent-factory-cli.py -i

  # Generate specific agent
  agent-factory-cli.py --name my-agent --type Implementation --domain backend

  # Generate from preset
  agent-factory-cli.py --preset frontend --type Implementation

  # Batch generation
  agent-factory-cli.py --batch agents.json
        """
    )

    parser.add_argument("-i", "--interactive", action="store_true",
                       help="Interactive mode (guided 5-question flow)")
    parser.add_argument("--name", help="Agent name (kebab-case)")
    parser.add_argument("--type", choices=["Strategic", "Implementation", "Quality", "Coordination"],
                       default="Implementation", help="Agent type")
    parser.add_argument("--domain", help="Agent domain/field")
    parser.add_argument("--preset", help="Generate from preset (domain name)")
    parser.add_argument("--batch", help="Batch generation from JSON config")
    parser.add_argument("--output", type=Path, help="Output directory (default: ~/.claude/agents/)")

    args = parser.parse_args()

    cli = AgentFactoryCLI()

    # Set custom output if provided
    if args.output:
        cli.output_base = args.output
        cli.output_base.mkdir(parents=True, exist_ok=True)

    # Execute appropriate mode
    if args.interactive:
        success = cli.interactive_mode()
    elif args.batch:
        success = cli.batch_mode(args.batch)
    elif args.preset:
        success = cli.preset_mode(args.preset, args.domain or args.preset)
    elif args.name:
        config = {
            "agent_name": args.name,
            "description": f"{args.type} agent for {args.domain or 'general tasks'}",
            "agent_type": args.type,
            "field": args.domain or "general"
        }
        success = cli._generate_and_save(config)
    else:
        parser.print_help()
        return

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
