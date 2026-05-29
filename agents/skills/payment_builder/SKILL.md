---
name: payment-orchestrator-builder
description: Automates a containerized multi-agent development lifecycle to design, test, and implement secure software modules via hot-reloadable prompts and TDD review loops.
---

# Payment Orchestrator Builder Skill

This skill manages our structural architecture compiler and implementation environments. It abstracts away context payload handling to guarantee data convergence and prevent code hallucinations.

## Available Sub-Agent Prompts
The prompt blueprints are divided logically into separate phase folders under `.agents/prompts/`:

### Phase 1 (Design Roles)
- `.agents/prompts/phase1/cto.txt`              
- `.agents/prompts/phase1/architect.txt`
- `.agents/prompts/phase1/security_auditor.txt`
- `.agents/prompts/phase1/test_specifier.txt`

### Phase 2 (Implementation Roles)
- `.agents/prompts/phase2/qa_generator.txt`
- `.agents/prompts/phase2/developer.txt`
- `.agents/prompts/phase2/pentester.txt`

## Operational Hooks

### 1. Execute Architecture & Spec Compilation (Phase 1)
```bash
python .agents/design_phase.py