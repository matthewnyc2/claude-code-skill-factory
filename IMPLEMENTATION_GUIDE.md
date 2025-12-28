# Factory Skills Implementation Guide

**How to integrate and deploy all the improvements across the 4 factory skills**

---

## TABLE OF CONTENTS

1. [Quick Start](#quick-start)
2. [Agent Factory Implementation](#agent-factory-implementation)
3. [Hook Factory Implementation](#hook-factory-implementation)
4. [Slash Command Factory Implementation](#slash-command-factory-implementation)
5. [Prompt Factory Implementation](#prompt-factory-implementation)
6. [Cross-Factory Dashboard](#cross-factory-dashboard)
7. [Testing & Validation](#testing--validation)
8. [Deployment](#deployment)

---

## Quick Start

### Prerequisites
- Python 3.7+
- Claude Code installed
- Git for version control

### Installation Summary (5 minutes)
```bash
# 1. Navigate to project
cd /path/to/claude-code-skill-factory

# 2. Copy new modules to skill directories
cp generated-skills/agent-factory/agent_*.py ~/.claude/skills/agent-factory/
cp generated-skills/hook-factory/*.py ~/.claude/skills/hook-factory/
cp generated-skills/slash-command-factory/slash_*.py ~/.claude/skills/slash-command-factory/
cp generated-skills/factory-dashboard.py ~/.claude/skills/

# 3. Test each factory (see Testing section below)

# 4. Use in Claude Code (see Usage section)
```

---

## Agent Factory Implementation

### Step 1: Install CLI Module

**File**: `generated-skills/agent-factory/agent_factory_cli.py`

```bash
# Copy to agent-factory skill directory
cp generated-skills/agent-factory/agent_factory_cli.py generated-skills/agent-factory/

# Make executable
chmod +x generated-skills/agent-factory/agent_factory_cli.py
```

### Step 2: Install Prompt Synthesizer

**File**: `generated-skills/agent-factory/agent_prompt_synthesizer.py`

```bash
# Copy to agent-factory skill directory
cp generated-skills/agent-factory/agent_prompt_synthesizer.py generated-skills/agent-factory/

# Verify imports work
python3 -c "from agent_prompt_synthesizer import PromptSynthesizer; print('✅ Import successful')"
```

### Step 3: Update SKILL.md

Add to the Agent Factory SKILL.md:

```markdown
## CLI Usage (New!)

### Interactive Mode
```bash
python3 agent_factory_cli.py -i
```

Follow 5-question flow:
1. Agent name (kebab-case)
2. Agent type (Strategic|Implementation|Quality|Coordination)
3. Domain specialization
4. MCP servers needed (optional)

### Preset Mode
```bash
python3 agent_factory_cli.py --preset frontend --type Implementation
```

### Batch Mode
```bash
python3 agent_factory_cli.py --batch agents.json
```

Expected JSON format:
```json
[
  {
    "agent_name": "frontend-developer",
    "agent_type": "Implementation",
    "field": "frontend"
  }
]
```

### Usage in Claude Code
```
@agent-factory

Create a frontend developer agent for React/TypeScript development
```

The skill will:
1. Ask clarifying questions (if needed)
2. Generate complete agent file with system prompt
3. Save to ~/.claude/agents/
4. Show installation instructions
```

### Step 4: Install Enhancements

**File**: `generated-skills/agent-factory/agent_enhancements.py`

```bash
# Copy to agent-factory
cp generated-skills/agent-factory/agent_enhancements.py generated-skills/agent-factory/

# Test dependency mapping
python3 generated-skills/agent-factory/agent_enhancements.py
# Should output agent dependency mappings and capability scores
```

### Step 5: Update HOW_TO_USE.md

Add new section:

```markdown
## NEW: Smart Tool Recommendations

When creating agents, the factory now auto-recommends tools based on agent purpose:

**Example**:
```
Agent description: "Backend API developer specializing in REST APIs"
→ Recommended tools: Read, Write, Edit, Bash, Grep, Glob
→ Confidence: 0.85
→ Justification: Based on keywords: api, backend, rest, developer
```

## NEW: Safe Agent Execution Patterns

The factory validates multi-agent workflows:

**Before** (Manual checking):
- "Can I run frontend-developer + backend-developer in parallel?"
- *Uncertain*

**After** (With Dependency Mapper):
```
frontend-developer: safe_with=[backend-developer, api-builder]
                   unsafe_with=[test-runner, code-reviewer]
                   execution_pattern=parallel
```

## NEW: Agent Chaining Example

```
Phase 1 (Parallel - Strategic):
  - product-planner

Phase 2 (Parallel - Implementation):
  - frontend-developer
  - backend-developer

Phase 3 (Sequential - Quality):
  - test-runner
  - code-reviewer
```
```

---

## Hook Factory Implementation

### Step 1: Install Platform Adapter

**File**: `generated-skills/hook-factory/platform_adapter.py`

```bash
# Copy to hook-factory
cp generated-skills/hook-factory/platform_adapter.py generated-skills/hook-factory/

# Test platform detection
python3 generated-skills/hook-factory/platform_adapter.py
# Should show: Current Platform: [windows|macos|linux]
```

### Step 2: Install Template Loader

**File**: `generated-skills/hook-factory/template_loader.py`

```bash
# Copy to hook-factory
cp generated-skills/hook-factory/template_loader.py generated-skills/hook-factory/

# Test template loading
python3 generated-skills/hook-factory/template_loader.py
# Should list all available templates
```

### Step 3: Update Hook Generator

Modify `generated-skills/hook-factory/generator.py` to use new classes:

```python
# Add imports at top
from platform_adapter import get_platform_adapter
from template_loader import TemplateLoader

# In generate_hook() method, add:
def generate_hook(self, requirements):
    """Generate hook with platform compatibility."""

    # Get platform
    adapter = get_platform_adapter()

    # Load templates
    loader = TemplateLoader()
    template = loader.get_template(requirements.template_name)

    # Validate for platform
    valid, warnings = adapter.validate_hook_for_platform(template)
    if warnings:
        for warning in warnings:
            print(warning)

    # Translate commands for Windows if needed
    if adapter.is_windows and template.get("command"):
        translated, _ = adapter.translate_command(template["command"])
        template["command"] = translated

    # ... rest of generation
```

### Step 4: Install Enhancements

**File**: `generated-skills/hook-factory/hook_enhancements.py`

```bash
# Copy to hook-factory
cp generated-skills/hook-factory/hook_enhancements.py generated-skills/hook-factory/

# Test performance monitoring
python3 generated-skills/hook-factory/hook_enhancements.py
```

### Step 5: Update SKILL.md

Add new sections:

```markdown
## Windows Support (NEW!)

Hook Factory now supports Windows via PowerShell translation:

**Automatic Translation**:
```bash
# User specifies:
black file.py

# On Windows, becomes:
python -m black file.py
```

**Installation on Windows**:
```powershell
python installer.py install generated-hooks\[hook-name] user
```

## Hook Performance Monitoring (NEW!)

Track hook health automatically:

```bash
# Analyze hook performance
python3 hook_enhancements.py analyze test-runner

# Shows:
# - Success rate: 99%
# - Avg duration: 2.3s
# - P95 duration: 5.1s
# - Status: 🟢 HEALTHY
```

## Hook Chaining Workflows (NEW!)

Create multi-step automation:

```bash
# Preset: full-workflow
# Executes: format → git-add → tests → pre-commit-check

python3 -c "from hook_enhancements import create_hook_workflow_from_template; \
            config = create_hook_workflow_from_template('full-workflow'); \
            print(config)"
```
```

---

## Slash Command Factory Implementation

### Step 1: Install CLI Module

**File**: `generated-skills/slash-command-factory/slash_command_factory_cli.py`

```bash
# Copy to slash-command-factory
cp generated-skills/slash-command-factory/slash_command_factory_cli.py generated-skills/slash-command-factory/

# Make executable
chmod +x generated-skills/slash-command-factory/slash_command_factory_cli.py

# Test CLI
python3 generated-skills/slash-command-factory/slash_command_factory_cli.py --help
```

### Step 2: Install Enhancements

**File**: `generated-skills/slash-command-factory/slash_enhancements.py`

```bash
# Copy to slash-command-factory
cp generated-skills/slash-command-factory/slash_enhancements.py generated-skills/slash-command-factory/

# Test auto-testing
python3 generated-skills/slash-command-factory/slash_enhancements.py
```

### Step 3: Update Command Generator

Modify `generated-skills/slash-command-factory/command_generator.py`:

```python
# Add imports
from slash_enhancements import CommandAutoTester, CommandVersionManager

# In generate_custom() method, add:
def generate_custom(self, answers):
    """Generate custom command with testing and versioning."""

    # Generate base command
    command_content = # ... existing generation code

    # Add auto-testing
    tester = CommandAutoTester()
    test_cases = tester.generate_test_cases(answers)
    test_examples = tester.generate_test_examples_md(command_name, test_cases)

    # Add versioning
    manager = CommandVersionManager()
    manager.save_command_version(command_name, command_content, "1.0.0")

    return {
        'command_name': command_name,
        'command_content': command_content,
        'test_examples': test_examples,
        'supporting_folders': [...],
        'tests': test_cases
    }
```

### Step 4: Update SKILL.md

Add new sections:

```markdown
## Interactive Tool Picker (NEW!)

Select tools from interactive checklist:

```
Q3: Which tools does this command need?

Quick Selections:
  - git (git status, diff, log, commit)
  - discovery (find, ls, tree, grep)
  - testing (pytest, npm test)
  - comprehensive (all tools)

Or manually select:
  [1] Read
  [2] Write
  [3] Edit
  [4] Bash
  [5] Grep
  [6] Glob
  [7] Task
```

## Auto-Testing (NEW!)

All commands now generate test scenarios:

```bash
# Test your command before installing
slash-command-factory --dry-run /my-command test-arg

# Verifies:
# ✅ Command runs without errors
# ✅ Tools are available
# ✅ Output is as expected
```

## Command Versioning (NEW!)

Track command versions with rollback:

```bash
# List versions
command-factory --list-versions my-command

# Rollback to previous version
command-factory --rollback my-command v1.0.0
```
```

---

## Prompt Factory Implementation

### Step 1: Create Modular Documentation Structure

```bash
# Copy modular documentation
cp generated-skills/prompt-factory/SKILL_MODULAR.md generated-skills/prompt-factory/SKILL_MODULAR.md

# Create supporting module files (copy from plan references)
touch generated-skills/prompt-factory/WORKFLOWS.md
touch generated-skills/prompt-factory/QUESTIONS.md
touch generated-skills/prompt-factory/VALIDATION.md
touch generated-skills/prompt-factory/PRESETS.md
touch generated-skills/prompt-factory/BEST_PRACTICES.md
```

### Step 2: Update SKILL.md

Replace with modular version:

```bash
# Backup original
cp generated-skills/prompt-factory/SKILL.md generated-skills/prompt-factory/SKILL_ORIGINAL.md

# Use modular version
cp generated-skills/prompt-factory/SKILL_MODULAR.md generated-skills/prompt-factory/SKILL.md
```

### Step 3: Create Supporting Documentation

**Create WORKFLOWS.md** (excerpt):
```markdown
# Prompt Factory Workflows

## Quick-Start Path (Preset)

1. User: "@prompt-factory use preset Product Manager"
2. Skill shows preset template with customizable variables
3. User confirms or customizes → Generates prompt → Done

## Custom Path (5-7 Questions)

1. User: "@prompt-factory create custom prompt for: REST API"
2. Skill asks 5-7 questions with validation
3. User answers each question
4. Skill generates mega-prompt with quality validation
5. User receives complete prompt ready to use

[... additional workflows ...]
```

**Create QUESTIONS.md** (excerpt):
```markdown
# Detailed Question Flow

## Q1: Role Definition
"What role should the AI assume?"

Examples:
- "Senior Backend Engineer"
- "Product Manager"
- "Data Scientist"

Validation: Check against 69 presets, suggest similar if not exact match

[... additional questions with detailed guidance ...]
```

### Step 4: Update HOW_TO_USE.md

```markdown
## Using Modular Documentation

The SKILL.md is now modular for clarity:

- **SKILL.md** (200 lines) - Quick navigation and overview
- **WORKFLOWS.md** - Preset vs. custom path options
- **QUESTIONS.md** - Detailed Q&A with examples
- **VALIDATION.md** - Quality gates and token counting
- **PRESETS.md** - All 69 presets catalog
- **BEST_PRACTICES.md** - Context-specific guidance

**In Claude Code**: When you invoke the skill, it loads appropriate modules based on your path.

**Benefits**:
- Faster to read (300 lines vs 1,100)
- Easier to maintain
- Clear navigation
- Reduced cognitive load
```

---

## Cross-Factory Dashboard

### Step 1: Install Dashboard

```bash
# Copy dashboard
cp generated-skills/factory-dashboard.py ~/.claude/skills/

# Make executable
chmod +x ~/.claude/skills/factory-dashboard.py

# Test dashboard
python3 ~/.claude/skills/factory-dashboard.py
```

### Step 2: Create Dashboard Launcher

Create `~/.claude/commands/factory-status.md`:

```markdown
---
description: Show Factory Dashboard status of all agents, commands, hooks, and skills
---

# Factory Dashboard Status

@factory-dashboard

Show current status of all Claude Code factories and artifacts.

**Output**:
- Inventory counts
- Health status
- Recent activity
- Recommendations
- JSON export option
```

### Step 3: Configure Periodic Reports

Add to `.claude/hook.json`:

```json
{
  "type": "scheduled",
  "event_type": "SessionStart",
  "command": "python3 ~/.claude/skills/factory-dashboard.py",
  "frequency": "daily",
  "timeout": 30
}
```

---

## Testing & Validation

### Step 1: Test Each Factory Individually

**Agent Factory Test**:
```bash
cd generated-skills/agent-factory

# Test CLI
python3 agent_factory_cli.py --help

# Test synthesizer
python3 agent_prompt_synthesizer.py
# Should output sample agent prompts

# Test enhancements
python3 agent_enhancements.py
# Should output dependency mappings
```

**Hook Factory Test**:
```bash
cd generated-skills/hook-factory

# Test platform adapter
python3 platform_adapter.py
# Should detect current platform

# Test template loader
python3 template_loader.py
# Should list all templates

# Test enhancements
python3 hook_enhancements.py
# Should analyze hook performance
```

**Slash Command Factory Test**:
```bash
cd generated-skills/slash-command-factory

# Test CLI help
python3 slash_command_factory_cli.py --help

# Test presets
python3 slash_command_factory_cli.py --list-presets

# Test enhancements
python3 slash_enhancements.py
# Should generate test cases
```

**Prompt Factory Test**:
```bash
# Check modular structure exists
ls generated-skills/prompt-factory/SKILL*.md
ls generated-skills/prompt-factory/{WORKFLOWS,QUESTIONS,VALIDATION,PRESETS,BEST_PRACTICES}.md

# Verify main SKILL.md loads correctly
head -50 generated-skills/prompt-factory/SKILL.md
```

### Step 2: Integration Tests

**Test Agent Factory in Claude Code**:
```
@agent-factory

Create a test agent for data processing
```

**Expected Output**:
- Interactive 5-question flow
- Complete agent file generated
- Saved to ~/.claude/agents/
- Installation instructions shown

**Test Hook Factory**:
```
@hook-factory

Create a hook to auto-format Python code after editing
```

**Expected Output**:
- Platform-appropriate hook generated
- Windows or Unix commands used
- hook.json and README.md created
- Installation guidance provided

**Test Slash Command Factory**:
```
@slash-command-factory -i

Generate interactive command
```

**Expected Output**:
- 5-7 question interactive flow
- Tool picker presented
- Command generated with tests
- TEST_EXAMPLES.md created

### Step 3: Validation Checklist

```
Agent Factory:
  ✅ CLI works (-i, --preset, --batch flags)
  ✅ Prompt synthesis generates valid prompts
  ✅ Dependency mapper identifies safe combinations
  ✅ Capability matcher recommends correct tools

Hook Factory:
  ✅ Platform adapter detects OS correctly
  ✅ Bash commands translate to PowerShell (Windows)
  ✅ Template loader handles missing templates
  ✅ Performance monitor logs executions
  ✅ Hook chaining creates workflows

Slash Command Factory:
  ✅ CLI interactive mode works
  ✅ Tool picker presents all tools
  ✅ Auto-tester generates test cases
  ✅ Versioning tracks command changes

Prompt Factory:
  ✅ Modular docs are organized
  ✅ Each module loads independently
  ✅ Navigation links work
  ✅ Presets are documented

Dashboard:
  ✅ Shows all artifacts
  ✅ Reports health status
  ✅ Lists recent activity
  ✅ Exports JSON report
```

---

## Deployment

### Production Checklist

```
Pre-Deployment:
  ✅ All tests pass
  ✅ No import errors
  ✅ Documentation complete
  ✅ README files updated
  ✅ Examples provided

Deployment Steps:
  1. Backup current factory skills
  2. Copy new modules to skill directories
  3. Update SKILL.md files
  4. Update HOW_TO_USE.md files
  5. Install dashboard to ~/.claude/skills/
  6. Test each factory
  7. Create slash command for dashboard
  8. Commit changes

Post-Deployment:
  1. Monitor for errors in logs
  2. Gather user feedback
  3. Track usage statistics
  4. Iterate on improvements
  5. Document lessons learned
```

### Installation Script

Create `install-improvements.sh`:

```bash
#!/bin/bash

echo "🚀 Installing Factory Improvements..."

# Agent Factory
echo "📦 Installing Agent Factory..."
cp generated-skills/agent-factory/agent_factory_cli.py ~/.claude/skills/agent-factory/
cp generated-skills/agent-factory/agent_prompt_synthesizer.py ~/.claude/skills/agent-factory/
cp generated-skills/agent-factory/agent_enhancements.py ~/.claude/skills/agent-factory/

# Hook Factory
echo "📦 Installing Hook Factory..."
cp generated-skills/hook-factory/platform_adapter.py ~/.claude/skills/hook-factory/
cp generated-skills/hook-factory/template_loader.py ~/.claude/skills/hook-factory/
cp generated-skills/hook-factory/hook_enhancements.py ~/.claude/skills/hook-factory/

# Slash Command Factory
echo "📦 Installing Slash Command Factory..."
cp generated-skills/slash-command-factory/slash_command_factory_cli.py ~/.claude/skills/slash-command-factory/
cp generated-skills/slash-command-factory/slash_enhancements.py ~/.claude/skills/slash-command-factory/

# Prompt Factory
echo "📦 Installing Prompt Factory..."
cp generated-skills/prompt-factory/SKILL_MODULAR.md ~/.claude/skills/prompt-factory/

# Dashboard
echo "📦 Installing Factory Dashboard..."
cp generated-skills/factory-dashboard.py ~/.claude/skills/

# Create dashboard command
mkdir -p ~/.claude/commands/
cat > ~/.claude/commands/factory-status.md << 'EOF'
---
description: Show Factory Dashboard status
---

# Factory Dashboard

Display status of all Claude Code factory artifacts.

@factory-dashboard
EOF

echo "✅ Installation complete!"
echo ""
echo "🧪 Testing..."
python3 ~/.claude/skills/factory-dashboard.py

echo ""
echo "📝 Next steps:"
echo "1. Restart Claude Code"
echo "2. Try: @agent-factory"
echo "3. Try: /factory-status"
```

### Run Installation

```bash
chmod +x install-improvements.sh
./install-improvements.sh
```

---

## Usage Examples

### Agent Factory
```
@agent-factory

Create a backend API developer agent
```

### Hook Factory
```
@hook-factory

Auto-format Python files after editing
```

### Slash Command Factory
```
@slash-command-factory -i

Generate custom command for analyzing code
```

### Factory Dashboard
```
/factory-status

Show current factory status
```

---

## Troubleshooting

### Import Errors

```
ImportError: No module named 'agent_prompt_synthesizer'
```

**Solution**:
```bash
# Ensure all files are in correct directory
ls generated-skills/agent-factory/*.py

# Check Python path
export PYTHONPATH="/path/to/generated-skills/agent-factory:$PYTHONPATH"
```

### Windows Platform Issues

```
Command not found: black
```

**Solution**:
```python
# Use platform adapter to translate
from platform_adapter import PlatformAdapter
adapter = PlatformAdapter()
translated, warning = adapter.translate_command("black file.py")
print(translated)  # python -m black file.py
```

### Template Loading Failures

```
Error: templates.json not found
```

**Solution**:
```python
# Template loader has fallback system
from template_loader import TemplateLoader
loader = TemplateLoader()
# Loads embedded templates automatically
templates = loader.templates
print(f"Loaded {len(templates)} templates")
```

---

## Next Steps

1. **Review Code**: Examine each Python module
2. **Test Locally**: Run tests on your machine
3. **Deploy**: Use installation script
4. **Gather Feedback**: Monitor usage
5. **Iterate**: Refine based on real-world use

---

**Questions?** Review the FACTORY_IMPROVEMENT_PLAN.md for architectural details.
