# Checkpoint Protocol — pAI-Replicator

## Overview

Every phase in pAI-Replicator ends with a mandatory user checkpoint. The orchestrator prints a structured summary, asks a phase-specific question, and waits for the user's response before advancing.

**Why so many checkpoints?** Paper replication requires domain knowledge about the specific paper. The user who provided the PDF often knows things that are not explicitly stated in the paper. Frequent checkpoints catch misunderstandings before they propagate through 5+ implementation phases.

---

## Standard Checkpoint Format

```
╔══════════════════════════════════════════════════════════════════╗
║  [CHECKPOINT] Phase {N}/12: {phase_name}                        ║
╠══════════════════════════════════════════════════════════════════╣
║ Status: COMPLETE                                                  ║
║ Files produced: {count}                                           ║
║ Rubric coverage: {items_covered}/{total_items} items             ║
║ CPU tests: {passed/not_run/N_of_M_passed}                        ║
╠══════════════════════════════════════════════════════════════════╣
║ SUMMARY                                                           ║
║ {phase-specific summary — see below for each phase}              ║
╠══════════════════════════════════════════════════════════════════╣
║ QUESTION                                                          ║
║ {phase-specific question — see below}                            ║
║                                                                  ║
║ Type PROCEED to continue, or describe any issues/corrections.    ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## Per-Phase Checkpoint Content

### Phase 1 — PDF Ingestion

**Summary to print:**
- Paper title, venue, year
- Table: extracted sections (model architecture ✓/✗, hyperparameters ✓/✗, datasets ✓/✗, metrics ✓/✗, baselines ✓/✗, ablations ✓/✗, pseudocode ✓/✗)
- Number of tables/figures inventoried
- Any sections flagged as potentially incomplete

**Question:** "Does this look like a complete extraction? Are there any sections I should re-read more carefully, or any important implementation details that were missed?"

---

### Phase 2 — Rubric Decomposition

**Summary to print:**
- Total rubric items: N
- Breakdown: Code Development (X items), Execution (Y items), Result Match (Z items)
- Top 5 highest-weight rubric items
- Any items flagged as "hard" difficulty

**Question:** "Does this rubric capture all the paper's implementation claims? Any important experiments or results that are missing from the rubric?"

---

### Phase 3 — Repository Architecture

**Summary to print:**
- Planned file tree (full tree, all files)
- Rubric coverage table: which rubric items map to which files
- Any rubric items with no assigned file (highlighted)

**Question:** "Does this architecture look right for the paper? Any files missing? Any items you know won't be coverable?"

---

### Phase 3b — Persona Council

**Summary to print:**
- Rounds completed
- Final verdicts: Code Architect (ACCEPT/REJECT), Rigor (ACCEPT/REJECT), Judge (ACCEPT/REJECT)
- Mandatory fixes list
- Any unresolved concerns

**Question:** "Do you want to proceed with this plan, or would you like to override any of the council's decisions?"

---

### Phase 4 — Core Algorithm

**Summary to print:**
- List of implemented files with line counts
- Key model components (class names, brief description)
- Rubric items in code_development/model_implementation now marked "implemented" (X/total)
- Any equations from the paper that required interpretation

**Question:** "Core algorithm implementation is complete. Please review the key model and loss files. Any implementation choices that look wrong to you?"

---

### Phase 5 — Data Pipeline

**Summary to print:**
- Table: dataset name → implementation status (implemented/excluded) → reason if excluded
- Data transforms implemented
- Config files created

**Question:** "All datasets have been addressed. Any datasets with proprietary access requirements I should handle differently, or any preprocessing steps I may have missed?"

---

### Phase 6 — Training Infrastructure

**Summary to print:**
- Optimizer and key hyperparameters (show the values from paper vs. what's in config)
- LR schedule
- Training loop structure (epochs vs. steps, gradient accumulation, etc.)
- Evaluation frequency and metrics

**Question:** "Does this training configuration match what the paper describes? Any training tricks or details I may have overlooked?"

---

### Phase 7 — CPU Verification

**Summary to print:**
- Full test output (ALL stdout/stderr from every test script)
- Pass/fail per category with error messages for failures

**Question:** "X/6 test categories passed. [If all pass:] PROCEED to continue. [If failures:] Type RETRY to fix and re-run, or describe what I should focus on."

---

### Phase 8 — Baseline Implementations

**Summary to print:**
- Table: baseline name → paper table/figure → implementation status → exclusion reason
- Any baselines that were excluded

**Question:** "These are all the baselines I found in the paper. Any that should be added or removed? Any baseline implementations that you know are handled differently in practice?"

---

### Phase 9 — Experiment Scripts

**Summary to print:**
- Table: script → paper table/figure → requires_gpu → estimated_runtime
- Any tables/figures without a script (highlighted)

**Question:** "Scripts created for all tables and figures. Note that GPU-required scripts are marked in the manifest but cannot be run here. Any issues with the script design or missing experiments?"

---

### Phase 10 — Documentation

**Summary to print:**
- README sections outline
- requirements.txt (full content, brief)
- Any result claims in the README that couldn't be fully verified

**Question:** "Does the README correctly describe how to reproduce all results? Any installation steps or dataset setup instructions that need updating?"

---

### Phase 11 — Rubric Audit

**Summary to print:**
- Coverage table by category: Code Development (X/M), Execution (X/M), Result Match (X/M)
- Preliminary PaperBench score estimate with confidence
- Top 10 unmet items by weight (specific, actionable)
- Items that are "skipped" with reasons

**Question:** "Estimated PaperBench score: X%. Top 10 unmet items shown above. Type PROCEED to go to final review, or FIXMORE to implement the top missing items (up to 2 FIXMORE cycles allowed)."

---

### Phase 12 — Final Review

**Summary to print:**
- Final PaperBench score estimate with per-category breakdown
- CPU test results (re-run confirmation: all still pass)
- Repository stats: total files, total LOC, baselines implemented, experiment scripts
- Top 5 improvements that would most boost the score

**Question:** "Replication complete. Final estimated PaperBench score: X%. All artifacts are in code_workspace/. Type DONE to finish, or CONTINUE to attempt more improvements."

---

## Handling Non-PROCEED Responses

When the user does not type PROCEED (or the equivalent positive response):

1. Parse the user's response for corrections, additions, or override instructions
2. Record the full response in `state.json → user_checkpoints` with `{phase, question, response, timestamp}`
3. Re-spawn the current phase as a new pass with the user's feedback injected:

```
USER FEEDBACK RECEIVED AT CHECKPOINT:
{user_response}

Please address the above feedback before completing this phase.
Specifically: {interpreted_instruction}
```

4. After the re-spawn, show a brief "Here's what changed" summary and re-ask the checkpoint question.

---

## Recording Checkpoints in State

```json
{
  "user_checkpoints": [
    {
      "phase": "pdf_ingestion",
      "pass": 2,
      "question": "Does this look like a complete extraction?",
      "response": "PROCEED",
      "timestamp": "2025-01-15T14:32:00Z"
    }
  ]
}
```
