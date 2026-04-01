# Phase 0: Paper Decomposition — Single-Repo vs. Multi-Repo Analysis

## Objective

Before building any rubric or writing any code, decide: does this paper require **one unified repository** or **multiple independent sub-repositories**? This decision shapes the entire pipeline.

**Why this matters for PaperBench:** PaperBench evaluates each sub-repository independently. A paper that requires two separate codebases (e.g., pretraining + finetuning) will have separate rubrics for each. If you lump them into one repo, you may fail rubric items that expect separate entry points and scripts.

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
      "id": "sub_repo_1",
      "name": "short-name-for-directory",
      "scope": "what this sub-repo implements (1-2 sentences)",
      "primary_paper_sections": ["Section 3", "Section 5"],
      "figures_covered": ["Figure 1", "Figure 2"],
      "tables_covered": ["Table 1"],
      "key_components": ["main model", "training loop"],
      "dependencies_on_other_sub_repos": [],
      "estimated_complexity": "low | medium | high",
      "rationale": "why this is a separate sub-repo"
    }
  ],
  "decomposition_rationale": "why single vs multi",
  "shared_components": ["data loading", "evaluation metrics"],
  "shared_component_strategy": "how shared components will be handled (copy vs. shared package)"
}
```

---

## Decision Rules

### When to choose SINGLE repo

Use a single repo when:
- All experiments use the same model training infrastructure
- The paper's contribution is a single method applied to multiple datasets
- All figures/tables can be reproduced from one codebase with different configs
- The paper is primarily theory with small supporting experiments

**Examples:**
- EOSS paper: all experiments use the same SGD+curvature-measurement infrastructure → single repo
- An optimizer paper: all experiments use the same optimizer code on different tasks → single repo
- A regularization technique: same technique, different datasets → single repo

### When to choose MULTI repo

Use multiple sub-repos when ANY of these hold:

1. **Fundamentally different tech stacks**: Part A uses PyTorch, Part B uses JAX. Part A is a vision model, Part B is a language model with completely different data formats.

2. **Separate entry-point architectures**: The paper proposes a pretraining method AND a downstream evaluation method where the downstream code is conceptually separate (different teams, different repos in practice). E.g., BERT: pretraining code ≠ finetuning code.

3. **Independent research contributions**: The paper makes two separate contributions that happen to be in one paper but are independently replicable (e.g., a new architecture AND a new training recipe that are tested separately).

4. **Large benchmark papers**: Each experiment is a separate method reimplementation (e.g., a paper that reimplements 5 baselines from scratch and proposes a 6th). Each reimplementation is a sub-repo.

5. **Explicit code modularity cue**: Paper text says "we release three separate codebases", or the paper's appendix shows clearly separated module hierarchies that don't share code.

### Edge cases (when uncertain, ask the user)

- Paper proposes method A on vision and method B on NLP: likely two sub-repos (different data + model stacks)
- Paper evaluates on 5 datasets with different preprocessings: likely single repo (same model, same training, different configs)
- Paper has a theory component with math proofs + an empirical component: single repo (the empirical code supports the theory)

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

### Step 3: If MULTI, define sub-repo boundaries

For each sub-repo:
- What are its inputs/outputs?
- What paper sections/figures does it cover?
- Does it depend on outputs from another sub-repo? (e.g., downstream code needs pretrained model from pretraining code)
- Dependency order: which sub-repo must be completed first?

### Step 4: Write paper_decomposition.json

Explicitly enumerate `sub_repos` (even if there is only 1 — just set `decomposition_type: "single"` and list the one sub-repo).

Always list exactly one sub-repo for single-repo papers so the orchestrator loop works uniformly:
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
I've analyzed the paper and determined it requires {1/N} repository/repositories:

{If single:}
  → Single unified repo: {name}
  → Covers: all {M} figures, {N} tables

{If multi:}
  → Sub-repo 1: {name} — {scope}
     Covers: Figures {X}, Tables {Y}
  → Sub-repo 2: {name} — {scope}
     Covers: Figures {X}, Tables {Y}
  → Sub-repo N depends on outputs of sub-repo M: {dependency description}

Does this decomposition look right? Type PROCEED or describe corrections.
```
