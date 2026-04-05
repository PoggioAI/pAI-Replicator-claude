# Phase 6: Training Infrastructure

## Objective

Implement the training loop, optimizer setup, LR scheduling, evaluation logic, checkpointing, and logging. This must match the paper's training procedure **exactly** — every hyperparameter value from the paper should end up in `configs/default.yaml`.

---

## Required Inputs

- `analysis_workspace/paper_analysis.json` — training_config section
- `analysis_workspace/architecture_plan.json`
- `analysis_workspace/implementation_checklist.json`

---

## Required Outputs

All in `code_workspace/{paper_short_name}/`:

- `src/training/trainer.py` — main Trainer class
- `src/training/optimizer.py` — optimizer and scheduler setup
- `src/training/loss.py` — loss functions (if not already in src/losses/)
- `src/evaluation/evaluator.py` — evaluation loop
- `src/evaluation/metrics.py` — all evaluation metrics
- `src/utils/logging.py` — logging utilities
- `src/utils/checkpointing.py` — checkpoint save/load
- `configs/default.yaml` — all paper hyperparameters

Updated `analysis_workspace/implementation_checklist.json` — mark training_loop items as "implemented".

---

## `configs/default.yaml` Must Include

Every hyperparameter mentioned in the paper. Use comments to cite paper location:

```yaml
# ============================================================
# {Paper Title} — Default Configuration
# All values from paper unless otherwise noted.
# ============================================================

model:
  name: {model_name}
  # Architecture parameters (Section 3, Table 1)
  num_layers: 12
  hidden_dim: 512
  num_heads: 8
  ffn_dim: 2048
  dropout: 0.1
  attention_dropout: 0.1      # Appendix B
  use_pre_norm: true           # Figure 2

training:
  # Optimizer (Section 4, Appendix B)
  optimizer: adamw
  learning_rate: 3.0e-4        # Table 3
  weight_decay: 0.01           # Appendix B
  beta1: 0.9                   # standard Adam
  beta2: 0.999                 # standard Adam
  epsilon: 1.0e-8

  # Schedule
  lr_schedule: cosine          # Section 4
  warmup_steps: 10000          # Appendix B
  total_steps: 300000          # Table 3

  # Regularization
  gradient_clip_norm: 1.0      # Appendix B
  label_smoothing: 0.1         # Section 4

  # Batch
  batch_size: 256              # Table 3
  gradient_accumulation_steps: 1

  # Checkpointing
  save_every_n_steps: 10000
  eval_every_n_steps: 1000

data:
  dataset: imagenet
  root: ./data/imagenet
  num_workers: 8
  image_size: 224
  # Preprocessing (Section 4.1)
  normalize_mean: [0.485, 0.456, 0.406]
  normalize_std: [0.229, 0.224, 0.225]
  random_crop_size: 224
  random_crop_padding: 32

evaluation:
  metrics: [top1_accuracy, top5_accuracy]

logging:
  log_every_n_steps: 100
  use_wandb: false
  project_name: {paper_short_name}

output:
  output_dir: ./results
  checkpoint_dir: ./checkpoints
```

---

## Trainer Class Design

```python
class Trainer:
    """Training loop per paper Section 4 and Appendix B.

    Implements the training procedure described in the paper exactly,
    including learning rate schedule, gradient clipping, and evaluation protocol.

    Reference: Section 4 (Training), Appendix B (Hyperparameters).
    """

    def __init__(self, model, optimizer, scheduler, criterion, config):
        self.model = model
        self.optimizer = optimizer
        self.scheduler = scheduler
        self.criterion = criterion
        self.config = config
        self.global_step = 0

    def train_step(self, batch):
        """One training step. Returns loss value."""
        ...

    def evaluate(self, dataloader):
        """Evaluation loop. Returns dict of metric_name -> value."""
        self.model.eval()
        with torch.no_grad():
            ...
        self.model.train()

    def save_checkpoint(self, path):
        """Save checkpoint with model, optimizer, scheduler state."""
        ...

    def load_checkpoint(self, path):
        """Load checkpoint."""
        ...

    def train(self, train_loader, val_loader, max_steps=None):
        """Main training loop."""
        # max_steps allows CPU smoke testing with --max-steps 1
        ...
```

---

## Implementation Notes

### Warmup + Cosine Schedule

```python
def get_cosine_schedule_with_warmup(optimizer, warmup_steps, total_steps):
    """Cosine LR schedule with warmup, per paper Appendix B."""
    def lr_lambda(step):
        if step < warmup_steps:
            return step / warmup_steps
        progress = (step - warmup_steps) / (total_steps - warmup_steps)
        return 0.5 * (1 + math.cos(math.pi * progress))
    return torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)
```

### Gradient Clipping

Must be applied AFTER `loss.backward()` but BEFORE `optimizer.step()`:

```python
loss.backward()
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=config.training.gradient_clip_norm)
optimizer.step()
```

### Evaluation Metric Computation

All metrics must save to `results/{experiment_name}_results.json`:

```python
results = {
    "top1_accuracy": 82.3,
    "top5_accuracy": 96.1,
    "eval_loss": 0.654,
    "step": global_step,
    "timestamp": datetime.now().isoformat(),
    "config": OmegaConf.to_container(config)
}
with open(f"results/{experiment_name}_results.json", "w") as f:
    json.dump(results, f, indent=2)
```

---

## After This Phase

Before marking complete:
- [ ] `configs/default.yaml` contains ALL hyperparameters from `paper_analysis.json → training_config`
- [ ] Trainer class has `max_steps` argument (enables CPU smoke test)
- [ ] Gradient clipping applied in correct position
- [ ] LR schedule matches paper description
- [ ] Evaluation saves results to `results/` directory
- [ ] Checkpoint save/load implemented
- [ ] `implementation_checklist.json` updated for training_loop items

---

## reproduce.sh — Initial Generation (paperbench_full mode only)

If `state.json → mode == "paperbench_full"`, also generate an initial `reproduce.sh` at the repo root. Use `{SKILL_DIR}/templates/reproduce.sh.tmpl` as a starting point. At this stage, it should contain:

1. Environment setup (`pip install -r requirements.txt`)
2. The `run_experiment` helper function
3. A placeholder comment: `# Experiments will be wired in Phase 9`

This file will be updated in Phase 9 (experiment scripts) with actual experiment entries, and validated in Phase 13 (integration test).

See `prompts/17-reproduce-sh.md` for the full specification.
