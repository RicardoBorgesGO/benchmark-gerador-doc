# Guia de Projeto LLM – Piloto local com Ollama

Piloto experimental para geração automática de Guia de Projeto de Software a partir de um repositório GitHub ou arquivo `.zip`, usando um modelo de linguagem executado localmente via Ollama.

## Objetivo

O pipeline foi desenhado para o projeto de pesquisa:

> Uso de modelos de linguagem open source executados em hardware on premises de baixo custo para geração de Guia de Projeto de Software.

A abordagem é deliberadamente simples para o piloto:

1. Receber URL de um repositório GitHub ou `.zip`.
2. Extrair/baixar o projeto.
3. Construir uma visão estrutural do repositório.
4. Selecionar arquivos relevantes, ignorando binários, dependências e artefatos.
5. Gerar resumos locais por arquivo/módulo.
6. Consolidar os resumos.
7. Gerar o Guia de Projeto seguindo uma estrutura inspirada em C4 + Diátaxis.
8. Registrar tempo e metadados do experimento.

## Arquitetura

```text
Streamlit
   |
   v
Repository Loader
   |---- GitHub URL
   |---- ZIP
   v
Repository Analyzer
   |---- árvore
   |---- arquivos relevantes
   |---- estatísticas
   v
Ollama
   |---- resumo de arquivos
   |---- consolidação
   |---- guia final
   v
Guide (.md)
```

## Requisitos

- Python 3.11+
- Ollama instalado e executando localmente
- Git instalado (necessário para URLs GitHub)
- Um modelo disponível no Ollama

### Modelo inicial sugerido

```bash
ollama pull qwen2.5-coder:7b
```

O projeto deixa o modelo configurável pela interface.

## Instalação

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

No Windows:

```powershell
.venv\Scripts\activate
pip install -r requirements.txt
```

## Execução

```bash
streamlit run app.py
```

Abra o endereço mostrado pelo Streamlit, normalmente:

```text
http://localhost:8501
```

## Primeiro teste

Recomenda-se começar com um projeto pequeno.

Na interface:

1. Selecione `GitHub`.
2. Informe uma URL pública, por exemplo:
   `https://github.com/pallets/flask`
3. Selecione o modelo `qwen2.5-coder:7b`.
4. Limite o número de arquivos para algo como 30–50 no primeiro teste.
5. Clique em `Gerar Guia`.

## Observações experimentais

O piloto não pretende reproduzir ainda todo o protocolo experimental da dissertação. Ele cria o pipeline funcional que depois poderá ser utilizado para:

- comparar diferentes modelos;
- comparar diferentes tamanhos de repositório;
- medir tempo de geração;
- medir quantidade de arquivos processados;
- avaliar documentação de referência com BERTScore/METEOR;
- avaliar repositórios sem documentação de referência com LLM-as-a-judge;
- registrar taxa de edição humana posteriormente.

## Estrutura

```text
guia_projeto_llm_piloto/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
└── core/
    ├── __init__.py
    ├── analyzer.py
    ├── ollama_client.py
    ├── prompts.py
    └── repository.py
```
