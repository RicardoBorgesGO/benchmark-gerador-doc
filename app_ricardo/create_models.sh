#!/bin/sh
# Compila os modelos customizados a partir dos Modelfiles.
# Usa OLLAMA_HOST para apontar para o servidor (ex.: http://ollama:11434).
set -e

MODELFILES_DIR="${MODELFILES_DIR:-Modelfiles}"
BASE_MODEL="${BASE_MODEL:-qwen2.5-coder:7b}"

echo "Baixando modelo base ${BASE_MODEL}..."
ollama pull "$BASE_MODEL"

ollama create doc-diataxis-tutorial -f "$MODELFILES_DIR/Modelfile.tutorial"
ollama create doc-diataxis-howto -f "$MODELFILES_DIR/Modelfile.howto"
ollama create doc-diataxis-reference -f "$MODELFILES_DIR/Modelfile.reference"
ollama create doc-diataxis-explanation -f "$MODELFILES_DIR/Modelfile.explanation"
ollama create doc-c4-level1 -f "$MODELFILES_DIR/Modelfile.c4level1"
ollama create doc-c4-level2 -f "$MODELFILES_DIR/Modelfile.c4level2"
ollama create doc-c4-level3 -f "$MODELFILES_DIR/Modelfile.c4level3"

echo "Modelos compilados:"
ollama list
