#!/usr/bin/env bash
# Start the Strands Decider server on :8099. Uses CUDA when it has enough free memory, else CPU.
# Override with DEVICE=cuda|cpu and CHECKPOINT=... .
set -euo pipefail
CHECKPOINT="${CHECKPOINT:-StrandsAgents/strands-decider-2B-qwen3.5-v1-2610}"
PORT="${PORT:-8099}"
if [[ -z "${DEVICE:-}" ]]; then
  free_mb=$(nvidia-smi --query-gpu=memory.free --format=csv,noheader,nounits 2>/dev/null | head -1 || echo 0)
  # The 2B torso is ~4 GB in bf16 before activations; below ~5 GB free, CPU is the safe choice.
  if [[ "${free_mb:-0}" -ge 5000 ]]; then DEVICE=cuda; else DEVICE=cpu; fi
fi
echo "strands-decider: ${CHECKPOINT} on ${DEVICE} at :${PORT}"
exec uv run strands-decider serve "${CHECKPOINT}" --device "${DEVICE}" --port "${PORT}"
