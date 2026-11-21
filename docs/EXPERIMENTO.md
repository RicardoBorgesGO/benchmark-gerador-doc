# Protocolo experimental

Alinhado ao `projeto-genai.txt`: impacto da geração com modelos de código aberto em hardware local de baixo custo sobre o tempo e a taxa de revisão humana na criação de Guias de Projeto (RTX com até 24 GB de VRAM, CPU de até 12 núcleos, 64 GB de RAM).

## 1. Variáveis

**Independentes:** repositório, modelo, idioma (`pt`, `en`), contexto (todos os arquivos ou top-k com `k` arquivos) e `num_ctx`.

**Dependentes (colunas de `generation_metrics.csv` e `evaluation_results.csv`):**

| Dimensão | Métrica |
|---|---|
| Tempo | `generation_time_seconds` (por execução e por documento) |
| Custo computacional | `prompt_tokens`, `output_tokens`, `gpu_energy_wh`, `gpu_peak_vram_mb`, `estimated_vram_gb` |
| Validade da execução | `truncated_calls` |
| Alinhamento com a documentação existente | `bert_f1`, `meteor` contra o README (`reference` indica `translated` ou `original`) |
| Qualidade segundo o juiz | `judge_*` (notas de 1 a 5), `judge_mean`, `judge_suggestions_total` |
| Fidelidade ao repositório | `references_missing`, `references_support_rate` |
| Taxa de revisão humana | `edit_rate` (interface, seção 6, ou `python -m docgen.edit_rate`) |

## 2. Execução

```bash
python -m benchmark.run_benchmark --models qwen2.5-coder:7b --repeats 3
python -m benchmark.run_benchmark --models qwen2.5-coder:7b --top-k 0 8 --resume
python -m benchmark.run_benchmark --models qwen2.5-coder:7b --languages pt en
python -m benchmark.summarize_results evaluation_results.csv
```

`--resume` pula execuções já registradas em `evaluation_results.csv`. O resumo traz média e desvio por configuração e a diferença pareada entre top-k e todos os arquivos (teste de Wilcoxon quando há `scipy` e ao menos 5 pares). Os documentos ficam em `autodoc/<modelo>/<repositório>/<idioma>/`; execuções que diferem só em `top_k`, `num_ctx` ou repetição sobrescrevem os arquivos, e os valores de cada execução ficam nos CSV.

## 3. Cuidados de validade

1. **Truncamento.** Se `chamadas_truncadas > 0`, o modelo não viu todo o código. Isso é esperado no contexto completo de repositórios grandes e deve ser reportado, não descartado. O top-k existe para esse caso.
2. **Top-k e repositórios pequenos.** Com `k` maior ou igual ao número de arquivos válidos, o conjunto enviado é o mesmo do contexto completo (a diferença fica só no limite de 4.000 caracteres por arquivo).
3. **Idioma.** BERTScore e METEOR em português são calculados contra o README traduzido; em inglês, contra o original. Os valores entre idiomas não são diretamente comparáveis, porque as referências e os prompts mudam juntos.
4. **Referência.** Repositórios sem README ficam sem BERTScore e METEOR (`referencia = nenhuma`).
5. **Juiz.** Evite usar o mesmo modelo para gerar e para julgar. O juiz recebe só o README e o texto do documento, então mede coerência com o README e não com o código; a checagem contra o código fica com `references_missing`. Valide as notas contra revisores humanos em uma amostra antes de usá-las como métrica principal.
6. **Contaminação.** Repositórios populares (`requests`, `body-parser`) podem estar nos dados de treino dos modelos.
7. **Repetições.** Sem `--seed-base` não há seed e a variação vem da temperatura; use `--repeats` e reporte média e desvio.

## 4. Parte humana

A hipótese compara com a escrita manual, então são necessários dois números humanos:

1. **Tempo de revisão:** uma pessoa revisa o guia gerado até considerá-lo utilizável para onboarding, com tempo cronometrado. Registre quem revisou e a experiência dela.
2. **Linha de base:** tempo para escrever o mesmo guia do zero (em ao menos 1 ou 2 repositórios pequenos) ou uma estimativa justificada por literatura.
3. **Taxa de edição:** `compute_edit_rate(gerado, revisado)`; palavras adicionadas e removidas distinguem "faltou conteúdo" de "havia conteúdo errado".
