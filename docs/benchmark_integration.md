# PaperBench Integration Guide

## Prerequisites

- A PaperBench paper bundle (from the official benchmark)
- Claude Code with pAI-Replicator skill installed

## Running in PaperBench Full Mode

### 1. Extract the paper bundle

PaperBench bundles are directories containing:
```
paper_id/
  paper.pdf
  paper.md
  addendum.md
  rubric.json
  blacklist.txt
  config.yaml
  assets/         (optional)
  judge.addendum.md  (optional)
```

### 2. Start replication

```
/pAI-Replicator
```

Select mode **[3] PaperBench Full**.

Provide the bundle directory path when asked.

### 3. Pipeline runs autonomously

The skill runs phases 0-13 without user checkpoints. Quality gates still fire:
- Gate 1 (rubric coverage): automatic retry if insufficient
- Gate 2 (CPU verification): hard block — fixes and retries automatically up to 3 times
- Gate 3 (score threshold): automatic restart from Phase 1 if score < 20%

### 4. Collect submission

After completion, the submission is at:
```
{WORKSPACE}/submission/
```

This directory is a self-contained git repo with `reproduce.sh` at root.

## Direct Submission Grading

To grade the submission outside of PaperBench's agent rollout pipeline:

```bash
# Validate the submission
python scripts/validate_submission.py {WORKSPACE}/submission/ --blacklist {WORKSPACE}/input/blacklist.txt

# Optional: test reproduction locally with Docker
./scripts/run_local_reproduce_check.sh {WORKSPACE}/submission/ --smoke

# Export for direct grading (if not already done by the skill)
python scripts/export_direct_submission.py {WORKSPACE}/code_workspace/{name}/ {output_dir}/
```

## Code-Dev Mode

For faster iteration (code quality only, no execution grading):

Select mode **[2] PaperBench Code-Dev**. Same bundle input, same autonomous execution, but no `reproduce.sh` generation or submission packaging.

## Limitations

- **No official grading**: We cannot run the PaperBench LLM judge locally. Submissions must be graded through the official pipeline.
- **No fresh-container testing**: The skill runs in the user's environment. Use `run_local_reproduce_check.sh` for Docker-based validation.
- **Internal scores are estimates**: Based on code inspection, not actual execution. They correlate with but do not equal official PaperBench scores.
- **GPU training not performed**: The skill generates scripts but does not run full training. Result-match items are estimated conservatively.
