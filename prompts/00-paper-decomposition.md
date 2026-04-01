# Phase 0: Paper Decomposition — Experiment Module Analysis

## Objective

Before building any rubric or writing any code, decide: does this paper's experiments form a **single coherent pipeline** or do they split into **distinct experiment modules** that are best developed in isolation?

**All modules always live in ONE unified repository.** This decision is about whether to run phases 2–12 once (for the whole paper) or once per module (e.g., toy-model experiments, vision experiments, NanoGPT runs). Shared infrastructure (training loops, base models, data utilities) is implemented once in `src/` and reused across modules.

**Why this matters for PaperBench:** PaperBench evaluates one repository. Multi-module decomposition helps organize complex papers without fragmenting the codebase — it ensures each experiment cluster gets dedicated rubric coverage, configs, and scripts.

---

## Required Inputs

- `input/paper.pdf` (via extracted `input/paper_text.txt`)
- `analysis_workspace/paper_analysis.json` — output of Phase 1

---

## Required Outputs

### `analysis_workspace/paper_decomposition.json`

```json
{
  "decomposition_type": "single | multi",
  "sub_repos": [
    {
      "id": "module_1",
      "name": "short-name-for-experiments-subdir",
      "scope": "what experiment cluster this module covers (1-2 sentences)",
      "primary_paper_sections": ["Section 3", "Section 5"],
      "figures_covered": ["Figure 1", "Figure 2"],
      "tables_covered": ["Table 1"],
      "key_components": ["main model", "training loop"],
      "dependencies_on_other_sub_repos": [],
      "estimated_complexity": "low | medium | high",
      "rationale": "why this cluster deserves its own module"
    }
  ],
  "decomposition_rationale": "why single vs multi-module",
  "shared_components": ["data loading", "base model", "evaluation metrics"],
  "shared_component_strategy": "all shared code lives in src/, imported by each module's scripts"
}
```

**Note:** All modules live in the same repository. `sub_repos` entries map to `experiments/{name}/`, `configs/{name}/`, and `scripts/{name}/` directories — not separate repo roots.

---

## Decision Rules

### When to choose SINGLE (one pass through phases 2–12)

Use single when:
- All experiments use the same model and training infrastructure
- The paper's contribution is one method applied to multiple datasets
- All figures/tables can be reproduced with different configs from the same entry point
- The paper is primarily theory with small supporting experiments

**Examples:**
- EOSS paper: all experiments use SGD + curvature measurement → single
- An optimizer paper: same optimizer on different tasks → single
- A regularization technique on multiple benchmarks → single

### When to choose MULTI (run phases 2–12 once per module)

Use multi when the paper has **distinct experiment clusters** that differ in model architecture, data format, or experimental setup. All modules still live in one repo — multi just means developing them in separate passes so each gets focused rubric, architecture design, and CPU testing.

**Examples:**
- Paper has toy 2D experiments + CIFAR-10 CNN + NanoGPT language model → three modules
- BERT: pretraining experiments + downstream finetuning experiments → two modules
- Paper proposes method A on vision and method B on NLP → two modules
- Large benchmark reimplementing 5 baselines + 1 new method → modules per method

### Edge cases (when uncertain, ask the user)

- Paper evaluates on 5 datasets with different preprocessings but same model: likely single (different configs)
- Theory paper with math proofs + empirical validation: single (empirical code supports theory)
- Paper releases experiments at very different scales (toy vs. large): two modules

---

## Process

### Step 1: Read paper_analysis.json holistically

Look at:
- `model_architecture.type` — is it one type or multiple fundamentally different types?
- `datasets` — do they all use the same model? Same training code?
- `table_figure_inventory` — are there clusters of figures that belong to different pipelines?
- `baselines` — are baselines simple variants or fully independent methods?
- `implementation_details_section` — does it describe one codebase or multiple?

### Step 2: Apply decision rules

Write out reasoning: "This paper uses [tech stack], [datasets], and [experiments]. Based on [rule], this is [single/multi]."

### Step 3: If MULTI, define module boundaries

For each module:
- What experiment cluster does it cover? (figures, tables, sections)
- What shared infrastructure does it use from `src/`?
- Does it depend on outputs from another module? (e.g., finetuning needs pretrained model)
- Dependency order: which module must be completed first?

### Step 4: Write paper_decomposition.json

Always enumerate `sub_repos` — even for single papers, list one entry so the orchestrator loop works uniformly:
```json
{
  "decomposition_type": "single",
  "sub_repos": [{"id": "main", "name": "paper-short-name", ...}]
}
```

---

## Checkpoint Question

After this phase, the orchestrator asks:

```
I've analyzed the paper and determined it needs {1/N} experiment module(s):

{If single:}
  → One unified pipeline: {name}
  → Covers: all {M} figures, {N} tables

{If multi:}
  → Module 1: {name} — {scope}
     Covers: Figures {X}, Tables {Y}
  → Module 2: {name} — {scope}
     Covers: Figures {X}, Tables {Y}
  → Module N depends on outputs of Module M: {dependency}

All modules share one repo. Each gets its own rubric pass, architecture design,
and CPU verification, with shared infrastructure in src/.

Does this decomposition look right? Type PROCEED or describe corrections.
```
