from __future__ import annotations

import ollama


class OllamaClient:
    def __init__(self, model: str, host: str = "http://localhost:11434"):
        self.model = model
        self.client = ollama.Client(host=host)

    def check(self) -> list[str]:
        response = self.client.list()
        models = []
        for item in response.models:
            name = getattr(item, "model", None) or getattr(item, "name", None)
            if name:
                models.append(name)
        return models

    def chat(self, system: str, prompt: str, temperature: float = 0.1) -> str:
        response = self.client.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            options={
                "temperature": temperature,
            },
        )
        return response.message.content
