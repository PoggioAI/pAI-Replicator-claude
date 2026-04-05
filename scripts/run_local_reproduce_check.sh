#!/usr/bin/env bash
set -euo pipefail

# Run reproduce.sh in a clean Docker container to validate reproducibility.
# This simulates the PaperBench fresh-container execution environment.
#
# Usage:
#   ./run_local_reproduce_check.sh <submission_dir> [--smoke]
#
# Options:
#   --smoke    Run with MAX_STEPS=1 (quick validation, no GPU needed)

SUBMISSION_DIR="${1:?Usage: $0 <submission_dir> [--smoke]}"
SMOKE_MODE=0
if [ "${2:-}" = "--smoke" ]; then SMOKE_MODE=1; fi

SUBMISSION_DIR="$(cd "$SUBMISSION_DIR" && pwd)"

if ! command -v docker &>/dev/null; then
    echo "Docker not found. Manual verification instructions:"
    echo ""
    echo "  1. Create a clean Python environment (venv or conda)"
    echo "  2. cd $SUBMISSION_DIR"
    echo "  3. pip install -r requirements.txt"
    if [ "$SMOKE_MODE" -eq 1 ]; then
        echo "  4. MAX_STEPS=1 DEVICE=cpu bash reproduce.sh"
    else
        echo "  4. bash reproduce.sh"
    fi
    echo ""
    echo "If all experiments complete without error, the submission is valid."
    exit 0
fi

echo "=== Running reproduce.sh in Docker container ==="
echo "Submission: $SUBMISSION_DIR"

DOCKER_ARGS="-v $SUBMISSION_DIR:/workspace -w /workspace"
ENV_ARGS=""
if [ "$SMOKE_MODE" -eq 1 ]; then
    ENV_ARGS="-e MAX_STEPS=1 -e DEVICE=cpu"
    echo "Mode: smoke test (MAX_STEPS=1, CPU only)"
else
    # Add GPU support if available
    if docker info 2>/dev/null | grep -q "nvidia"; then
        DOCKER_ARGS="$DOCKER_ARGS --gpus all"
        echo "Mode: full run (GPU detected)"
    else
        ENV_ARGS="-e DEVICE=cpu"
        echo "Mode: full run (no GPU, using CPU)"
    fi
fi

docker run --rm $DOCKER_ARGS $ENV_ARGS python:3.11-slim bash -c \
    "pip install -r requirements.txt && bash reproduce.sh" \
    2>&1 | tee /tmp/reproduce_check.log

EXIT_CODE=${PIPESTATUS[0]}
if [ "$EXIT_CODE" -eq 0 ]; then
    echo ""
    echo "=== reproduce.sh completed successfully ==="
else
    echo ""
    echo "=== reproduce.sh FAILED (exit code: $EXIT_CODE) ==="
    echo "Log saved to: /tmp/reproduce_check.log"
fi
exit "$EXIT_CODE"
