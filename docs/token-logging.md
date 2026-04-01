# Token Logging — pAI-Replicator

## Overview

After every subagent call, run this zero-LLM-cost Python logging script to track phase progress and token usage.

## Logging Script

```bash
python3 -c "
import json, os, sys
from datetime import datetime

workspace = sys.argv[1]
phase = sys.argv[2]
pass_num = int(sys.argv[3])
prompt_file = sys.argv[4]
response_summary = sys.argv[5]

logs_dir = os.path.join(workspace, 'logs')
os.makedirs(logs_dir, exist_ok=True)

# Append to phase log (JSONL)
phase_log = os.path.join(logs_dir, f'phase_{phase}.jsonl')
with open(phase_log, 'a') as f:
    entry = {
        'timestamp': datetime.now().isoformat(),
        'phase': phase,
        'pass': pass_num,
        'prompt_file': prompt_file,
        'prompt_content': open(prompt_file).read() if os.path.exists(prompt_file) else '',
        'response_summary': response_summary
    }
    f.write(json.dumps(entry) + '\n')

# Update summary (JSON)
summary_path = os.path.join(logs_dir, 'token_summary.json')
if os.path.exists(summary_path):
    summary = json.load(open(summary_path))
else:
    summary = {'total_subagent_calls': 0, 'phases': {}}

summary['total_subagent_calls'] += 1
if phase not in summary['phases']:
    summary['phases'][phase] = {'calls': 0, 'passes': []}
summary['phases'][phase]['calls'] += 1
summary['phases'][phase]['passes'].append({
    'pass': pass_num,
    'timestamp': datetime.now().isoformat()
})

with open(summary_path, 'w') as f:
    json.dump(summary, f, indent=2)

print(f'[LOG] Phase {phase} pass {pass_num} logged.')
" {workspace} {phase_name} {pass_number} {prompt_file_path} "{one_line_summary}"
```

## Outputs

- `logs/phase_{phase_name}.jsonl` — append-only log per phase, includes full prompt content
- `logs/token_summary.json` — call counts per phase, timestamps
- `logs/stall_warnings.json` — written when stall detection triggers
- `logs/phase_warnings.json` — written when max passes reached with incomplete artifacts

## Usage

Call after every subagent invocation:

```
After spawning subagent for phase "core_algorithm" pass 2:
  workspace = /path/to/replication_001
  phase = core_algorithm
  pass_number = 2
  prompt_file = /path/to/pAI-Replicator-claude/prompts/08-core-algorithm.md
  summary = "Implemented TransformerEncoder, MultiHeadAttention, LayerNorm"
```
