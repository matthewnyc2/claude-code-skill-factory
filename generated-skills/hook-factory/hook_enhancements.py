#!/usr/bin/env python3
"""
Hook Factory Enhancements - Performance monitoring and hook chaining.

Adds:
1. Hook performance analysis (execution times, failures, health)
2. Hook chaining/workflows (multi-step automation)
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import statistics


class HookPerformanceMonitor:
    """Monitors and analyzes hook performance."""

    def __init__(self, log_dir: str = None):
        """Initialize performance monitor."""
        if log_dir is None:
            log_dir = str(Path.home() / ".claude" / "hook-logs")

        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

    def log_hook_execution(self, hook_name: str, success: bool, duration_ms: int,
                          error: Optional[str] = None):
        """Log a hook execution."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "hook": hook_name,
            "success": success,
            "duration_ms": duration_ms,
            "error": error
        }

        hook_log = self.log_dir / f"{hook_name}.jsonl"
        with open(hook_log, 'a') as f:
            f.write(json.dumps(log_entry) + "\n")

    def analyze_hook_performance(self, hook_name: str, days: int = 30) -> Dict:
        """Analyze hook performance over time."""
        hook_log = self.log_dir / f"{hook_name}.jsonl"

        if not hook_log.exists():
            return {"error": f"No logs found for {hook_name}"}

        entries = []
        cutoff_date = datetime.now() - timedelta(days=days)

        with open(hook_log, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line)
                    entry_date = datetime.fromisoformat(entry["timestamp"])
                    if entry_date > cutoff_date:
                        entries.append(entry)
                except json.JSONDecodeError:
                    continue

        if not entries:
            return {"error": f"No recent logs for {hook_name}"}

        # Calculate metrics
        successful = [e for e in entries if e["success"]]
        failed = [e for e in entries if not e["success"]]
        durations = [e["duration_ms"] for e in successful]

        return {
            "hook_name": hook_name,
            "total_executions": len(entries),
            "success_rate": round(len(successful) / len(entries) * 100, 1),
            "failure_count": len(failed),
            "avg_duration_ms": round(statistics.mean(durations)) if durations else 0,
            "min_duration_ms": min(durations) if durations else 0,
            "max_duration_ms": max(durations) if durations else 0,
            "p95_duration_ms": round(statistics.quantiles(durations, n=20)[18]) if len(durations) > 2 else 0,
            "status": self._determine_health(len(successful), len(failed), durations),
            "recommendations": self._generate_recommendations(len(successful), len(failed), durations)
        }

    def _determine_health(self, successes: int, failures: int, durations: List[int]) -> str:
        """Determine hook health status."""
        total = successes + failures
        success_rate = successes / total if total > 0 else 0

        if success_rate < 0.9:
            return "🔴 FAILING"
        elif success_rate < 0.99:
            return "🟡 UNRELIABLE"
        elif durations and statistics.mean(durations) > 5000:
            return "🟡 SLOW"
        else:
            return "🟢 HEALTHY"

    def _generate_recommendations(self, successes: int, failures: int, durations: List[int]) -> List[str]:
        """Generate optimization recommendations."""
        recommendations = []
        total = successes + failures

        if failures > total * 0.1:
            recommendations.append("⚠️ High failure rate. Check prerequisites and error handling.")

        if durations and statistics.mean(durations) > 5000:
            recommendations.append("⚠️ Slow execution. Consider async execution or optimization.")

        if durations and statistics.mean(durations) > 30000:
            recommendations.append("⚠️ Very slow. This hook may need refactoring.")

        if not recommendations:
            recommendations.append("✅ Hook is performing well.")

        return recommendations

    def get_health_dashboard(self) -> Dict[str, Dict]:
        """Get dashboard of all hook health statuses."""
        dashboard = {}

        for log_file in self.log_dir.glob("*.jsonl"):
            hook_name = log_file.stem
            performance = self.analyze_hook_performance(hook_name)

            if "error" not in performance:
                dashboard[hook_name] = {
                    "status": performance["status"],
                    "success_rate": performance["success_rate"],
                    "executions": performance["total_executions"],
                    "avg_duration": performance["avg_duration_ms"]
                }

        return dashboard


class HookChainer:
    """Manages hook chains and workflows."""

    def __init__(self):
        """Initialize hook chainer."""
        self.chains = {}

    def create_hook_chain(self, chain_name: str, hooks: List[str],
                         on_failure: str = "stop") -> Dict:
        """
        Create a hook execution chain.

        Args:
            chain_name: Name of the chain
            hooks: List of hook names in execution order
            on_failure: "stop" or "continue" on hook failure

        Returns:
            Chain configuration
        """
        chain_config = {
            "name": chain_name,
            "hooks": hooks,
            "on_failure": on_failure,
            "created": datetime.now().isoformat(),
            "execution_pattern": self._determine_pattern(hooks)
        }

        self.chains[chain_name] = chain_config
        return chain_config

    def _determine_pattern(self, hooks: List[str]) -> str:
        """Determine execution pattern (parallel, sequential, mixed)."""
        # This could be smarter - for now, sequential is safe
        return "sequential"

    def validate_chain(self, chain_config: Dict) -> Tuple[bool, List[str]]:
        """Validate hook chain configuration."""
        errors = []
        hooks = chain_config.get("hooks", [])

        if not hooks or len(hooks) < 2:
            errors.append("Chain must have at least 2 hooks")

        # Check for circular dependencies
        if self._has_circular_dependency(hooks):
            errors.append("Chain has circular dependency")

        # Check all hooks exist (placeholder validation)
        for hook in hooks:
            if not self._hook_exists(hook):
                errors.append(f"Hook '{hook}' does not exist")

        return len(errors) == 0, errors

    def _has_circular_dependency(self, hooks: List[str]) -> bool:
        """Check for circular dependencies in hook chain."""
        # Simple check: no hook should appear twice
        return len(hooks) != len(set(hooks))

    def _hook_exists(self, hook_name: str) -> bool:
        """Check if hook is registered (placeholder)."""
        # In real implementation, would check against hook registry
        return True

    def generate_hook_chain_config(self, chain: Dict) -> str:
        """
        Generate hook configuration that implements the chain.

        Args:
            chain: Chain configuration

        Returns:
            Hook JSON configuration
        """
        hooks_list = chain.get("hooks", [])

        # Build hook commands that chain execution
        hook_commands = []

        for i, hook_name in enumerate(hooks_list):
            if i == 0:
                # First hook runs normally
                hook_commands.append({
                    "type": "command",
                    "name": hook_name,
                    "command": f"run-hook {hook_name}",
                    "on_failure": chain.get("on_failure", "stop")
                })
            else:
                # Subsequent hooks trigger if previous succeeded
                hook_commands.append({
                    "type": "command",
                    "name": hook_name,
                    "command": f"if [ $? -eq 0 ]; then run-hook {hook_name}; fi",
                    "on_failure": chain.get("on_failure", "stop")
                })

        config = {
            "name": chain["name"],
            "description": f"Hook chain: {' → '.join(hooks_list)}",
            "event_type": "PostToolUse",  # Trigger after tool use
            "hooks": hook_commands,
            "chain_metadata": {
                "total_hooks": len(hooks_list),
                "execution_pattern": chain.get("execution_pattern", "sequential"),
                "on_failure": chain.get("on_failure", "stop")
            }
        }

        return json.dumps(config, indent=2)

    def get_preset_chains(self) -> Dict[str, List[str]]:
        """Get pre-built hook chain templates."""
        return {
            "full-workflow": [
                "auto-format-code",
                "auto-add-git",
                "run-tests",
                "pre-commit-check"
            ],
            "testing-workflow": [
                "auto-format-code",
                "run-unit-tests",
                "run-integration-tests"
            ],
            "git-workflow": [
                "pre-commit-format",
                "auto-add-git",
                "git-commit-template"
            ],
            "quality-workflow": [
                "run-tests",
                "code-coverage-check",
                "lint-check"
            ]
        }


def create_hook_workflow_from_template(template_name: str) -> Optional[Dict]:
    """
    Create a complete hook workflow from a template.

    Args:
        template_name: Name of preset template

    Returns:
        Hook workflow configuration or None
    """
    chainer = HookChainer()
    presets = chainer.get_preset_chains()

    if template_name not in presets:
        return None

    hooks = presets[template_name]
    chain = chainer.create_hook_chain(
        chain_name=template_name,
        hooks=hooks,
        on_failure="stop"
    )

    return chainer.generate_hook_chain_config(chain)


if __name__ == "__main__":
    # Test performance monitoring
    monitor = HookPerformanceMonitor()

    # Simulate hook executions
    print("Logging hook executions...")
    import random
    for _ in range(20):
        duration = random.randint(100, 5000)
        success = random.random() > 0.1  # 90% success rate
        monitor.log_hook_execution("test-runner", success, duration)

    # Analyze performance
    print("\n" + "=" * 60)
    print("HOOK PERFORMANCE ANALYSIS")
    print("=" * 60)

    perf = monitor.analyze_hook_performance("test-runner")
    print(f"Hook: {perf['hook_name']}")
    print(f"Status: {perf['status']}")
    print(f"Success Rate: {perf['success_rate']}%")
    print(f"Executions: {perf['total_executions']}")
    print(f"Avg Duration: {perf['avg_duration_ms']}ms")
    print(f"P95 Duration: {perf['p95_duration_ms']}ms")
    print("\nRecommendations:")
    for rec in perf['recommendations']:
        print(f"  {rec}")

    # Test hook chaining
    print("\n" + "=" * 60)
    print("HOOK CHAINING")
    print("=" * 60)

    chainer = HookChainer()
    chain = chainer.create_hook_chain(
        chain_name="full-workflow",
        hooks=["auto-format-code", "auto-add-git", "run-tests"],
        on_failure="stop"
    )

    print(f"Chain: {chain['name']}")
    print(f"Hooks: {' → '.join(chain['hooks'])}")
    print(f"On Failure: {chain['on_failure']}")

    # Validate chain
    valid, errors = chainer.validate_chain(chain)
    print(f"Valid: {valid}")

    # Generate config
    config = chainer.generate_hook_chain_config(chain)
    print("\nGenerated Configuration:")
    print(config[:300] + "...")
