# pAI-Replicator

A Claude Code skill for replicating ICML/ICLR/NeurIPS papers from a PDF. Produces a complete, executable code repository that maximizes score on [PaperBench](https://openai.com/index/paperbench/).

**Target:** Beat PaperBench. Current best AI agent: 27%. Humans: 41%.

---

## What It Does

Given a paper PDF, pAI-Replicator runs a 12-phase pipeline:

1. **PDF Ingestion** — Deep extraction of all implementation details (architecture, hyperparameters, datasets, baselines, ablations)
2. **Rubric Decomposition** — Builds a PaperBench-style hierarchical rubric (40-100+ items)
3. **Repository Architecture** — Designs the complete file structure before writing code
4. **Persona Council** — Three specialized reviewers (Code Architect, Algorithmic Rigor, PaperBench Judge) debate the plan
5. **Core Algorithm** — Implements models, losses, and key algorithms with paper equation citations
6. **Data Pipeline** — Implements data loading with mock-data CPU support
7. **Training Infrastructure** — Training loop, optimizer, evaluation, logging
8. **CPU Verification** — Mandatory: ALL tests must pass before advancing. Tests: imports, forward pass, loss, training step, data pipeline, script smoke test
9. **Baseline Implementations** — All comparison methods from paper tables
10. **Experiment Scripts** — One script per table and figure, with `--max-steps 1` support
11. **Documentation** — Complete README with reproduction instructions
12. **Rubric Audit** — Final coverage assessment + PaperBench score estimate

**Checkpoints after every single phase.** Never advances without user confirmation.

---

## Installation

```bash
# Clone into Claude Code skills directory
git clone https://github.com/PoggioAI/pAI-Replicator-claude.git
cd pAI-Replicator-claude
```

No additional dependencies needed — the skill runs through Claude Code.

---

## Usage

### Start a new replication

```
/pAI-Replicator
```

Or:
```
Replicate this paper: /path/to/paper.pdf
```

The skill will ask for the PDF path and a short project name, then start the pipeline.

### Resume an interrupted replication

```
/pAI-Replicator
```

Select "Resume" and provide the workspace path. The skill picks up from where it stopped.

---

## What Gets Produced

For each replicated paper, the skill creates a workspace:

```
replication_{timestamp}/
  input/
    paper.pdf
  analysis_workspace/
    paper_analysis.json       # Deep structured extraction
    rubric.json               # PaperBench-style rubric (40-100+ items)
    architecture_plan.json    # File → rubric item mapping
    implementation_checklist.json
    final_summary.md          # One-page replication summary
  code_workspace/{paper_name}/
    README.md                 # Full reproduction guide
    requirements.txt
    src/                      # Model, data, training, evaluation
    baselines/                # All comparison methods
    scripts/                  # run_table1.py, run_figure3.py, etc.
    configs/                  # default.yaml + per-experiment configs
    tests/                    # CPU sanity test suite
    results/                  # Experiment outputs
  verification_workspace/
    cpu_test_results.json     # All 6 test categories, all must pass
    shape_checks.log
    loss_curve_checks.log
  rubric_audit/
    rubric_gap_report.md
    paperbench_score_estimate.json
  persona_workspace/
    council_synthesis_round_N.md
```

---

## Constraints

- **No GPU job submission** — Scripts are written and smoke-tested on CPU, but full training is not run
- **CPU experiments only** — Phase 7 runs mandatory CPU tests (all must pass)
- **No cluster submissions** — Works entirely locally
- **Very interactive** — Checkpoints after every phase; never advances silently

---

## Architecture

pAI-Replicator is modeled after the [poggioai-msc-claude](../poggioai-msc-claude) skill but repurposed for replication:

| | MSc Skill | pAI-Replicator |
|---|---|---|
| Input | Research hypothesis | Paper PDF |
| Output | final_paper.tex | Executable code repo |
| Personas | Practical, Rigor, Narrative | Architect, Rigor, PaperBench Judge |
| Checkpoints | Key milestones | Every phase |
| CPU experiments | Optional | Mandatory gate |
| Score metric | Review score ≥6/10 | PaperBench estimate |

---

## File Structure

```
pAI-Replicator-claude/
  SKILL.md                    # Main orchestrator
  README.md                   # This file
  templates/
    state.json                # State machine template
    rubric_template.json      # PaperBench rubric schema
  docs/
    execution-protocol.md     # Pass limits + RESUME template
    cpu-verification-protocol.md  # Required CPU tests
    persona-council.md        # Council debate rules
    checkpoint-protocol.md    # Per-phase checkpoint format
    paperbench-scoring.md     # Scoring strategy reference
    token-logging.md          # Logging script
  prompts/
    01-persona-architect.md   # Code Architect persona
    02-persona-rigor.md       # Algorithmic Rigor persona
    03-persona-paperbench-judge.md  # PaperBench Judge persona
    04-persona-synthesis.md   # Council Synthesis coordinator
    05-pdf-ingestion.md       # Phase 1
    06-rubric-decomposition.md  # Phase 2
    07-repo-architecture.md   # Phase 3
    08-core-algorithm.md      # Phase 4
    09-data-pipeline.md       # Phase 5
    10-training-infrastructure.md  # Phase 6
    11-cpu-verification.md    # Phase 7 (mandatory gate)
    12-baseline-implementation.md  # Phase 8
    13-experiment-scripts.md  # Phase 9
    14-documentation.md       # Phase 10
    15-rubric-audit.md        # Phase 11
    16-final-review.md        # Phase 12
```

---

## Why PaperBench?

PaperBench (OpenAI, 2025) is the hardest paper replication benchmark available:
- 20 ICML 2024 Spotlight/Oral papers
- 8,316 individually gradable rubric items
- Three categories: Code Development (40%), Execution (30%), Result Match (30%)
- Best AI agent: 27% — humans: 41%

Our approach targets this benchmark by:
1. Building a PaperBench-style rubric for each paper before writing code
2. Ensuring every implementation decision traces to a rubric item
3. Running CPU sanity checks that guarantee the code is at least runnable
4. Creating execution scripts for every table and figure in the paper
