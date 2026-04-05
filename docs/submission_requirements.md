# Submission Requirements for PaperBench

A valid PaperBench submission is a self-contained git repository. The following requirements must be met.

## Mandatory Files

| File | Purpose |
|------|---------|
| `reproduce.sh` | Executable script that reproduces all results |
| `requirements.txt` | Python dependencies (pinned versions preferred) |
| `README.md` | Paper citation, installation, reproduction instructions |

## reproduce.sh Contract

- Must be at the repository root
- Must be executable (`chmod +x`)
- Must start with `#!/usr/bin/env bash`
- Must install dependencies (`pip install -r requirements.txt`)
- Must run all experiments needed to produce results
- Must handle `MAX_STEPS` environment variable for smoke testing
- Must handle `DEVICE` environment variable (default: `cuda`)
- Must exit 0 on success

## Git Requirements

- All files needed for reproduction must be git-tracked
- `git clean -fd` must not remove anything needed
- Repository size should be under 500MB
- No large binary blobs (models, datasets) committed

## Compliance

- No URLs from `blacklist.txt` may appear in any file
- No references to the paper's original code repository
- No absolute paths
- No hardcoded credentials or API keys

## Environment Assumptions

The grading container provides:
- Ubuntu 24.04
- Python 3.11+
- pip
- NVIDIA A10 GPU (optional — code must handle CPU fallback)
- Internet access for `pip install`
- No pre-installed ML libraries (everything via requirements.txt)

## Validation

Run the validator before submission:

```bash
python scripts/validate_submission.py <repo_dir> --blacklist <blacklist.txt>
```

This checks all requirements above and reports issues.
