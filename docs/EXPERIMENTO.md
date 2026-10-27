# Protocolo experimental

Descrição: pergunta de pesquisa (impacto na redução do
tempo e da taxa de revisão humana), hipótese (tempo de escrita inicial
reduzido, só revisões pontuais) e infraestrutura delimitada (RTX até 24 GB
VRAM, CPU até 12 núcleos, 64 GB RAM).

## 1. Variáveis

**Independentes:** repositório (porte: pequeno/médio/grande; com e sem docs),
modelo (e quantização), `num_ctx`, estratégia (`baseline`, `flat` e `rag`),
técnicas ligadas/desligadas (plano, reparo Mermaid, RAG top-k).

**Dependentes (todas já registradas em `runs.csv`):**

| Dimensão do projeto | Métrica |
|---|---|
| Tempo | `tempo_total_s`, tempo por seção (`sections.csv`) |
| Custo computacional | tokens de entrada/saída, `energia_wh`, `vram_pico_mb`, `vram_estimada_gb` |
| Validade do experimento | `chamadas_truncadas` (contexto cortado) |
| Qualidade, cenário 1 (com doc) | `bert_f1`, `meteor` contra README+docs |
| Qualidade, cenário 2 (sem doc) | `falhas_juiz_total` (juiz LLM) |
| Fidelidade | `refs_inexistentes`, `taxa_suporte_refs` (verificador determinístico) |
| Taxa de revisão humana | `edit_rate` (interface, seção 6, ou `python -m docgen.edit_rate`) |

## 2. Como executar

```bash
python -m benchmark.run_benchmark --tier pequeno --models qwen2.5-coder:7b --repeats 3
python -m benchmark.run_benchmark --tier medio --num-ctx 8192 16384 32768
python -m benchmark.summarize_results benchmark_results/runs.csv
```

Os guias gerados ficam em `benchmark_results/docs/<repo>/<modelo>/<estrategia>/rN/`
para a revisão humana.

## 3. Cuidados de validade (leia antes de coletar dados)

1. **Vazamento:** README/docs são excluídos da entrada do gerador (`exclude_docs`).
   Sem isso, BERTScore/METEOR medem cópia, não geração.
2. **Contaminação:** repositórios muito populares podem estar no treino do modelo.
   Inclua projetos pequenos, recentes ou obscuros e reporte os resultados por grupo.
3. **Truncamento:** se `chamadas_truncadas > 0`, o modelo não viu todo o código;
   reporte isso como limitação das estratégias que enviam o repositório inteiro, não descarte a linha.
4. **Repetições:** ≥3 por configuração (seed muda por repetição, registrada no CSV);
   reporte média±desvio e teste pareado.
5. **Juiz:** use família diferente do gerador e valide contra humanos (amostra de
   30–50 críticas, Cohen's kappa) antes de tratar "falhas do juiz" como métrica.
6. **Métricas com referência:** BERTScore/METEOR comparam o guia inteiro contra o
   README; servem como sinal de alinhamento, não como medida de correção.

## 4. Medindo a taxa de revisão e o tempo (parte humana)

A hipótese compara com a escrita manual, então são necessários dois números humanos:

1. **Tempo de revisão:** um desenvolvedor (idealmente que NÃO conhece o repositório
   e outro que conhece) revisa o guia gerado até considerá-lo utilizável para
   onboarding. Cronometre. Registre quem revisou e a experiência dele.
2. **Linha de base:** tempo para escrever o mesmo guia do zero (amostra menor,
   p. ex. 1–2 repositórios pequenos) ou, no mínimo, uma estimativa justificada
   por literatura. Sem isso, "redução de tempo" não é demonstrável.
3. **Taxa de edição:** `compute_edit_rate(gerado, revisado)` (palavras adicionadas ×
   removidas distinguem "faltou conteúdo" de "havia conteúdo errado").

Pedir ao revisor uma nota 1–5 de utilidade para onboarding por seção,
para triangular com as métricas automáticas.

## 5. Ablação sugerida (ordem)

1. `baseline` × `flat` × `rag` (efeito da recuperação e do prompt).
2. `rag` sem plano; sem reparo Mermaid; com top-k 4/8/16.
3. `num_ctx` 8k/16k/32k (e KV cache quantizado, se disponível).
4. Modelos 7B × 14B (trade-off qualidade × VRAM × tempo).
