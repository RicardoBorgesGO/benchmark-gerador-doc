# DocGen

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
├── apps/streamlit/        interface
├── benchmark/             execução em lote e resumo dos resultados
├── tests/
└── docs/                  protocolo experimental e técnicas pendentes
```

## Configuração da geração

Três opções independentes:

**Estratégia**

| Chave | Descrição |
|---|---|
| `baseline` | Prompts de sistema por documento e seleção de arquivos originais (`baseline.py`, `baseline_prompts.py`). Uma chamada por documento. |
| `rag` | Prompts por seção (`sections.py`), mapa de assinaturas do repositório, plano antes da escrita, exemplo de formato e regra de citação de nomes. Duas chamadas por seção. |

**Contexto enviado**

| Chave | Descrição |
|---|---|
| `completo` | Todos os arquivos selecionados pela estratégia. No `baseline`, o conteúdo integral; no `rag`, no máximo 4.000 caracteres por arquivo. |
| `topk` | Apenas `k` arquivos por seção, cada um com no máximo 4.000 caracteres. |

**Seleção dos k arquivos** (somente com `topk`)

| Chave | Descrição |
|---|---|
| `embeddings` | Os `k` arquivos mais próximos, por similaridade de embeddings, da consulta de cada seção (RAG). |
| `heuristica` | Os mesmos `k` arquivos em todas as seções: manifestos primeiro, depois código-fonte, por número de linhas. Sem embeddings. |

Combinações e o que cada uma representa:

| Configuração | Uso |
|---|---|
| `baseline / completo` | Versão original do pipeline. |
| `baseline / topk / embeddings` | Prompts originais com recuperação. |
| `rag / topk / embeddings` | Pipeline com recuperação por embeddings. |
| `rag / topk / heuristica` | Mesmos prompts e `k`, sem recuperação (controle). |
| `rag / completo` | Mesmos prompts, sem limite de `k`. |

`num_ctx` e `seed` são enviados ao Ollama em todas as chamadas, e as chamadas com prompt provavelmente truncado são contadas.

## Instalação

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[app]"            # interface
pip install -e ".[app,eval]"       # inclui BERTScore, METEOR e scipy
```

Modelos no Ollama:

```bash
ollama pull qwen2.5-coder:7b       # geração
ollama pull nomic-embed-text       # embeddings
ollama pull llama3.1:8b            # juiz
```

## Uso

```bash
streamlit run apps/streamlit/app.py

python -m benchmark.run_benchmark --tier pequeno --models qwen2.5-coder:7b --repeats 3
python -m benchmark.run_benchmark --tier medio --selections embeddings heuristica
python -m benchmark.summarize_results benchmark_results/runs.csv

python -m unittest discover -s tests
```

## Juiz

O juiz é um segundo modelo que audita cada seção gerada e devolve uma lista de críticas. A contagem de críticas é a métrica `falhas_juiz_total`.

- **Interface:** marque "Executar juiz LLM após a geração" e informe o modelo juiz. As críticas aparecem no expander "Juiz" de cada seção, e "Avaliar execução" inclui o total no resultado. Se o juiz falhar (por exemplo, modelo não baixado), o guia é mantido e aparece um aviso.
- **Benchmark:** o juiz roda por padrão, depois da geração, e não entra no tempo medido. `--no-judge` desativa e `--judge-model` troca o modelo.
- **Modelo:** use uma família diferente da do gerador para reduzir o viés de autoavaliação.
- **Limitação:** o juiz recebe apenas o texto da seção, não o código do repositório. Ele avalia estrutura, coerência e aderência aos frameworks, mas não confere afirmações contra o código. Essa checagem é feita pelo verificador de referências (`refs_inexistentes`).

## Docker

```bash
docker compose up --build
```

Sobe o Ollama, baixa os modelos (`pull_models.sh`) e inicia a interface em `http://localhost:8501`. Para usar a GPU NVIDIA, descomente o bloco `deploy` do serviço `ollama`. O devcontainer usa os mesmos serviços.

## Documentação

- `docs/EXPERIMENTO.md`: variáveis, métricas e protocolo.
