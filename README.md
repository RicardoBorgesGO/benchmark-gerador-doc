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

## Estratégias de geração

| Chave | Descrição |
|---|---|
| `rag` | Mapa de assinaturas do repositório, recuperação por embeddings dos arquivos relevantes a cada seção, plano antes da escrita, exemplo de formato e reparo de Mermaid. |
| `baseline` | Estratégia da branch `baseline`: todo o código em um único prompt por documento, com os prompts de sistema e a seleção de arquivos originais (`src/docgen/baseline.py`, `baseline_prompts.py`). |
| `flat` | Mesmo formato da estratégia `baseline` (repositório inteiro por seção), mas usando os prompts das seções do `rag`. Serve de controle para isolar o efeito da recuperação. |

Nas três, `num_ctx` e `seed` são enviados ao Ollama e as chamadas com prompt provavelmente truncado são contadas.

## Instalação

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[app]"            # interface
pip install -e ".[app,eval]"       # inclui BERTScore, METEOR e scipy
```

Modelos no Ollama:

```bash
ollama pull qwen2.5-coder:7b
ollama pull nomic-embed-text
ollama pull llama3.1:8b            # juiz
```

## Uso

```bash
streamlit run apps/streamlit/app.py

python -m benchmark.run_benchmark --tier pequeno --models qwen2.5-coder:7b --repeats 3
python -m benchmark.summarize_results benchmark_results/runs.csv

python -m unittest discover -s tests
```

## Docker

```bash
docker compose up --build
```

Sobe o Ollama, baixa os modelos (`pull_models.sh`) e inicia a interface em `http://localhost:8501`. Para usar a GPU NVIDIA, descomente o bloco `deploy` do serviço `ollama`. O devcontainer usa os mesmos serviços.

## Docs

Veja `docs/EXPERIMENTO.md` para as métricas e o protocolo.
