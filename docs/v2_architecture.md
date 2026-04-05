# pAI-Replicator V2 Architecture

## Three Modes

| Feature | Interactive (PDF) | PaperBench Code-Dev | PaperBench Full |
|---------|-------------------|---------------------|-----------------|
| **Input** | Paper PDF | PaperBench bundle | PaperBench bundle |
| **Autonomy** | Checkpoint every phase | Fully autonomous | Fully autonomous |
| **Rubric** | Generated internally | Official rubric.json | Official rubric.json |
| **reproduce.sh** | Not generated | Not generated | First-class artifact |
| **Submission export** | No | No | Yes |
| **CPU verification** | 6 categories | 6 categories | 7 categories (+reproduce.sh) |
| **Grading target** | Internal estimate | Code-Dev score | Full PaperBench score |
| **Primary use** | Human-guided replication | Autonomous code gen | Benchmark-faithful submission |

## What Is Benchmark-Faithful

**Benchmark-faithful** means the output can be fed directly into PaperBench's official evaluation pipeline. Specifically:

1. Submission is a self-contained git repo
2. `reproduce.sh` at root executes all experiments
3. All files are git-tracked (`git clean -fd` removes nothing needed)
4. No blacklisted URLs/repos referenced
5. `requirements.txt` lists all dependencies
6. Runs in a fresh Ubuntu 24.04 container with single NVIDIA A10

**What we cannot verify locally:**
- Fresh-container reproduction (requires Docker — `scripts/run_local_reproduce_check.sh` helps)
- Official LLM judge grading (requires PaperBench infrastructure)
- Actual result correctness (requires GPU training runs)

## What Is NOT Benchmark-Faithful

The interactive mode (mode 1) produces good code repositories but:
- Has no `reproduce.sh`
- Has no submission packaging
- No blacklist compliance checking
- Internal score estimates are based on code inspection, not actual execution

## Architecture Diagram

```
[Input]                  [Mode Selection]            [Pipeline]
  PDF ─────────────────→ Interactive (1) ──→ Phase 1 (PDF ingestion) ──→ Phases 2-13
  PaperBench bundle ──→ Code-Dev (2) ────→ Phase 0.5 (bundle) ────→ Phases 2-13
  PaperBench bundle ──→ Full (3) ────────→ Phase 0.5 (bundle) ────→ Phases 2-13 + submission
```

All three modes share the same core pipeline (phases 2-12). They differ in:
- How input is ingested (PDF vs. bundle)
- Whether checkpoints block (interactive) or log (autonomous)
- Whether reproduce.sh and submission packaging run (full only)
