from __future__ import annotations

import statistics
import time
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List

import pandas as pd


@dataclass
class SpeechPipeline:
    """Wrap speech engines for benchmarking or integration tests."""

    stt: Callable[[bytes], str]
    tts: Callable[[str], bytes]

    def round_trip(self, utterance: str) -> Dict[str, float]:
        t0 = time.perf_counter()
        audio = self.tts(utterance)
        t_tts = time.perf_counter() - t0
        t1 = time.perf_counter()
        transcript = self.stt(audio)
        t_stt = time.perf_counter() - t1
        accuracy = 1.0 if transcript.strip().lower() == utterance.strip().lower() else 0.0
        return {
            "utterance": utterance,
            "tts_seconds": t_tts,
            "stt_seconds": t_stt,
            "round_trip_seconds": t_tts + t_stt,
            "accuracy": accuracy,
        }


def benchmark_tts(tts: Callable[[str], bytes], prompts: Iterable[str]) -> List[Dict[str, float]]:
    results = []
    for prompt in prompts:
        start = time.perf_counter()
        tts(prompt)
        duration = time.perf_counter() - start
        results.append({"prompt": prompt, "seconds": duration})
    return results


def benchmark_stt(stt: Callable[[bytes], str], samples: Iterable[bytes]) -> List[Dict[str, float]]:
    results = []
    for audio in samples:
        start = time.perf_counter()
        stt(audio)
        duration = time.perf_counter() - start
        results.append({"seconds": duration})
    return results


def summarise_benchmark(rows: List[Dict[str, float]]) -> Dict[str, float]:
    durations = [row["seconds"] for row in rows if "seconds" in row]
    if not durations:
        return {"count": 0}
    return {
        "count": len(durations),
        "mean": statistics.mean(durations),
        "p95": statistics.quantiles(durations, n=100)[94] if len(durations) > 1 else durations[0],
        "max": max(durations),
    }


def benchmark_suite(
    *,
    tts: Callable[[str], bytes],
    stt: Callable[[bytes], str],
    prompts: Iterable[str],
    stt_samples: Iterable[bytes],
) -> pd.DataFrame:
    tts_rows = benchmark_tts(tts, prompts)
    stt_rows = benchmark_stt(stt, stt_samples)
    for row in tts_rows:
        row["engine"] = "tts"
    for row in stt_rows:
        row["engine"] = "stt"
    df = pd.DataFrame(tts_rows + stt_rows)
    return df
