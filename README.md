# 📘 Gerador Docs (DocGen)

Geração de Guia de Projeto de Software (Diátaxis e C4) a partir de um repositório, com modelos de linguagem executados localmente no Ollama.

## Estrutura

```text
.
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
├── pull_models.sh
├── .devcontainer/
├── src/docgen/            pacote com o pipeline
│   └── prompts/           prompts em português (pt.py) e inglês (en.py)
├── apps/streamlit/        interface
├── benchmark/             execução em lote e resumo dos resultados
├── translated_readme/     READMEs traduzidos, usados como referência em português
├── tests/
└── docs/                  protocolo experimental
```

## Como funciona

Para cada repositório, o pipeline faz uma chamada ao modelo por documento (7 no total: 4 de Diátaxis e 3 de C4), enviando o código dos arquivos selecionados no prompt de usuário e um prompt de sistema específico do documento. Parâmetros de geração: `num_ctx` 16384, `num_predict` 8192, `temperature` 0,2, `repeat_penalty` 1,15 e `repeat_last_n` 128.

**Seleção de arquivos** (`src/docgen/harness.py`): extensões de código e configuração; ignora `node_modules`, `.git`, `__pycache__`, `doc`, `docs`, `env`, `venv`, `dist`, `build`, `test`, `tests` e pastas ocultas. O filtro de pastas é aplicado ao caminho relativo à raiz do repositório.

**Top-k (opcional).** Para repositórios grandes, limita o envio a `k` arquivos: manifestos primeiro, depois código-fonte, por número de linhas, com no máximo 4.000 caracteres cada. Os mesmos `k` arquivos vão em todos os documentos, e o prompt de usuário passa a dizer "principais arquivos" em vez de "código-fonte completo". Sem top-k, todos os arquivos válidos são enviados.

**Idioma.** `pt` ou `en`. Troca o prompt de sistema de cada documento, o prompt de usuário, o prompt do juiz e o prompt de reparo de Mermaid. Os prompts em inglês são tradução fiel dos em português (mesma estrutura, mesmas regras e mesmos exemplos de Mermaid). O nome dos arquivos gerados não muda.

**Reparo de Mermaid (opcional, desligado por padrão).** Valida os diagramas dos documentos C4 e, se encontrar problemas, faz uma chamada extra de correção. Não faz parte do harness original.

## Avaliação

- **BERTScore e METEOR** do guia (os 7 documentos concatenados) contra o README (`evaluate_documentation`). Em português usa o README traduzido de `translated_readme/` quando existe; em inglês, ou sem tradução, usa o README original do repositório. A coluna `reference` do CSV registra qual foi usado (`translated`, `original` ou `none`). A pasta de saída não recebe cópia do README, para que ele não entre na comparação como se fosse documento gerado.
- **Juiz LLM** (`evaluate_markdown`): para cada documento recebe o README, o prompt de sistema do documento e o texto gerado, e devolve JSON com quatro notas de 1 a 5 (coerência com o repositório, adesão aos frameworks, utilidade para onboarding, clareza) e uma lista de sugestões. `judge_suggestions_total` é o total de sugestões. O juiz não vê o código do repositório, e a coerência é medida contra o README.
- **Verificador de referências:** arquivos e identificadores citados entre crases que não existem no repositório (`references_missing`).
- **Taxa de edição** entre o guia gerado e a versão revisada por uma pessoa.
- **Tempo, tokens, chamadas truncadas** (prompt que ocupa quase todo o `num_ctx`), energia e VRAM de pico (`nvidia-smi`, quando disponível).

## Instalação

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[app]"            # interface
pip install -e ".[app,eval]"       # inclui BERTScore, METEOR, scipy e json-repair
```

Modelos no Ollama:

```bash
ollama pull qwen2.5-coder:7b       # geração
ollama pull gemma4:12b             # juiz
```

## Uso

Execute os comandos a partir da raiz do projeto.

```bash
streamlit run apps/streamlit/app.py

python -m benchmark.run_benchmark --models qwen2.5-coder:7b --repos https://github.com/epidemian/snake
python -m benchmark.run_benchmark --models qwen2.5-coder:7b --languages pt en --top-k 0 8
python -m benchmark.run_benchmark --resume
python -m benchmark.summarize_results evaluation_results.csv

python -m unittest discover -s tests
```

Sem argumentos, `benchmark.run_benchmark` percorre todos os `REPOSITORIES` e `OLLAMA_MODELS` de `benchmark/config.py`. Opções: `--repos`, `--models`, `--languages`, `--top-k` (0 = todos os arquivos), `--num-ctx`, `--repeats`, `--seed-base`, `--judge-model`, `--no-judge`, `--mermaid-repair`, `--translated-dir`, `--resume`, `--host`, `--out`, `--csv-dir`.

### Saídas

```text
autodoc/<modelo com ":" trocado por "_">/<repositório>/<idioma>/
├── 01_tutorials.md ... C4_architecture_level3.md
├── llm_eval.json        notas e sugestões do juiz por documento
└── run_info.json        configuração da última execução (top_k, num_ctx, run, seed, data)
generation_metrics.csv   uma linha por documento
evaluation_results.csv   uma linha por execução
```

A pasta de saída inclui o idioma, mas não o top-k, o `num_ctx` nem o número da repetição. Execuções que diferem só nesses valores gravam os documentos na mesma pasta e a última sobrescreve a anterior; as métricas de todas ficam nos CSV, distinguidas pelas colunas `top_k`, `num_ctx` e `run`, e `run_info.json` indica qual execução produziu os arquivos.

**`generation_metrics.csv`** tem as colunas `repository`, `document`, `model`, `prompt_tokens`, `output_tokens`, `generation_time_seconds` e também `language`, `top_k`, `num_ctx`, `run`, `truncated_calls`, `mermaid_repaired` e as notas do juiz do documento. `repository` é a URL.

**`evaluation_results.csv`** tem as colunas `model`, `repository`, `meteor`, `bert_precision`, `bert_recall`, `bert_f1` e também `repository_url`, `language`, `top_k`, `num_ctx`, `run`, `seed`, `reference`, `overlap_score`, tempo, tokens, `truncated_calls`, arquivos válidos e enviados, as médias do juiz (`judge_*`), `references_*`, energia e VRAM. `repository` é o nome da pasta.

## Docker

```bash
docker compose up --build
```

Sobe o Ollama, baixa os modelos (`pull_models.sh`) e inicia a interface em `http://localhost:8501`. Para usar a GPU NVIDIA, descomente o bloco `deploy` do serviço `ollama`. O devcontainer usa os mesmos serviços.

## Documentação

`docs/EXPERIMENTO.md`: variáveis, métricas e protocolo.
