#!/usr/bin/env python3
"""
Agent Factory Enhancements - Dependency mapping and capability matcher.

Adds intelligent features:
1. Agent dependency mapping (safe execution patterns)
2. Auto-recommended tool access based on agent purpose
"""

from typing import Dict, List, Set, Optional
import re


class AgentDependencyMapper:
    """Maps agent dependencies and safe execution patterns."""

    # Agent type execution patterns
    EXECUTION_PATTERNS = {
        "Strategic": {
            "pattern": "parallel",
            "max_concurrent": 5,
            "description": "Can safely run 4-5 strategic agents in parallel",
            "safe_with": ["Strategic", "Planning", "Research"]
        },
        "Implementation": {
            "pattern": "coordinated",
            "max_concurrent": 3,
            "description": "Run 2-3 implementation agents with coordination",
            "safe_with": ["Implementation", "Building"]
        },
        "Quality": {
            "pattern": "sequential",
            "max_concurrent": 1,
            "description": "MUST run one at a time (never parallel)",
            "safe_with": []
        },
        "Coordination": {
            "pattern": "orchestrator",
            "max_concurrent": 1,
            "description": "Manages other agents",
            "safe_with": ["Strategic", "Implementation"]
        }
    }

    # Safe agent combinations
    SAFE_COMBINATIONS = {
        "frontend-developer": {
            "safe_with": ["backend-developer", "api-builder", "database-designer"],
            "unsafe_with": ["test-runner", "code-reviewer"],
            "execution_pattern": "parallel"
        },
        "backend-developer": {
            "safe_with": ["frontend-developer", "api-builder", "database-designer"],
            "unsafe_with": ["test-runner", "code-reviewer"],
            "execution_pattern": "parallel"
        },
        "test-runner": {
            "safe_with": [],
            "unsafe_with": ["frontend-developer", "backend-developer"],
            "execution_pattern": "sequential"
        },
        "code-reviewer": {
            "safe_with": ["security-auditor"],
            "unsafe_with": ["frontend-developer", "backend-developer"],
            "execution_pattern": "sequential"
        }
    }

    def map_agent_dependencies(self, agent_config: Dict) -> Dict:
        """
        Map agent dependencies and safe execution patterns.

        Args:
            agent_config: Agent configuration

        Returns:
            Dependency mapping with execution rules
        """
        agent_name = agent_config.get("agent_name", "unknown")
        agent_type = agent_config.get("agent_type", "Implementation")

        # Get base execution pattern
        pattern_info = self.EXECUTION_PATTERNS.get(agent_type, {})

        # Get specific safe combinations if known
        safe_with = self.SAFE_COMBINATIONS.get(agent_name, {}).get("safe_with", [])
        unsafe_with = self.SAFE_COMBINATIONS.get(agent_name, {}).get("unsafe_with", [])

        return {
            "agent_name": agent_name,
            "execution_pattern": pattern_info.get("pattern", "coordinated"),
            "max_concurrent": pattern_info.get("max_concurrent", 1),
            "safe_with": safe_with,
            "unsafe_with": unsafe_with,
            "description": pattern_info.get("description", ""),
            "workflow_example": self._generate_workflow_example(agent_name, agent_type)
        }

    def _generate_workflow_example(self, agent_name: str, agent_type: str) -> str:
        """Generate workflow example for agent."""
        if agent_type == "Coordination":
            return f"""
Workflow: Multi-Agent Coordination
1. {agent_name} (Coordinator) - Analyzes requirements
2. [implementation-agent] (parallel execution)
   - frontend-developer
   - backend-developer
3. {agent_name} (Coordinator) - Validates integration
4. [quality-agent] (sequential)
   - test-runner
"""
        elif agent_type == "Implementation":
            return f"""
Workflow: Feature Development
1. {agent_name} - Implement feature
2. [parallel-agent] - Build complementary component
3. [sequential-agent] - Run tests
"""
        else:
            return f"Single {agent_type} agent workflow"

    def validate_agent_workflow(self, agents: List[str], execution_order: List[str]) -> Dict:
        """
        Validate a multi-agent workflow.

        Args:
            agents: List of agent names
            execution_order: Desired execution order

        Returns:
            Validation result with warnings
        """
        warnings = []
        errors = []

        # Check for incompatible concurrent agents
        quality_agents = ["test-runner", "code-reviewer", "security-auditor"]
        concurrent_agents = agents[:3]  # Assume first 3 run in parallel

        quality_in_concurrent = [a for a in concurrent_agents if a in quality_agents]
        if len(quality_in_concurrent) > 0:
            warnings.append(f"⚠️ Quality agents should not run in parallel: {quality_in_concurrent}")

        # Check for unsafe combinations
        for i, agent1 in enumerate(agents):
            for agent2 in agents[i+1:]:
                safe_with = self.SAFE_COMBINATIONS.get(agent1, {}).get("safe_with", [])
                unsafe_with = self.SAFE_COMBINATIONS.get(agent1, {}).get("unsafe_with", [])

                if agent2 in unsafe_with:
                    errors.append(f"❌ {agent1} cannot run with {agent2}")
                if safe_with and agent2 not in safe_with and agent1 in self.SAFE_COMBINATIONS:
                    warnings.append(f"⚠️ {agent1} not optimized for {agent2}")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings,
            "recommended_order": self._recommend_execution_order(agents)
        }

    def _recommend_execution_order(self, agents: List[str]) -> List[List[str]]:
        """Recommend execution order (phases) for agents."""
        strategic = [a for a in agents if any(x in a.lower() for x in ["planner", "architect", "analyzer"])]
        implementation = [a for a in agents if any(x in a.lower() for x in ["developer", "builder", "engineer"])]
        quality = [a for a in agents if any(x in a.lower() for x in ["test", "reviewer", "auditor"])]

        phases = []
        if strategic:
            phases.append(strategic)
        if implementation:
            phases.append(implementation)
        if quality:
            phases.append(quality)

        return phases or [[a] for a in agents]


class CapabilityMatcher:
    """Auto-recommends tools based on agent purpose."""

    # Keyword patterns for tool recommendations
    KEYWORD_PATTERNS = {
        "Read": [
            "analyze", "review", "inspect", "examine", "read", "understand",
            "scan", "check", "assess", "evaluate", "audit"
        ],
        "Write": [
            "create", "generate", "write", "produce", "build", "make",
            "compose", "draft", "synthesize", "document"
        ],
        "Edit": [
            "modify", "update", "edit", "improve", "refactor", "fix",
            "change", "adjust", "enhance", "correct", "revise"
        ],
        "Bash": [
            "execute", "run", "deploy", "install", "manage", "script",
            "command", "terminal", "system", "infrastructure", "ci/cd"
        ],
        "Grep": [
            "search", "find", "locate", "hunt", "match", "pattern",
            "regex", "query", "discover", "scan"
        ],
        "Glob": [
            "list", "enumerate", "directory", "folder", "filesystem",
            "structure", "organization", "discover", "catalog"
        ]
    }

    def match_tools(self, agent_type: str, agent_name: str, description: str) -> Dict[str, object]:
        """
        Match tools to agent based on purpose and type.

        Args:
            agent_type: Strategic, Implementation, Quality, Coordination
            agent_name: Agent name
            description: Agent description/purpose

        Returns:
            Tool recommendations with confidence scores
        """
        recommendations = self._score_tools(description)
        base_tools = self._get_base_tools_for_type(agent_type)

        # Combine: base tools + recommended additional tools
        combined_tools = set(base_tools)
        for tool, score in recommendations.items():
            if score > 0.5:  # Confidence threshold
                combined_tools.add(tool)

        return {
            "recommended_tools": sorted(list(combined_tools)),
            "confidence": self._calculate_confidence(recommendations),
            "base_tools": base_tools,
            "additional_tools": [t for t in combined_tools if t not in base_tools],
            "tool_justifications": self._build_justifications(combined_tools, description)
        }

    def _score_tools(self, description: str) -> Dict[str, float]:
        """Score each tool based on description keywords."""
        scores = {tool: 0.0 for tool in self.KEYWORD_PATTERNS.keys()}
        description_lower = description.lower()

        for tool, keywords in self.KEYWORD_PATTERNS.items():
            matches = sum(1 for kw in keywords if kw in description_lower)
            scores[tool] = min(matches / len(keywords), 1.0)

        return scores

    def _get_base_tools_for_type(self, agent_type: str) -> List[str]:
        """Get base tools recommended for agent type."""
        from agent_generator import AgentGenerator

        base = AgentGenerator.TOOL_RECOMMENDATIONS.get(agent_type, ["Read", "Write"])
        return base if isinstance(base, list) else list(base)

    def _calculate_confidence(self, recommendations: Dict[str, float]) -> float:
        """Calculate overall confidence in recommendations."""
        if not recommendations:
            return 0.0
        avg_score = sum(recommendations.values()) / len(recommendations)
        return round(avg_score, 2)

    def _build_justifications(self, tools: set, description: str) -> Dict[str, str]:
        """Build justifications for each recommended tool."""
        justifications = {}
        description_lower = description.lower()

        for tool in tools:
            if tool in self.KEYWORD_PATTERNS:
                keywords = [kw for kw in self.KEYWORD_PATTERNS[tool] if kw in description_lower]
                if keywords:
                    justifications[tool] = f"Based on: {', '.join(keywords)}"
                else:
                    justifications[tool] = f"Standard tool for {tool.lower()} operations"

        return justifications


def generate_agent_with_enhancements(config: Dict) -> Dict:
    """
    Generate agent with enhanced mapping and tool recommendations.

    Args:
        config: Agent configuration

    Returns:
        Enhanced agent config with dependencies and tools
    """
    # Map dependencies
    dependency_mapper = AgentDependencyMapper()
    dependencies = dependency_mapper.map_agent_dependencies(config)

    # Match tools
    capability_matcher = CapabilityMatcher()
    tool_match = capability_matcher.match_tools(
        agent_type=config.get("agent_type", "Implementation"),
        agent_name=config.get("agent_name", ""),
        description=config.get("description", "")
    )

    # If no tools specified, use recommended
    if "tools" not in config or not config["tools"]:
        config["tools"] = tool_match["recommended_tools"]

    # Add enhancements
    config["dependencies"] = dependencies
    config["tool_recommendations"] = tool_match

    return config


if __name__ == "__main__":
    # Test dependency mapping
    mapper = AgentDependencyMapper()
    deps = mapper.map_agent_dependencies({
        "agent_name": "frontend-developer",
        "agent_type": "Implementation"
    })

    print("=" * 60)
    print("AGENT DEPENDENCY MAPPING")
    print("=" * 60)
    print(f"Agent: {deps['agent_name']}")
    print(f"Pattern: {deps['execution_pattern']}")
    print(f"Max Concurrent: {deps['max_concurrent']}")
    print(f"Safe With: {', '.join(deps['safe_with'])}")
    print(f"Unsafe With: {', '.join(deps['unsafe_with'])}")

    # Test capability matching
    print("\n" + "=" * 60)
    print("CAPABILITY MATCHING")
    print("=" * 60)

    matcher = CapabilityMatcher()
    match = matcher.match_tools(
        agent_type="Implementation",
        agent_name="backend-developer",
        description="Builds REST APIs with proper error handling and database integration"
    )

    print(f"Recommended Tools: {', '.join(match['recommended_tools'])}")
    print(f"Confidence: {match['confidence']}")
    print("\nJustifications:")
    for tool, justification in match['tool_justifications'].items():
        print(f"  - {tool}: {justification}")

    # Test workflow validation
    print("\n" + "=" * 60)
    print("WORKFLOW VALIDATION")
    print("=" * 60)

    agents = ["product-planner", "frontend-developer", "backend-developer", "test-runner"]
    validation = mapper.validate_agent_workflow(agents, agents)

    print(f"Valid: {validation['valid']}")
    if validation['errors']:
        print("Errors:")
        for error in validation['errors']:
            print(f"  - {error}")
    if validation['warnings']:
        print("Warnings:")
        for warning in validation['warnings']:
            print(f"  - {warning}")
    print(f"\nRecommended Execution Order:")
    for i, phase in enumerate(validation['recommended_order'], 1):
        print(f"  Phase {i}: {', '.join(phase)}")
