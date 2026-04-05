# Phase 0.5: PaperBench Bundle Ingestion

## Objective

Parse a PaperBench paper bundle into the same structured representation that Phase 1 (PDF ingestion) produces. This phase runs INSTEAD of Phase 1 in `paperbench_code_dev` and `paperbench_full` modes.

The bundle contains cleaner inputs than a raw PDF: pre-extracted markdown, author clarifications, the official rubric, and a blacklist of forbidden resources. Use all of these.

---

## Required Inputs

All files are in `{WORKSPACE}/input/`:

| File | Required | Purpose |
|------|----------|---------|
| `paper.md` | Yes | Paper text as clean markdown (no PDF extraction needed) |
| `paper.pdf` | Yes | Original PDF (for figures, equations) |
| `addendum.md` | Yes | Author clarifications: scope boundaries, implementation details, what to include/exclude |
| `rubric.json` | Yes | Official PaperBench rubric (hierarchical, weighted, leaf-based) |
| `blacklist.txt` | Yes | URLs/domains the agent must NOT access (e.g., original paper repo) |
| `config.yaml` | Yes | Paper metadata (ID, title, venue) |
| `assets/` | Optional | Figures and images from the paper |
| `judge.addendum.md` | Optional | Additional info for the judge (read but do not optimize against) |

---

## Required Outputs

### 1. `analysis_workspace/paper_analysis.json`

**Same schema as Phase 1 output.** The downstream pipeline is identical regardless of whether ingestion came from PDF or bundle. Populate all fields:

- `paper_metadata`: from `config.yaml` and `paper.md`
- `model_architecture`: from `paper.md` methodology sections
- `training_config`: from `paper.md` experimental setup
- `datasets`: from `paper.md` + `addendum.md` clarifications
- `metrics`, `baselines`, `ablations`, `algorithms`: from `paper.md`
- `loss_function`: from `paper.md` equations
- `table_figure_inventory`: from `paper.md` + `assets/`
- `implementation_details_section`: from `paper.md` appendix + `addendum.md`
- `paper_type`: infer from content (theory | architecture | optimizer | benchmark | empirical)
- `ambiguities`: anything still unclear AFTER reading `addendum.md` (should be fewer than PDF-only mode)

### 2. `analysis_workspace/paper_extracted.md`

Human-readable narrative (same format as Phase 1 output).

### 3. `analysis_workspace/official_rubric.json`

Copy `input/rubric.json` here. This is the official rubric that Phase 2 will import directly instead of generating from scratch. Do NOT modify it.

### 4. `analysis_workspace/blacklist.txt`

Copy `input/blacklist.txt` here. Store parsed URLs in `state.json → blacklisted_urls`.

### 5. `analysis_workspace/addendum_notes.md`

Structured summary of key clarifications from `addendum.md`:
- Scope inclusions/exclusions
- Implementation details not in the paper
- Dataset-specific notes
- Any author corrections to the paper

---

## Process

### Step 1: Read config.yaml

Extract paper ID, title, and venue. Update `state.json` with `paper_title` and `paper_venue`.

### Step 2: Read paper.md (primary source)

This is clean markdown — no PDF extraction issues. Read it cover to cover. Extract the same 12 top-level keys as Phase 1 (see `prompts/05-pdf-ingestion.md` for the full schema).

### Step 3: Read addendum.md (author clarifications)

The addendum contains critical information not in the paper:
- Which experiments are in scope vs. out of scope
- Specific implementation choices the authors made
- Dataset preprocessing details
- Hardware and runtime details

**Integrate addendum clarifications directly into `paper_analysis.json`.** Do not treat them as separate — they are authoritative.

### Step 4: Read rubric.json (official grading criteria)

Parse the official rubric to understand what will actually be graded. Note:
- Which categories have the most items (focus here)
- Which items require execution (these need `reproduce.sh`)
- Which items require result matching (hardest category)
- Which items are purely code-development (lowest-hanging fruit)

Do NOT modify the rubric. Copy it verbatim to `analysis_workspace/official_rubric.json`.

### Step 5: Parse blacklist.txt

Read each line. Store as `state.json → blacklisted_urls`. These URLs must NEVER appear in any generated code, comments, README, or configuration. Typical entries:
- The paper's official code repository URL
- Author GitHub profiles
- Specific dataset mirrors

### Step 6: Read paper.pdf for figures and equations

Use the PDF (or `assets/` directory) to verify:
- Equation rendering (markdown may lose formatting)
- Figure details (architecture diagrams, training curves)
- Table formatting and footnotes

### Step 7: Write all outputs

Write `paper_analysis.json`, `paper_extracted.md`, copy `official_rubric.json` and `blacklist.txt`, write `addendum_notes.md`.

---

## Quality Check

Before marking complete:
- [ ] `paper_analysis.json` has all 12 top-level keys populated
- [ ] `addendum.md` clarifications are integrated (not just listed as ambiguities)
- [ ] `official_rubric.json` is an exact copy of `input/rubric.json`
- [ ] `blacklist.txt` parsed and stored in state.json
- [ ] `ambiguities` list is shorter than it would be from PDF-only (addendum resolves many)
- [ ] `paper_type` field is set

---

## Checkpoint

Show:
```
Bundle ingestion complete:
  Paper: {title} ({venue})
  Paper type: {paper_type}
  Model architecture: {model_name} ({N} components)
  Datasets: {N} ({names})
  Official rubric: {N} leaf items ({cd} CD, {ex} EX, {rm} RM)
  Blacklisted URLs: {N}
  Ambiguities remaining: {N} ({N_high} HIGH severity)
```

In autonomous modes, log this and continue. In interactive mode, wait for PROCEED.
