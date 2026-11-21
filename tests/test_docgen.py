import re
import tempfile
import unittest
from pathlib import Path

from docgen import harness, prompts
from docgen.documents import DOCUMENTS
from docgen.evaluation import evaluate_markdown, evaluate_run, judge_summary, normalize_judge, parse_llm_json
from docgen.edit_rate import compute_edit_rate
from docgen.hardware import estimate_vram_gb
from docgen.mermaid_validate import validate_document
from docgen.ollama_client import OllamaClient
from docgen.pipeline import generate_documents
from docgen.references import reference_for
from docgen.selection import heuristic_top_k
from docgen.verifier import verify_document

PT_WORDS = re.compile(r"\b(você|não|para|uma|dos|das|com|ser|que|deve|código)\b", re.IGNORECASE)

JUDGE_PT = '{"scores": {"coerencia_repositorio": 4, "adesao_frameworks": 5, "utilidade_onboarding": 3, "clareza_conteudo": 4}, "suggestions": ["a", "b"]}'
JUDGE_EN = '```json\n{"scores": {"repository_coherence": 2, "framework_adherence": 2, "onboarding_usefulness": 2, "content_clarity": 2}, "suggestions": []}\n```'


class FakeClient(OllamaClient):
    def __init__(self, num_ctx=16384, prompt_size=500, judge_reply=JUDGE_PT):
        super().__init__("fake-model", num_ctx=num_ctx)
        self.prompt_size = prompt_size
        self.judge_reply = judge_reply
        self.systems: list[str] = []
        self.prompts: list[str] = []

    def chat(self, system, prompt, model=None):
        self.systems.append(system)
        self.prompts.append(prompt)
        self.usage.calls += 1
        self.usage.prompt_tokens += self.prompt_size
        self.usage.output_tokens += 50
        if self.prompt_size >= int(self.num_ctx * 0.98):
            self.usage.truncated_calls += 1
        if system in (prompts.judge_system_prompt("pt"), prompts.judge_system_prompt("en")):
            return self.judge_reply
        return "# Titulo\nVeja `app.py`, `calcular_total()` e `Inexistente.py`.\n"


def make_repo(root: Path) -> None:
    (root / "app.py").write_text("def calcular_total(a, b):\n    return a + b\n")
    (root / "README.md").write_text("# Projeto\nCalcula totais.\n")
    (root / "docs").mkdir()
    (root / "docs" / "guia.md").write_text("Guia.\n")
    (root / "tests").mkdir()
    (root / "tests" / "test_app.py").write_text("def test_x():\n    pass\n")
    (root / ".hidden").mkdir()
    (root / ".hidden" / "segredo.py").write_text("x = 1\n")


class PromptTests(unittest.TestCase):
    def test_both_languages_have_all_documents(self):
        for language in prompts.LANGUAGES:
            for document in DOCUMENTS:
                self.assertTrue(prompts.system_prompt(document.filename, language).strip())

    def test_english_prompts_have_no_portuguese(self):
        texts = [prompts.system_prompt(d.filename, "en") for d in DOCUMENTS]
        texts += [prompts.user_template("en"), prompts.user_template("en", partial=True), prompts.judge_system_prompt("en")]
        for text in texts:
            self.assertIsNone(PT_WORDS.search(text), PT_WORDS.search(text))

    def test_portuguese_prompts_are_original(self):
        self.assertIn("Você é um redator técnico", prompts.system_prompt("01_tutorials.md", "pt"))
        self.assertIn("EXCLUSIVAMENTE Português", prompts.user_template("pt"))
        self.assertIn("EXCLUSIVELY English", prompts.user_template("en"))

    def test_structure_matches_between_languages(self):
        for document in DOCUMENTS:
            pt = prompts.system_prompt(document.filename, "pt")
            en = prompts.system_prompt(document.filename, "en")
            self.assertEqual(pt.count("## "), en.count("## "), document.filename)
            self.assertEqual(pt.count("mermaid"), en.count("mermaid"), document.filename)
            self.assertEqual(pt.count("|"), en.count("|"), document.filename)

    def test_templates_have_code_placeholder(self):
        for language in prompts.LANGUAGES:
            for partial in (False, True):
                self.assertEqual(prompts.user_template(language, partial).count("{code}"), 1)

    def test_invalid_language(self):
        with self.assertRaises(ValueError):
            prompts.user_template("fr")


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        make_repo(self.repo)

    def tearDown(self):
        self.tmp.cleanup()

    def make_many_files(self, n=30):
        for i in range(n):
            (self.repo / f"mod_{i}.py").write_text(f"def f{i}():\n    return {i}\n" * (i + 1))

    def test_scan_filters(self):
        entries, stats = harness.scan_files(self.repo)
        paths = {p for p, _ in entries}
        self.assertEqual(paths, {"app.py"})
        self.assertEqual(stats["selected_files"], 1)

    def test_scan_repository_matches_main_output_format(self):
        entries, _ = harness.scan_files(self.repo)
        self.assertEqual(harness.scan_repository(self.repo), harness.format_files(entries))
        self.assertTrue(harness.scan_repository(self.repo).startswith("--- app.py ---\n"))

    def test_generates_all_documents_in_each_language(self):
        for language in prompts.LANGUAGES:
            client = FakeClient()
            result = generate_documents(self.repo, "demo", client, language=language)
            self.assertEqual(len(result.documents), len(DOCUMENTS))
            self.assertEqual(result.language, language)
            expected = [prompts.system_prompt(d.filename, language) for d in DOCUMENTS]
            self.assertEqual(client.systems, expected)
            self.assertTrue(all(prompts.user_template(language).split("{code}")[0] in p for p in client.prompts))

    def test_invalid_language_raises(self):
        with self.assertRaises(ValueError):
            generate_documents(self.repo, "demo", FakeClient(), language="fr")

    def test_top_k_limits_files_and_uses_partial_template(self):
        self.make_many_files()
        client = FakeClient()
        result = generate_documents(self.repo, "demo", client, language="en", top_k=3)
        self.assertEqual(len(result.documents[0].files_sent), 3)
        for prompt in client.prompts:
            self.assertEqual(prompt.count("\n--- "), 3)
            self.assertIn("main files", prompt)
        self.assertEqual(result.top_k, 3)

    def test_top_k_sends_less_than_complete(self):
        self.make_many_files()
        full, limited = FakeClient(), FakeClient()
        generate_documents(self.repo, "demo", full, top_k=None)
        generate_documents(self.repo, "demo", limited, top_k=3)
        self.assertLess(sum(map(len, limited.prompts)), sum(map(len, full.prompts)))
        self.assertTrue(all("código-fonte completo" in p for p in full.prompts))

    def test_heuristic_prefers_manifest_then_larger_files(self):
        entries = [("a.txt", "x"), ("big.py", "l\n" * 50), ("small.py", "l\n"), ("package.json", "{}")]
        self.assertEqual([p for p, _ in heuristic_top_k(entries, 3)], ["package.json", "big.py", "small.py"])

    def test_truncation_detected(self):
        client = FakeClient(num_ctx=4096, prompt_size=4096)
        result = generate_documents(self.repo, "demo", client)
        self.assertGreater(result.usage.truncated_calls, 0)

    def test_mermaid_repair_only_when_enabled(self):
        class BadMermaid(FakeClient):
            def chat(self, system, prompt, model=None):
                super().chat(system, prompt, model)
                return "# T\n```mermaid\nC4Context\n```\n"

        off, on = BadMermaid(), BadMermaid()
        generate_documents(self.repo, "demo", off)
        generate_documents(self.repo, "demo", on, use_mermaid_repair=True)
        self.assertEqual(off.usage.calls, 7)
        self.assertEqual(on.usage.calls, 10)


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        make_repo(self.repo)

    def tearDown(self):
        self.tmp.cleanup()

    def test_judge_json_parsing(self):
        pt = parse_llm_json(JUDGE_PT)
        en = parse_llm_json(JUDGE_EN)
        self.assertEqual(pt["scores"]["coerencia_repositorio"], 4)
        self.assertEqual(en["scores"]["repository_coherence"], 2)
        self.assertEqual(normalize_judge(pt)["scores"]["framework_adherence"], 5)
        self.assertEqual(normalize_judge(en)["scores"]["repository_coherence"], 2)
        self.assertEqual(len(normalize_judge(pt)["suggestions"]), 2)
        self.assertIsNone(parse_llm_json("sem json"))
        self.assertIsNone(parse_llm_json(None))
        self.assertIsNone(normalize_judge(None))
        self.assertIsNotNone(parse_llm_json("texto antes " + JUDGE_PT + " depois"))

    def test_evaluate_markdown_and_summary(self):
        for language, reply in (("pt", JUDGE_PT), ("en", JUDGE_EN)):
            client = FakeClient(judge_reply=reply)
            result = generate_documents(self.repo, "demo", client, language=language)
            for item in result.documents:
                evaluate_markdown(client, language, item, "readme", "outro-modelo")
            summary = judge_summary(result)
            self.assertEqual(summary["judge_parse_failures"], 0)
            self.assertEqual(summary["judge_suggestions_total"], 14 if language == "pt" else 0)
            self.assertEqual(client.systems[-1], prompts.judge_system_prompt(language))
            self.assertTrue(all(d.judge is not None for d in result.documents))

    def test_judge_failure_is_counted(self):
        client = FakeClient(judge_reply="não é json")
        result = generate_documents(self.repo, "demo", client)
        for item in result.documents:
            evaluate_markdown(client, "pt", item, "readme")
        self.assertEqual(judge_summary(result)["judge_parse_failures"], 7)

    def test_evaluate_run_columns(self):
        client = FakeClient()
        result = generate_documents(self.repo, "demo", client)
        for item in result.documents:
            evaluate_markdown(client, "pt", item, "readme")
        row = evaluate_run(result, self.repo, "", "none")
        for column in ("language", "reference", "references_missing", "judge_mean",
                       "judge_suggestions_total", "prompt_tokens", "generation_time_seconds"):
            self.assertIn(column, row)
        self.assertEqual(row["language"], "pt")

    def test_reference_selection_by_language(self):
        with tempfile.TemporaryDirectory() as translated:
            Path(translated, "my_repo.md").write_text("traduzido")
            text, kind = reference_for(self.repo, "my-repo", "pt", translated)
            self.assertEqual((text, kind), ("traduzido", "translated"))
            text, kind = reference_for(self.repo, "my-repo", "en", translated)
            self.assertEqual(kind, "original")
            self.assertIn("Calcula totais", text)
            text, kind = reference_for(self.repo, "outro", "pt", translated)
            self.assertEqual(kind, "original")

    def test_reference_missing(self):
        (self.repo / "README.md").unlink()
        self.assertEqual(reference_for(self.repo, "x", "en", "inexistente"), ("", "none"))

    def test_bundled_translations_match_benchmark_repos(self):
        from benchmark import config
        from docgen.references import find_translated_readme

        root = Path(__file__).resolve().parent.parent / "translated_readme"
        for url in config.REPOSITORIES:
            self.assertIsNotNone(find_translated_readme(url.rstrip("/").split("/")[-1], root), url)

    def test_verifier_edit_rate_mermaid_vram(self):
        report = verify_document("Use `app.py`, `calcular_total()` e `Fantasma.py`.", self.repo)
        self.assertEqual(report.missing, ["Fantasma.py"])
        self.assertEqual(compute_edit_rate("a b c", "a b c")["edit_rate"], 0.0)
        problems_pt = validate_document("```mermaid\nC4Context\n```", "pt")
        problems_en = validate_document("```mermaid\nC4Context\n```", "en")
        self.assertIn("nativa", problems_pt[0][0])
        self.assertIn("native", problems_en[0][0])
        self.assertLess(estimate_vram_gb("qwen2.5-coder:7b", 32768, kv_bits=8), estimate_vram_gb("qwen2.5-coder:7b", 32768))


if __name__ == "__main__":
    unittest.main()
