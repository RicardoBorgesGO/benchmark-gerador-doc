SYSTEM_PROMPT = """
Você é um engenheiro de software responsável por produzir documentação técnica
precisa a partir de um repositório de código.

Regras:
- Não invente funcionalidades, componentes, dependências ou fluxos.
- Diferencie fatos observados de inferências.
- Quando a evidência for insuficiente, escreva "não identificado no código analisado".
- Use nomes reais de arquivos, classes, funções, módulos e dependências quando disponíveis.
- Priorize relações entre componentes e o propósito do sistema.
- A documentação deve ser útil para onboarding de um novo desenvolvedor.
- Responda em português do Brasil.
"""


def file_summary_prompt(path: str, content: str) -> str:
    return f"""
Analise o arquivo abaixo como parte de um repositório maior.

ARQUIVO: {path}

CÓDIGO/CONTEÚDO:
```text
{content}
```

Produza um resumo técnico curto contendo:
1. propósito do arquivo;
2. principais classes, funções ou componentes;
3. dependências relevantes;
4. entradas e saídas importantes;
5. relações aparentes com outros módulos;
6. observações arquiteturais relevantes.

Não invente informações. Se algo não puder ser determinado, indique isso.
"""


def final_guide_prompt(tree: str, stats: dict, summaries: str) -> str:
    return f"""
Gere um Guia de Projeto de Software para o repositório analisado.

A documentação deve ser orientada a onboarding e manutenibilidade e deve
combinar princípios do Modelo C4 e da abordagem Diátaxis.

Estrutura obrigatória:

# Guia de Projeto de Software

## 1. Visão geral
- propósito do sistema;
- principais funcionalidades identificadas;
- tecnologias.

## 2. Estrutura do repositório
Explique os principais diretórios e arquivos.

## 3. Arquitetura
Apresente uma visão textual:
- C4 nível Context;
- C4 nível Container, quando houver evidência;
- principais componentes/módulos.

## 4. Fluxos principais
Descreva os fluxos de execução ou de negócio que puderem ser identificados.

## 5. Guia de instalação e execução
Forneça instruções somente quando existirem evidências no README,
arquivos de configuração ou scripts analisados.

## 6. Guia de tarefas comuns
Inclua orientações de manutenção/desenvolvimento quando houver evidência.

## 7. Referência técnica
Liste APIs, módulos, classes, funções, configurações ou comandos relevantes.

## 8. Explicações arquiteturais
Explique decisões e relações importantes identificadas no código.

## 9. Pontos de atenção
Liste ambiguidades, lacunas documentais, riscos de manutenção ou partes
que exigiriam confirmação humana.

## 10. Limitações da análise
Informe que a documentação foi produzida a partir dos arquivos analisados
e identifique eventuais partes não processadas.

REGRAS CRÍTICAS:
- Não invente.
- Não atribua comportamento a um componente sem evidência.
- Se os dados forem insuficientes, diga explicitamente.
- Não copie grandes trechos de código.
- Use tabelas quando forem úteis.
- O resultado deve ser um documento técnico, não uma conversa.

ESTRUTURA DO REPOSITÓRIO:
{tree}

ESTATÍSTICAS:
{stats}

RESUMOS DOS ARQUIVOS:
{summaries}
"""
