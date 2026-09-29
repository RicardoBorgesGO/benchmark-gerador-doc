Deixar API do OLLAMA ativa antes de rodar

# Executar APP
pip install -r requirements.txt
fastapi run api.py
streamlit run app.py

# Compilar modelos
ollama create doc-diataxis-tutorial -f Modelfiles/Modelfile.tutorial
ollama create doc-diataxis-howto -f Modelfiles/Modelfile.howto
ollama create doc-diataxis-reference -f Modelfiles/Modelfile.reference
ollama create doc-diataxis-explanation -f Modelfiles/Modelfile.explanation
ollama create doc-c4-level1 -f Modelfiles/Modelfile.c4level1
ollama create doc-c4-level2 -f Modelfiles/Modelfile.c4level2
ollama create doc-c4-level3 -f Modelfiles/Modelfile.c4level3

# Executar com Docker
docker compose up --build

- Ollama: http://localhost:11434
- API (FastAPI): http://localhost:8000/docs
- App (Streamlit): http://localhost:8501

Na primeira execução o serviço `ollama-init` baixa o `qwen2.5-coder:7b` e compila os Modelfiles
(`create_models.sh`); os modelos ficam no volume `ollama_data`. Os documentos gerados ficam em `./autodoc`.
Para GPU NVIDIA, descomente o bloco `deploy` do serviço `ollama` no `docker-compose.yml`.

# Devcontainer
Abra a pasta `app_ricardo` no VS Code e use "Dev Containers: Reopen in Container".
Ele vai subir o o ollama (com os modelos compilados) e um container de desenvolvimento; dentro dele:

fastapi dev api.py --host 0.0.0.0
streamlit run app.py
