# CPU Verification Protocol — pAI-Replicator

## Purpose

Phase 7 runs a mandatory suite of CPU-only sanity tests before any baseline or experiment work begins. Code that cannot pass these tests on a laptop CPU will not score on PaperBench's Execution category.

**Hard rule:** Every test in this protocol must pass before Phase 7 exits. There is no "warn-and-proceed" path. If tests fail after 3 attempts, the orchestrator escalates to the user.

---

## Constraints

- ALL tests must be CPU-only (`device="cpu"`, no CUDA calls, no `torch.cuda.*`)
- ALL tests must complete in under **30 minutes total** (all categories combined)
- Use **synthetic / random data only** — never download real datasets
- Use **tiny configurations**: 2 layers, small hidden dim (≤64), batch_size=2, seq_len=8
- Every test script goes in `verification_workspace/cpu_test_scripts/`
- Results written to `verification_workspace/cpu_test_results.json`

---

## Required Test Categories

### Category 1: Import Tests

**Script:** `cpu_test_scripts/test_imports.py`

```python
"""Test that all src/ modules import without error."""
import sys
sys.path.insert(0, ".")

def test_all_imports():
    import importlib
    import pkgutil
    # Walk src/ and import every module
    for finder, name, ispkg in pkgutil.walk_packages(["src"], prefix="src."):
        try:
            importlib.import_module(name)
            print(f"  OK: {name}")
        except Exception as e:
            print(f"  FAIL: {name} — {e}")
            raise

if __name__ == "__main__":
    test_all_imports()
    print("CATEGORY 1 PASSED")
```

**Pass criteria:**
- All `src/` modules importable without ImportError or circular import
- All required packages present (no ModuleNotFoundError)

---

### Category 2: Forward Pass Tests

**Script:** `cpu_test_scripts/test_forward_pass.py`

```python
"""Test forward pass with synthetic data on CPU."""
import torch
import numpy as np

def make_tiny_config(original_config):
    """Override config with tiny dimensions for CPU testing."""
    # Implementations must provide a get_tiny_config() function
    # or accept overrides via __init__ kwargs
    pass

def test_forward_pass():
    # Import the main model
    from src.models import MainModel  # adjust import to actual class name

    # Instantiate with tiny config
    model = MainModel(num_layers=2, hidden_dim=32, ...)  # tiny config
    model.eval()

    # Synthetic input (batch_size=2)
    x = torch.randn(2, 8, 32)  # adjust shape to match model input

    with torch.no_grad():
        output = model(x)

    # Check output shape
    expected_shape = (2, ...)  # fill in expected
    assert output.shape == expected_shape, f"Shape mismatch: {output.shape} != {expected_shape}"

    # Check for NaN/Inf
    assert not torch.isnan(output).any(), "NaN in output"
    assert not torch.isinf(output).any(), "Inf in output"

    print(f"  Forward pass OK: output shape {output.shape}")
    print("CATEGORY 2 PASSED")

if __name__ == "__main__":
    test_forward_pass()
```

**Pass criteria:**
- Model instantiates without error
- Forward pass on batch_size=2 synthetic input completes without error
- Output shape matches expected shape (as defined by paper architecture)
- No NaN or Inf values in output

---

### Category 3: Loss Computation Tests

**Script:** `cpu_test_scripts/test_loss.py`

```python
"""Test loss computation and backward pass."""
import torch

def test_loss_computation():
    from src.losses import MainLoss  # adjust to actual class
    from src.models import MainModel

    model = MainModel(num_layers=2, hidden_dim=32, ...)
    criterion = MainLoss(...)

    # Synthetic batch
    x = torch.randn(2, 8, 32)
    targets = torch.randint(0, 10, (2,))  # adjust to task

    # Forward + loss
    output = model(x)
    loss = criterion(output, targets)

    # Check loss is finite scalar
    assert loss.ndim == 0, f"Loss is not scalar: shape {loss.shape}"
    assert torch.isfinite(loss), f"Loss is not finite: {loss.item()}"
    assert loss.item() > 0, f"Loss is zero or negative: {loss.item()}"

    # Backward pass
    loss.backward()

    # Check gradients exist and are finite
    for name, param in model.named_parameters():
        if param.grad is not None:
            assert torch.isfinite(param.grad).all(), f"Non-finite gradient in {name}"
            assert not (param.grad == 0).all(), f"All-zero gradient in {name}"

    print(f"  Loss OK: {loss.item():.4f}")
    print("CATEGORY 3 PASSED")

if __name__ == "__main__":
    test_loss_computation()
```

**Pass criteria:**
- Loss is a finite scalar (not NaN, not Inf, not zero)
- `loss.backward()` completes without error
- At least some parameters have non-zero, finite gradients

---

### Category 4: Training Step Tests

**Script:** `cpu_test_scripts/test_training_step.py`

```python
"""Test that one training step executes and loss decreases."""
import torch

def test_training_step():
    from src.models import MainModel
    from src.losses import MainLoss

    model = MainModel(num_layers=2, hidden_dim=32, ...)
    criterion = MainLoss(...)
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

    # Synthetic batch (fixed seed for reproducibility)
    torch.manual_seed(42)
    x = torch.randn(2, 8, 32)
    targets = torch.randint(0, 10, (2,))

    # One training step
    optimizer.zero_grad()
    output = model(x)
    loss = criterion(output, targets)
    loss.backward()
    optimizer.step()

    # Verify parameters changed
    # (store initial params before step and compare)
    print(f"  Training step OK: loss = {loss.item():.4f}")

    # 5-step overfit test (same batch)
    losses = []
    for step in range(5):
        optimizer.zero_grad()
        output = model(x)
        loss = criterion(output, targets)
        loss.backward()
        optimizer.step()
        losses.append(loss.item())

    # Loss should decrease (overfit on same batch)
    assert losses[-1] < losses[0], \
        f"Loss did not decrease over 5 steps: {losses[0]:.4f} -> {losses[-1]:.4f}"

    print(f"  5-step overfit test OK: {losses[0]:.4f} -> {losses[-1]:.4f}")
    print("CATEGORY 4 PASSED")

if __name__ == "__main__":
    test_training_step()
```

**Pass criteria:**
- One optimizer step completes without error
- Model parameters change after the step
- Loss decreases over 5 consecutive steps on the same synthetic batch

---

### Category 5: Data Pipeline Tests

**Script:** `cpu_test_scripts/test_data_pipeline.py`

```python
"""Test data loading with mock/synthetic data."""
import torch
import tempfile
import os

def test_data_pipeline():
    from src.data import MainDataset, get_dataloader  # adjust imports

    # Create temporary mock data directory
    with tempfile.TemporaryDirectory() as tmpdir:
        # Generate mock data files (format depends on paper dataset)
        # e.g., for image datasets: create tiny PNG files
        # e.g., for text: create small .txt files
        # ... (generate mock data appropriate to dataset format)

        # Instantiate dataset
        dataset = MainDataset(root=tmpdir, split="train", ...)

        # Instantiate dataloader
        loader = get_dataloader(dataset, batch_size=2, num_workers=0)

        # Load one batch
        batch = next(iter(loader))

        # Check batch structure
        assert isinstance(batch, (tuple, dict, list)), "Unexpected batch type"

        # Check shapes (fill in expected shapes based on paper)
        if isinstance(batch, (tuple, list)):
            x, y = batch[0], batch[1]
            print(f"  Batch shapes: x={x.shape}, y={y.shape}")

    print("CATEGORY 5 PASSED")

if __name__ == "__main__":
    test_data_pipeline()
```

**Pass criteria:**
- DataLoader instantiates without error using mock/temporary data
- At least one batch loads successfully
- Batch shapes match expected shapes from paper

---

### Category 6: Script Smoke Tests

**Script:** `cpu_test_scripts/test_script_smoke.py`

```python
"""Smoke test: at least one experiment script runs for 1 step."""
import subprocess
import sys
import os

def test_script_smoke():
    # Find the first experiment script
    scripts_dir = "scripts"
    scripts = [f for f in os.listdir(scripts_dir)
               if f.startswith("run_") and f.endswith(".py")]

    if not scripts:
        print("  WARNING: No Python experiment scripts found in scripts/")
        print("  Checking for shell scripts...")
        # If only .sh scripts exist, validate they reference real Python files
        return

    script = os.path.join(scripts_dir, scripts[0])

    # Run with max-steps=1 or dry-run
    result = subprocess.run(
        [sys.executable, script, "--max-steps", "1", "--no-gpu"],
        capture_output=True, text=True, timeout=300  # 5 min max
    )

    if result.returncode != 0:
        print(f"  FAIL: {script}")
        print(f"  STDOUT: {result.stdout[-500:]}")
        print(f"  STDERR: {result.stderr[-500:]}")
        raise AssertionError(f"Script failed with code {result.returncode}")

    print(f"  Smoke test OK: {script}")
    print("CATEGORY 6 PASSED")

if __name__ == "__main__":
    test_script_smoke()
```

**Pass criteria:**
- At least one experiment script runs with `--max-steps 1` and exits 0
- If scripts are shell-only (`.sh`), they must reference Python files that are importable

---

## Category 7: reproduce.sh Smoke Test (paperbench_full mode ONLY)

This category is **only** tested when `state.json → mode == "paperbench_full"`. In other modes, skip it.

```python
def test_reproduce_sh():
    """Category 7: reproduce.sh runs with MAX_STEPS=1 and exits 0."""
    import subprocess, os

    repo_dir = "code_workspace/{paper_short_name}/"
    reproduce_sh = os.path.join(repo_dir, "reproduce.sh")

    # Check file exists
    assert os.path.exists(reproduce_sh), f"reproduce.sh not found at {reproduce_sh}"

    # Check executable
    assert os.access(reproduce_sh, os.X_OK), "reproduce.sh is not executable"

    # Check has shebang
    with open(reproduce_sh) as f:
        first_line = f.readline()
    assert first_line.startswith("#!/"), f"Missing shebang: {first_line[:50]}"

    # Check contains pip install
    content = open(reproduce_sh).read()
    assert "pip install" in content or "conda install" in content, "No dependency install step"

    # Run with MAX_STEPS=1 (smoke test)
    env = os.environ.copy()
    env["MAX_STEPS"] = "1"
    env["DEVICE"] = "cpu"
    result = subprocess.run(
        ["bash", reproduce_sh],
        cwd=repo_dir,
        capture_output=True, text=True,
        timeout=300,
        env=env,
    )
    assert result.returncode == 0, (
        f"reproduce.sh exited with code {result.returncode}\n"
        f"STDERR: {result.stderr[-500:]}"
    )
    print("CATEGORY 7 PASSED")
```

**Pass criteria:**
- reproduce.sh exists, is executable, has shebang
- Contains a dependency install step
- Exits 0 when run with `MAX_STEPS=1 DEVICE=cpu`

---

## Results Schema

All test results written to `verification_workspace/cpu_test_results.json`:

```json
{
  "timestamp": "ISO-8601",
  "attempt_number": 1,
  "overall_passed": true,
  "categories": {
    "imports": {"status": "pass", "details": "..."},
    "forward_pass": {"status": "pass", "output_shape": "[2, 10]"},
    "loss_computation": {"status": "pass", "loss_value": 2.3},
    "training_step": {"status": "pass", "losses": [2.3, 2.1, 1.9, 1.7, 1.5]},
    "data_pipeline": {"status": "pass", "batch_shapes": "x=[2,3,32,32]"},
    "script_smoke": {"status": "pass", "script": "scripts/run_table1.py"},
    "reproduce_sh": {"status": "pass", "note": "paperbench_full only"}
  },
  "errors": []
}
```

---

## Failure Handling

When any test fails:

1. Print the full error trace to the console
2. Update `cpu_test_results.json` with `"status": "fail"` and the error message
3. Increment `state.json → cpu_verification_attempts`
4. Identify the failing code location
5. Fix the code (edit the source files)
6. Re-run the full test suite (all 6 categories)

After 3 failed attempts, print:
```
╔══════════════════════════════════════════════════════════╗
║         CPU VERIFICATION — ESCALATION REQUIRED          ║
╠══════════════════════════════════════════════════════════╣
║ 3 verification attempts have failed.                     ║
║                                                          ║
║ Failing tests:                                           ║
║   [list failing categories and errors]                   ║
║                                                          ║
║ Please advise: should I continue debugging, skip a       ║
║ failing test category, or restructure the code?          ║
╚══════════════════════════════════════════════════════════╝
```
