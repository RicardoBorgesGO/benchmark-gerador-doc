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