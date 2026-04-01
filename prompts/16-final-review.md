# Phase 12: Final Quality Review

## Objective

Perform a final holistic review of the replication. Re-run all CPU tests to confirm nothing broke. Produce a final PaperBench score estimate. Generate a comprehensive final summary report for the user.

---

## Required Inputs

- All of `code_workspace/{paper_short_name}/`
- `rubric_audit/paperbench_score_estimate.json`
- `verification_workspace/cpu_test_results.json`
- `analysis_workspace/final_summary.md` (if exists)

---

## Required Outputs

- Re-run confirmation: all CPU tests still pass
- Updated `rubric_audit/paperbench_score_estimate.json` (final)
- `analysis_workspace/final_summary.md`
- Final `code_workspace/{paper_short_name}/README.md` (last update)

---

## Process

### Step 1: Re-run all CPU tests

Run all 6 CPU test categories (same as Phase 7) to confirm nothing broke during later phases:

```bash
cd {workspace}/code_workspace/{paper_short_name}
python tests/test_imports.py
python tests/test_forward_pass.py
python tests/test_loss.py
python tests/test_training_step.py
python tests/test_data_pipeline.py
python tests/test_script_smoke.py
```

If any test now fails that previously passed: fix it before proceeding.

### Step 2: Compute final score estimate

Load `rubric_audit/paperbench_score_estimate.json` from Phase 11.
Verify the score is based on the latest state of the code (re-audit any items changed in FIXMORE cycles or Phase 10).

Update with final scores and write:

```json
{
  "is_final": true,
  "timestamp": "ISO-8601",
  "score_estimate": 0.XX,
  "confidence": "medium",
  "breakdown": {
    "code_development": {"score": 0.XX, "satisfied": N, "total": M},
    "execution": {"score": 0.XX, "satisfied": N, "total": M},
    "result_match": {"score": 0.XX, "satisfied": N, "total": M}
  },
  "cpu_tests_rerun": true,
  "cpu_tests_passed": 6,
  "top_remaining_gaps": [
    {"id": "RM-001", "description": "Main results require GPU to verify", "effort": "GPU run required"}
  ],
  "what_would_improve_score": [
    "Run full GPU training to verify result_match items (+{X}% if results match)",
    "Add causal masking in attention.py (+{Y}%)",
    "Create missing script for Figure 5 (+{Z}%)"
  ]
}
```

### Step 3: Write final summary

`analysis_workspace/final_summary.md`:

```markdown
# Replication Summary: {Paper Title}

**Paper:** {title} ({venue} {year})
**Estimated PaperBench Score:** {score}% (confidence: {level})

---

## What Was Accomplished

- **Repository created:** `code_workspace/{name}/` ({N} files, {LOC} lines of code)
- **Core model implemented:** {model name} with {N} components
- **Datasets:** {list of datasets, with implementation status}
- **Baselines implemented:** {N}/{total} baselines ({exclusion_count} excluded with justification)
- **Experiment scripts:** {N} scripts covering {M} tables and {K} figures
- **CPU verification:** All 6 test categories pass on CPU

## Score Breakdown

| Category | Score | Items |
|---------|-------|-------|
| Code Development | {X}% | {satisfied}/{total} items |
| Execution | {X}% | {satisfied}/{total} items |
| Result Match | {X}% | {satisfied}/{total} items (estimated) |
| **Total** | **{X}%** | |

## Main Remaining Gaps

These items would most improve the score if addressed:

1. {gap 1} — fix: {specific action}
2. {gap 2} — fix: {specific action}
3. {gap 3} — fix: {specific action}

## How to Run Full Experiments

The CPU smoke tests pass, but full training requires GPU:

```bash
# Full training (Table 1 main results)
# Requirements: {N} x {GPU model}, ~{X} hours
python scripts/run_table1.py --config configs/experiment_table1.yaml

# See README.md for complete instructions
```

## Files Produced

```
code_workspace/{name}/
{full directory tree here}
```
```

### Step 4: Final Gate 3 check

Read `paperbench_score_estimate.json → score_estimate`:
- `< 0.20` (< 20%): Trigger one more FIXMORE loop (Phase 11) then force-pass
- `>= 0.20` (≥ 20%): PASS — proceed to completion

### Step 5: Final README update

Update `README.md` with any improvements made in this phase. Ensure the reproduction commands are accurate.

---

## Completion Banner

When all steps pass, print:

```
╔══════════════════════════════════════════════════════════════════════╗
║              pAI-REPLICATOR — REPLICATION COMPLETE                 ║
╠══════════════════════════════════════════════════════════════════════╣
║                                                                      ║
║  Paper: {title} ({venue} {year})                                    ║
║                                                                      ║
║  Estimated PaperBench Score: {score}%                               ║
║    Code Development: {cd_score}%  ({cd_satisfied}/{cd_total} items) ║
║    Execution:        {ex_score}%  ({ex_satisfied}/{ex_total} items) ║
║    Result Match:     {rm_score}%  ({rm_satisfied}/{rm_total} items) ║
║    (estimated — result_match requires GPU runs to fully verify)     ║
║                                                                      ║
║  Repository: {workspace}/code_workspace/{name}/                     ║
║  Files created: {N} files, {LOC} lines of code                     ║
║  CPU tests: ALL 6 CATEGORIES PASS ✓                                ║
║                                                                      ║
║  Top improvements if you continue manually:                         ║
║    1. {improvement_1} (+{X}%)                                       ║
║    2. {improvement_2} (+{Y}%)                                       ║
║    3. {improvement_3} (+{Z}%)                                       ║
║                                                                      ║
║  See analysis_workspace/final_summary.md for full details.          ║
╚══════════════════════════════════════════════════════════════════════╝

Type DONE to finish, or CONTINUE to attempt more improvements.
```
