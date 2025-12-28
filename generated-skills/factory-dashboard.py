#!/usr/bin/env python3
"""
Factory Dashboard - Unified view of all Claude Code factory outputs.

Provides overview of agents, commands, hooks, and skills with health status,
recent activity, and quick actions.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from collections import defaultdict


class FactoryDashboard:
    """Unified dashboard for all factory outputs."""

    def __init__(self):
        """Initialize dashboard."""
        self.agents_dir = Path.home() / ".claude" / "agents"
        self.commands_dir = Path.home() / ".claude" / "commands"
        self.hooks_dir = Path.home() / ".claude" / "hooks"
        self.skills_dir = Path.cwd() / "generated-skills"

    def get_inventory(self) -> Dict[str, int]:
        """Get count of all artifacts."""
        return {
            "agents": len(list(self.agents_dir.glob("*.md"))) if self.agents_dir.exists() else 0,
            "commands": len(list(self.commands_dir.glob("*.md"))) if self.commands_dir.exists() else 0,
            "hooks": len(list(self.hooks_dir.glob("*.json"))) if self.hooks_dir.exists() else 0,
            "skills": len(list(self.skills_dir.glob("*/SKILL.md"))) if self.skills_dir.exists() else 0,
        }

    def get_agent_status(self) -> Dict[str, Dict]:
        """Get status of all agents."""
        agents = {}

        if not self.agents_dir.exists():
            return agents

        for agent_file in self.agents_dir.glob("*.md"):
            try:
                with open(agent_file, 'r') as f:
                    content = f.read()

                # Extract metadata from YAML
                yaml_section = content.split("---")[1] if "---" in content else ""

                agents[agent_file.stem] = {
                    "status": "✅ Ready",
                    "type": self._extract_yaml_field(yaml_section, "color"),
                    "domain": self._extract_yaml_field(yaml_section, "field"),
                    "file_size_kb": agent_file.stat().st_size / 1024,
                    "modified": self._get_modified_time(agent_file),
                }
            except Exception as e:
                agents[agent_file.stem] = {"status": f"❌ Error: {e}"}

        return agents

    def get_command_status(self) -> Dict[str, Dict]:
        """Get status of all commands."""
        commands = {}

        if not self.commands_dir.exists():
            return commands

        for cmd_file in self.commands_dir.glob("*.md"):
            try:
                with open(cmd_file, 'r') as f:
                    content = f.read()

                # Extract metadata from YAML
                yaml_section = content.split("---")[1] if "---" in content else ""
                has_test_examples = "TEST_EXAMPLES.md" in str(self.commands_dir)

                commands[cmd_file.stem] = {
                    "status": "✅ Ready" if has_test_examples else "⚠️ Untested",
                    "has_tests": has_test_examples,
                    "tools": self._extract_yaml_field(yaml_section, "allowed-tools"),
                    "file_size_kb": cmd_file.stat().st_size / 1024,
                    "modified": self._get_modified_time(cmd_file),
                }
            except Exception as e:
                commands[cmd_file.stem] = {"status": f"❌ Error: {e}"}

        return commands

    def get_hook_status(self) -> Dict[str, Dict]:
        """Get status of all hooks."""
        hooks = {}

        if not self.hooks_dir.exists():
            return hooks

        for hook_file in self.hooks_dir.glob("*.json"):
            try:
                with open(hook_file, 'r') as f:
                    hook_config = json.load(f)

                hooks[hook_file.stem] = {
                    "status": "✅ Ready",
                    "event_type": hook_config.get("matcher", {}).get("type", "Unknown"),
                    "modified": self._get_modified_time(hook_file),
                }
            except Exception as e:
                hooks[hook_file.stem] = {"status": f"❌ Error: {e}"}

        return hooks

    def get_skill_status(self) -> Dict[str, Dict]:
        """Get status of all skills."""
        skills = {}

        if not self.skills_dir.exists():
            return skills

        for skill_dir in self.skills_dir.iterdir():
            if not skill_dir.is_dir():
                continue

            skill_md = skill_dir / "SKILL.md"
            if skill_md.exists():
                try:
                    with open(skill_md, 'r') as f:
                        content = f.read()

                    # Extract metadata
                    yaml_section = content.split("---")[1] if "---" in content else ""
                    description = self._extract_yaml_field(yaml_section, "description")

                    skills[skill_dir.name] = {
                        "status": "✅ Production",
                        "description": description[:50] + "..." if len(description) > 50 else description,
                        "files": len(list(skill_dir.glob("*.py"))),
                        "modified": self._get_modified_time(skill_md),
                    }
                except Exception as e:
                    skills[skill_dir.name] = {"status": f"❌ Error: {e}"}

        return skills

    def get_health_summary(self) -> Dict:
        """Get overall health summary."""
        agents = self.get_agent_status()
        commands = self.get_command_status()
        hooks = self.get_hook_status()
        skills = self.get_skill_status()

        untested_commands = [c for c, s in commands.items() if not s.get("has_tests")]
        errored_artifacts = (
            [a for a, s in agents.items() if "❌" in s.get("status", "")] +
            [c for c, s in commands.items() if "❌" in s.get("status", "")] +
            [h for h, s in hooks.items() if "❌" in s.get("status", "")]
        )

        return {
            "total_artifacts": sum(len(d) for d in [agents, commands, hooks, skills]),
            "healthy_status": len(errored_artifacts) == 0,
            "issues": {
                "untested_commands": len(untested_commands),
                "errored_artifacts": len(errored_artifacts),
            },
            "recommendations": self._generate_recommendations(
                untested_commands, errored_artifacts
            )
        }

    def print_dashboard(self):
        """Print formatted dashboard to console."""
        inventory = self.get_inventory()
        health = self.get_health_summary()

        print("\n" + "=" * 70)
        print("🏭 CLAUDE CODE FACTORY DASHBOARD")
        print("=" * 70)

        # Inventory
        print("\n📦 INVENTORY")
        print(f"   Agents:   {inventory['agents']:3d} {'✅' if inventory['agents'] > 0 else '❌'}")
        print(f"   Commands: {inventory['commands']:3d} {'✅' if inventory['commands'] > 0 else '❌'}")
        print(f"   Hooks:    {inventory['hooks']:3d} {'✅' if inventory['hooks'] > 0 else '❌'}")
        print(f"   Skills:   {inventory['skills']:3d} {'✅' if inventory['skills'] > 0 else '❌'}")

        # Health
        print("\n🏥 HEALTH")
        if health["healthy_status"]:
            print("   Status: 🟢 HEALTHY")
        else:
            print("   Status: 🟡 ISSUES DETECTED")

        if health["issues"]["untested_commands"] > 0:
            print(f"   ⚠️  {health['issues']['untested_commands']} untested commands")

        if health["issues"]["errored_artifacts"] > 0:
            print(f"   ❌ {health['issues']['errored_artifacts']} errored artifacts")

        # Recent activity
        print("\n📋 RECENT ACTIVITY")
        agents = self.get_agent_status()
        if agents:
            latest_agent = max(agents.items(), key=lambda x: x[1].get("modified", ""))
            print(f"   Latest agent: {latest_agent[0]}")

        # Recommendations
        if health["recommendations"]:
            print("\n💡 RECOMMENDATIONS")
            for rec in health["recommendations"]:
                print(f"   - {rec}")

        print("\n" + "=" * 70 + "\n")

    def _extract_yaml_field(self, yaml_section: str, field_name: str) -> str:
        """Extract field from YAML."""
        import re
        match = re.search(rf'^{field_name}:\s*(.+)$', yaml_section, re.MULTILINE)
        return match.group(1).strip() if match else "unknown"

    def _get_modified_time(self, file_path: Path) -> str:
        """Get human-readable modified time."""
        try:
            mtime = file_path.stat().st_mtime
            dt = datetime.fromtimestamp(mtime)
            return dt.strftime("%Y-%m-%d %H:%M")
        except:
            return "unknown"

    def _generate_recommendations(self, untested_commands: List[str],
                                 errored_artifacts: List[str]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []

        if untested_commands:
            recommendations.append(f"Add tests for: {', '.join(untested_commands[:3])}")

        if errored_artifacts:
            recommendations.append(f"Fix errors in: {', '.join(errored_artifacts[:3])}")

        if not untested_commands and not errored_artifacts:
            recommendations.append("✅ Everything looks good! Keep building!")

        return recommendations

    def export_report(self, output_file: str = "factory-report.json"):
        """Export dashboard data to JSON report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "inventory": self.get_inventory(),
            "health": self.get_health_summary(),
            "agents": self.get_agent_status(),
            "commands": self.get_command_status(),
            "hooks": self.get_hook_status(),
            "skills": self.get_skill_status(),
        }

        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"✅ Report exported to {output_file}")
        return output_file


if __name__ == "__main__":
    dashboard = FactoryDashboard()
    dashboard.print_dashboard()

    # Export report
    dashboard.export_report()
