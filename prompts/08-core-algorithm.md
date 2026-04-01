# Phase 4: Core Algorithm Implementation

## Objective

Implement the paper's core model architectures, loss functions, and key algorithms. This is the most mathematically intensive phase. Every function must be traceable to the paper section or equation it implements.

**Quality bar:** A PaperBench evaluator reading your code should be able to verify each class/function against the corresponding paper equation without ambiguity.

---

## Required Inputs

- `analysis_workspace/paper_analysis.json` — architecture details, algorithms, loss functions
- `analysis_workspace/architecture_plan.json` — which files to create and what they implement
- `persona_workspace/council_synthesis.md` — mandatory fixes from persona council
- `analysis_workspace/implementation_checklist.json` — what to implement and in what priority
- `analysis_workspace/rubric.json` — which CD items need to be satisfied

---

## Required Outputs

All in `code_workspace/{paper_short_name}/`:

- `src/models/` — all model classes
- `src/losses/` — all loss functions
- `src/utils/` — shared utilities (metrics, tensor ops, logging)

Updated `analysis_workspace/implementation_checklist.json` — mark all covered code_development/model_implementation and training_loop items as "implemented".

---

## Implementation Standards

### Standard 1: Paper Citation in Every Function

Every class and function that implements a paper component must have a docstring citing the exact paper location:

```python
class MultiHeadAttention(nn.Module):
    """Multi-head self-attention from Section 3.2, Equation 1-3.

    Implements the standard scaled dot-product attention with learned
    query, key, value projections and output projection.

    Args:
        d_model: Model dimension (paper: d_model=512)
        num_heads: Number of attention heads (paper: h=8)
        dropout: Attention dropout rate (paper: 0.1, Appendix B)

    Reference: Section 3.2, Figure 2, Equations 1-3.
    """
```

### Standard 2: Hyperparameters as Arguments (Never Hardcoded)

Every hyperparameter from the paper must be a function argument with its paper default as a Python default value:

```python
def __init__(
    self,
    d_model: int = 512,      # paper: Table 3, d_model=512
    num_heads: int = 8,       # paper: Table 3, h=8
    dropout: float = 0.1,     # paper: Appendix B
    use_pre_norm: bool = True  # paper: Figure 2 shows pre-norm
):
```

### Standard 3: Explicit Shape Comments

For every tensor operation, comment the shape:

```python
# Q: (batch, seq_len, d_k), K: (batch, seq_len, d_k), V: (batch, seq_len, d_v)
scores = torch.matmul(Q, K.transpose(-2, -1))  # (batch, seq_len, seq_len)
scores = scores / math.sqrt(self.d_k)          # scaled, per Eq. 1
```

### Standard 4: CPU-Compatible By Default

All model code must run on CPU out of the box:
- No `.cuda()` calls in model files
- Device should be passed as argument or derived from input tensors
- No hardcoded `torch.cuda.*` calls

### Standard 5: Tiny Config Support

Every model class must support tiny configurations for CPU testing. Add a class method or separate config:

```python
@classmethod
def tiny_config(cls):
    """Returns a tiny model config for CPU testing."""
    return cls(
        d_model=32,
        num_heads=2,
        num_layers=2,
        ffn_dim=64
    )
```

---

## Implementation Process

### Pass 1: Core model architecture

1. Read `paper_analysis.json → model_architecture.components` for every component
2. Read `architecture_plan.json → files` to find which files to create
3. Implement each model component in its designated file
4. Start with leaf components (attention, FFN, normalization) before composing them

**Order of implementation:**
1. Utility functions (softmax, layer norm, etc.)
2. Atomic components (attention head, feed-forward block)
3. Composed components (transformer layer, encoder block)
4. Full model (stacks components)
5. Model variants (if paper describes multiple variants)

### Pass 2: Loss functions and training utilities

1. Read `paper_analysis.json → loss_function` for the complete loss specification
2. Implement `src/losses/` — main loss and all auxiliary losses
3. Implement `src/utils/metrics.py` — all evaluation metrics from the paper
4. Implement `src/utils/checkpointing.py` — standard checkpoint save/load

### Pass 3+: Review and gap-filling

1. Re-read `persona_workspace/council_synthesis.md` — implement all mandatory fixes
2. Re-read `paper_analysis.json → algorithms` — verify each algorithm step is implemented
3. Run a mental test: can you trace from every equation in the paper to a line of code?
4. Update `implementation_checklist.json` for all items now implemented

---

## Common Implementation Traps

**Normalization order:** Pre-LayerNorm (LN before sublayer) vs. post-LayerNorm (LN after sublayer) is often a critical detail. Check the paper figure or description carefully. PyTorch's `nn.TransformerEncoderLayer` uses post-norm by default.

**Attention scaling:** The scaling factor is `1/sqrt(d_k)`, not `1/sqrt(d_model)` if d_k != d_model.

**Causal masking:** Decoder-only models require a causal (autoregressive) mask. The mask must prevent attending to future positions. Ensure `attn_mask` is correctly passed.

**Positional encoding:** Learned vs. sinusoidal vs. rotary vs. ALiBi — the paper will specify. Default implementations often use sinusoidal; many modern papers use rotary.

**Batch normalization in eval mode:** Call `model.eval()` during evaluation. BatchNorm, Dropout, and LayerNorm (if using `training=True/False` variants) all behave differently.

**Weight initialization:** The paper may specify initialization (Xavier, Kaiming, truncated normal). PyTorch defaults may differ. Check the paper's experimental setup or appendix.

**Gradient checkpointing:** If the paper mentions memory efficiency, they may use gradient checkpointing. This affects the forward pass structure.

---

## After This Phase

Before marking complete:
- [ ] All files in `src/models/` and `src/losses/` exist and are non-empty
- [ ] Every file has docstrings with paper citations
- [ ] No hardcoded hyperparameter values (all are function arguments)
- [ ] `tiny_config()` or equivalent exists for at least the main model class
- [ ] `implementation_checklist.json` updated for all implemented items
- [ ] No `.cuda()` calls in any `src/` file
