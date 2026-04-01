# Phase 3: Repository Architecture Design

## Objective

Design the complete repository structure **before writing any code**. Every file in the planned structure must have a clear purpose, and every rubric item must be assigned to at least one file. This is the blueprint — implementation phases follow it exactly.

Do not write implementation code in this phase. Only plan the structure.

---

## Required Inputs

- `analysis_workspace/paper_analysis.json`
- `analysis_workspace/rubric.json`
- `analysis_workspace/rubric_coverage.json`

---

## Required Outputs

### 1. `analysis_workspace/architecture_plan.json`

A file-by-file plan of the repository:

```json
{
  "repo_name": "",
  "repo_root": "code_workspace/{repo_name}/",
  "files": [
    {
      "path": "src/models/transformer.py",
      "purpose": "Main TransformerEncoder model class",
      "key_classes": ["TransformerEncoder", "TransformerEncoderLayer"],
      "key_functions": ["forward", "encode"],
      "rubric_items_covered": ["CD-001", "CD-002", "CD-003"],
      "paper_references": ["Section 3.2", "Figure 2", "Equation 1-4"],
      "dependencies": ["src/models/attention.py", "src/models/ffn.py"],
      "estimated_lines": 120,
      "implementation_notes": "Must use pre-LayerNorm (not PyTorch default). See CD-005."
    }
  ],
  "directories": [
    {
      "path": "src/models/",
      "purpose": "Model architecture implementations"
    }
  ],
  "uncovered_rubric_items": []
}
```

### 2. `analysis_workspace/implementation_checklist.json`

Maps every rubric item to the file responsible for implementing it, all initialized as "pending":

```json
{
  "CD-001": {
    "description": "TransformerEncoder uses pre-LayerNorm",
    "responsible_file": "src/models/transformer.py",
    "status": "pending",
    "priority": "high",
    "verification_method": "code_check"
  }
}
```

### 3. Empty directory scaffold

Create the empty directory structure in `code_workspace/{paper_short_name}/` using `mkdir -p`. No code files yet — just the directories:

```
code_workspace/{name}/
  src/
    models/
    data/
    training/
    evaluation/
    utils/
  baselines/
  scripts/
  configs/
  results/
  tests/
  docs/
```

---

## Standard Repository Layout

Every replication should follow this structure. Adapt as needed for the specific paper:

```
{paper_short_name}/
  README.md                     # Paper citation, installation, reproduction guide
  requirements.txt              # Pinned dependencies
  setup.py                      # Optional: if the repo should be installable
  .gitignore

  src/
    __init__.py
    models/
      __init__.py
      {main_model}.py           # Main model class
      {components}.py           # Sub-components (attention, ffn, etc.)
    data/
      __init__.py
      {dataset_name}.py         # One file per dataset
      transforms.py             # Data transforms and augmentations
      utils.py                  # Data utilities
    training/
      __init__.py
      trainer.py                # Main Trainer class
      optimizer.py              # Optimizer and scheduler setup
      loss.py                   # Loss function(s)
    evaluation/
      __init__.py
      metrics.py                # Metric computation
      evaluator.py              # Evaluation loop
    utils/
      __init__.py
      logging.py                # Logging utilities
      checkpointing.py          # Checkpoint save/load

  baselines/
    __init__.py
    {baseline_name}.py          # One file per baseline method

  scripts/
    run_table1.py               # One script per major table
    run_table2.py
    run_figure3.py              # One script per major figure
    ...

  configs/
    default.yaml                # All hyperparameters from paper
    experiment_table1.yaml      # Overrides for Table 1 experiment
    experiment_table2.yaml
    ...

  results/                      # Experiment outputs (created at runtime)
    .gitkeep

  tests/
    test_imports.py
    test_forward_pass.py
    test_loss.py
    test_training_step.py
    test_data_pipeline.py

  docs/
    architecture.md             # Architecture description
```

---

## Architecture Design Rules

### Rule 1: One class = one file (for major components)

Each major model component (TransformerEncoder, AttentionModule, etc.) should have its own file. This makes:
- Rubric item tracing easy (CD-001 → src/models/attention.py:45)
- CPU testing isolated (test_attention.py doesn't need the full model)
- PaperBench checking straightforward

### Rule 2: All hyperparameters in configs/

Every hyperparameter value mentioned in the paper must appear in at least one config file. Never hardcode values in model files. A comment referencing the paper is acceptable:

```yaml
# From paper Table 1, Appendix B
learning_rate: 3e-4
warmup_steps: 10000
```

### Rule 3: Every experiment script saves to results/

Every `scripts/run_*.py` must save its output to `results/{experiment_name}_results.json`. This is how PaperBench verifies numerical results.

### Rule 4: Every script accepts standard arguments

All experiment scripts must accept:
- `--config` — path to config file
- `--seed` — random seed (for reproducibility)
- `--output-dir` — where to save results
- `--max-steps` — maximum training steps (enables smoke testing)
- `--no-gpu` or `--device cpu` — force CPU execution

### Rule 5: Rubric coverage is complete

After designing the file tree, go through every rubric item in `rubric.json`:
- Every code_development item must map to at least one file in `src/` or `baselines/`
- Every execution item must map to a script, config, or README
- Every result_match item must map to a script that produces checkable output

If any rubric item has no assigned file: add a file, or mark it as `skip_reason: "requires proprietary data"` / `skip_reason: "requires GPU execution"`.

---

## Rubric Coverage Table

After designing the structure, produce this table (to show at user checkpoint):

```
Rubric Item Coverage Summary:
  Code Development: {X}/{total_CD} items have assigned files
  Execution: {X}/{total_EX} items have assigned files
  Result Match: {X}/{total_RM} items have assigned scripts

Unassigned items (need attention):
  CD-XXX: [description] — no file assigned yet
  ...
```

Any item in `uncovered_rubric_items` must be explained: is it a blocker, or is there a legitimate reason it can't be covered?
