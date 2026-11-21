from __future__ import annotations

import os
from datetime import datetime

import streamlit as st

from docgen import harness
from docgen.analyzer import build_tree, find_readme
from docgen.edit_rate import compute_edit_rate
from docgen.evaluation import evaluate_markdown, evaluate_run, full_metrics_available
from docgen.hardware import estimate_tokens_from_chars, estimate_vram_gb
from docgen.ollama_client import OllamaClient
from docgen.pipeline import MAX_CHARS_PER_FILE, generate_documents
from docgen.references import reference_for
from docgen.repository import download_github_repository, load_from_zip

LANGUAGE_LABELS = {"pt": "Português", "en": "English"}
RESERVED_PROMPT_TOKENS = 3000
REFERENCE_LABELS = {"translated": "traduzido", "original": "original", "none": "nenhum"}

st.set_page_config(
    page_title="Gerador Docs (DocGen)",
    page_icon="📘",
    layout="wide",
)

st.title("📘 Gerador Docs")
st.caption(
    "DocGen: Gerador de documentação/guia de projetos."
)

with st.sidebar:
    st.header("🌐 Idioma")
    language = st.radio("Idioma dos prompts e dos documentos", list(LANGUAGE_LABELS), format_func=LANGUAGE_LABELS.get, key="language")

    st.divider()
    st.header("🤖 Modelos")
    model = st.text_input("Modelo de geração", value="qwen2.5-coder:7b")
    judge_model = st.text_input("Modelo juiz", value="gemma4:12b")
    ollama_host = st.text_input("Endereço do Ollama", value=os.environ.get("OLLAMA_HOST", "http://localhost:11434"))

    st.divider()
    st.header("📏 Contexto")
    num_ctx = st.select_slider("num_ctx", options=[4096, 8192, 16384, 32768], value=16384)
    use_top_k = st.checkbox("Limitar a k arquivos (repositórios grandes)", value=False)
    top_k = st.slider("Número de arquivos (k)", 2, 40, 8, disabled=not use_top_k)
    vram_est = estimate_vram_gb(model, num_ctx)
    if vram_est:
        st.caption(f"VRAM estimada: {vram_est} GB")

    with st.expander("🎛️ Parâmetros de geração"):
        temperature = st.number_input("temperature", 0.0, 2.0, 0.2, 0.05)
        num_predict = st.number_input("num_predict", 256, 16384, 8192, 256)
        repeat_penalty = st.number_input("repeat_penalty", 1.0, 2.0, 1.15, 0.05)
        repeat_last_n = st.number_input("repeat_last_n", 0, 1024, 128, 16)
        seed = st.number_input("seed (0 = aleatória)", min_value=0, value=0, step=1)

    st.divider()
    st.header("🔧 Opções")
    use_mermaid_repair = st.checkbox("Reparo de Mermaid", value=False)
    use_judge = st.checkbox("Executar juiz LLM após a geração", value=False)

st.divider()
st.subheader("📁 1. Repositório")

source_type = st.radio("Origem", ["GitHub", "ZIP"], horizontal=True)

if source_type == "GitHub":
    github_url = st.text_input("URL do GitHub")
    if github_url and st.button("Carregar repositório"):
        with st.spinner("Clonando..."):
            try:
                st.session_state["repo"] = download_github_repository(github_url)
                st.session_state.pop("result", None)
            except Exception as exc:
                st.error(str(exc))
else:
    uploaded = st.file_uploader("Arquivo .zip", type=["zip"])
    if uploaded and st.button("Carregar ZIP"):
        with st.spinner("Extraindo..."):
            try:
                st.session_state["repo"] = load_from_zip(uploaded)
                st.session_state.pop("result", None)
            except Exception as exc:
                st.error(str(exc))

repo = st.session_state.get("repo")

if repo:
    st.divider()
    st.subheader("🔎 2. Análise")

    entries, stats = harness.scan_files(repo.path)
    selected = harness.select_files(entries, top_k if use_top_k else None, MAX_CHARS_PER_FILE)
    sent_tokens = estimate_tokens_from_chars(sum(len(c) for _, c in selected))

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Arquivos no repositório", stats["total_files"])
    c2.metric("Arquivos válidos", stats["selected_files"])
    c3.metric("Arquivos enviados", len(selected))
    c4.metric("Tokens estimados no código", f"{sent_tokens:,}")

    if sent_tokens + RESERVED_PROMPT_TOKENS > num_ctx:
        st.warning(
            f"O código enviado (~{sent_tokens:,} tokens) mais o prompt de sistema excede num_ctx={num_ctx}. "
            "Parte do código será truncada. Reduza k ou aumente o num_ctx."
        )

    with st.expander("Árvore do repositório"):
        st.code(build_tree(repo.path), language="text")

    with st.expander("Arquivos enviados ao modelo"):
        st.dataframe(
            [{"arquivo": p, "caracteres": len(c)} for p, c in selected],
            hide_index=True,
        )
    
    st.divider()
    st.subheader("⚙️ 3. Geração")

    if st.button("Gerar guia", type="primary"):
        progress_bar = st.progress(0.0)
        status = st.empty()

        def on_progress(stage: str, detail: str, fraction: float) -> None:
            progress_bar.progress(min(fraction, 1.0))
            status.write(f"{stage}: {detail}")

        try:
            client = OllamaClient(
                model=model,
                host=ollama_host,
                num_ctx=num_ctx,
                num_predict=int(num_predict),
                temperature=float(temperature),
                repeat_penalty=float(repeat_penalty),
                repeat_last_n=int(repeat_last_n),
                seed=int(seed) or None,
            )
            available = client.check()
            if not any(model == item or item.startswith(model + ":") for item in available):
                st.warning(f"O modelo {model} não consta na lista do Ollama.")

            result = generate_documents(
                repo_path=repo.path,
                repo_name=repo.name,
                client=client,
                language=language,
                top_k=top_k if use_top_k else None,
                use_mermaid_repair=use_mermaid_repair,
                progress_callback=on_progress,
            )

            reference_text, reference_kind = reference_for(repo.path, repo.name, language)
            readme_text = find_readme(repo.path)
            st.session_state["result"] = result
            st.session_state["repo_path"] = repo.path
            st.session_state["reference"] = (reference_text, reference_kind)
            st.session_state["readme"] = readme_text
            st.session_state["run_options"] = {
                "idioma": language, "k": top_k if use_top_k else "todos",
                "temperature": temperature, "num_predict": int(num_predict),
                "repeat_penalty": repeat_penalty, "repeat_last_n": int(repeat_last_n),
                "seed": int(seed) or None, "reparo_mermaid": use_mermaid_repair,
            }

            if use_judge:
                status.write("juiz: auditando documentos")
                try:
                    for item in result.documents:
                        evaluate_markdown(client, result.language, item, readme_text, judge_model)
                except Exception as exc:
                    st.warning(f"Falha no juiz (o guia foi mantido): {exc}")

            st.success(f"Guia gerado em {result.total_elapsed_seconds:.1f} s")
        except Exception as exc:
            st.error(f"Falha na geração: {exc}")

result = st.session_state.get("result")

if result:
    st.divider()
    st.subheader("📄 4. Resultado")

    cols = st.columns(5)
    cols[0].metric("Idioma", LANGUAGE_LABELS[result.language])
    cols[1].metric("Tempo total", f"{result.total_elapsed_seconds:.1f} s")
    cols[2].metric("Tokens (entrada / saída)", f"{result.usage.prompt_tokens:,} / {result.usage.output_tokens:,}")
    cols[3].metric("Arquivos enviados", len(result.documents[0].files_sent))
    cols[4].metric("Mermaid reparado", sum(1 for d in result.documents if d.mermaid_repaired))

    if result.usage.truncated_calls:
        st.warning(
            f"{result.usage.truncated_calls} chamada(s) com prompt provavelmente truncado por num_ctx={result.num_ctx}."
        )

    full_guide = result.assemble_markdown()
    metadata = (
        "\n---\n## Metadados\n\n"
        f"- Data: {datetime.now().isoformat(timespec='seconds')}\n"
        f"- Repositório: {result.repo_name}\n"
        f"- Modelo: {result.model}\n"
        f"- num_ctx: {result.num_ctx}\n"
        f"- Opções: {st.session_state.get('run_options', {})}\n"
        f"- Tempo total: {result.total_elapsed_seconds:.2f} s\n"
        f"- Tokens: entrada={result.usage.prompt_tokens}, saída={result.usage.output_tokens}, "
        f"truncadas={result.usage.truncated_calls}\n"
        f"- Tempo por documento: {', '.join(f'{d.document.key}={d.elapsed_seconds:.1f}s' for d in result.documents)}\n"
    )

    st.download_button(
        "⬇️ Baixar guia completo (.md)",
        data=full_guide + "\n" + metadata,
        file_name=f"{result.repo_name}_guia_{result.language}.md",
        mime="text/markdown",
    )

    tabs = st.tabs([d.document.title(result.language) for d in result.documents])
    for tab, item in zip(tabs, result.documents):
        with tab:
            info = st.columns(3)
            info[0].caption(f"Tempo: {item.elapsed_seconds:.1f} s")
            info[1].caption(f"Tokens: {item.prompt_tokens:,} / {item.output_tokens:,}")
            info[2].caption(f"Mermaid reparado: {'sim' if item.mermaid_repaired else 'não'}")

            if item.judge_raw is not None:
                with st.expander("Juiz"):
                    if item.judge:
                        st.json(item.judge)
                    else:
                        st.warning("Resposta do juiz fora do formato JSON esperado.")
                        st.text(item.judge_raw)

            st.download_button(
                f"Baixar {item.document.filename}",
                data=item.content,
                file_name=item.document.filename,
                mime="text/markdown",
                key=f"dl_{item.document.key}",
            )
            st.markdown(item.content)

    st.divider()
    st.subheader("📊 5. Avaliação")

    reference_text, reference_kind = st.session_state.get("reference", ("", "none"))
    repo_path = st.session_state.get("repo_path")
    if reference_text.strip():
        st.caption(f"Referência: README {REFERENCE_LABELS[reference_kind]}.")
        if not full_metrics_available():
            st.caption("bert-score e nltk ausentes: usando sobreposição lexical.")
    else:
        st.caption("Repositório sem README de referência.")

    if st.button("Avaliar execução"):
        st.json(evaluate_run(result, repo_path, reference_text, reference_kind))

    st.divider()
    st.subheader("✏️ 6. Taxa de edição")
    revised = st.text_area("Guia revisado (Markdown)", height=200)
    if revised.strip() and st.button("Calcular taxa de edição"):
        st.json(compute_edit_rate(full_guide, revised))
