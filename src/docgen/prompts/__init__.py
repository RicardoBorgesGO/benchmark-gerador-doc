from __future__ import annotations

from . import en, pt

LANGUAGES = ("pt", "en")
_MODULES = {"pt": pt, "en": en}


def _module(language: str):
    if language not in _MODULES:
        raise ValueError(f"language deve ser um de {LANGUAGES}")
    return _MODULES[language]


def system_prompt(filename: str, language: str) -> str:
    return _module(language).SYSTEM_PROMPTS[filename]


def user_template(language: str, partial: bool = False) -> str:
    module = _module(language)
    return module.USER_TEMPLATE_PARTIAL if partial else module.USER_TEMPLATE


def judge_system_prompt(language: str) -> str:
    return _module(language).EVAL_PROMPTS["judge_score"]


def judge_user_message(language: str, readme: str, instructions: str, target_file: str, document: str) -> str:
    return _module(language).JUDGE_USER_TEMPLATE.format(
        readme=readme, instructions=instructions, target_file=target_file, document=document
    )


def mermaid_problem(language: str, key: str) -> str:
    return _module(language).MERMAID_PROBLEMS[key]


def mermaid_repair_prompt(language: str, problems: str, document: str) -> str:
    return _module(language).MERMAID_REPAIR_TEMPLATE.format(problems=problems, document=document)


def guide_title(language: str) -> str:
    return _module(language).GUIDE_TITLE
