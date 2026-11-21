from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Document:
    key: str
    filename: str
    titles: dict
    needs_mermaid: bool = False

    def title(self, language: str) -> str:
        return self.titles[language]


DOCUMENTS: list[Document] = [
    Document("tutorial", "01_tutorials.md", {"pt": "Tutorial", "en": "Tutorial"}),
    Document("howto", "02_how_to_guide.md", {"pt": "Guia prático (How-To)", "en": "How-To Guide"}),
    Document("reference", "03_reference.md", {"pt": "Referência técnica", "en": "Technical Reference"}),
    Document("explanation", "04_explanation.md", {"pt": "Entendimento arquitetural", "en": "Architectural Understanding"}),
    Document("c4_level1", "C4_architecture_level1.md", {"pt": "C4 nível 1: Contexto", "en": "C4 Level 1: Context"}, True),
    Document("c4_level2", "C4_architecture_level2.md", {"pt": "C4 nível 2: Contêineres", "en": "C4 Level 2: Containers"}, True),
    Document("c4_level3", "C4_architecture_level3.md", {"pt": "C4 nível 3: Componentes", "en": "C4 Level 3: Components"}, True),
]
