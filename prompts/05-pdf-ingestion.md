# Phase 1: PDF Ingestion and Deep Analysis

## Objective

Perform a deep, systematic extraction of every implementation-relevant detail from the paper PDF. Your goal is not a summary — it is a complete specification that a developer could use to implement the paper without access to the original PDF.

**You will need to read this paper carefully multiple times.** The first pass extracts the obvious content. Subsequent passes catch the subtle details buried in appendices, footnotes, and experimental setup sections.

---

## Required Inputs

- `input/paper.pdf` — the original paper
- `input/paper.md` — clean extracted paper text, preferred over PDF when present; required in `paperbench_autonomous` mode
- `input/addendum.md` — author clarifications; required in `paperbench_autonomous` mode and optional in `legacy_interactive_pdf` mode
- `input/blacklist.txt` — forbidden URLs/repos; required in `paperbench_autonomous` mode
- Any files in `input/supplementary/` — supplementary PDFs, appendices

---

## Required Outputs

### 1. `analysis_workspace/paper_analysis.json`

A structured JSON with these top-level keys:

```json
{
  "paper_metadata": {
    "title": "",
    "authors": [],
    "venue": "",
    "year": 0,
    "arxiv_id": "",
    "abstract": ""
  },
  "model_architecture": {
    "name": "",
    "type": "transformer | cnn | gnn | hybrid | other",
    "components": [
      {
        "name": "",
        "description": "",
        "paper_section": "",
        "key_dimensions": {},
        "implementation_notes": ""
      }
    ],
    "total_parameters": "",
    "variants": []
  },
  "training_config": {
    "optimizer": "",
    "learning_rate": "",
    "lr_schedule": "",
    "warmup_steps": "",
    "batch_size": "",
    "gradient_clip_norm": "",
    "weight_decay": "",
    "training_steps_or_epochs": "",
    "precision": "fp32 | fp16 | bf16",
    "hardware": "",
    "other_hyperparameters": {}
  },
  "datasets": [
    {
      "name": "",
      "split": "train | val | test",
      "size": "",
      "preprocessing": [],
      "augmentation": [],
      "paper_section": "",
      "publicly_available": true,
      "download_url": ""
    }
  ],
  "metrics": [
    {
      "name": "",
      "higher_is_better": true,
      "definition": "",
      "paper_section": ""
    }
  ],
  "baselines": [
    {
      "name": "",
      "paper_reference": "",
      "config_used": "",
      "implementation_notes": "",
      "results_table": ""
    }
  ],
  "ablations": [
    {
      "name": "",
      "paper_table_or_figure": "",
      "what_varies": "",
      "conditions": [],
      "key_finding": ""
    }
  ],
  "algorithms": [
    {
      "name": "",
      "paper_section": "",
      "pseudocode_verbatim": "",
      "steps": [],
      "inputs": [],
      "outputs": []
    }
  ],
  "loss_function": {
    "main_loss": "",
    "auxiliary_losses": [],
    "regularization": [],
    "loss_weights": {},
    "paper_equation": ""
  },
  "table_figure_inventory": [
    {
      "id": "Table 1",
      "caption": "",
      "what_it_shows": "",
      "requires_gpu": true,
      "estimated_runtime": ""
    }
  ],
  "implementation_details_section": "",
  "reproducibility_statement": "",
  "code_availability": {
    "mentioned_in_paper": false,
    "url": "",
    "notes": ""
  },
  "paper_type": "theory | architecture | optimizer | benchmark | empirical",
  "paper_type_rationale": "why this type — affects rubric weighting in Phase 2",
  "ambiguities": [
    {
      "id": "AMB-001",
      "severity": "high | medium | low",
      "what_is_unclear": "",
      "most_likely_interpretation": "",
      "impact_if_wrong": ""
    }
  ]
}
```

### 2. `analysis_workspace/paper_extracted.md`

A human-readable narrative of everything extracted. Sections:
- Paper summary (2-3 paragraphs)
- Core contribution (bulleted)
- Architecture description with equations
- Training procedure step by step
- Datasets and preprocessing
- All baselines with notes
- All ablations
- Key results table (reproduced from paper)
- Implementation notes and gotchas
- Anything ambiguous or underspecified

### 3. Mode 4-only supporting outputs

When `mode == "paperbench_autonomous"`, also write:

- `analysis_workspace/addendum_notes.md` — structured summary of author clarifications from `input/addendum.md`
- `analysis_workspace/blacklist.txt` — exact copy of `input/blacklist.txt`
- `state.json → blacklisted_urls` — parsed non-empty blacklist lines

Do not create or import `analysis_workspace/official_rubric.json` in Mode 4.

---

## Process

### Pass 1: Full paper read (cover to cover)

0. Choose the primary paper text:
   - In `paperbench_autonomous` mode, read `input/paper.md` first and treat it as the primary source for analysis; use `input/paper.pdf` for figures, equations, tables, and fallback checks.
   - In `legacy_interactive_pdf` mode, use `input/paper.pdf` as the primary source unless `input/paper.md` is already available.
1. Read the abstract, introduction, and related work to understand the context.
2. Read the methodology section thoroughly. For every equation, note:
   - The equation number and section
   - What mathematical operation it defines
   - What the variables represent
   - Any edge cases or special handling noted
3. Read the experimental setup section. Extract ALL:
   - Dataset names and splits
   - Preprocessing steps
   - Training hyperparameters (from tables, text, and captions)
   - Baseline methods and their configurations
4. Read the results sections. Inventory every table and figure.
5. Read the appendix and supplementary material. This is where critical implementation details hide.
6. Read `input/addendum.md` when present. In `paperbench_autonomous` mode this is mandatory. The addendum contains authoritative clarifications such as:
   - Which experiments are in scope vs. out of scope
   - Specific implementation choices the authors made
   - Dataset preprocessing details
   - Hardware and runtime details

**Integrate addendum clarifications directly into `paper_analysis.json`.** Do not treat them as a separate side note. In particular, use the addendum to resolve or downgrade entries in `ambiguities[]` where possible; only keep ambiguities that remain unclear after reading the addendum.
7. In `paperbench_autonomous` mode, read `input/blacklist.txt`, copy it to `analysis_workspace/blacklist.txt`, parse each non-empty line into `state.json → blacklisted_urls`, and ensure none of these URLs are included in generated notes, code comments, READMEs, configs, or scripts.

**After Pass 1:** Write the initial `paper_analysis.json` and `paper_extracted.md`.

In `paperbench_autonomous` mode, also write `analysis_workspace/addendum_notes.md` with:
- Scope inclusions/exclusions
- Implementation details not in the paper
- Dataset-specific notes
- Author corrections to the paper
- Ambiguities resolved by the addendum

### Pass 2: Gap-filling pass

Re-read the paper focusing on:

1. **Hyperparameter completeness**: Go through every number in the paper. Is it in `training_config` or `other_hyperparameters`?
2. **Baseline completeness**: Every method in every comparison table/figure is a baseline. Are all in `baselines`?
3. **Ablation completeness**: Every table/figure that varies one aspect of the method is an ablation. Are all in `ablations`?
4. **Algorithm completeness**: Every pseudocode box or step-by-step description is an algorithm. Are all in `algorithms`?
5. **Table/figure inventory**: Does `table_figure_inventory` include EVERY table and figure (not just the main ones)?

**After Pass 2:** Update both files with any gaps found.

### Pass 3+ (if needed): Deep dives

If any section is incomplete, re-read it. Focus on:
- Footnotes (often contain critical implementation notes)
- Figure captions (often contain hyperparameter values)
- Appendix sections on "implementation details" or "experimental details"
- Any "we follow [citation] for..." references (extract what was followed)

---

## Common Extraction Pitfalls

1. **Missing appendix details**: Most papers put crucial implementation details in appendices. Always read to the end.

2. **Hyperparameters in figure captions**: Many papers report batch size or LR in the caption of training curves. Don't miss these.

3. **"We use the standard X"**: When the paper says "we use the standard preprocessing from [citation]", extract what that preprocessing is (even if you need to infer it from the citation context).

4. **Implicit normalization**: Papers often say "we normalize inputs" without specifying how. Flag this as ambiguous.

5. **Hardware-dependent details**: "4 A100 GPUs" implies gradient accumulation or distributed training. Note the implied training setup.

6. **Table footnotes**: Asterisks and daggers in tables often explain implementation variants or cherry-picked comparisons.

---

## Quality Check

Before marking Pass 1 complete, verify:
- [ ] `model_architecture.components` has at least 3 entries (or the paper has an unusually simple model)
- [ ] `training_config` has at least optimizer, learning_rate, and batch_size filled in
- [ ] `datasets` has at least 1 entry with preprocessing noted
- [ ] `baselines` has at least 2 entries (most papers compare against multiple methods)
- [ ] `table_figure_inventory` lists ALL tables and figures (count them in the PDF)
- [ ] `algorithms` has at least 1 entry if the paper has a pseudocode box
- [ ] `loss_function.main_loss` is filled in and cites the paper equation
- [ ] In `paperbench_autonomous` mode, `addendum.md` clarifications are integrated into `paper_analysis.json`, `addendum_notes.md` exists, `blacklist.txt` is copied, and `state.json → blacklisted_urls` is populated
- [ ] In `paperbench_autonomous` mode, no official rubric has been imported or referenced

---

## Note on Ambiguities

When you encounter something that is underspecified or ambiguous, do NOT make an assumption and silently proceed. Instead:
- Add it to `paper_analysis.json → ambiguities[]` with `severity: "high | medium | low"`
- Describe what is unclear, your best interpretation, and the impact of guessing wrong
- Flag it prominently in `paper_extracted.md`

## Note on Paper Type

Classify the paper into one type:
- **theory**: primary contribution is a theorem/proof; experiments are illustrative
- **architecture**: primary contribution is a new model architecture (ViT, ResNet, etc.)
- **optimizer**: primary contribution is a new training algorithm (Adam, SAM, etc.)
- **benchmark**: primary contribution is a new dataset or evaluation suite
- **empirical**: primary contribution is an empirical study/analysis (e.g., scaling laws)

The paper type is used by Phase 2 to weight rubric categories appropriately:
- Theory → emphasize measurement code correctness
- Architecture → emphasize model implementation fidelity
- Optimizer → emphasize training loop correctness
- Benchmark → emphasize data pipeline and evaluation scripts
- Empirical → emphasize experiment coverage and result reproduction

## Checkpoint — Ambiguity Review (MANDATORY)

At the Phase 1 checkpoint, **before asking PROCEED**, explicitly list all HIGH-severity ambiguities:

```
⚠️  HIGH-SEVERITY AMBIGUITIES FOUND — please resolve before Phase 2:

AMB-001: {what_is_unclear}
  My interpretation: {most_likely_interpretation}
  Impact if wrong: {impact}
  → Please confirm or correct

AMB-002: ...

If these look right, type PROCEED. Otherwise, describe corrections.
```

Do NOT advance to Phase 2 until the user has acknowledged the ambiguity list.
