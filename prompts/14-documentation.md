# Phase 10: Documentation

## Objective

Write complete, accurate documentation. The README is itself a PaperBench evaluation target — documentation rubric items are among the easiest wins in the scoring rubric.

---

## Required Inputs

- All of `code_workspace/{paper_short_name}/`
- `analysis_workspace/experiment_manifest.json`
- `analysis_workspace/paper_analysis.json`
- `analysis_workspace/baseline_coverage.json`

---

## Required Outputs

- `code_workspace/{paper_short_name}/README.md` — comprehensive guide
- `code_workspace/{paper_short_name}/requirements.txt` — pinned dependencies
- `code_workspace/{paper_short_name}/docs/architecture.md` — architecture notes

Updated `analysis_workspace/implementation_checklist.json` — documentation items updated.

---

## README.md Structure

```markdown
# {Paper Title}

Official replication of "{Paper Title}" ({venue} {year}).

> {one-sentence paper summary}

## Citation

```bibtex
@inproceedings{...}
```

## Overview

{2-3 sentence description of the paper's contribution}

**Key results:**
- Table 1: Our method achieves {X}% on {dataset} (vs. {baseline} at {Y}%)
- {key ablation finding}

## Installation

```bash
# Clone repository
git clone {repo_url}
cd {repo_name}

# Create conda environment (recommended)
conda create -n {name} python=3.10
conda activate {name}

# Install dependencies
pip install -r requirements.txt
```

**Requirements:**
- Python 3.9+
- PyTorch {version}+
- CUDA {version}+ (for GPU training)
- See `requirements.txt` for full dependency list

## Data Setup

### {Dataset 1}
{Where to download, expected directory structure}

```bash
# Download and prepare {Dataset 1}
{exact command}
```

Expected directory structure after setup:
```
data/
  {dataset}/
    train/
    val/
    test/
```

### {Dataset 2}
{Same structure}

## Reproducing Results

### Table 1: {Main Results Table Caption}

{Brief description of what Table 1 shows}

```bash
# Full training (requires GPU)
python scripts/run_table1.py --config configs/experiment_table1.yaml

# CPU smoke test (verifies code runs, 1 step)
python scripts/run_table1.py --max-steps 1 --no-gpu
```

Results saved to: `results/table1_results.json`

Expected results:
| Method | Metric 1 | Metric 2 |
|--------|----------|----------|
| Ours   | {X}%     | {Y}%     |

### Table 2: {Table 2 Caption}

{Same structure for each table}

### Figure {N}: {Figure Caption}

{Same structure for each figure}

### Ablation Studies

{For each ablation table/figure, same structure}

## Baselines

| Baseline | Status | Notes |
|----------|--------|-------|
| {Name}   | Implemented | `baselines/{name}.py` |
| {Name}   | Excluded | {reason} |

## Hardware Requirements

- **Training**: {N} x {GPU model} (~{X} hours)
- **Inference only**: CPU sufficient
- **Memory**: ~{X}GB GPU memory for batch_size={N}

## Project Structure

```
{paper_short_name}/
  src/
    models/      # Model architectures
    data/        # Data loading and preprocessing
    training/    # Training loop, optimizer, loss
    evaluation/  # Metrics and evaluation
    utils/       # Shared utilities
  baselines/     # Baseline method implementations
  scripts/       # Experiment reproduction scripts
  configs/       # Hyperparameter configuration files
  results/       # Experiment outputs (created at runtime)
  tests/         # CPU sanity tests
```

## Configuration

All hyperparameters are in `configs/default.yaml`. Key parameters:

| Parameter | Value | Paper Reference |
|-----------|-------|-----------------|
| learning_rate | {X} | Table 3 |
| batch_size | {X} | Section 4.1 |
| {others...} | | |

Experiment-specific overrides in `configs/experiment_*.yaml`.

## Troubleshooting

**ImportError: No module named 'X'**
```bash
pip install -r requirements.txt
```

**CUDA out of memory**
Reduce `batch_size` in the config file or use gradient accumulation:
```yaml
training:
  batch_size: 64  # reduce from 256
  gradient_accumulation_steps: 4  # equivalent effective batch size
```

**Dataset not found**
See [Data Setup](#data-setup) section above.
```

---

## `requirements.txt`

Pin specific versions for reproducibility:

```
torch==2.1.0
torchvision==0.16.0
numpy==1.24.0
scipy==1.11.0
scikit-learn==1.3.0
pyyaml==6.0.1
tqdm==4.66.1
wandb==0.16.0
matplotlib==3.7.0
```

Use `pip freeze | grep -E "(torch|numpy|scipy|yaml|tqdm)"` as a reference for currently installed versions if available.

---

## Process

### Pass 1: Write README

1. Fill in every section following the template above
2. For every table and figure in `experiment_manifest.json`, add a reproduction section
3. Add the hardware requirements from `paper_analysis.json → training_config.hardware`
4. Write the project structure section

### Pass 2: Completeness check

Go through every documentation rubric item in `rubric.json` and verify:
- [ ] Paper citation present (BibTeX)
- [ ] Installation instructions (conda/pip commands)
- [ ] Data download instructions for each dataset
- [ ] Reproduction command for each table and figure
- [ ] Expected results table for each experiment
- [ ] Hardware requirements
- [ ] `requirements.txt` with pinned versions
- [ ] Project structure description
- [ ] Config parameter table

Update `implementation_checklist.json` for all documentation items.
