# Persona Council Protocol — pAI-Replicator

## When the Council Runs

The persona council runs once in Phase 3b, after the repository architecture has been designed but before any code is written. Its purpose is to catch architectural and specification errors early — when they are cheap to fix.

The council is **advisory with blocking authority**: if consensus fails after 5 rounds, the orchestrator logs all concerns and proceeds, but the concerns are injected as constraints into Phase 4.

---

## The Three Personas

1. **Code Architect** (`prompts/01-persona-architect.md`) — evaluates code structure, modularity, testability, and hidden implementation pitfalls.
2. **Algorithmic Rigor** (`prompts/02-persona-rigor.md`) — evaluates mathematical fidelity to the paper, equation correctness, and hyperparameter faithfulness.
3. **PaperBench Judge** (`prompts/03-persona-paperbench-judge.md`) — evaluates rubric coverage, easy-win identification, and what will definitely fail PaperBench.

---

## Debate Round Structure

Each round:
1. Spawn Code Architect subagent → writes to `persona_workspace/persona_architect_round_{N}.md`
2. Spawn Algorithmic Rigor subagent → writes to `persona_workspace/persona_rigor_round_{N}.md`
3. Spawn PaperBench Judge subagent → writes to `persona_workspace/persona_judge_round_{N}.md`
4. Spawn Synthesis subagent → reads all three, writes to `persona_workspace/council_synthesis_round_{N}.md`, updates `analysis_workspace/architecture_plan.json`

**Round injection for rounds 2+:** Prepend to each persona's prompt:

```
ROUND {N} OF PERSONA COUNCIL (Architecture Review)

You previously evaluated this architecture in Round {N-1}.
Your Round {N-1} evaluation is at: persona_workspace/persona_{role}_round_{N-1}.md
The architecture was updated based on all personas' feedback.
The updated architecture plan is at: analysis_workspace/architecture_plan.json

Be HARDER this round. The previous round surfaced some concerns.
Check whether they were properly addressed. If your previous concerns were
addressed satisfactorily, say so explicitly. If new concerns have emerged
from the revised plan, surface them.

Your verdict must still be ACCEPT or REJECT (last line of your response).
```

---

## Exit Rules

- **Round 3, all three ACCEPT** → exit council, proceed to Phase 4
- **Round 3, any persona REJECT** → extend to Round 4
- **Round 4, all three ACCEPT** → exit, proceed to Phase 4
- **Round 4, any persona REJECT** → extend to Round 5
- **Round 5** → exit regardless of verdicts. Log any remaining concerns to `persona_workspace/unresolved_concerns.md`. Inject as constraints into Phase 4.
- **DO NOT exit before Round 3** even if all three accept in Round 1 or 2.

---

## Synthesis Rules

The Synthesis coordinator (not a persona, but a separate subagent) integrates all three verdicts:

| Verdicts | Synthesis Action |
|----------|-----------------|
| All 3 ACCEPT | Proceed. Integrate all "nice-to-fix" suggestions as optional improvements. |
| 2 ACCEPT, 1 REJECT | Proceed if the REJECT concerns can be addressed as mandatory fixes in Phase 4. Add them to implementation_checklist.json as priority items. |
| 1 ACCEPT, 2 REJECT | Another round (up to Round 5). Revise architecture_plan.json to address the two REJECT reviewers' core concerns. |
| All 3 REJECT | Substantial redesign required. Revise architecture_plan.json significantly. Another round. |

**Priority ordering for conflicts:**
1. PaperBench Judge's "easy win" fixes (highest ROI for rubric score)
2. Algorithmic Rigor's equation-level blockers (implementation bugs)
3. Code Architect's structural concerns (non-blocking if minor)

**Synthesis output (`council_synthesis_round_{N}.md`) must contain:**
1. Verdict summary table (persona → ACCEPT/REJECT + one-line reason)
2. Mandatory fixes list (ordered by rubric impact)
3. Optional improvements list
4. Updated architecture assessment (one paragraph)
5. Whether council exits or continues

---

## Post-Council Checkpoint

After the council exits, the orchestrator prints:

```
╔══════════════════════════════════════════════════════════════════╗
║              PERSONA COUNCIL — ARCHITECTURE REVIEW              ║
╠══════════════════════════════════════════════════════════════════╣
║ Rounds completed: {N}                                            ║
║                                                                  ║
║ Final verdicts:                                                  ║
║   Code Architect: {ACCEPT/REJECT}                               ║
║   Algorithmic Rigor: {ACCEPT/REJECT}                            ║
║   PaperBench Judge: {ACCEPT/REJECT}                             ║
║                                                                  ║
║ Mandatory fixes before Phase 4:                                  ║
║   1. {fix_1}                                                     ║
║   2. {fix_2}                                                     ║
║   ...                                                            ║
║                                                                  ║
║ Unresolved concerns (will be injected as Phase 4 constraints):  ║
║   {any_unresolved}                                               ║
╚══════════════════════════════════════════════════════════════════╝

Does this plan look good? Type PROCEED to start implementation,
or describe any overrides you want to make to the council's decisions.
```

User response is recorded in `state.json → user_checkpoints`.
