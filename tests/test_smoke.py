import tempfile
import unittest
from pathlib import Path

import numpy as np

from docgen import baseline
from docgen.analyzer import collect_files, find_reference_doc
from docgen.edit_rate import compute_edit_rate
from docgen.evaluation import count_judge_issues, evaluate_run
from docgen.hardware import estimate_vram_gb
from docgen.ollama_client import OllamaClient
from docgen.pipeline import STRATEGIES, run_pipeline
from docgen.sections import SECTIONS
from docgen.verifier import verify_document


class FakeClient(OllamaClient):
    def __init__(self, num_ctx=16384, prompt_size=500):
        super().__init__("fake-model", num_ctx=num_ctx)
        self.prompt_size = prompt_size
        self.systems: list[str] = []
        self.prompts: list[str] = []

    def chat(self, system, prompt, temperature=0.1, model=None):
        self.systems.append(system)
        self.prompts.append(prompt)
        self.usage.calls += 1
        self.usage.prompt_tokens += self.prompt_size
        self.usage.output_tokens += 50
        if self.prompt_size >= int(self.num_ctx * 0.98):
            self.usage.truncated_calls += 1
        return "# Titulo\nVeja `app.py`, `calcular_total()` e `Inexistente.py`.\n"

    def embed(self, texts, model="x"):
        return [np.random.default_rng(len(t)).random(8).tolist() for t in texts]


def make_repo(root: Path) -> None:
    (root / "app.py").write_text("def calcular_total(a, b):\n    return a + b\n")
    (root / "README.md").write_text("# Projeto\nCalcula totais.\n")
    (root / "docs").mkdir()
    (root / "docs" / "guia.md").write_text("Guia de uso.\n")
    (root / "tests").mkdir()
    (root / "tests" / "test_app.py").write_text("def test_x():\n    pass\n")
    (root / ".hidden").mkdir()
    (root / ".hidden" / "segredo.py").write_text("x = 1\n")


class DocgenTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        make_repo(self.repo)

    def tearDown(self):
        self.tmp.cleanup()

    def test_exclude_docs(self):
        names = {f.path for f in collect_files(self.repo, exclude_docs=True)}
        self.assertIn("app.py", names)
        self.assertNotIn("README.md", names)
        self.assertNotIn("docs/guia.md", names)
        self.assertIn("Calcula totais", find_reference_doc(self.repo))

    def test_all_strategies_generate_all_sections(self):
        files = collect_files(self.repo, exclude_docs=True)
        for strategy in STRATEGIES:
            result = run_pipeline(self.repo, "demo", files, FakeClient(), strategy=strategy)
            self.assertEqual(len(result.sections), len(SECTIONS))
            self.assertEqual(result.strategy, strategy)
            self.assertGreater(result.usage.prompt_tokens, 0)

    def test_baseline_scan_filters(self):
        code, stats = baseline.scan_repository(self.repo)
        self.assertIn("--- app.py ---", code)
        self.assertNotIn("test_app.py", code)
        self.assertNotIn("segredo.py", code)
        self.assertNotIn("Calcula totais", code)
        self.assertEqual(stats["selected_files"], 1)

    def test_baseline_uses_original_prompts(self):
        client = FakeClient()
        run_pipeline(self.repo, "demo", [], client, strategy="baseline", use_mermaid_repair=False)
        self.assertEqual(len(client.systems), len(SECTIONS))
        self.assertEqual(len(set(client.systems)), len(SECTIONS))
        self.assertTrue(all("<repository_code>" in p for p in client.prompts))
        for section in SECTIONS:
            self.assertIn(section.key, baseline.DOCUMENT_BY_SECTION)

    def test_rag_uses_less_code_than_flat_on_many_files(self):
        for i in range(30):
            (self.repo / f"mod_{i}.py").write_text(f"def f{i}():\n    return {i}\n" * 20)
        files = collect_files(self.repo, exclude_docs=True)
        rag, flat = FakeClient(), FakeClient()
        run_pipeline(self.repo, "demo", files, rag, strategy="rag", top_k=3, use_plan_step=False)
        run_pipeline(self.repo, "demo", files, flat, strategy="flat")
        self.assertLess(sum(map(len, rag.prompts)), sum(map(len, flat.prompts)))

    def test_truncation_detected(self):
        files = collect_files(self.repo, exclude_docs=True)
        client = FakeClient(num_ctx=4096, prompt_size=4096)
        result = run_pipeline(self.repo, "demo", files, client, strategy="flat")
        self.assertGreater(result.usage.truncated_calls, 0)

    def test_verifier(self):
        report = verify_document("Use `app.py`, `calcular_total()` e `Fantasma.py`.", self.repo)
        self.assertEqual(report.n_missing, 1)
        self.assertIn("Fantasma.py", report.missing)

    def test_evaluate_run_without_reference(self):
        files = collect_files(self.repo, exclude_docs=True)
        result = run_pipeline(self.repo, "demo", files, FakeClient(), strategy="rag")
        row = evaluate_run(result, self.repo, reference_text="")
        self.assertEqual(row["cenario"], "sem_referencia")
        self.assertIn("refs_inexistentes", row)

    def test_edit_rate_and_judge_count(self):
        self.assertEqual(compute_edit_rate("a b c", "a b c")["edit_rate"], 0.0)
        self.assertGreater(compute_edit_rate("a b c", "x y z")["edit_rate"], 0.9)
        self.assertEqual(count_judge_issues("* um\n* dois\n* Nenhum problema relevante identificado."), 2)

    def test_vram_estimate(self):
        self.assertLess(
            estimate_vram_gb("qwen2.5-coder:7b", 32768, kv_bits=8),
            estimate_vram_gb("qwen2.5-coder:7b", 32768),
        )
        self.assertIsNone(estimate_vram_gb("desconhecido", 8192))


if __name__ == "__main__":
    unittest.main()
