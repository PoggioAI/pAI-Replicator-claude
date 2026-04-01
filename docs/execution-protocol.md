# Execution Protocol — pAI-Replicator

## Pass Limits Per Phase

| Phase | Min Passes | Max Passes | Rationale |
|-------|-----------|-----------|-----------|
| pdf_ingestion | 2 | 5 | PDFs are complex; tables/figures need multiple extraction passes |
| rubric_decomposition | 2 | 4 | Cross-checking rubric against paper tables/figures needs refinement |
| repo_architecture | 2 | 3 | File tree design improves with review pass |
| persona_council | 1 | 1 | 3–5 internal debate rounds handle iteration |
| core_algorithm | 3 | unbounded | Implementation quality is critical; iterate until stable |
| data_pipeline | 2 | 4 | Dataset edge cases emerge on second pass |
| training_infrastructure | 2 | 4 | Training loop correctness needs careful verification |
| cpu_verification | 2 | unbounded | Must loop until ALL tests pass; no cap |
| baseline_implementation | 2 | 4 | Baseline correctness needs verification pass |
| experiment_scripts | 2 | 3 | Scripts need review for correctness and completeness |
| documentation | 2 | 3 | README quality improves with second pass |
| rubric_audit | 2 | 4 | Gap identification deepens with multiple passes |
| final_review | 1 | 2 | Final assessment; one revision pass if needed |

**Stall detection for unbounded phases:** If the set of artifacts produced in pass N is identical to pass N-1 (same file sizes, same checksums), mark the phase as stalled and exit the pass loop. Log a stall warning to `logs/stall_warnings.json`.

---

## RESUME Prompt Template

Every phase invocation after pass 1 must prepend this block to the phase prompt:

```
RESUME (pass {N}/{max_or_"unbounded"}): You are continuing work on the {phase_name} phase.

Previous pass artifacts are already in the workspace at: {workspace_path}

IMPORTANT: Do NOT restart from scratch. Do NOT re-execute the Process steps
from the beginning. Instead:

1. READ all artifacts you produced in previous passes (they are already on disk)
2. CHECK completeness: are all required outputs present? Are they thorough?
3. If INCOMPLETE: identify exactly what is missing and produce ONLY that.
   Do not regenerate content that already exists and is good.
4. If COMPLETE but improvable: make targeted improvements. Do not rewrite
   from scratch — edit specific sections that need strengthening.
5. SAVE updated artifacts. When refining, preserve the existing structure;
   append or patch specific sections rather than overwriting the whole file.

SKIP any Process steps from the prompt below that you already completed in
previous passes. Go directly to what needs work.

Required outputs for this phase:
{list_of_required_artifacts}

Current pass: {N}
```

---

## Output Validation

After every phase subagent call, the orchestrator must verify that all required output files exist and are non-empty before advancing. If any required file is missing or empty:

1. Increment the pass counter
2. Re-spawn the subagent with the RESUME template
3. If max passes reached AND files still missing: log a warning to `logs/phase_warnings.json` and advance with a `phase_status: "incomplete"` flag in `state.json`

### Validation Script Pattern

```bash
python3 -c "
import json, os, sys

workspace = sys.argv[1]
phase = sys.argv[2]
required_files = sys.argv[3:]

missing = []
empty = []
for f in required_files:
    path = os.path.join(workspace, f)
    if not os.path.exists(path):
        missing.append(f)
    elif os.path.getsize(path) == 0:
        empty.append(f)

result = {
    'phase': phase,
    'missing': missing,
    'empty': empty,
    'valid': len(missing) == 0 and len(empty) == 0
}
print(json.dumps(result))
" {workspace} {phase} {file1} {file2} ...
```

---

## Context Block Injection

Every subagent call must include a context block prepended to the phase prompt. The context block has this format:

```
=== pAI-REPLICATOR CONTEXT ===
Replication ID: {replication_id}
Paper: {paper_title} ({paper_venue})
Workspace: {workspace}
Current Phase: {phase_name} (pass {N})
Completed Phases: {comma-separated list}
Rubric Items: {rubric_items_covered}/{rubric_item_count} covered so far
CPU Verification: {passed/not_yet_run/failed_N_times}
PaperBench Score Estimate: {score or "not yet computed"}

State file: {workspace}/state.json
Paper analysis: {workspace}/analysis_workspace/paper_analysis.json
Rubric: {workspace}/analysis_workspace/rubric.json
Architecture plan: {workspace}/analysis_workspace/architecture_plan.json
Implementation checklist: {workspace}/analysis_workspace/implementation_checklist.json
=== END CONTEXT ===
```

---

## Logging

After every subagent call, run the token-logging script (see `docs/token-logging.md`).

After every 5 phases, write an orchestrator context summary:

```python
summary = {
    "timestamp": datetime.now().isoformat(),
    "current_phase": state["current_phase"],
    "completed_phases": state["completed_phases"],
    "rubric_coverage": f"{state['rubric_items_covered']}/{state['rubric_item_count']}",
    "cpu_verification": state["cpu_verification_passed"],
    "gate_results": state["gate_results"],
    "last_checkpoint_response": state["user_checkpoints"][-1] if state["user_checkpoints"] else None
}
# Write to: {workspace}/analysis_workspace/orchestrator_context_summary.json
```
