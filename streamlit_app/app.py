from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path

import streamlit as st

from core.analyzer import build_tree, collect_files, read_file, summarize_stats
from core.ollama_client import OllamaClient
from core.prompts import SYSTEM_PROMPT, file_summary_prompt, final_guide_prompt
from core.repository import load_from_github, load_from_zip

st.set_page_config(
    page_title="Guia de Projeto LLM",
    page_icon="📚",
    layout="wide",
)

st.title("📚 Guia de Projeto LLM – Piloto local")
st.caption("Piloto experimental para geração de documentação técnica de repositórios com Ollama.")

with st.sidebar:
    st.header("Configuração")

    model = st.text_input(
        "Modelo Ollama",
        value="qwen2.5-coder:7b",
        help="O modelo precisa estar previamente disponível no Ollama.",
    )

    ollama_host = st.text_input(
        "Ollama",
        value="http://localhost:11434",
    )

    max_files = st.slider(
        "Máximo de arquivos analisados",
        min_value=5,
        max_value=200,
        value=40,
        step=5,
    )

    st.info(
        "Para o primeiro teste, use 20–50 arquivos. "
        "Depois aumente gradualmente para estudar o impacto do tamanho do repositório."
    )

st.subheader("1. Fonte do projeto")

source_type = st.radio(
    "Como fornecer o repositório?",
    ["GitHub", "ZIP"],
    horizontal=True,
)

repo = None

if source_type == "GitHub":
    github_url = st.text_input(
        "URL pública do GitHub",
        placeholder="https://github.com/pallets/flask",
    )
    if github_url:
        if st.button("Carregar repositório", type="secondary"):
            with st.spinner("Clonando repositório..."):
                try:
                    st.session_state["repo"] = load_from_github(github_url)
                    st.success("Repositório carregado.")
                except Exception as exc:
                    st.error(str(exc))
else:
    uploaded = st.file_uploader(
        "Envie um arquivo .zip",
        type=["zip"],
    )
    if uploaded and st.button("Carregar ZIP", type="secondary"):
        with st.spinner("Extraindo projeto..."):
            try:
                st.session_state["repo"] = load_from_zip(uploaded)
                st.success("ZIP carregado.")
            except Exception as exc:
                st.error(str(exc))

repo = st.session_state.get("repo")

if repo:
    st.subheader("2. Análise estrutural")

    files = collect_files(repo.path, max_files=max_files)
    stats = summarize_stats(repo.path, files)

    c1, c2, c3 = st.columns(3)
    c1.metric("Arquivos visíveis", stats["all_files_visible"])
    c2.metric("Arquivos analisados", stats["files_analyzed"])
    c3.metric("Tamanho visível", f"{stats['repository_bytes_visible'] / 1024:.1f} KB")

    with st.expander("Árvore do repositório"):
        st.code(build_tree(repo.path), language="text")

    with st.expander("Arquivos selecionados"):
        st.dataframe(
            [
                {
                    "arquivo": f.path,
                    "linhas": f.lines,
                    "bytes": f.size,
                    "linguagem": f.language,
                }
                for f in files
            ],
            use_container_width=True,
            hide_index=True,
        )

    st.subheader("3. Geração")

    if st.button("🚀 Gerar Guia de Projeto", type="primary", use_container_width=True):
        started = time.perf_counter()

        try:
            client = OllamaClient(model=model, host=ollama_host)
            available = client.check()

            if not any(model == item or item.startswith(model + ":") for item in available):
                st.warning(
                    f"O modelo '{model}' não apareceu na lista local. "
                    "A chamada ainda será tentada."
                )

            summaries = []
            progress = st.progress(0)
            status = st.empty()

            for index, file_info in enumerate(files, start=1):
                status.write(f"Analisando {index}/{len(files)}: `{file_info.path}`")
                content = read_file(repo.path, file_info.path)
                summary = client.chat(
                    SYSTEM_PROMPT,
                    file_summary_prompt(file_info.path, content),
                    temperature=0.1,
                )
                summaries.append(
                    f"### {file_info.path}\n{summary}"
                )
                progress.progress(index / len(files))

            status.write("Consolidando a documentação final...")

            final_prompt = final_guide_prompt(
                build_tree(repo.path),
                stats,
                "\n\n".join(summaries),
            )

            guide = client.chat(
                SYSTEM_PROMPT,
                final_prompt,
                temperature=0.1,
            )

            elapsed = time.perf_counter() - started

            metadata = f"""
---
## Metadados do experimento

- Data/hora: {datetime.now().isoformat(timespec="seconds")}
- Fonte: {repo.source}
- Modelo: {model}
- Arquivos analisados: {len(files)}
- Tempo total de geração: {elapsed:.2f} s
- Ollama: {ollama_host}
- Observação: piloto de geração de documentação; revisão humana permanece necessária.
"""

            final_document = guide.rstrip() + "\n" + metadata

            st.session_state["guide"] = final_document
            st.session_state["elapsed"] = elapsed

            st.success(f"Guia gerado em {elapsed:.2f} segundos.")

        except Exception as exc:
            st.error(
                "Falha durante a geração. Verifique se o Ollama está executando, "
                f"se o modelo existe e se há memória suficiente.\n\nDetalhes: {exc}"
            )

if "guide" in st.session_state:
    st.subheader("4. Resultado")

    st.download_button(
        "⬇️ Baixar Guia (.md)",
        data=st.session_state["guide"],
        file_name=f"{repo.name}_guia.md",
        mime="text/markdown",
        use_container_width=True,
    )

    st.markdown(st.session_state["guide"])
