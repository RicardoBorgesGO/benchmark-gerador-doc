"""Estimativa de VRAM e medição de energia/VRAM via nvidia-smi."""

from __future__ import annotations

import shutil
import subprocess
import threading
import time

MODEL_ARCHITECTURES = {
    "qwen2.5:7b": {"parameters_b": 7.6, "quant_bits": 4.5, "embedding_length": 3584, "num_layers": 28},
    "qwen2.5-coder:7b": {"parameters_b": 7.6, "quant_bits": 4.5, "embedding_length": 3584, "num_layers": 28},
    "qwen2.5-coder:14b": {"parameters_b": 14.8, "quant_bits": 4.5, "embedding_length": 5120, "num_layers": 48},
    "deepseek-coder:6.7b": {"parameters_b": 6.7, "quant_bits": 4.0, "embedding_length": 4096, "num_layers": 32},
    "codellama:7b": {"parameters_b": 7.0, "quant_bits": 4.0, "embedding_length": 4096, "num_layers": 32},
}


def estimate_tokens(text: str) -> int:
    return int(len(text) / 3.3)


def estimate_vram_gb(model_name: str, context_tokens: int, kv_bits: int = 16, overhead_gb: float = 1.0) -> float | None:
    cfg = MODEL_ARCHITECTURES.get(model_name)
    if cfg is None:
        return None
    weights = cfg["parameters_b"] * cfg["quant_bits"] / 8.0
    kv_elements = 2 * cfg["num_layers"] * cfg["embedding_length"] * context_tokens
    kv_gb = kv_elements * (kv_bits / 8) / (1024**3)
    return round(weights + kv_gb + overhead_gb, 2)


class GpuSampler:

    def __init__(self, interval: float = 1.0):
        self.interval = interval
        self.available = shutil.which("nvidia-smi") is not None
        self.energy_wh = 0.0
        self.peak_vram_mb = 0.0
        self.avg_power_w = 0.0
        self._samples = 0
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def _read(self) -> tuple[float, float] | None:
        try:
            out = subprocess.run(
                ["nvidia-smi", "--query-gpu=power.draw,memory.used",
                 "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=5,
            ).stdout.strip().splitlines()[0]
            power, mem = (float(x) for x in out.split(","))
            return power, mem
        except Exception:
            return None

    def _loop(self) -> None:
        last = time.perf_counter()
        total_power = 0.0
        while not self._stop.wait(self.interval):
            now = time.perf_counter()
            sample = self._read()
            if sample:
                power, mem = sample
                self.energy_wh += power * (now - last) / 3600.0
                self.peak_vram_mb = max(self.peak_vram_mb, mem)
                total_power += power
                self._samples += 1
            last = now
        self.avg_power_w = total_power / self._samples if self._samples else 0.0

    def __enter__(self) -> "GpuSampler":
        if self.available:
            self._thread = threading.Thread(target=self._loop, daemon=True)
            self._thread.start()
        return self

    def __exit__(self, *exc) -> None:
        if self._thread:
            self._stop.set()
            self._thread.join(timeout=5)
