import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from benchmark import run_benchmark
from benchmark.run_benchmark import EVALUATION_FIELDS, GENERATION_FIELDS
from docgen.documents import DOCUMENTS
from docgen.repository import Repository
from test_docgen import JUDGE_PT, FakeClient, make_repo

URL = "https://github.com/someone/demo.git"


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


class BenchmarkTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.out = self.root / "autodoc"
        self.csv_dir = self.root / "csv"
        self.csv_dir.mkdir()
        self.calls = 0

    def tearDown(self):
        self.tmp.cleanup()

    def fake_download(self, url):
        folder = Path(tempfile.mkdtemp(dir=self.root)) / "repo"
        folder.mkdir()
        make_repo(folder)
        return Repository(folder, url, "demo")

    def run_benchmark(self, **kwargs):
        def client_factory(model, **kw):
            client = FakeClient(num_ctx=kw.get("num_ctx", 16384), judge_reply=JUDGE_PT)
            client.model = model
            return client

        with mock.patch.object(run_benchmark, "download_github_repository", self.fake_download), \
                mock.patch.object(run_benchmark, "OllamaClient", client_factory):
            run_benchmark.run_pipeline(
                [URL], ["qwen2.5-coder:7b"], output_dir=str(self.out), csv_dir=str(self.csv_dir),
                translated_dir=str(self.root / "sem_traducao"), **kwargs,
            )

    def test_output_layout_and_csv_in_english(self):
        self.run_benchmark(languages=["pt", "en"], top_k_values=[0])

        for language in ("pt", "en"):
            folder = self.out / "qwen2.5-coder_7b" / "demo" / language
            for document in DOCUMENTS:
                self.assertTrue((folder / document.filename).is_file())
            evaluations = json.loads((folder / "llm_eval.json").read_text(encoding="utf-8"))
            self.assertEqual(set(evaluations), {d.filename for d in DOCUMENTS})
            self.assertIn("coerencia_repositorio", evaluations["01_tutorials.md"]["scores"])
            info = json.loads((folder / "run_info.json").read_text(encoding="utf-8"))
            self.assertEqual((info["language"], info["top_k"]), (language, 0))

        generation = read_csv(self.csv_dir / "generation_metrics.csv")
        evaluation = read_csv(self.csv_dir / "evaluation_results.csv")
        self.assertEqual(len(generation), 2 * len(DOCUMENTS))
        self.assertEqual(len(evaluation), 2)
        self.assertEqual(list(generation[0])[:6], ["repository", "document", "model", "prompt_tokens",
                                                   "output_tokens", "generation_time_seconds"])
        self.assertEqual(list(evaluation[0])[:6], ["model", "repository", "meteor", "bert_precision",
                                                   "bert_recall", "bert_f1"])
        self.assertEqual(generation[0]["repository"], URL)
        self.assertEqual(evaluation[0]["repository"], "demo")
        self.assertEqual(evaluation[0]["repository_url"], URL)
        self.assertEqual(set(generation[0]) , set(GENERATION_FIELDS))
        self.assertEqual(set(evaluation[0]), set(EVALUATION_FIELDS))
        self.assertEqual(evaluation[0]["reference"], "original")
        self.assertEqual(evaluation[0]["judge_suggestions_total"], "14")

    def test_top_k_does_not_change_folder(self):
        self.run_benchmark(languages=["pt"], top_k_values=[0, 2])
        folders = [p.name for p in (self.out / "qwen2.5-coder_7b" / "demo").iterdir()]
        self.assertEqual(folders, ["pt"])
        evaluation = read_csv(self.csv_dir / "evaluation_results.csv")
        self.assertEqual([r["top_k"] for r in evaluation], ["0", "2"])
        info = json.loads((self.out / "qwen2.5-coder_7b" / "demo" / "pt" / "run_info.json").read_text(encoding="utf-8"))
        self.assertEqual(info["top_k"], 2)

    def test_no_judge_does_not_write_llm_eval(self):
        self.run_benchmark(languages=["pt"], use_judge=False)
        folder = self.out / "qwen2.5-coder_7b" / "demo" / "pt"
        self.assertFalse((folder / "llm_eval.json").exists())

    def test_resume_skips_finished_runs(self):
        self.run_benchmark(languages=["pt"])
        self.run_benchmark(languages=["pt"], resume=True)
        self.assertEqual(len(read_csv(self.csv_dir / "evaluation_results.csv")), 1)
        self.run_benchmark(languages=["pt"], resume=False)
        self.assertEqual(len(read_csv(self.csv_dir / "evaluation_results.csv")), 2)


if __name__ == "__main__":
    unittest.main()
