"""Seções do guia (Diátaxis e C4) com consulta de recuperação, plano e instrução de escrita."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Section:
    key: str
    title: str
    filename: str
    retrieval_query: str
    plan_instruction: str
    write_instruction: str
    few_shot_example: str
    needs_mermaid: bool = False


_MERMAID_RULES = """
REGRAS RIGOROSAS DO MERMAID (SINTAXE INVIOLÁVEL):
- Abra o código com ```mermaid e feche com ```.
- Use apenas sintaxe Mermaid pura (`flowchart TB` ou `flowchart LR`), NUNCA a sintaxe nativa `C4Context`.
- IDs dos nós devem ser alfanuméricos simples, sem acentos (ex: Player, TicTacToeGame, PaymentAPI).
- Rótulo de seta entre aspas duplas, delimitado por barras verticais: `Origem -->|"Rótulo"| Destino`.
- Para quebrar linha dentro de um nó/rótulo, use a tag HTML `<br/>`. Nunca use `\\n`.
"""

SECTIONS: list[Section] = [
    Section(
        key="c4_level1",
        title="Visão Geral e Contexto (C4 Nível 1)",
        filename="01_c4_contexto.md",
        retrieval_query=(
            "ponto de entrada da aplicação, README, propósito do sistema, "
            "clientes externos, APIs de terceiros, autenticação, integrações externas"
        ),
        plan_instruction=(
            "Liste em formato curto (JSON simples): o(s) ator(es)/usuário(s), o sistema "
            "principal, e quaisquer sistemas externos REAIS identificados no código "
            "(ex.: APIs de terceiros, gateways de pagamento, serviços de autenticação). "
            "Se não houver nenhum sistema externo real, diga isso explicitamente. "
            "Não inclua ambiente de execução (navegador, SO, terminal) como sistema externo."
        ),
        write_instruction=f"""
Gere o documento de Contexto (C4 Nível 1) em Markdown, usando o PLANO acima como
base e o CÓDIGO RELEVANTE RECUPERADO como evidência.

ESTRUTURA OBRIGATÓRIA:
# Visão Geral e Contexto (C4 Nível 1) - [NOME DO PROJETO]

## Descrição do Sistema
2 a 3 parágrafos: o que o projeto é, quem interage com ele, tecnologia base.

## Tabela de Elementos
| Elemento | Tipo | Descrição e Papel no Ecossistema |

## Diagrama de Contexto
```mermaid
flowchart TB
    Ator["Nome<br/>Papel"] -->|"Ação"| Sistema["Nome do Projeto<br/>Tecnologia"]
```
{_MERMAID_RULES}
""",
        few_shot_example="""
EXEMPLO (projeto fictício "TaskAPI"):
Entrada observada: endpoints REST que criam tarefas e chamam a API da Stripe para cobrança.
Saída esperada (trecho):
| Cliente | Ator / Usuário | Consome a API para criar/consultar tarefas |
| TaskAPI | Sistema Principal | Gerencia o ciclo de vida das tarefas |
| Stripe | Sistema Externo | Processa cobranças de pagamento |
```mermaid
flowchart TB
    Cliente["Cliente<br/>Usuário"] -->|"Cria/consulta tarefas"| TaskAPI["TaskAPI<br/>FastAPI"]
    TaskAPI -->|"Processa cobrança"| Stripe["Stripe<br/>Gateway de Pagamento"]
```
""",
        needs_mermaid=True,
    ),
    Section(
        key="c4_level2",
        title="Contêineres (C4 Nível 2)",
        filename="02_c4_containers.md",
        retrieval_query=(
            "arquivos de configuração, docker-compose, manifestos de dependência, "
            "scripts de entrada, servidor web, banco de dados, filas, workers"
        ),
        plan_instruction=(
            "Liste os CONTÊINERES reais do projeto (aplicações web/mobile, APIs, "
            "bancos de dados, filas, scripts/módulos executáveis principais) e a "
            "tecnologia de cada um. Não detalhe classes/arquivos isolados."
        ),
        write_instruction=f"""
Gere o documento de Contêineres (C4 Nível 2) em Markdown, usando o PLANO e o
CÓDIGO RELEVANTE RECUPERADO como evidência.

ESTRUTURA OBRIGATÓRIA:
# Contêineres (C4 Nível 2) - [NOME DO PROJETO]

## Descrição dos Contêineres
Para cada contêiner: nome, tecnologia, responsabilidade.

## Diagrama de Contêineres
```mermaid
flowchart TB
    subgraph SystemBoundary["Nome Real do Sistema"]
        A["Contêiner A<br/>Tecnologia"]
        B["Contêiner B<br/>Tecnologia"]
    end
    A -->|"chama/consulta"| B
```
{_MERMAID_RULES}
- O título do subgraph SystemBoundary DEVE ser o nome real do software.
""",
        few_shot_example="",
        needs_mermaid=True,
    ),
    Section(
        key="c4_level3",
        title="Componentes (C4 Nível 3)",
        filename="03_c4_components.md",
        retrieval_query=(
            "módulos internos, controllers, services, handlers, managers, "
            "repositories, classes principais, organização de pastas do código"
        ),
        plan_instruction=(
            "Identifique o contêiner principal da aplicação e liste os módulos/"
            "componentes lógicos internos reais (controllers, services, handlers, "
            "managers, repositories etc.), evitando listar arquivos isolados como "
            "se fossem componentes."
        ),
        write_instruction=f"""
Gere o documento de Componentes (C4 Nível 3) em Markdown, usando o PLANO e o
CÓDIGO RELEVANTE RECUPERADO como evidência.

ESTRUTURA OBRIGATÓRIA:
# Componentes (C4 Nível 3) - [NOME DO PROJETO]

## Descrição dos Componentes
Para cada componente: responsabilidade e como se conecta aos outros.

## Diagrama de Componentes
```mermaid
flowchart TB
    subgraph ContainerBoundary["Nome do Contêiner Principal"]
        C1["Componente 1"]
        C2["Componente 2"]
    end
    C1 -->|"chama"| C2
```
{_MERMAID_RULES}
""",
        few_shot_example="",
        needs_mermaid=True,
    ),
    Section(
        key="tutorial",
        title="Tutorial: Primeiros Passos",
        filename="04_tutorial.md",
        retrieval_query=(
            "instruções de instalação, dependências, comando para rodar o projeto, "
            "variáveis de ambiente, README, arquivo principal de execução"
        ),
        plan_instruction=(
            "Liste os passos mínimos, na ordem correta, para alguém com o "
            "repositório clonado rodar o projeto pela primeira vez (instalação de "
            "dependências, variáveis de ambiente necessárias, comando de execução)."
        ),
        write_instruction="""
Gere o TUTORIAL "Primeiros Passos" em Markdown, orientado a aprendizagem prática
(framework Diátaxis), assumindo que o leitor já está com o repositório clonado,
na raiz dele pelo terminal. Use o PLANO e o CÓDIGO RELEVANTE RECUPERADO como
evidência. Se alguma informação de instalação/execução não puder ser confirmada
pelo código/README, diga isso explicitamente em vez de inventar.

# Tutorial: Primeiros Passos
""",
        few_shot_example="",
    ),
    Section(
        key="howto",
        title="Guia Prático (How-To)",
        filename="05_howto.md",
        retrieval_query=(
            "testes automatizados, scripts de build, arquivos de configuração, "
            "pontos de extensão, exemplos de uso, comandos de desenvolvimento"
        ),
        plan_instruction=(
            "Identifique de 2 a 4 tarefas práticas e reais que um desenvolvedor "
            "precisaria fazer neste projeto específico (ex.: rodar os testes, "
            "adicionar uma rota, configurar uma variável de ambiente)."
        ),
        write_instruction="""
Gere o guia de COMO FAZER (How-To Guides, framework Diátaxis) em Markdown.
Orientado a tarefas específicas: receitas diretas no formato "Como [Ação]",
tom imperativo. Use o PLANO e o CÓDIGO RELEVANTE RECUPERADO como evidência.

# Guia Prático de Desenvolvimento (How-To)
""",
        few_shot_example="",
    ),
    Section(
        key="reference",
        title="Referência Técnica",
        filename="06_reference.md",
        retrieval_query=(
            "assinaturas de funções e classes públicas, endpoints, parâmetros, "
            "variáveis de configuração, arquivos de API"
        ),
        plan_instruction=(
            "Liste os elementos de referência mais importantes identificados "
            "(funções/classes públicas, endpoints, parâmetros, variáveis de "
            "ambiente) com nomes EXATOS extraídos do código."
        ),
        write_instruction="""
Gere a REFERÊNCIA TÉCNICA (framework Diátaxis) em Markdown. Tom neutro e
descritivo — não ensine, não explique conceitos de arquitetura, apenas liste
e descreva com rigor. Use o PLANO e o CÓDIGO RELEVANTE RECUPERADO como
evidência, com nomes exatos de arquivos, classes, funções e parâmetros.

# Referência Técnica
""",
        few_shot_example="",
    ),
    Section(
        key="explanation",
        title="Entendimento Arquitetural",
        filename="07_explanation.md",
        retrieval_query=(
            "fluxo principal de execução, ponto de entrada, chamadas entre "
            "módulos, decisões de arquitetura, ciclo de vida da aplicação"
        ),
        plan_instruction=(
            "Descreva em tópicos o ciclo de vida/fluxo principal da aplicação: "
            "por onde a execução começa e como os dados/eventos percorrem os "
            "módulos até o resultado final."
        ),
        write_instruction="""
Gere o documento de ENTENDIMENTO ARQUITETURAL (pilar Explanation do Diátaxis)
em Markdown. Foco em conceitos e entendimento: como a aplicação funciona
internamente de ponta a ponta. Use o PLANO e o CÓDIGO RELEVANTE RECUPERADO
como evidência.

# Entendimento Arquitetural e Fluxo da Aplicação
""",
        few_shot_example="",
    ),
]


JUDGE_SYSTEM_PROMPT = """
Você é um auditor sênior de documentação técnica em software.
Será apresentado um documento gerado por outro LLM, baseado nos frameworks
Diátaxis e C4 Model, destinado a servir como parte de um Guia de Projeto de
Software. Seu papel é analisá-lo e verificar se ele segue esses frameworks
adequadamente, apontando erros e pontos de melhoria onde for aplicável.

REGRAS OBRIGATÓRIAS DE RESPOSTA:
1. Retorne EXCLUSIVAMENTE uma lista de sugestões de melhoria em bullet points (*).
2. Cada bullet point deve conter EXATAMENTE UMA crítica acionável e direta.
3. Se não houver problemas relevantes, retorne "* Nenhum problema relevante identificado."
"""


def domain_adaptation_hint(category: str) -> str:
    hints = {
        "api": "Este é um projeto de API/back-end. Use terminologia de endpoints, rotas, autenticação e integrações.",
        "webapp": "Este é um projeto de aplicação web front-end. Use terminologia de componentes de UI, estado, rotas de página.",
        "cli": "Este é um projeto de ferramenta de linha de comando. Use terminologia de comandos, flags e subcomandos.",
        "game": "Este é um projeto de jogo. Use terminologia de loop de jogo, entidades, cenas e eventos.",
        "lib": "Este é um projeto de biblioteca/pacote reutilizável. Use terminologia de API pública, módulos exportados e dependências.",
        "desconhecido": "Não foi possível classificar o domínio do projeto com confiança; evite assumir um tipo específico sem evidência.",
    }
    return hints.get(category, hints["desconhecido"])
