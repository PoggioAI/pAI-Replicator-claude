# Phase 8: Baseline Implementations

## Objective

Implement every baseline comparison method mentioned in the paper. Every method in every comparison table or figure must have either:
1. A correct implementation in `baselines/`
2. An explicit justification for exclusion in `analysis_workspace/baseline_coverage.json`

Baselines are high-value PaperBench targets — they account for a significant portion of the code_development and result_match rubric items.

---

## Required Inputs

- `analysis_workspace/paper_analysis.json` — baselines section
- `analysis_workspace/rubric.json` — baseline rubric items
- `analysis_workspace/architecture_plan.json`
- `analysis_workspace/implementation_checklist.json`

---

## Required Outputs

- `code_workspace/{paper_short_name}/baselines/` — one file/directory per baseline
- `analysis_workspace/baseline_coverage.json` — status of every baseline
- Updated `configs/` — baseline configuration files
- Updated `analysis_workspace/implementation_checklist.json` — baseline items updated

---

## `baseline_coverage.json` Schema

```json
{
  "baselines": [
    {
      "name": "TransformerXL",
      "paper_reference": "[Chen et al., 2019]",
      "paper_tables": ["Table 1", "Table 2"],
      "implementation_file": "baselines/transformer_xl.py",
      "config_file": "configs/baseline_transformer_xl.yaml",
      "implementation_status": "implemented",
      "exclusion_reason": null,
      "implementation_notes": "Uses paper's reported hyperparameters from [Chen 2019] Table 3",
      "rubric_items": ["CD-045", "CD-046", "RM-023"]
    }
  ]
}
```

Valid `implementation_status` values:
- `implemented` — full implementation in `baselines/`
- `excluded_proprietary` — uses proprietary code/data, cannot implement
- `excluded_trivial` — trivial variant (e.g., "no regularization" = remove one line from main model)
- `excluded_not_applicable` — baseline is an evaluation metric, not a model
- `excluded_too_complex` — implementation would require weeks; noted with justification

---

## Baseline Implementation Standards

### Standard 1: Baseline as a First-Class Module

Each baseline should be implemented as a proper Python class in its own file, not as a copy-paste from the main model with modifications. This makes it independently testable:

```python
# baselines/transformer_xl.py
class TransformerXLBaseline(nn.Module):
    """TransformerXL baseline from [Chen et al., 2019].

    Implements the TransformerXL model as used in Table 1 comparison.
    Configuration follows the paper's reported hyperparameters unless
    otherwise noted.

    Reference: Chen et al. (2019), "Transformer-XL: Attentive Language Models
    Beyond a Fixed-Length Context". Configuration from their Table 3.
    """
```

### Standard 2: Separate Config Files

Every baseline needs its own config file in `configs/baseline_{name}.yaml` with:
- All hyperparameters used for the comparison
- Notes on where values came from (original paper vs. matched to our paper's setup)

```yaml
# configs/baseline_transformer_xl.yaml
# TransformerXL baseline configuration
# Values from Chen et al. (2019) Table 3 (Wiki-103 setting)
# except batch_size matched to our experimental setup (Section 4.1)

model:
  type: transformer_xl
  num_layers: 18
  d_model: 256
  num_heads: 8
  d_head: 32
  d_inner: 1024
  dropout: 0.1
  mem_len: 150  # memory length, from Chen et al.

training:
  batch_size: 256  # matched to our setup, not original paper
  learning_rate: 2.5e-4  # original paper value
  ...
```

### Standard 3: Baseline Must Use Same Interface

Every baseline must have the same `forward()` signature as the main model (or a documented adapter). This enables running experiment scripts with `--model-type baseline_x` without changing the training loop:

```python
def forward(self, x, **kwargs):
    """
    Args:
        x: Input tensor (batch, seq_len) or (batch, C, H, W) depending on task
        **kwargs: Additional arguments (ignored for compatibility)
    Returns:
        logits: (batch, num_classes) or (batch, seq_len, vocab_size)
    """
```

### Standard 4: Acknowledge Approximations

When the baseline has implementation details not specified in the original paper, document them explicitly:

```python
# NOTE: Chen et al. (2019) do not specify weight initialization.
# We use Xavier uniform initialization (standard practice for transformers).
# This may differ from their actual implementation.
```

---

## Process

### Pass 1: Implement each baseline

For each baseline in `paper_analysis.json → baselines`:

1. Check if the baseline is from a well-known paper that has a standard implementation:
   - If yes, model your implementation after the original paper's description
   - If there's an official open-source implementation, use it as reference (but write your own code)

2. Check if the baseline is a simple variant of the main model (ablation baseline):
   - If yes, implement it as a subclass or a factory function with modified config

3. For each baseline, create:
   - `baselines/{baseline_name}.py`
   - `configs/baseline_{baseline_name}.yaml`

4. Update `baseline_coverage.json` with status

### Pass 2: Verify and update checklist

1. Re-read each baseline implementation against its source paper description
2. Check that all baseline rubric items from `rubric.json` are covered
3. Run quick import test: `python -c "from baselines.{name} import *; print('OK')"` for each baseline
4. Update `implementation_checklist.json` for all baseline rubric items

---

## When to Exclude Baselines

Exclusion is acceptable with justification. Never silently omit a baseline.

**Acceptable exclusion reasons:**
- `excluded_proprietary`: "This method requires proprietary code from [Company]; no open-source implementation exists"
- `excluded_too_complex`: "Implementing [Method] from scratch would require replicating an entire separate paper (e.g., [citation]). We use the reported numbers from the original paper's Table 2."
- `excluded_trivial`: "This baseline is equivalent to our main model with the proposed component removed. It is implemented as `main_model(use_component=False)` in the main model config."

Document all exclusions in `baseline_coverage.json` and in `README.md → Baselines` section.
