# Phase 11: Rubric Audit

## Objective

Walk every rubric item systematically and assess the current state of the replication. Produce a preliminary PaperBench score estimate. Spawn a mini persona council (1 round) to get a prioritized list of quick fixes. This is the "are we done yet?" phase.

---

## Required Inputs

- `analysis_workspace/rubric.json` — complete rubric
- `analysis_workspace/implementation_checklist.json` — current status per item
- All of `code_workspace/{paper_short_name}/`
- `verification_workspace/cpu_test_results.json`
- `analysis_workspace/experiment_manifest.json`

---

## Required Outputs

- `rubric_audit/rubric_gap_report.md` — per-item status
- `rubric_audit/rubric_coverage_final.json` — final coverage counts
- `rubric_audit/paperbench_score_estimate.json` — score estimate with breakdown

---

## Audit Process

### Pass 1: Item-by-item assessment

For every rubric item in `rubric.json`, assess its status:

**For code_development items:**
- Open the `evidence_file` specified in the rubric item (or find the implementing file)
- Check whether the specific criterion is satisfied
- Status: `satisfied` / `partial` / `not_satisfied` / `skipped`
- Evidence: specific file path and line number if satisfied

**For execution items:**
- Check file existence for `file_exists` items
- Run import check for `import_check` items
- Check config contains the value for `value_check` items
- Check smoke test result for `run_check` items

**For result_match items:**
- If the experiment script exists AND passes smoke test: estimate `partial`
- If the code implementing the experiment is correct: estimate `partial`
- If the GPU experiment was actually run (unlikely): check actual number

**Write to `rubric_audit/rubric_gap_report.md`:**

```markdown
# Rubric Audit Report

## Summary
Total items: {N}
Satisfied: {X} ({X/N * 100:.0f}%)
Partial: {Y}
Not satisfied: {Z}
Skipped: {S}

Estimated PaperBench score: {score}% (confidence: {level})

## Code Development ({satisfied}/{total} items)

### model_implementation
| ID | Description | Status | Evidence |
|----|-------------|--------|---------|
| CD-001 | Pre-LayerNorm used | satisfied | src/models/transformer.py:45 |
| CD-002 | 12 encoder layers | satisfied | configs/default.yaml:model.num_layers |
| CD-003 | Hidden dim = 512 | satisfied | configs/default.yaml:model.hidden_dim |
| CD-015 | Causal masking for decoder | NOT SATISFIED | No causal mask in attention.py |

### data_pipeline
...

### training_loop
...

### baselines
...

## Execution ({satisfied}/{total} items)
...

## Result Match ({satisfied}/{total} items)
...

## Top 10 Unmet Items by Weight (Quick Wins)
1. [CD-015, weight=0.15] Causal masking — add 5 lines to attention.py
2. [EX-012, weight=0.10] run_figure5.py missing — create ablation script
...
```

### Pass 2: Scoring computation

Compute the PaperBench score estimate:

```python
# For each category:
# score = sum(weight * satisfaction_score) for items in category
# where satisfaction_score: satisfied=1.0, partial=0.5, not_satisfied=0.0, skipped=0.0

code_dev_score = sum(item.weight * satisfaction_score(item)
                     for item in rubric["code_development"])
execution_score = sum(item.weight * satisfaction_score(item)
                     for item in rubric["execution"])
result_match_score = sum(item.weight * satisfaction_score(item)
                         for item in rubric["result_match"])

# Category weights from paperbench-scoring.md
total = 0.40 * code_dev_score + 0.30 * execution_score + 0.30 * result_match_score
```

Write to `rubric_audit/paperbench_score_estimate.json`:

> **IMPORTANT:** This is an INTERNAL ESTIMATE — not an official PaperBench score. Official scores require the PaperBench LLM judge pipeline. Internal estimates are based on code inspection and CPU tests, not actual execution results.

```json
{
  "timestamp": "ISO-8601",
  "score_estimate": 0.XX,
  "score_type": "INTERNAL_ESTIMATE",
  "confidence": "medium",
  "breakdown": {
    "code_development": {
      "score": 0.XX,
      "satisfied": 0,
      "partial": 0,
      "not_satisfied": 0,
      "total": 0
    },
    "execution": {...},
    "result_match": {...}
  },
  "top_unmet_by_weight": [
    {"id": "CD-015", "weight": 0.15, "description": "...", "fix_effort": "5 minutes"}
  ],
  "quick_wins_potential": 0.XX,
  "note": "Result match score is estimated conservatively (50% of verified code items)"
}
```

### Mini Persona Council (1 round)

Spawn all three personas on the audit results — 1 round each, no debate:

- **Code Architect**: read `rubric_gap_report.md`. What code-level gaps are quickest to fix?
- **Rigor**: read `rubric_gap_report.md`. Any equation-level gaps still open?
- **PaperBench Judge**: read `rubric_gap_report.md`. Top 5 easy wins by rubric score per effort.

Synthesis: produce `rubric_audit/quick_wins_list.md` — ordered list of fixes by (score gain / effort):

```markdown
# Quick Wins — Ordered by Score Impact

1. **[10 min, +2.1%]** Add causal mask to src/models/attention.py (CD-015, weight=0.15)
   Fix: Add `causal_mask = ...` to MultiHeadAttention.forward(), 5 lines

2. **[5 min, +1.5%]** Create scripts/run_figure5.py (EX-012, weight=0.10)
   Fix: Copy run_table1.py template, change experiment config

3. **[5 min, +1.2%]** Add warmup_steps to configs/default.yaml (EX-008, weight=0.08)
   Fix: One line: `warmup_steps: 10000  # paper Appendix B`
```

---

## FIXMORE Loop

If the user responds with FIXMORE at the checkpoint:

1. Read `rubric_audit/quick_wins_list.md`
2. Take the top N quick wins (N = how many the user wants, or all if unspecified)
3. Implement them directly (no subagent needed for simple fixes like adding config values)
4. Re-run the audit (full Pass 1 + Pass 2)
5. Update the score estimate
6. Show the updated score and ask again: "Updated score: X% (was Y%). PROCEED or FIXMORE?"

Maximum 2 FIXMORE cycles.
