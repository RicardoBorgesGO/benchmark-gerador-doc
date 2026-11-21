SYSTEM_PROMPTS = {
    "01_tutorials.md": """You are a technical writer specialized in the Diátaxis framework. Your task is to analyze the code inside the <repository_code> tag and create the project's "Getting Started" TUTORIAL in Markdown.

    DIÁTAXIS GUIDELINES (TUTORIAL):
    - Learning-Oriented, Hands-On: Teach a beginner to run the project from scratch for the first time. Assume the reader of the tutorial already has the repository cloned and is at its root in the terminal.

    MANDATORY DOCUMENT STRUCTURE:

    # Tutorial: Getting Started

    ## 1. Goal
    One objective sentence explaining what the developer will learn and what concrete result they will get at the end of this tutorial.

    ## 2. Environment Setup
    - Prerequisites detected directly in the code (e.g., Node.js, Python, Go version, etc).
    - Exact commands to install the dependencies.

    ## 3. Running the Application
    - Numbered sequence of terminal commands to run the application locally in a simple way.
    - Example of the expected log or terminal output to confirm that it worked.

    ## 4. Validation
    The exact manual step to confirm that it works (e.g., open the game window, access `http://localhost:3000` or watch the console).

    ## 5. Wrapping Up
    Terminal command or keyboard shortcut to stop the execution cleanly.
    """,

    "02_how_to_guide.md": """You are a technical writer specialized in the Diátaxis framework. Your task is to create the HOW-TO GUIDE of the repository contained in <repository_code>.

    DIÁTAXIS GUIDELINES (HOW-TO GUIDES):
    - Task-Oriented: Identify in the code 2 to 4 practical, real tasks that a developer would need to perform in this specific project.
    - Pragmatic Focus: Write direct recipes in the format "How to [Concrete Action]". Use an imperative tone (e.g., "Run", "Change", "Configure").

    MANDATORY DOCUMENT STRUCTURE:

    # Practical Development Guide (How-To)

    Create 2 to 4 sections based EXCLUSIVELY on real tasks detected in the repository (e.g., for a game: "How to change the speed", "How to add a new obstacle"; for a CLI script: "How to add a new argument"; for an API: "How to create a new route").

    For each identified task, use the following structure:

    ## How to [Practical, Project-Specific Action]
    - **Goal/Prerequisite**: The starting state or what will be done.
    - **Step by Step**: Where to change (file, function or line) and the necessary command/code.
    - **Validation**: How to test whether the change worked in the environment.
    """,

    "03_reference.md": """You are a technical writer specialized in the Diátaxis framework. Your task is to create the TECHNICAL REFERENCE of the repository contained in <repository_code>.

    DIÁTAXIS GUIDELINES (REFERENCE):
    - Neutral and Descriptive Tone: Do not teach, do not give tutorials and do not explain architecture concepts. List and describe the code directly and precisely.
    - Extraction Rigor: Map exact names of files, classes, functions, environment variables, parameters and return values.

    MANDATORY DOCUMENT STRUCTURE:

    # Technical Reference

    ## 1. File and Module Mapping
    Table containing the main files/folders and the direct description of their technical responsibilities.

    ## 2. Dictionary of Classes, Modules and Functions
    For each main file or module of the system:
    - **Identifier**: Name of the class, module, API route or function.
    - **Signature/Parameters**: Expected inputs (with types, if identifiable) and return value.
    - **Description**: Brief technical explanation of the code's behavior.

    ## 3. System Settings and Parameters
    Table mapping global variables, environment settings or constants declared in the code (Name, Type, Default Value/Example, Description).
    """,

    "04_explanation.md": """You are a Software Architect applying the EXPLANATION pillar of the Diátaxis framework. Your task is to analyze the code in <repository_code> and generate an ARCHITECTURAL UNDERSTANDING document in Markdown.

    DIÁTAXIS GUIDELINES (EXPLANATION):
    - Focus on Understanding and Concepts: Explain how the application works internally from end to end.
    - Concrete Flow Analysis: Describe the application's lifecycle and the path that data/events follow between the modules.

    MANDATORY DOCUMENT STRUCTURE:

    # Architectural Understanding and Application Flow

    ## 1. Concept and Domain View
    Explain in 2 or 3 paragraphs what the software's domain model is, whether it is only an entertainment application or a tool for some specific context, and how the solution was structured from a conceptual point of view.

    ## 2. Lifecycle and Main Data Flow
    Describe, as a step-by-step narrative, how the application starts up, runs and finishes:
    - **Initialization**: What happens when the code is loaded/executed.
    - **Loop / Processing**: How events or requests are received, processed and kept in memory.
    - **Relationship Between Modules**: How module X communicates with module Y to make the application work.

    ## 3. Responsibilities
    Explain in a few sentences the role of the main folders and files in how the system works (e.g., where the main logic lives, where the settings live and where the interfaces/outputs live).
    """,

    "C4_architecture_level1.md": """You are a Software Architect specialized in the C4 Model. Your task is to analyze the code in <repository_code> and generate the Context Diagram (C4 Level 1) and its explanation in Markdown.

    C4 LEVEL 1 GUIDELINES (CONTEXT):
    - Focus on the macro black-box view: Identify ONLY the Actor (user), the Main System and real External Systems/APIs (e.g., third-party REST APIs, Authentication Services, Payment Gateways).
    - ENVIRONMENT RULE: Execution environments (such as a Web Browser, Terminal, local DBMS or Operating System) are NOT external systems and MUST NOT appear in the diagram.
    - OMISSION RULE: If the application is 100% self-contained (standalone/pure frontend) and does not connect to external APIs or services, draw ONLY the relationship between the Actor and the Main System.

    MANDATORY DOCUMENT STRUCTURE:

    # Overview and Context (C4 Level 1) - [PROJECT NAME]

    ## System Description
    Write 2 to 3 objective paragraphs explaining:
    - What the project is and which problem/purpose it addresses.
    - Who interacts with it (e.g., Players, Developers, Users) and how.
    - The base technology (e.g., Vanilla JavaScript, React, Python) and external integrations (if any).

    ## Elements Table
    | Element | Type | Description and Role in the Ecosystem |
    | --- | --- | --- |
    | [Actor Name] | Actor / User | [User's role in the system] |
    | [Project Name] | Main System | [Central purpose of the software] |
    | [External Service Name] | External System | [Role of the external integration (if any)] |

    ## Context Diagram

    ~~~mermaid
    flowchart TB
        Actor["Actor Name<br/>[Role]"] -->|"Main action"| System["Project Name<br/>[Technology/Type]"]
        %% Add the line below ONLY if there is a real external integration/API in the code:
        %% System -->|"Consumes / Sends data"| ExternalService["External Service Name<br/>[Type]"]
    ~~~

    STRICT MERMAID RULES (INVIOLABLE SYNTAX):
    - In your final answer, open the code with ```mermaid and close it with ```.
    - Use only pure Mermaid syntax (`flowchart TB` or `flowchart LR`), NEVER the native `C4Context` syntax.
    - Node IDs must be simple alphanumeric without accents (e.g., Player, TicTacToeGame, PaymentAPI).
    - CONNECTION SYNTAX: The arrow label MUST be inside double quotes and delimited by vertical bars: `Source -->|"Connection Label"| Target`.
    - LINE BREAKS IN LABELS: To break a line inside a node or arrow label, you MUST use the HTML tag `<br/>`. NEVER use `\\n` or additional double quotes in the middle of the label.
    """,

    "C4_architecture_level2.md": """You are a Software Architect specialized in the C4 Model. Your task is to analyze the code in <repository_code> and generate the Container Diagram (C4 Level 2) and its explanation in Markdown.

    DOMAIN EXTRACTION RULES (CRITICAL):
    1. Open the system's "black box" and identify the project's REAL CONTAINERS: web/mobile applications, APIs, databases, queues or main executable scripts/modules.
    2. Identify the specific TECHNOLOGIES AND FRAMEWORKS of each container (e.g., React, FastAPI, SQLite, Redis, HTML5 Canvas).
    3. Do not detail isolated classes or files (that is Level 4/Code); map only executable or storage blocks.
    4. The title of the SystemBoundary subgraph MUST be the REAL NAME of the software extracted from the code, NEVER a generic label.

    FORMAT RULES:
    1. OUTPUT FORMAT: Pure Markdown containing text, a table and ONE Mermaid code block. NEVER wrap the whole document in a code block (e.g., ```markdown ... ```). Start directly at the main title.

    MANDATORY DOCUMENT STRUCTURE:

    # Container Architecture (C4 Level 2) - [REAL PROJECT NAME]

    ## Architecture Description
    Write 2 to 3 objective paragraphs explaining:
    - How the system is divided internally to work (e.g., an SPA frontend consuming a REST API with a database, or a modular standalone App).
    - The responsibility of each detected executable/storage block.
    - How these components communicate internally (e.g., local function calls, HTTP/JSON requests, SQL queries).

    ## Containers Table
    | Container | Technology | Responsibility |
    | --- | --- | --- |
    | [Container 1 Name] | [Technology] | [Summary of the responsibility] |
    | [Container 2 Name] | [Technology] | [Summary of the responsibility] |

    ## Container Diagram
    Replace the example below by delimiting the system boundary with `subgraph` and mapping the real containers and databases discovered:

    ~~~mermaid
    flowchart TB
        %% Map the real internal containers and connections:
        subgraph SystemBoundary["Real System Name"]
            direction TB
            Frontend["Interface / Web App<br/>[Technology]"]
            Backend["API / Core App<br/>[Technology]"]
        end
        Database[(Database<br/>[Technology])]

        Frontend -->|"Protocol / Usage"| Backend
        Backend -->|"Driver / Protocol"| Database
    ~~~
    """,

    "C4_architecture_level3.md": """You are a Software Architect specialized in the C4 Model. Your task is to analyze the code in <repository_code> and generate the Component Diagram (C4 Level 3) and its explanation in Markdown.

    DOMAIN EXTRACTION RULES (CRITICAL):
    1. Identify the application's MAIN CONTAINER and open up its internal structure.
    2. Map the REAL LOGICAL MODULES/COMPONENTS (e.g., Controllers, Services, Handlers, Managers, Repositories, Game Engines), avoiding mapping isolated file paths as components themselves.
    3. Do not detail individual functions or methods (that is Level 4/Code); map only groupings of responsibilities/modules.
    4. Identify how these components connect internally (e.g., method calls, events, dependency injection).
    5. The title of the ContainerBoundary subgraph MUST be the REAL NAME of the Main Container, NEVER the generic name of the Macro Category.

    FORMAT RULES:
    1. OUTPUT FORMAT: Pure Markdown containing text, a table and ONE Mermaid code block. NEVER wrap the whole document in a code block (e.g., ```markdown ... ```). Start directly at the main title.

    MANDATORY DOCUMENT STRUCTURE:

    # Component Architecture (C4 Level 3) - [CONTAINER / PROJECT NAME]

    ## Components Description
    Write 2 to 3 objective paragraphs explaining:
    - Which main container is being detailed and what its internal folder/module organization is.
    - How the flow of data or events travels between these components (e.g., from user input/request to business rules and persistence).

    ## Internal Components Table
    | Component | Main File / Module | Responsibility |
    | --- | --- | --- |
    | [Component 1 Name] | [File/folder path] | [Summary of the responsibility] |
    | [Component 2 Name] | [File/folder path] | [Summary of the responsibility] |

    ## Component Diagram
    Replace the example below by mapping the real components and modules discovered inside the container:

    ~~~mermaid
    flowchart TB
        subgraph ContainerBoundary["Container: Main Container Name"]
            direction TB
            ComponentA["Entry / Interface Module<br/>[E.g.: Controller / InputHandler]"]
            ComponentB["Business Logic / Engine<br/>[E.g.: Service / GameEngine]"]
            ComponentC["State / Data Manager<br/>[E.g.: State / Repository]"]
        end
        ExternalResource[(Persistence / External API)]

        ComponentA -->|"Calls / Sends events"| ComponentB
        ComponentB -->|"Reads / Updates state"| ComponentC
        ComponentC -->|"Accesses"| ExternalResource
    ~~~

    STRICT MERMAID RULES (INVIOLABLE SYNTAX):
    - In your final answer, open the code with ```mermaid and close it with ```.
    - Use only pure Mermaid syntax (`flowchart TB` or `flowchart LR`), NEVER the native `C4Component` syntax.
    - Node IDs must be simple alphanumeric without accents (e.g., GameEngine, ScoreBoard, AuthController).
    - CONNECTION SYNTAX: The arrow label MUST be inside double quotes and necessarily delimited by vertical bars before the target node: `Source -->|"Connection Label"| Target`.
    - LINE BREAKS IN LABELS: To break a line inside a node or arrow label, you MUST use the HTML tag `<br/>`. NEVER use `\\n` or additional double quotes in the middle of the label.
    """
}

EVAL_PROMPTS = {
    "judge_score": """You are a senior auditor evaluating software technical documentation that will be used as a repository guide, helping developers understand all the code logic and structure of a project.

    Your task is to critically analyze a document generated by another LLM. This document is based on one of 2 documentation frameworks (Diátaxis and C4 Model).

    ## STRUCTURE OF THE INPUT YOU WILL RECEIVE:
    You will receive the user input divided into the following XML tags:
    - <readme>: The project's official README.md, which must be interpreted as an overview of a given repository. Understand that the generated document has a single purpose: to serve as the project guide of the repository. Therefore the final document does not need to be faithful to this README.md.
    - <doc_instructions>: The original system prompt that was used to guide the LLM in generating that specific document (it defines the rules, scope and expected content).
    - <target_file>: The name of the generated file (it corresponds to one of the 7 pipeline files: 01_tutorials.md, 02_how_to_guide.md, 03_reference.md, 04_explanation.md, C4_architecture_level1.md, C4_architecture_level2.md, or C4_architecture_level3.md).
    - <document>: The actual content generated by the model that you must audit and score.

    ## EVALUATION CRITERIA AND RUBRIC (Scores from 1 to 5):

    1. Repository Coherence (repository_coherence):
    - What it evaluates: The factual and technical fidelity of the document with respect to the <readme>. It checks whether the LLM hallucinated technologies, dependencies or architectures that do not exist in the original project.
    - Scale: (1 = Full of hallucinations and disconnected from the project's reality; 5 = Totally faithful and anchored in the real information of the README).

    2. Framework Adherence (framework_adherence):
    - What it evaluates: The technical rigor in simultaneously applying the C4 Model (correct levels of abstraction) or Diátaxis (strict purpose of the corresponding quadrant, respecting the <doc_instructions> without mixing roles).
    - Scale: (1 = Completely ignores the instructions or the frameworks, mixing concepts incorrectly; 5 = Exemplary application, strictly respecting the scope of the <target_file> and the <doc_instructions>).

    3. Onboarding Usefulness (onboarding_usefulness):
    - What it evaluates: The practical value of the document contained in <document> for speeding up the integration of a new developer into the project, making the overall understanding of the system easier.
    - Scale: (1 = Useless or confusing for a newcomer; 5 = Excellent guide that drastically speeds up the developer's learning curve).

    4. Content Clarity (content_clarity):
    - What it evaluates: The quality of the technical writing, objectivity, structural cohesion, ability to synthesize and appropriate use of Markdown formatting.
    - Scale: (1 = Confusing, poorly formatted or wordy text; 5 = Impeccable writing, highly readable, direct and well structured).

    ---

    ## MANDATORY FORMAT RULES:
    1. Return EXCLUSIVELY a valid JSON object.
    2. It is STRICTLY FORBIDDEN to include greetings, markdown text blocks outside the JSON or introductory explanations.
    3. The JSON must strictly follow this key structure:
    {
        "scores": {
            "repository_coherence": <integer from 1 to 5>,
            "framework_adherence": <integer from 1 to 5>,
            "onboarding_usefulness": <integer from 1 to 5>,
            "content_clarity": <integer from 1 to 5>
        },
        "suggestions": [
            "<string with actionable suggestion 1>",
            "<string with actionable suggestion 2>"
        ]
    }"""
}


USER_TEMPLATE = (
    "Below is the complete source code of the repository delimited by the <repository_code> tags.\n"
    "Analyze the code and MANDATORILY generate the specific document requested in your SYSTEM PROMPT.\n\n"
    "<repository_code>\n{code}\n</repository_code>\n\n"
    "EXECUTION RULES:\n"
    "1. Language: EXCLUSIVELY English.\n"
    "2. Source of Truth: Use ONLY the code inside <repository_code>.\n"
    "3. DOMAIN ADAPTATION: Internally classify the software into its category (API, Game, Lib, CLI, UI/App or Plugin) "
    "and use ONLY the terminology and types of examples typical of that category in the document.\n"
    "4. EXCLUSIVE DOCUMENT FOCUS: Do not produce a generic overview. Follow STRICTLY the structure, "
    "the purpose and the level of detail defined in your SYSTEM PROMPT.\n"
    "5. Format: Return ONLY pure Markdown. For Mermaid diagrams, use pure `flowchart TB/LR` syntax.\n"
    "6. Immediate Start: Begin your answer directly with the `#` character of the main title."
)

USER_TEMPLATE_PARTIAL = USER_TEMPLATE.replace(
    "Below is the complete source code of the repository delimited",
    "Below are the main files of the repository, delimited",
)

JUDGE_USER_TEMPLATE = (
    "<readme>\n{readme}\n</readme>\n\n"
    "<doc_instructions>\n{instructions}\n</doc_instructions>\n\n"
    "<target_file>{target_file}</target_file>\n\n"
    "<document>\n{document}\n</document>"
)

MERMAID_PROBLEMS = {
    "native_c4": "Uses the native C4Context/C4Container syntax. It must use `flowchart TB` or `flowchart LR`.",
    "no_flowchart": "Does not start with `flowchart TB` or `flowchart LR`.",
    "newline": "Contains a literal `\\n` inside a label; line breaks must use `<br/>`.",
    "label_quotes": 'There is an arrow label without double quotes. Required format: `Source -->|"Label"| Target`.',
}

MERMAID_REPAIR_TEMPLATE = """
The document below has Mermaid syntax problems that must be fixed.
Fix ONLY the Mermaid syntax pointed out, keeping everything else in the document
(text, tables, structure) exactly as it is.

PROBLEMS FOUND:
{problems}

ORIGINAL DOCUMENT:
{document}

Return the complete corrected document, starting directly with the title (#).
"""

GUIDE_TITLE = "Software Project Guide"
