from __future__ import annotations

import os
from datetime import datetime

import streamlit as st

from docgen.analyzer import build_tree, collect_files, find_reference_doc, summarize_stats
from docgen.edit_rate import compute_edit_rate
from docgen.evaluation import evaluate_run, full_metrics_available, run_judge
from docgen.hardware import estimate_vram_gb
from docgen.ollama_client import OllamaClient
from docgen.pipeline import run_pipeline
from docgen.repository import load_from_github, load_from_zip

STRATEGY_LABELS = {
    "baseline": "Baseline: repositório inteiro por seção (prompts e seleção originais)",
    "rag": "RAG: repo map e recuperação por seção (top-k arquivos mais relevantes)",
    "flat": "Flat: repositório inteiro por seção (prompts do RAG)",
}

st.set_page_config(page_title="Gerador Docs (DocGen)", layout="wide")
st.title("Gerador Docs (DocGen)")
st.caption(
    "benchmark-gerador-doc: Gerador de documentação (Guia de Projeto)."
)

with st.sidebar:
    st.header("Modelos")
    model = st.text_input("Modelo de geração", value="qwen2.5-coder:7b")
    embed_model = st.text_input("Modelo de embedding", value="nomic-embed-text")
    judge_model = st.text_input("Modelo juiz", value="llama3.1:8b")
    ollama_host = st.text_input("Endereço do Ollama", value=os.environ.get("OLLAMA_HOST", "http://localhost:11434"))

    st.divider()
    st.header("Estratégia e contexto")
    strategy = st.radio("Estratégia", list(STRATEGY_LABELS), format_func=STRATEGY_LABELS.get, key="strategy")
    num_ctx = st.select_slider("num_ctx", options=[4096, 8192, 16384, 32768], value=16384)
    seed = st.number_input("Seed", min_value=0, value=42, step=1)
    vram_est = estimate_vram_gb(model, num_ctx)
    if vram_est:
        st.caption(f"VRAM estimada: {vram_est} GB")

    st.divider()
    st.header("Arquivos")
    uses_selection = strategy != "baseline"
    max_files = st.slider("Máximo de arquivos", 5, 300, 60, step=5, disabled=not uses_selection)
    exclude_docs = st.checkbox("Excluir README e docs da entrada", value=True, disabled=not uses_selection)
    top_k = st.slider("Arquivos recuperados por seção (top-k)", 2, 20, 8, disabled=strategy != "rag")

    st.divider()
    st.header("Opções")
    use_plan_step = st.checkbox("Plano antes de escrever", value=True, disabled=strategy != "rag")
    use_mermaid_repair = st.checkbox("Reparo de Mermaid", value=True)
    use_judge = st.checkbox("Executar juiz LLM após a geração", value=False)

st.subheader("1. Repositório")

source_type = st.radio("Origem", ["GitHub", "ZIP"], horizontal=True)

if source_type == "GitHub":
    github_url = st.text_input("URL do GitHub")
    if github_url and st.button("Carregar repositório"):
        with st.spinner("Clonando"):
            try:
                st.session_state["repo"] = load_from_github(github_url)
                st.session_state.pop("result", None)
            except Exception as exc:
                st.error(str(exc))
else:
    uploaded = st.file_uploader("Arquivo .zip", type=["zip"])
    if uploaded and st.button("Carregar ZIP"):
        with st.spinner("Extraindo"):
            try:
                st.session_state["repo"] = load_from_zip(uploaded)
                st.session_state.pop("result", None)
            except Exception as exc:
                st.error(str(exc))

repo = st.session_state.get("repo")

if repo:
    st.subheader("2. Análise")

    files = collect_files(repo.path, max_files=max_files, exclude_docs=exclude_docs)
    stats = summarize_stats(repo.path, files)

    c1, c2, c3 = st.columns(3)
    c1.metric("Arquivos no repositório", stats["all_files_visible"])
    c2.metric("Arquivos selecionados", "todos os válidos" if strategy == "baseline" else stats["files_analyzed"])
    c3.metric("Tamanho", f"{stats['repository_bytes_visible'] / 1024:.1f} KB")

    with st.expander("Árvore do repositório"):
        st.code(build_tree(repo.path), language="text")

    if strategy != "baseline":
        with st.expander("Arquivos selecionados"):
            st.dataframe(
                [{"arquivo": f.path, "linhas": f.lines, "bytes": f.size, "linguagem": f.language} for f in files],
                hide_index=True,
            )

    st.subheader("3. Geração")

    if st.button("Gerar guia", type="primary"):
        progress_bar = st.progress(0.0)
        status = st.empty()

        def on_progress(stage: str, detail: str, fraction: float) -> None:
            progress_bar.progress(min(fraction, 1.0))
            status.write(f"{stage}: {detail}")

        try:
            client = OllamaClient(model=model, host=ollama_host, num_ctx=num_ctx, seed=int(seed))
            available = client.check()
            if not any(model == item or item.startswith(model + ":") for item in available):
                st.warning(f"O modelo {model} não consta na lista do Ollama.")

            result = run_pipeline(
                repo_path=repo.path,
                repo_name=repo.name,
                files=files,
                client=client,
                strategy=strategy,
                embed_model=embed_model,
                top_k=top_k,
                use_plan_step=use_plan_step,
                use_mermaid_repair=use_mermaid_repair,
                progress_callback=on_progress,
            )
            if use_judge:
                status.write("juiz: auditando seções")
                run_judge(result, client, judge_model)

            st.session_state["result"] = result
            st.session_state["reference_doc"] = find_reference_doc(repo.path)
            st.session_state["repo_path"] = repo.path
            st.session_state["run_options"] = {
                "plano": use_plan_step, "reparo_mermaid": use_mermaid_repair,
                "juiz": use_judge, "seed": int(seed), "top_k": top_k,
            }
            st.success(f"Guia gerado em {result.total_elapsed_seconds:.1f} s")
        except Exception as exc:
            st.error(f"Falha na geração: {exc}")

result = st.session_state.get("result")

if result:
    st.subheader("4. Resultado")

    cols = st.columns(5)
    cols[0].metric("Estratégia", result.strategy)
    cols[1].metric("Tempo total", f"{result.total_elapsed_seconds:.1f} s")
    cols[2].metric("Tokens (entrada / saída)", f"{result.usage.prompt_tokens:,} / {result.usage.output_tokens:,}")
    cols[3].metric("Arquivos na entrada", result.files_in_input)
    cols[4].metric("Mermaid reparado", sum(1 for x in result.sections if x.mermaid_repaired))

    if result.usage.truncated_calls:
        st.warning(
            f"{result.usage.truncated_calls} chamada(s) com prompt provavelmente truncado por num_ctx={result.num_ctx}."
        )

    options = st.session_state.get("run_options", {})
    full_guide = result.assemble_markdown()
    metadata = (
        "\n---\n## Metadados\n\n"
        f"- Data: {datetime.now().isoformat(timespec='seconds')}\n"
        f"- Repositório: {result.repo_name}\n"
        f"- Estratégia: {result.strategy}\n"
        f"- Modelo: {result.model}\n"
        f"- num_ctx: {result.num_ctx}\n"
        f"- Opções: {options}\n"
        f"- Tempo total: {result.total_elapsed_seconds:.2f} s\n"
        f"- Tokens: entrada={result.usage.prompt_tokens}, saída={result.usage.output_tokens}, "
        f"truncadas={result.usage.truncated_calls}\n"
        f"- Tempo por seção: {', '.join(f'{s.section.key}={s.elapsed_seconds:.1f}s' for s in result.sections)}\n"
    )

    st.download_button(
        "Baixar guia completo (.md)",
        data=full_guide + "\n" + metadata,
        file_name=f"{result.repo_name}_guia.md",
        mime="text/markdown",
    )

    tabs = st.tabs([s.section.title for s in result.sections])
    for tab, item in zip(tabs, result.sections):
        with tab:
            info = st.columns(3)
            info[0].caption(f"Tempo: {item.elapsed_seconds:.1f} s")
            info[1].caption(f"Tokens: {item.prompt_tokens:,} / {item.output_tokens:,}")
            info[2].caption(f"Mermaid reparado: {'sim' if item.mermaid_repaired else 'não'}")

            if result.strategy == "rag":
                with st.expander(f"Arquivos recuperados ({len(item.retrieved_paths)})"):
                    st.write(item.retrieved_paths)
            if item.plan:
                with st.expander("Plano"):
                    st.text(item.plan)
            if item.judge_feedback:
                with st.expander("Juiz"):
                    st.markdown(item.judge_feedback)

            st.download_button(
                f"Baixar {item.section.filename}",
                data=item.content,
                file_name=item.section.filename,
                mime="text/markdown",
                key=f"dl_{item.section.key}",
            )
            st.markdown(item.content)

    st.divider()
    st.subheader("5. Avaliação")

    reference_doc = st.session_state.get("reference_doc", "")
    repo_path = st.session_state.get("repo_path")
    if reference_doc.strip():
        st.caption("Referência: README e docs do repositório.")
        if not full_metrics_available():
            st.caption("bert-score e nltk ausentes: usando sobreposição lexical.")
    else:
        st.caption("Repositório sem documentação de referência.")

    if st.button("Avaliar execução"):
        st.json(evaluate_run(result, repo_path, reference_doc))

    st.divider()
    st.subheader("6. Taxa de edição")
    revised = st.text_area("Guia revisado (Markdown)", height=200)
    if revised.strip() and st.button("Calcular taxa de edição"):
        st.json(compute_edit_rate(full_guide, revised))
