# Phase 2: PaperBench-Style Rubric Decomposition

## Official Rubric Import (PaperBench modes only)

If `analysis_workspace/official_rubric.json` exists (placed there by Phase 0.5 bundle ingestion), **do NOT generate a rubric from scratch.** Instead:

1. Load the official rubric and convert it to the internal format (adding `status`, `evidence_file`, `evidence_line` fields to each leaf item, all initialized as `"pending"`).
2. **Preserve all item IDs, weights, categories, and descriptions exactly.** Do not rename, reorder, or reweight anything.
3. You MAY add supplementary items that the agent identifies as missing (mark these with `"source": "agent_added"` to distinguish from official items).
4. Write `rubric_coverage.json` as normal.

Then proceed to the checkpoint. The Gate 1 threshold check still applies but should pass easily since official rubrics are already well-structured.

---

## Objective

Build a hierarchical rubric that mirrors PaperBench's evaluation structure. Every leaf node is a single, verifiable, pass/fail claim. This rubric will be your scoreboard throughout the replication — every implementation decision should be traceable to one or more rubric items.

**Think like a PaperBench evaluator**, not like the paper's author. You are writing the grading rubric, not the paper summary.

---

## Required Inputs

- `analysis_workspace/paper_analysis.json`
- `analysis_workspace/paper_extracted.md`
- `analysis_workspace/official_rubric.json` (if present — from bundle ingestion)
- `templates/rubric_template.json` (schema reference)

---

## Required Outputs

### 1. `analysis_workspace/rubric.json`

A hierarchical rubric following the `rubric_template.json` schema. Every leaf item must have:

```json
{
  "id": "CD-001",
  "category": "code_development",
  "subcategory": "model_implementation",
  "description": "The transformer encoder uses pre-LayerNorm (LN before attention, not after)",
  "verification_method": "code_check",
  "weight": 0.15,
  "difficulty": "easy",
  "paper_reference": "Section 3.2, Figure 2",
  "status": "pending",
  "evidence_file": null,
  "evidence_line": null,
  "skip_reason": null
}
```

**ID prefix conventions:**
- `CD-` = Code Development
- `EX-` = Execution
- `RM-` = Result Match

Number sequentially within each category: CD-001, CD-002, ...

### 2. `analysis_workspace/rubric_coverage.json`

Initialized with all rubric items set to "pending":

```json
{
  "total_items": 0,
  "items_by_status": {
    "pending": 0,
    "implemented": 0,
    "verified": 0,
    "skipped": 0
  },
  "items_by_category": {
    "code_development": {"total": 0, "pending": 0, "implemented": 0, "verified": 0},
    "execution": {"total": 0, "pending": 0, "implemented": 0, "verified": 0},
    "result_match": {"total": 0, "pending": 0, "implemented": 0, "verified": 0}
  },
  "rubric_items": {}
}
```

---

## Rubric Item Generation Guide

### Code Development Items (target: 30–60 items)

**model_implementation subcategory:**
- One item per major architectural choice: "uses X layers", "hidden dim is Y", "uses Z attention heads"
- One item per normalization choice: "uses pre-LayerNorm", "uses batch norm after conv layers"
- One item per activation function: "uses GELU activation (not ReLU)"
- One item per weight initialization: "uses Xavier initialization for projection weights"
- One item per architectural variant reported in ablations

**data_pipeline subcategory:**
- One item per dataset: "CIFAR-10 dataset is used for training and evaluation"
- One item per preprocessing step: "images are normalized with mean=[0.485, 0.456, 0.406]"
- One item per augmentation: "random crop with padding=4 is applied during training"
- One item per data split: "10% of training set used as validation"

**training_loop subcategory:**
- One item per optimizer configuration: "AdamW optimizer is used", "beta1=0.9", "beta2=0.999"
- One item per LR schedule: "cosine LR decay is used", "warmup for 10000 steps"
- One item per regularization: "dropout rate of 0.1 applied to attention weights"
- One item for gradient clipping: "gradients clipped at max_norm=1.0"
- One item for loss function: "cross-entropy loss with label_smoothing=0.1"

**baselines subcategory:**
- One item per baseline: "[Baseline Name] is implemented as a comparison method"
- One item per baseline configuration: "[Baseline Name] uses the configuration from [citation]"

### Execution Items (target: 15–30 items)

**runnable_scripts subcategory:**
- One item per table/figure: "scripts/run_table1.py exists and is executable"
- One item per script output: "run_table1.py saves results to results/table1_results.json"
- One item per script argument: "run_table1.py accepts --config, --seed, --output-dir arguments"
- One item for smoke test: "running run_table1.py --max-steps 1 exits with code 0"

**configuration subcategory:**
- One item per config file: "configs/default.yaml exists and contains all main hyperparameters"
- One item per critical hyperparameter in config: "configs/default.yaml specifies learning_rate"
- One item for experiment configs: "configs/experiment_table1.yaml exists with experiment-specific overrides"

**documentation subcategory:**
- "README.md contains paper citation"
- "README.md contains installation instructions"
- "README.md contains data download/setup instructions"
- "README.md contains command to reproduce Table {N}" (one per major table)
- "requirements.txt or environment.yml exists with pinned versions"

### Result Match Items (target: 20–40 items)

**main_results subcategory:**
- One item per reported metric per row in the main results table
- Example: "Table 1 row 'Ours': Top-1 accuracy on ImageNet ≈ 82.3% (±1%)"
- Use ±1-2% tolerance for single numbers, ±5% for ratios/speedups

**ablation_results subcategory:**
- One item per ablation condition per table/figure
- Example: "Table 3 'w/o LayerNorm': accuracy drops by ≈ 2.1% compared to full model"
- Focus on qualitative trends when quantitative values are hard to pin down

**baseline_comparisons subcategory:**
- One item per baseline per table: "[Baseline X] achieves ≈ 78.5% on ImageNet (Table 1)"

---

## Pass 2: Verification and Weighting

After generating the initial rubric, do a second pass to:

1. **Assign weights**: Within each subcategory, allocate weights summing to 1.0. Higher weight for:
   - Core architectural claims (vs. peripheral details)
   - Results in the main table (vs. ablation tables)
   - Items that are uniquely characteristic of this paper's contribution

2. **Assign difficulty**:
   - `easy`: file_exists checks, hyperparameter value checks — anything verifiable without running code
   - `medium`: code_check items — verifiable by reading the code
   - `hard`: result_match items requiring full training runs

3. **Cross-check completeness**: For every entry in `paper_analysis.json → table_figure_inventory`, verify there is at least one result_match rubric item.

4. **Minimum count check**: Ensure at least 40 total leaf items, with ≥10 in code_development, ≥5 in execution, ≥10 in result_match.

---

## Rubric Generation Mindset

**Do NOT write rubric items that are:**
- Too vague: "The model is implemented correctly" (unverifiable)
- Too broad: "All experiments reproduce" (not a leaf node)
- Redundant: Multiple items saying the same thing in different words

**DO write rubric items that are:**
- Specific enough to check without ambiguity
- Testable: you can clearly say pass or fail
- Traced to a paper section/table/figure

**When in doubt about a specific value**, write the item as a range:
- "learning_rate is between 1e-4 and 1e-3" (matches typical range for Adam)
- "Table 1 Top-1 accuracy is within 2% of reported 82.3%" (numerical tolerance)
