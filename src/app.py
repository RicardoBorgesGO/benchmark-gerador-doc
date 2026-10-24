from pathlib import Path
import streamlit as st
import requests

API_URL = "http://localhost:8000/generate"
AUTODOC_DIR = Path("./autodoc")

# Configuração simples da página
st.set_page_config(page_title="Guia de Projeto LLM", page_icon="📚", layout="wide")

st.title("Gerador de Documentação Local")
st.caption("Lembre-se de estar com o Ollama e a API ativos localmente antes de gerar")

model = st.text_input(
    "Modelo Ollama",
    value="qwen2.5-coder:7b",
    help="Modelo que será utilizado pelo pipeline."
)

# 2. Campo para a URL do Repositório
github_url = st.text_input(
    "URL do Repositório GitHub",
    placeholder="https://github.com/pallets/flask"
)

# 3. Botão para acionar o pipeline
if st.button("🚀 Executar Pipeline", type="primary"):
    if not github_url.strip():
        st.warning("Por favor, informe a URL do repositório.")
    else:
        with st.spinner("Processando o repositório no pipeline... Isso pode levar alguns minutos."):
            try:
                # Monta o payload enviado para a API
                payload = {
                    "github_url": github_url.strip(),
                    "model": model.strip(),
                }
                
                # Chamada POST para a sua rota FastAPI
                response = requests.post(API_URL, json=payload, timeout=600)

                if response.status_code == 200:
                    st.success("Pipeline executado com sucesso!")
                    # Marca no session_state que a geração foi concluída com sucesso
                    st.session_state["pipeline_success"] = True
                else:
                    st.error(f"Erro na API ({response.status_code}): {response.text}")

            except requests.exceptions.RequestException as e:
                st.error(f"Falha ao conectar na API local ({API_URL}): {e}")

# 4. Exibição dos resultados varrendo a pasta ./autodoc
if AUTODOC_DIR.exists() and AUTODOC_DIR.is_dir():
    # Busca todos os arquivos .md dentro do diretório autodoc
    markdown_files = list(AUTODOC_DIR.glob("*.md"))

    if markdown_files:
        st.write("---")
        st.subheader("📁 Arquivos Gerados (`./autodoc`)")

        for file_path in markdown_files:
            # Lê o conteúdo de cada arquivo .md
            content = file_path.read_text(encoding="utf-8")
            file_name = file_path.name

            with st.expander(f"📄 {file_name}"):
                st.download_button(
                    label=f"⬇️ Baixar {file_name}",
                    data=content,
                    file_name=file_name,
                    mime="text/markdown",
                    key=f"dl_{file_name}"
                )
                st.markdown(content)