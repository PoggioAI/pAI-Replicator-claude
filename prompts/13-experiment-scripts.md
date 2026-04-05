# Phase 9: Experiment Scripts

## Objective

Create one self-contained, runnable Python script for every table and every figure in the paper. These scripts are PaperBench's primary execution targets — if a script doesn't exist or doesn't run, those result_match rubric items score 0.

**Every script must be independently runnable.** It should not import from other scripts.

---

## Required Inputs

- `analysis_workspace/paper_analysis.json` — table_figure_inventory
- `analysis_workspace/rubric.json` — execution rubric items
- All of `code_workspace/{paper_short_name}/src/`
- `analysis_workspace/experiment_manifest.json` (if exists from prior phases)

---

## Required Outputs

- `code_workspace/{paper_short_name}/scripts/run_table{N}.py` — one per table
- `code_workspace/{paper_short_name}/scripts/run_figure{N}.py` — one per figure
- `code_workspace/{paper_short_name}/configs/experiment_table{N}.yaml` — per-experiment configs
- `analysis_workspace/experiment_manifest.json`

Updated `analysis_workspace/implementation_checklist.json` — execution items updated.

---

## `experiment_manifest.json` Schema

```json
{
  "experiments": [
    {
      "id": "table1_main",
      "paper_element": "Table 1",
      "caption": "Main results on ImageNet",
      "script": "scripts/run_table1.py",
      "config": "configs/experiment_table1.yaml",
      "requires_gpu": true,
      "estimated_runtime_hours": 24,
      "expected_metrics": {
        "top1_accuracy": 82.3,
        "top5_accuracy": 96.1
      },
      "output_file": "results/table1_results.json",
      "rubric_items": ["EX-001", "EX-002", "RM-001", "RM-002"],
      "notes": "Main comparison experiment. Requires 8x A100 GPUs per paper."
    }
  ]
}
```

---

## Experiment Script Template

Every `scripts/run_*.py` must follow this template:

```python
#!/usr/bin/env python3
"""
Reproduces {Table/Figure N}: {caption from paper}.

Paper: {title}
Section: {section reference}

Usage:
    python scripts/run_tableN.py --config configs/experiment_tableN.yaml
    python scripts/run_tableN.py --config configs/experiment_tableN.yaml --seed 42
    python scripts/run_tableN.py --max-steps 1  # CPU smoke test (1 step only)

Results saved to: results/tableN_results.json
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Ensure src/ is on path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models.{main_model} import {ModelClass}
from src.data.{dataset} import get_dataloader
from src.training.trainer import Trainer
from src.training.optimizer import get_optimizer, get_scheduler
from src.training.loss import {LossClass}
from src.evaluation.metrics import compute_metrics


def parse_args():
    parser = argparse.ArgumentParser(description="Reproduce Table N from {paper title}")
    parser.add_argument("--config", default="configs/experiment_tableN.yaml",
                        help="Path to config file")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed for reproducibility")
    parser.add_argument("--output-dir", default="results",
                        help="Directory to save results")
    parser.add_argument("--max-steps", type=int, default=None,
                        help="Maximum training steps (for CPU smoke testing)")
    parser.add_argument("--device", default=None,
                        help="Device (cpu/cuda). Auto-detected if not specified.")
    parser.add_argument("--no-gpu", action="store_true",
                        help="Force CPU execution")
    return parser.parse_args()


def set_seed(seed):
    import torch
    import random
    import numpy as np
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def load_config(config_path):
    """Load YAML config. Falls back to default.yaml if experiment config missing."""
    import yaml
    if os.path.exists(config_path):
        with open(config_path) as f:
            return yaml.safe_load(f)
    print(f"Warning: {config_path} not found, using default config")
    with open("configs/default.yaml") as f:
        return yaml.safe_load(f)


def main():
    args = parse_args()
    set_seed(args.seed)

    # Device
    import torch
    if args.no_gpu or args.max_steps is not None:
        device = torch.device("cpu")
    elif args.device:
        device = torch.device(args.device)
    else:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    # Config
    config = load_config(args.config)
    if args.max_steps is not None:
        config["training"]["total_steps"] = args.max_steps
        config["training"]["eval_every_n_steps"] = args.max_steps
        config["data"]["num_workers"] = 0

    # Model
    model = {ModelClass}(**config["model"]).to(device)
    print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")

    # Data (use mock=True if max_steps set, to avoid real dataset downloads)
    use_mock = (args.max_steps is not None)
    train_loader = get_dataloader(
        config["data"]["root"], split="train",
        batch_size=config["training"]["batch_size"],
        mock=use_mock
    )
    val_loader = get_dataloader(
        config["data"]["root"], split="val",
        batch_size=config["training"]["eval_batch_size"],
        mock=use_mock
    )

    # Optimizer and scheduler
    optimizer = get_optimizer(model, config["training"])
    scheduler = get_scheduler(optimizer, config["training"])

    # Loss
    criterion = {LossClass}(**config.get("loss", {}))

    # Trainer
    trainer = Trainer(model, optimizer, scheduler, criterion, config)

    # Train
    print(f"Training for {config['training']['total_steps']} steps...")
    trainer.train(train_loader, val_loader, max_steps=config["training"]["total_steps"])

    # Evaluate
    print("Running final evaluation...")
    metrics = trainer.evaluate(val_loader)
    print(f"Results: {json.dumps(metrics, indent=2)}")

    # Save results
    os.makedirs(args.output_dir, exist_ok=True)
    results = {
        "experiment": "tableN_main",
        "paper_table": "Table N",
        "metrics": metrics,
        "seed": args.seed,
        "device": str(device),
        "config": config,
        "timestamp": datetime.now().isoformat()
    }
    output_path = os.path.join(args.output_dir, "tableN_results.json")
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"Results saved to {output_path}")


if __name__ == "__main__":
    main()
```

---

## Process

### Pass 1: Create all experiment scripts

For each entry in `paper_analysis.json → table_figure_inventory`:

1. Create `scripts/run_{table_or_figure}_{id}.py` following the template above
2. Adapt the template to the specific experiment:
   - Import the correct model class and dataloader
   - Set the correct config file path
   - Set the correct output filename
   - Add any experiment-specific logic (e.g., multiple ablation conditions in a loop)
3. Create `configs/experiment_{id}.yaml` with overrides for this specific experiment

4. For ablation experiments (multiple conditions in one table):
   - Create ONE script that loops over all conditions
   - Save separate JSON files per condition: `results/table2_ablation_{condition}.json`

### Pass 2: Validate scripts are complete

For each script:
- [ ] Script has `--max-steps`, `--seed`, `--output-dir`, `--no-gpu` arguments
- [ ] Script saves results to `results/{experiment}_results.json`
- [ ] Script handles `mock=True` when `--max-steps` is set
- [ ] Import at top of file works (no missing imports)
- [ ] Docstring accurately describes what the script reproduces

Update `experiment_manifest.json` and `implementation_checklist.json` for all execution items.

---

## GPU vs. CPU Scripts

Mark in `experiment_manifest.json → requires_gpu`:
- `requires_gpu: false` → runs in Phase 7 smoke test
- `requires_gpu: true` → cannot be run during skill execution; marked in README

Even GPU-required scripts must:
- Have the `--max-steps 1 --no-gpu` path work (smoke test)
- Be syntactically correct and importable
- Save to the right output path when run with real args

---

## reproduce.sh Update (paperbench_full mode only)

If `state.json → mode == "paperbench_full"`, after creating all experiment scripts:

1. Read `experiment_manifest.json` for the full list of experiments and their dependency order
2. Regenerate `reproduce.sh` (at repo root) with one `run_experiment` call per manifest entry
3. Ensure experiments are ordered by dependencies (if experiment B depends on A's outputs, A comes first)
4. Ensure `reproduce.sh` is executable (`chmod +x`)

See `prompts/17-reproduce-sh.md` for the full reproduce.sh specification.
