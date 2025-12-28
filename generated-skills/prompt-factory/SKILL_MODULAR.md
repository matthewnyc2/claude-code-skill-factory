---
name: prompt-factory
description: World-class prompt powerhouse generating production-ready mega-prompts through intelligent 7-question flow with 69 presets, multiple formats, and quality validation gates
---

# Prompt Factory - Modular Documentation

**Generate world-class, production-ready prompts in one shot.**

---

## Quick Navigation

Choose your path:

- **📚 [New User?](#quick-start)** → Start here
- **⚡ [Just Need a Prompt?](#quick-start-preset)** → Use a preset (30 seconds)
- **🎯 [Building Custom Prompt?](#custom-workflow)** → Follow guided flow (5-7 questions)
- **📖 [Need Details?](#documentation-modules)** → Read detailed docs
- **✅ [Quality Standards?](#quality-gates)** → See validation criteria

---

## ⚠️ CRITICAL: What This Skill Does

**✅ This skill GENERATES PROMPTS only.**

It does NOT implement the work described in the prompt. See [SKILL.md differences](#what-this-skill-does) for details.

---

## Quick Start

### Path 1: Preset (Fastest - 30 seconds)

```
@prompt-factory

Use the /prompt-factory preset for: Product Manager
```

**Available presets** (69 total):
- **Technical** (8): Full-Stack Engineer, DevOps, Mobile, Data Scientist, etc.
- **Business** (8): Product Manager, Project Manager, Analyst, etc.
- **Legal** (4), **Finance** (4), **HR** (4), **Design** (4), and 9 more domains

→ See [PRESETS.md](./PRESETS.md) for complete list

### Path 2: Custom (Guided - 5-7 questions)

```
@prompt-factory

Create a custom prompt for: Building a REST API
```

**Skill asks questions** → **You answer** → **Complete prompt generated**

→ See [QUESTIONS.md](./QUESTIONS.md) for detailed Q&A guide

---

## Documentation Modules

Click to expand each module:

| Module | Purpose | Length |
|--------|---------|--------|
| **[WORKFLOWS.md](./WORKFLOWS.md)** | Quick-start workflows, preset selection, custom generation flow | 300 lines |
| **[QUESTIONS.md](./QUESTIONS.md)** | Detailed Q&A with examples, response validation, hints | 250 lines |
| **[VALIDATION.md](./VALIDATION.md)** | 7-point quality gates, token counting, output requirements | 200 lines |
| **[PRESETS.md](./PRESETS.md)** | All 69 presets indexed by domain with descriptions | 300+ lines |
| **[BEST_PRACTICES.md](./BEST_PRACTICES.md)** | Context-specific best practices from OpenAI/Anthropic/Google | 250 lines |

---

## What This Skill Does

### ✅ Generates

- Complete mega-prompts (5K-12K tokens)
- Multiple output formats (XML/Claude/ChatGPT/Gemini)
- Testing scenarios (advanced mode)
- Prompt variations (concise/balanced/comprehensive)
- Optimization recommendations

### ❌ Does NOT

- ❌ Implement code from the prompt
- ❌ Create architectural diagrams
- ❌ Build infrastructure
- ❌ Write actual business documents
- ❌ Execute the generated prompt

**If you want implementation**: Use generated prompt in fresh conversation or different tool.

---

## Workflow Summary

1. **Choose path** - Preset or Custom
2. **Answer questions** - 5-7 guided questions (custom only)
3. **Select format** - XML/Claude/ChatGPT/Gemini
4. **Pick mode** - Core (5K) or Advanced (12K)
5. **Receive prompt** - Complete, tested, ready to use
6. **Copy & use** - Paste in your LLM conversation

---

## Quality Standards

Every prompt passes 7-point validation:

✅ **XML Valid** - All tags properly closed (if XML format)
✅ **Complete** - All questionnaire answers incorporated
✅ **Token Optimized** - Core: 3-6K, Advanced: 8-12K
✅ **No Placeholders** - All `[...]` filled with actual content
✅ **Actionable** - Clear, executable workflow
✅ **Best Practices** - Context-relevant guidance included
✅ **Examples** - At least 2 examples demonstrating behavior

→ See [VALIDATION.md](./VALIDATION.md) for details

---

## 69 Available Presets

Organized by domain (15 total):

**Technical** (8): Full-Stack Engineer, DevOps Engineer, Mobile Engineer, Data Scientist, Security Engineer, Cloud Architect, Database Engineer, QA Engineer

**Business** (8): Product Manager, Project Manager, Operations Manager, Sales Manager, Business Analyst, Marketing Manager, Product Owner, Product Engineer

**Legal & Compliance** (4), **Finance** (4), **HR** (4), **Design** (4), **Manufacturing** (4), **Executive** (7), **Specialized Tech** (6), **Research** (3), **Creative Media** (4), **R&D** (2), **Regulatory** (1), **Specialized** (4)

→ See [PRESETS.md](./PRESETS.md) for complete descriptions

---

## Key Features

| Feature | Description |
|---------|-------------|
| **69 Presets** | Quick-start prompts for common roles |
| **7-Question Flow** | Intelligent questions with validation |
| **4 Output Formats** | XML / Claude / ChatGPT / Gemini |
| **2 Generation Modes** | Core (simple) / Advanced (comprehensive) |
| **Quality Gates** | 7-point validation before delivery |
| **Testing Scenarios** | Advanced mode includes test cases |
| **Prompt Variations** | 3 token sizes (concise/balanced/comprehensive) |

---

## Quick Examples

### Example: Generate PM Prompt (Preset)
```
@prompt-factory

Generate the "Product Manager" preset with XML format
```
**Output**: Complete Product Manager mega-prompt (5K tokens)

### Example: Custom Backend API Prompt
```
@prompt-factory

Create a custom prompt for: Building and optimizing REST APIs
```
**Skill asks**:
1. "What role? (Backend Engineer)"
2. "What domain? (API Development)"
3. "What task? (Build REST APIs)"
4. ... (4 more questions)

**Output**: Complete customized prompt

---

## Installation & Usage

### Direct Use
Simply invoke this skill in Claude Code:
```
@prompt-factory
[describe your prompt need]
```

### Using Generated Prompts

1. **Copy prompt** from skill output
2. **Start new conversation** (or different tool)
3. **Paste prompt** at beginning
4. **Add your specific request**
5. AI now operates under that prompt config

### Output Formats
- **XML** - Best for LLM parsing
- **Claude** - Native Claude system prompt format
- **ChatGPT** - Custom instructions format
- **Gemini** - Google Gemini format

---

## When to Use This Skill

✅ **Use when you need**:
- A specialized role/domain prompt
- Multiple output format versions
- Testing scenarios for prompt validation
- Prompt variations at different token levels
- Best practices for your role/domain

❌ **Don't use when**:
- You just want to chat (use Claude directly)
- You need implementation (use after generating prompt)
- You need to edit code (different tool)

---

## Support

**Questions?** See detailed modules:
- How do I pick a preset? → [WORKFLOWS.md](./WORKFLOWS.md)
- What questions will be asked? → [QUESTIONS.md](./QUESTIONS.md)
- How is quality validated? → [VALIDATION.md](./VALIDATION.md)
- What best practices apply? → [BEST_PRACTICES.md](./BEST_PRACTICES.md)

**Direct References**:
- `templates/presets/` - 15 core role templates
- `references/best-practices/` - OpenAI/Anthropic/Google techniques
- `examples/` - 5 complete example outputs

---

**Version**: 2.0 (Modular)
**Status**: Production-ready
**Presets**: 69 available
**Formats**: 4 (XML, Claude, ChatGPT, Gemini)
**Validation**: 7-point quality gates

**Ready to create world-class prompts?** Start with [WORKFLOWS.md](./WORKFLOWS.md) →
