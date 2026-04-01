# pAI-Replicator Smoke Test Report
**Paper:** Edge of Stochastic Stability: Revisiting the Edge of Stability for SGD (ICML 2026 under review)
**Date:** 2026-04-01
**Phases run:** 0 (paper decomposition), 1 (PDF ingestion), 2 (rubric), 3 (architecture), 3b (persona council), 4-6 (implementation), 7 (CPU verification)

---

## Overall Verdict: MOSTLY WORKS ✓ — 13 mandatory fixes identified

CPU tests: **ALL 6 CATEGORIES PASS**
Rubric items generated: **72**
Architecture files planned: **54 files**
Persona council: **All 3 personas REJECT** (identified 13 concrete fixes)

---

## Phase-by-Phase Results

### Phase 0 — Paper Decomposition (NEW — not yet run in this test)
- Not run (was added after the smoke test)
- For this paper: would output `decomposition_type: "single"` (all experiments use same SGD + curvature measurement infrastructure)

### Phase 1 — PDF Ingestion ✓
**Works well.** The agent read all 81 pages and extracted:
- 6 model architectures (MLP-2, MLP-4, CNN-5, ResNet-10/14/20)
- Complete Batch Sharpness definition (Definition 1.1)
- All 54 figures inventoried
- 13 ambiguities flagged (useful)

**Issues found:**
1. **MEDIUM** — CNN architecture underspecified in paper (filter sizes, kernel dimensions not given). Agent noted this and flagged it but had to guess. A human reviewer would need to clarify.
2. **MEDIUM** — Number of MC batches K for Batch Sharpness estimation is unspecified. Agent chose K=10 (reasonable but possibly wrong).
3. **LOW** — `pdftotext` and `poppler-utils` not installed on macOS by default. The skill currently fails silently if pymupdf isn't available — should detect this and guide the user to install it.

**Missing in Phase 1 prompt (`05-pdf-ingestion.md`):**
- No instruction to detect and use `anthropic-skills:pdf` skill as fallback for PDF reading
- Should handle the case where PDF extraction yields mostly line numbers (ICML format adds line numbers 000-999) — the current extraction has them but the agent handled it fine

---

### Phase 2 — Rubric Decomposition ✓
**Works well.** Produced 72 rubric items with good coverage.

**Issues found:**
4. **HIGH** — The rubric template has a `result_match` weight of 0.30 but PaperBench's actual category weights are unknown (estimated from the benchmark description). The skill's score estimates will be off if the real weights differ.
5. **MEDIUM** — Rubric items for theory papers are different from code papers. For this paper, many "code_development" items are really "measurement_code" items (compute Batch Sharpness correctly). The rubric prompt doesn't distinguish these. Worked fine in practice, but could be cleaner.
6. **LOW** — Gate 1 minimum of 40 items almost triggers here (72 is fine) but for shorter papers (4-page workshop papers), this gate would reject valid extractions.

---

### Phase 3 — Repository Architecture ✓
**Works well.** Planned 54 files with complete rubric item → file mapping.

**Issues found:**
7. **HIGH** — The architecture plan does not specify a `src/curvature/` directory — this was invented by the agent for this paper's measurement code. The `07-repo-architecture.md` prompt has a fixed standard layout (`src/models/`, `src/data/`, `src/training/`, etc.) that doesn't have a slot for custom measurement infrastructure. The agent correctly deviated from the template, but this deviation should be explicitly allowed in the prompt.
8. **MEDIUM** — The `uncovered_rubric_items` check works, but 9 GPU-only result_match items are listed without suggesting the user confirm the exclusion is acceptable.

---

### Phase 3b — Persona Council ✓
**Works excellently — this is the most valuable phase.** All 3 personas REJECT, identifying 13 concrete mandatory fixes:

| # | Persona | Issue | Severity |
|---|---------|-------|---------|
| 1 | Architect | Noisy-GD covariance dimensionality unresolved (N(mu_w, Sigma_w) over 2M params is impossible) | BLOCKING |
| 2 | Architect | compute_ias() missing from gni.py | BLOCKING |
| 3 | Rigor | MSE normalization convention: `reduction='mean'` divides by b×C, breaking the 2/η threshold | BLOCKING |
| 4 | Rigor | SDE noise amplitude missing sqrt(dt) factor | BLOCKING |
| 5 | Rigor | b=2 MLP λ_b_max experiment uses wrong η (0.02 not 0.01) | BLOCKING |
| 6 | Judge | 13/14 scripts missing `--max-steps` argument | BLOCKER |
| 7 | Judge | No canonical results/{name}_results.json output path | BLOCKER |
| 8 | Judge | compute_ias() missing (RM-021 fails) | BLOCKER |
| 9 | Judge | Figures 31-32 (trace Hessian) have no script | GAP |
| 10 | Judge | Figure 2 η=0.0025 missing from config | GAP |
| 11 | Rigor | LOBPCG warm-restart uses power iteration not true LOBPCG | IMPORTANT |
| 12 | Architect | Results/ output path not canonically enforced | IMPORTANT |
| 13 | Architect | HVP `.detach()` boundary for vector v needs explicit guard | IMPORTANT |

**Skill design note:** The council correctly caught issues #3 (MSE normalization), #4 (SDE sqrt(dt)), and #5 (wrong η) which are subtle mathematical bugs that would cause wrong results silently. The personas are well-calibrated.

---

### Phases 4-6 — Core Implementation ✓
**Works well.** All 18 source files created and syntax-valid.

**Issues found:**
9. **MEDIUM** — The implementation agent invented `tiny_config()` classmethods (good!) but the prompt in `08-core-algorithm.md` doesn't require this name specifically. Different agents will use different naming conventions (e.g., `make_tiny()`, `small_config()`), which breaks the CPU test scripts that call `model.tiny_config()`.
10. **MEDIUM** — The `scripts/` directory was left empty. Phase 9 creates scripts, but Phase 7 (CPU verification) tries to smoke-test a script and falls back to an inline test when scripts/ is empty. This fallback works but the `test_script_smoke.py` test becomes a weaker test.
11. **LOW** — Config file (`configs/default.yaml`) hardcodes `mc_batches: 10` for the unknown K parameter. The agent notes it's unspecified in the paper, but there's no mechanism to surface this ambiguity to the user at Phase 6 checkpoint.

---

### Phase 7 — CPU Verification ✓ (ALL 6 PASS)
**This is the strongest phase — works exactly as designed.**

**Issues found:**
12. **HIGH** — The 5-step overfit test DIVERGES at the paper's actual step size η=0.1 with batch_size=2 (tiny config). The agent correctly reduced η to 0.01 for the test but did NOT change the source code. This means the source code has η=0.1 as default, but the CPU test uses η=0.01. The gate passes but the source code is not validated at the paper's actual η.
    - **Root cause:** At initialization, sharpness ≈ 350 >> 2/0.1 = 20. The paper's experiments start from a point where sharpness is already near the EOSS regime. You can't replicate the paper's η on random tiny data.
    - **Fix needed:** The CPU test should use a smaller model AND validate stability at init, not convergence to lower loss.
13. **LOW** — `test_script_smoke.py` passes trivially because scripts/ is empty. It runs an inline SGDTrainer test instead. The test should explicitly warn when no scripts are found.

---

## Skill Design Issues (Not Paper-Specific)

### Issue A — No fallback for PDF extraction failure
**Severity: HIGH**
The skill calls `python3 -c "import fitz ..."` but has no fallback if pymupdf isn't installed. The `anthropic-skills:pdf` skill is available and would handle this. The SKILL.md startup should detect pymupdf availability and use the pdf skill as fallback.

**Fix:** Add to SKILL.md startup:
```python
try:
    import fitz
    # use pymupdf
except ImportError:
    # invoke Skill("pdf") to extract text
```

### Issue B — No multi-repo decomposition (NOW FIXED)
**Severity: HIGH**
The original skill had no Phase 0 and no loop over sub-repos. A paper like BERT (pretraining + finetuning + downstream tasks) would have been lumped into one repo, producing a mess.

**Status: FIXED** — Phase 0 (`prompts/00-paper-decomposition.md`) and the multi-repo loop in SKILL.md were added in this session.

### Issue C — Standard layout doesn't accommodate measurement infrastructure
**Severity: MEDIUM**
The standard repo layout in `07-repo-architecture.md` doesn't have a slot for custom modules like `src/curvature/`. Papers that have custom measurement or utility code (very common in empirical ML papers) will either be shoehorned into `src/utils/` or the agent will invent its own directory (which it did correctly here but inconsistently).

**Fix:** Add a `src/custom/` or `src/contrib/` directory to the standard layout, or add a note saying "add domain-specific directories as needed (e.g., src/curvature/, src/metrics/, src/probes/)".

### Issue D — Persona council runs sequentially, not in parallel
**Severity: MEDIUM**
The SKILL.md says "All three can run in parallel (parallel Agent tool calls)" but this is aspirational — Claude Code's orchestrator runs one agent at a time by default. In this smoke test, personas ran sequentially. Parallel execution would cut Phase 3b time by ~3x.

**Fix:** The SKILL.md orchestrator would need to explicitly spawn all 3 persona agents in a single message with multiple `Agent` tool calls.

### Issue E — No paper-type detection
**Severity: MEDIUM**
The skill treats all papers identically. But the optimal strategy differs significantly:
- **Theory paper with light experiments** (like EOSS): measurement code is central; focus rubric on curvature computation, less on model diversity
- **Architecture paper** (like ViT): model implementation is central; focus rubric on architecture fidelity
- **Methods/optimizer paper**: training loop is central
- **Benchmark paper**: experiment scripts are central; may need multi-repo

**Fix:** Add a `paper_type` field to paper_analysis.json and have Phase 2 (rubric) adjust weightings based on paper type.

### Issue F — The `tiny_config()` naming is not enforced
**Severity: LOW**
Phase 4 prompt asks for "tiny_config() or equivalent" but different agents name it differently. Phase 7 test scripts need to call it, creating fragility.

**Fix:** Standardize the convention in `08-core-algorithm.md`: "Every model class MUST have a class method named exactly `tiny_config()` that returns a minimal model instance for CPU testing."

### Issue G — Ambiguities from Phase 1 are not fed back to user before Phase 2
**Severity: MEDIUM**
Phase 1 produces an `ambiguities` field in `paper_analysis.json`. Phase 2 checkpoint doesn't explicitly surface these ambiguities to the user. Critical ambiguities (like the CNN architecture spec or K for MC Batch Sharpness) get silently filled with agent guesses.

**Fix:** Phase 1 checkpoint should explicitly list all HIGH-impact ambiguities and ask the user to resolve them before proceeding to Phase 2.

---

## Summary of Required Fixes

### Blocking (will cause wrong results or broken pipeline):
- [ ] Fix Phase 1 checkpoint to surface HIGH-impact ambiguities
- [ ] Phase 0 prompt now created — integrate into startup flow
- [ ] Ensure `tiny_config()` naming is standardized in Phase 4 prompt

### Important (reduce PaperBench score significantly):
- [ ] Add `src/curvature/`-style domain directories to standard layout in `07-repo-architecture.md`
- [ ] Add paper-type detection to Phase 1 and adjust Phase 2 rubric weightings
- [ ] CPU verification should test at a stable η, not paper's η — clarify this in test design
- [ ] Phase 1 needs PDF extraction fallback to `anthropic-skills:pdf`

### Minor:
- [ ] Gate 1 threshold of 40 items is too aggressive for short papers
- [ ] Phase 7 smoke test should warn explicitly when scripts/ is empty
- [ ] results/{name}_results.json path should be enforced in Phase 9 template

---

## What Works Well (Keep As-Is)

- **Persona council is excellent** — caught subtle bugs (MSE normalization, SDE factor, wrong η) that would silently produce wrong results. Keep 3-round minimum.
- **CPU verification gate is the right design** — hard blocking, all 6 categories actually ran, loop to fix is correct
- **Multi-pass with RESUME pattern works** — Phase 1 naturally does multiple passes; RESUME pattern prevents redundant work
- **Paper analysis depth is good** — 81-page paper fully extracted in one agent call; 54-figure inventory produced
- **State machine + workspace layout** — clean separation, easy to resume
- **Paper citation in every function** — the Phase 4 prompt enforces this correctly; all generated code had `# Section 3.2, Equation 1` comments
