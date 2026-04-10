# pAI-Replicator

A Claude Code skill for replicating ML papers. Three modes: interactive PDF replication, autonomous PaperBench Code-Dev, and full PaperBench submission with `reproduce.sh`.

## Install

```bash
npx skills add PoggioAI/pAI-Replicator-claude
```

---

## Modes

| Mode | Input | Autonomy | Output |
|------|-------|----------|--------|
| **[1] Interactive (PDF)** | Paper PDF | Checkpoint every phase | Code repo (no submission) |
| **[2] PaperBench Code-Dev** | PaperBench bundle | Fully autonomous | Code repo (no reproduce.sh) |
| **[3] PaperBench Full** | PaperBench bundle | Fully autonomous | Submission-ready git repo |

**Interactive** is for human-guided replication of any ML paper from a PDF. You approve each phase before the pipeline advances.

**Code-Dev** ingests a PaperBench bundle (paper.md, rubric.json, addendum, blacklist) and runs the full pipeline autonomously. No `reproduce.sh` generation — targets PaperBench's code-only grading variant.

**Full** does everything Code-Dev does, plus generates `reproduce.sh`, validates the submission against PaperBench requirements, and exports a self-contained git repo ready for the official evaluation pipeline.

---

## Quick Start

```
/pAI-Replicator
```

The skill prompts for mode selection and input path, then runs the pipeline.

### Interactive mode

```
Replicate this paper: /path/to/paper.pdf
```

### PaperBench modes

Provide a PaperBench bundle directory:
```
/pAI-Replicator
# Select mode [2] or [3]
# Provide bundle path: /path/to/paper_id/
```

Bundle format (from official PaperBench):
```
paper_id/
  paper.pdf
  paper.md
  addendum.md
  rubric.json
  blacklist.txt
  config.yaml
  assets/         (optional)
```

### Resume

```
/pAI-Replicator
# Select "Resume"
# Provide workspace path
```

---

## Pipeline (13 Phases)

| # | Phase | What happens |
|---|-------|-------------|
| 0.5 | Bundle Ingestion | Parse PaperBench bundle (modes 2-3 only) |
| 1 | PDF Ingestion | Deep extraction from paper PDF (mode 1 only) |
| 2 | Rubric Decomposition | Build/import PaperBench-style rubric |
| 3 | Repository Architecture | Design file structure mapped to rubric |
| 4 | Persona Council | Three reviewers debate the plan |
| 5 | Core Algorithm | Models, losses, key algorithms |
| 6 | Data Pipeline | Data loading with mock-data CPU support |
| 7 | Training Infrastructure | Training loop, optimizer, evaluation |
| 8 | CPU Verification | **Hard gate** — all 6-7 test categories must pass |
| 9 | Baselines | Comparison methods from paper tables |
| 10 | Experiment Scripts | One script per table/figure |
| 11 | Documentation | README, configs, reproduction instructions |
| 12 | Rubric Audit | Coverage assessment + score estimate |
| 13 | Final Review | Re-run tests, final score, submission packaging (mode 3) |

**Quality gates:**
- Gate 1: Rubric coverage must be sufficient (auto-retry)
- Gate 2: CPU verification — hard block, 3 auto-retries then escalate
- Gate 3: Score < 20% triggers restart from Phase 1 with gap context

---

## What Gets Produced

```
replication_{timestamp}/
  input/                        # Paper PDF or bundle files
  analysis_workspace/
    paper_analysis.json         # Structured extraction
    rubric.json                 # Rubric (generated or imported from bundle)
    official_rubric.json        # Official rubric (PaperBench modes)
    architecture_plan.json
    experiment_manifest.json
  code_workspace/{name}/
    README.md
    requirements.txt
    reproduce.sh                # PaperBench Full mode only
    src/
    baselines/
    scripts/                    # run_table1.py, run_figure3.py, etc.
    configs/
    results/
  verification_workspace/
    cpu_test_results.json       # All test categories must pass
  rubric_audit/
    paperbench_score_estimate.json
    rubric_gap_report.md
  submission/                   # PaperBench Full mode only
```

---

## Submission Validation (PaperBench Full)

```bash
python scripts/validate_submission.py <repo_dir> --blacklist <blacklist.txt>
```

Optional Docker-based reproduction test:
```bash
./scripts/run_local_reproduce_check.sh <repo_dir> --smoke
```

See `docs/submission_requirements.md` for the full submission spec.

---

## Limitations

- **Internal scores are estimates, not official PaperBench scores.** The skill estimates scores by inspecting code and running CPU tests. Official scores require the PaperBench LLM judge pipeline, which we cannot run locally.
- **No GPU training.** Scripts are generated and smoke-tested on CPU (`--max-steps 1`). Full training requires GPU hardware.
- **No fresh-container testing.** The skill runs in your environment. Use `run_local_reproduce_check.sh` with Docker for container-based validation.
- **Result match items are conservative estimates.** Without running full experiments, result correctness is inferred from code quality.

---

## File Structure

```
pAI-Replicator-claude/
  SKILL.md                          # Main orchestrator (v2.0)
  templates/
    state.json                      # State machine template
    rubric_template.json            # Rubric schema
    reproduce.sh.tmpl               # reproduce.sh boilerplate
  prompts/
    00-paper-decomposition.md       # Experiment module decomposition
    00a-bundle-ingestion.md         # Phase 0.5: PaperBench bundle parsing
    01-04: Persona definitions + synthesis
    05-16: Phase prompts (ingestion → final review)
    17-reproduce-sh.md              # reproduce.sh spec
    18-submission-packaging.md      # Submission validation + export
  scripts/
    validate_submission.py          # Submission checker
    export_direct_submission.py     # Clean export
    run_local_reproduce_check.sh    # Docker reproduction test
  docs/
    v2_architecture.md              # Mode comparison
    benchmark_integration.md        # PaperBench integration guide
    submission_requirements.md      # Valid submission spec
    cpu-verification-protocol.md    # CPU test categories
    paperbench-scoring.md           # Scoring reference
    ...
```

---

## PaperBench Context

[PaperBench](https://openai.com/index/paperbench/) (OpenAI, 2025) evaluates AI agents on replicating 20 ICML 2024 papers across 8,316 rubric items. Three categories: Code Development (~40%), Execution (~30%), Result Match (~30%).

Best AI agents score ~21-27%. ML PhD humans score ~41%. The Code-Dev variant (code quality only) reaches ~43% for the best agent.

This skill targets PaperBench by building a rubric-first pipeline: decompose the paper into gradable items, then implement to maximize coverage. CPU verification ensures the code runs. Experiment scripts ensure execution items are covered.
