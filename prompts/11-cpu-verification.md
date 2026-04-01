# Phase 7: CPU Sanity Verification

## Objective

Run a mandatory suite of CPU-only tests to verify that the implementation is correct at small scale. This phase **must not advance** until ALL tests pass. Code that doesn't run on a laptop CPU will score 0 on PaperBench's Execution category.

**This is the most important quality gate in the pipeline.** A working model at small scale on CPU is a strong signal of correctness. A broken model on CPU will never produce correct results on GPU.

---

## Required Inputs

- All of `code_workspace/{paper_short_name}/src/`
- `code_workspace/{paper_short_name}/configs/default.yaml`
- `docs/cpu-verification-protocol.md` — exact test specifications

---

## Required Outputs

- `verification_workspace/cpu_test_scripts/` — one test script per category (6 total)
- `verification_workspace/cpu_test_results.json` — pass/fail per category
- `verification_workspace/shape_checks.log` — output of forward pass tests
- `verification_workspace/loss_curve_checks.log` — loss values over 5 steps

---

## Process

### Step 1: Set up test scripts

Create all 6 test scripts from `docs/cpu-verification-protocol.md`. Adapt them to the specific model and data format in this paper.

Key adaptations needed:
- Import the actual model class (not `MainModel`)
- Use the correct input shape for the paper's model (e.g., image tensors vs. token sequences)
- Use the correct tiny config dimensions (2 layers, small hidden dim)
- Use the correct target format for the paper's loss function

### Step 2: Run all tests

Execute each test script and capture ALL output:

```bash
cd {workspace}/code_workspace/{paper_short_name}
python verification_workspace/cpu_test_scripts/test_imports.py 2>&1 | tee verification_workspace/shape_checks.log
python verification_workspace/cpu_test_scripts/test_forward_pass.py 2>&1 | tee -a verification_workspace/shape_checks.log
python verification_workspace/cpu_test_scripts/test_loss.py 2>&1 | tee -a verification_workspace/shape_checks.log
python verification_workspace/cpu_test_scripts/test_training_step.py 2>&1 | tee verification_workspace/loss_curve_checks.log
python verification_workspace/cpu_test_scripts/test_data_pipeline.py 2>&1 | tee -a verification_workspace/shape_checks.log
python verification_workspace/cpu_test_scripts/test_script_smoke.py 2>&1 | tee -a verification_workspace/shape_checks.log
```

### Step 3: Parse results and update state

After all tests run, write `verification_workspace/cpu_test_results.json`:

```json
{
  "timestamp": "ISO-8601",
  "attempt_number": 1,
  "overall_passed": false,
  "categories": {
    "imports": {"status": "pass|fail", "details": "..."},
    "forward_pass": {"status": "pass|fail", "output_shape": "...", "error": null},
    "loss_computation": {"status": "pass|fail", "loss_value": null, "error": null},
    "training_step": {"status": "pass|fail", "losses": [], "error": null},
    "data_pipeline": {"status": "pass|fail", "batch_shapes": null, "error": null},
    "script_smoke": {"status": "pass|fail", "script": null, "error": null}
  },
  "errors": [],
  "fix_actions": []
}
```

### Step 4: Fix failures (if any)

For each failing test:

1. Read the full error message from the test output
2. Identify the root cause:
   - `ImportError` → missing dependency or typo in import path
   - `AttributeError` → method doesn't exist or wrong class being tested
   - `RuntimeError` → shape mismatch, missing tensor operations
   - `AssertionError` → output shape/value doesn't match expected
3. Fix the source code in `src/`
4. Re-run that specific test to confirm the fix
5. Re-run ALL tests to confirm no regressions

**Critical:** Do not fix the test scripts to hide failures. Fix the source code.

### Step 5: Repeat until all tests pass

Keep cycling through Steps 2-4 until `overall_passed: true`.

After 3 failed attempts (all 6 tests combined), document the failures in `cpu_test_results.json → fix_actions` and escalate to the user.

---

## Adaptation Guide for Different Model Types

### Vision Models (CNNs, ViTs)

```python
# Tiny config
model = MainModel(num_layers=2, hidden_dim=32, patch_size=4, img_size=16)
# Synthetic input
x = torch.randn(2, 3, 16, 16)  # batch=2, C=3, H=16, W=16
# Expected output
# For classification: (batch, num_classes)
# For detection: depends on model
```

### Language Models (Transformers, LSTMs)

```python
# Tiny config
model = MainModel(vocab_size=100, d_model=32, num_layers=2, num_heads=2)
# Synthetic input
x = torch.randint(0, 100, (2, 8))  # batch=2, seq_len=8
# Expected output
# For LM: (batch, seq_len, vocab_size)
# For classification: (batch, num_classes)
```

### Graph Neural Networks

```python
# Tiny config
model = MainModel(in_features=8, hidden_dim=16, num_layers=2, num_classes=5)
# Synthetic input using PyG or DGL
from torch_geometric.data import Data
x = torch.randn(10, 8)   # 10 nodes, 8 features
edge_index = torch.randint(0, 10, (2, 20))  # 20 edges
data = Data(x=x, edge_index=edge_index)
```

### Diffusion Models

```python
# Tiny config
model = MainModel(in_channels=1, model_channels=8, num_res_blocks=1, image_size=8)
# Synthetic input
x = torch.randn(2, 1, 8, 8)   # batch=2, C=1, H=8, W=8
t = torch.randint(0, 1000, (2,))  # timestep
```

---

## Checklist Before Marking Phase Complete

- [ ] All 6 test categories have `status: "pass"` in `cpu_test_results.json`
- [ ] `shape_checks.log` shows correct output shapes
- [ ] `loss_curve_checks.log` shows loss decreasing over 5 steps
- [ ] `state.json → cpu_verification_passed` set to `true`
- [ ] `state.json → gate_results.cpu_verification_gate` set to `"passed"`
- [ ] `implementation_checklist.json` updated: items verified by CPU tests marked "verified"
