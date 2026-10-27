from __future__ import annotations

from dataclasses import dataclass

import ollama


@dataclass
class UsageStats:
    calls: int = 0
    prompt_tokens: int = 0
    output_tokens: int = 0
    truncated_calls: int = 0

    def snapshot(self) -> "UsageStats":
        return UsageStats(self.calls, self.prompt_tokens, self.output_tokens, self.truncated_calls)

    def minus(self, other: "UsageStats") -> "UsageStats":
        return UsageStats(
            self.calls - other.calls,
            self.prompt_tokens - other.prompt_tokens,
            self.output_tokens - other.output_tokens,
            self.truncated_calls - other.truncated_calls,
        )


class OllamaClient:
    def __init__(
        self,
        model: str,
        host: str = "http://localhost:11434",
        num_ctx: int = 16384,
        seed: int | None = 42,
        keep_alive: str | int = "10m",
    ):
        self.model = model
        self.num_ctx = num_ctx
        self.seed = seed
        self.keep_alive = keep_alive
        self.client = ollama.Client(host=host)
        self.usage = UsageStats()

    def check(self) -> list[str]:
        response = self.client.list()
        names = []
        for item in response.models:
            name = getattr(item, "model", None) or getattr(item, "name", None)
            if name:
                names.append(name)
        return names

    def chat(self, system: str, prompt: str, temperature: float = 0.1, model: str | None = None) -> str:
        options = {"temperature": temperature, "num_ctx": self.num_ctx}
        if self.seed is not None:
            options["seed"] = self.seed

        response = self.client.chat(
            model=model or self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            options=options,
            keep_alive=self.keep_alive,
        )

        prompt_tokens = int(getattr(response, "prompt_eval_count", 0) or 0)
        output_tokens = int(getattr(response, "eval_count", 0) or 0)
        self.usage.calls += 1
        self.usage.prompt_tokens += prompt_tokens
        self.usage.output_tokens += output_tokens
        # prompt que ocupa quase todo o num_ctx indica truncamento
        if prompt_tokens >= int(self.num_ctx * 0.98):
            self.usage.truncated_calls += 1

        return response.message.content

    def embed(self, texts: list[str], model: str = "nomic-embed-text") -> list[list[float]]:
        response = self.client.embed(model=model, input=texts)
        vectors = getattr(response, "embeddings", None)
        if vectors is None:
            vectors = response["embeddings"]
        return [list(v) for v in vectors]
