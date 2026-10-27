import tempfile
import unittest
from pathlib import Path

import numpy as np

from docgen import baseline
from docgen.analyzer import collect_files, find_reference_doc
from docgen.edit_rate import compute_edit_rate
from docgen.evaluation import count_judge_issues, evaluate_run, run_judge
from docgen.hardware import estimate_vram_gb
from docgen.ollama_client import OllamaClient
from docgen.pipeline import CONTEXTS, SELECTIONS, STRATEGIES, run_pipeline
from docgen.selection import heuristic_top_k
from docgen.sections import JUDGE_SYSTEM_PROMPT, SECTIONS
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
        if system == JUDGE_SYSTEM_PROMPT:
            return "* primeira critica\n* segunda critica\n"
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

    def test_all_combinations_generate_all_sections(self):
        files = collect_files(self.repo, exclude_docs=True)
        for strategy in STRATEGIES:
            for context in CONTEXTS:
                for selection in SELECTIONS:
                    result = run_pipeline(
                        self.repo, "demo", files, FakeClient(),
                        strategy=strategy, context=context, selection=selection,
                    )
                    self.assertEqual(len(result.sections), len(SECTIONS))
                    self.assertEqual((result.strategy, result.context), (strategy, context))
                    self.assertGreater(result.usage.prompt_tokens, 0)

    def test_invalid_options_raise(self):
        for kwargs in ({"strategy": "x"}, {"context": "x"}, {"selection": "x"}):
            with self.assertRaises(ValueError):
                run_pipeline(self.repo, "demo", [], FakeClient(), **kwargs)

    def test_baseline_scan_filters(self):
        entries, stats = baseline.scan_files(self.repo)
        paths = {p for p, _ in entries}
        self.assertEqual(paths, {"app.py"})
        self.assertEqual(stats["selected_files"], 1)

    def test_baseline_completo_uses_original_prompts_and_whole_repo(self):
        client = FakeClient()
        run_pipeline(self.repo, "demo", [], client, strategy="baseline", context="completo", use_mermaid_repair=False)
        self.assertEqual(len(client.systems), len(SECTIONS))
        self.assertEqual(len(set(client.systems)), len(SECTIONS))
        self.assertTrue(all("--- app.py ---" in p for p in client.prompts))
        self.assertTrue(all("código-fonte completo" in p for p in client.prompts))
        for section in SECTIONS:
            self.assertIn(section.key, baseline.DOCUMENT_BY_SECTION)

    def make_many_files(self, n=30):
        for i in range(n):
            (self.repo / f"mod_{i}.py").write_text(f"def f{i}():\n    return {i}\n" * (i + 1))

    def test_baseline_topk_embeddings_sends_only_k_files(self):
        self.make_many_files()
        client = FakeClient()
        run_pipeline(self.repo, "demo", [], client, strategy="baseline", context="topk",
                     selection="embeddings", top_k=3, use_mermaid_repair=False)
        for prompt in client.prompts:
            self.assertLessEqual(prompt.count("\n--- "), 3)
            self.assertIn("selecionados por relevância", prompt)
            self.assertNotIn("código-fonte completo", prompt)
        self.assertEqual(set(client.systems), {baseline.system_prompt_for(s.key) for s in SECTIONS})

    def test_topk_heuristica_sends_same_files_in_every_section(self):
        self.make_many_files()
        client = FakeClient()
        run_pipeline(self.repo, "demo", [], client, strategy="baseline", context="topk",
                     selection="heuristica", top_k=3, use_mermaid_repair=False)
        headers = {tuple(line for line in p.splitlines() if line.startswith("--- ")) for p in client.prompts}
        self.assertEqual(len(headers), 1)
        self.assertEqual(len(next(iter(headers))), 3)
        self.assertTrue(all("principais arquivos" in p for p in client.prompts))

    def test_heuristic_prefers_manifest_then_larger_files(self):
        entries = [("a.txt", "x"), ("big.py", "l\n" * 50), ("small.py", "l\n"), ("package.json", "{}")]
        picked = [p for p, _ in heuristic_top_k(entries, 3)]
        self.assertEqual(picked, ["package.json", "big.py", "small.py"])

    def test_rag_topk_sends_less_code_than_rag_completo(self):
        self.make_many_files()
        files = collect_files(self.repo, exclude_docs=True)
        topk, full = FakeClient(), FakeClient()
        run_pipeline(self.repo, "demo", files, topk, strategy="rag", context="topk", top_k=3, use_plan_step=False)
        run_pipeline(self.repo, "demo", files, full, strategy="rag", context="completo", use_plan_step=False)
        self.assertLess(sum(map(len, topk.prompts)), sum(map(len, full.prompts)))

    def test_judge_feedback_is_counted(self):
        files = collect_files(self.repo, exclude_docs=True)
        result = run_pipeline(self.repo, "demo", files, FakeClient(), strategy="rag")
        run_judge(result, FakeClient(), "outro-modelo")
        self.assertTrue(all(s.judge_feedback for s in result.sections))
        row = evaluate_run(result, self.repo, "")
        self.assertEqual(row["falhas_juiz_total"], 2 * len(SECTIONS))

    def test_truncation_detected(self):
        files = collect_files(self.repo, exclude_docs=True)
        client = FakeClient(num_ctx=4096, prompt_size=4096)
        result = run_pipeline(self.repo, "demo", files, client, strategy="baseline", context="completo")
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
