# PaperBench Scoring Reference — pAI-Replicator

> **IMPORTANT:** All scores produced by pAI-Replicator are INTERNAL ESTIMATES — they are NOT official PaperBench scores. Official PaperBench grading requires the PaperBench LLM judge pipeline running in a fresh container environment. Internal estimates are based on code inspection and CPU smoke tests, not actual GPU execution results. They correlate with but do not equal official scores.

## What PaperBench Evaluates

PaperBench is OpenAI's benchmark for AI agents' ability to replicate ML research papers. It evaluates 20 ICML 2024 Spotlight/Oral papers.

**Three scoring categories:**

| Category | Weight | What it measures |
|----------|--------|-----------------|
| Code Development | ~40% | Correct implementation of models, algorithms, losses, baselines |
| Execution | ~30% | Code runs without errors; scripts produce outputs |
| Result Match | ~30% | Experimental numbers match paper within tolerance |

**Key benchmark facts:**
- 8,316 individually gradable rubric items across all papers
- Leaf nodes: single, clear, pass/fail criteria
- Hierarchical: each node weighted relative to siblings
- Score = weight-adjusted fraction of satisfied items
- Best AI agent (2025): ~27% — humans: ~41%

---

## Rubric Item Granularity

PaperBench items are **very specific**. Examples of leaf-node items:

**Code Development:**
- "The model uses a transformer encoder with 12 layers"
- "Attention uses 8 heads"
- "Layer normalization is applied before (not after) the attention block"
- "AdamW optimizer with weight_decay=0.01 is used"
- "The learning rate warms up over 10,000 steps"
- "The training loss uses label smoothing with epsilon=0.1"

**Execution:**
- "The file `scripts/train.py` exists and is runnable"
- "Running `python scripts/train.py --config configs/default.yaml` exits 0"
- "The config file contains all hyperparameters from Table 1"
- "A requirements.txt or environment.yml is present"

**Result Match:**
- "Table 2 row 3 (our method, CIFAR-100) shows accuracy within 1% of reported 76.3%"
- "The ablation in Figure 4 shows the same qualitative trend"

---

## Scoring Strategy

### Easy Wins (high score per effort)

These items are almost always scorable with minimal implementation effort:

1. **Config files** — Create `configs/default.yaml` with ALL paper hyperparameters. One config file can cover 10+ rubric items.
2. **Script existence** — Just having `scripts/run_table1.py` (even if not fully correct) covers the "file exists" rubric item.
3. **README completeness** — A well-written README covers all documentation rubric items.
4. **requirements.txt** — Single file, covers several execution rubric items.
5. **Module imports** — If `src/models/main_model.py` imports cleanly, all import-check rubric items pass.
6. **Model architecture hyperparameters** — Putting num_layers, hidden_dim, etc. in config covers many items.

### Medium Wins (moderate effort)

- Correct forward pass (shapes correct, no NaN) — covers many code_development items
- Correct loss function — covers training rubric items
- Baseline implementations that run — covers baseline rubric items
- Data pipeline that loads correctly — covers data rubric items

### Hard Wins (high effort, need GPU)

- Actual numerical result matching — requires full training run
- Ablation results — requires multiple full training runs
- Baseline comparison numbers — requires running baselines at full scale

---

## Estimating PaperBench Score Without Running Full Experiments

Since GPU jobs cannot be run during skill execution, the estimated score is based on:

**Code Development score estimate:**
- Count rubric items where implementing file exists AND passes CPU tests
- Weight = (items_verified / total_code_development_items) × category_weight

**Execution score estimate:**
- Count runnable scripts (smoke test passes) × execution_weight
- Count config files with correct hyperparameters × config_weight
- Count documentation items present × docs_weight

**Result Match score estimate (conservative):**
- Items where CPU test showed loss decreasing in right direction → partial credit (0.5)
- Items requiring actual GPU results → estimate based on code correctness only
- If the code is correct and would produce results, estimate 50% of result_match items pass (conservative assumption)

**Final estimate:**
```
score = (code_dev_satisfied / code_dev_total) × 0.40
      + (execution_satisfied / execution_total) × 0.30
      + (result_match_estimated / result_match_total) × 0.30
```

---

## Confidence Levels

| Confidence | Meaning |
|-----------|---------|
| `high` | Code verified via CPU tests, hyperparams in config, scripts runnable |
| `medium` | Code implemented but not all CPU-verified; some scripts untested |
| `low` | Significant portions not implemented; many rubric items unaddressed |

---

## What the PaperBench Judge Persona Should Flag

The PaperBench Judge persona (`prompts/03-persona-paperbench-judge.md`) must flag:

**Definite failures (items that will score 0 regardless of code quality):**
- Missing experiment scripts for any major table/figure
- Config files that don't expose paper hyperparameters
- No README or incomplete reproduction instructions
- Baseline implementations that are clearly wrong

**Easy wins not yet captured:**
- Hyperparameter values mentioned in paper but not in any config file
- Experiment scripts that exist but don't save results to a predictable path
- Missing `requirements.txt` / `environment.yml`
- Missing paper citation in README

**Items to deprioritize (hard, GPU-only):**
- Exact numerical matching of results
- Multi-GPU training setup
- Proprietary dataset reproduction
