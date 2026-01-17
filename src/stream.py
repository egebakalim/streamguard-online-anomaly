# src/stream.py
from __future__ import annotations

import csv
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, List

import numpy as np

from src.detector import OnlineZScoreDetector


REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "outputs"
ALERTS_CSV = OUT_DIR / "alerts.csv"


@dataclass
class Event:
    t: int
    value: float


def generate_stream(
    n: int = 600,
    seed: int = 42,
    drift_at: int = 350,
    spike_points: List[int] | None = None,
) -> Iterator[Event]:
    """
    Synthetic stream:
    - normal values around mean 0
    - inject a few spikes (anomalies)
    - drift: after drift_at, mean shifts (simulates real world change)
    """
    rng = np.random.default_rng(seed)
    if spike_points is None:
        spike_points = [120, 260, 420, 510]

    for t in range(n):
        mean = 0.0 if t < drift_at else 1.5
        value = float(rng.normal(loc=mean, scale=1.0))

        if t in spike_points:
            value += float(rng.normal(loc=7.0, scale=0.5))  # big spike

        yield Event(t=t, value=value)


def run_stream(
    n: int = 600,
    threshold: float = 0.75,
    sleep_s: float = 0.01,
) -> None:
    OUT_DIR.mkdir(exist_ok=True, parents=True)

    det = OnlineZScoreDetector(z_threshold=4.0)

    with ALERTS_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["t", "value", "score", "is_anomaly"])
        writer.writeheader()

        print(f"Streaming {n} events... (writing {ALERTS_CSV})")
        for ev in generate_stream(n=n):
            x = {"value": ev.value}
            res = det.process_one(x)

            writer.writerow(
                {
                    "t": ev.t,
                    "value": ev.value,
                    "score": res.score,
                    "is_anomaly": int(res.is_anomaly),
                }
            )

            if res.is_anomaly:
                print(f"[ALERT] t={ev.t:>3} value={ev.value:>6.2f} score={res.score:>5.2f}")

            if sleep_s > 0:
                time.sleep(sleep_s)

    print("Done.")


def main():
    run_stream()


if __name__ == "__main__":
    main()
