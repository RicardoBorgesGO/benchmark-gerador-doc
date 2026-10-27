#!/bin/sh
set -e

BASE_MODEL="${BASE_MODEL:-qwen2.5-coder:7b}"
EMBED_MODEL="${EMBED_MODEL:-nomic-embed-text}"

ollama pull "$BASE_MODEL"
ollama pull "$EMBED_MODEL"

if [ -n "${JUDGE_MODEL:-}" ]; then
  ollama pull "$JUDGE_MODEL"
fi

ollama list
