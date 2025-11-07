import pandas as pd

from src.voice import SpeechPipeline, benchmark_suite


def dummy_tts(prompt: str) -> bytes:
    return prompt.encode()


def dummy_stt(audio: bytes) -> str:
    return audio.decode()


def test_benchmark_suite():
    df = benchmark_suite(tts=dummy_tts, stt=dummy_stt, prompts=["hello"], stt_samples=[b"hello"])
    assert isinstance(df, pd.DataFrame)
    assert set(df["engine"]) == {"tts", "stt"}
