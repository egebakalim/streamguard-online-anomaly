# src/detector.py
from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass
class AnomalyResult:
    score: float
    is_anomaly: bool


class OnlineZScoreDetector:
    """
    Simple, stable online anomaly detector for 1D numeric streams.
    Maintains running mean/std (Welford's algorithm).
    score = |z|  (how many std devs away)
    """

    def __init__(self, z_threshold: float = 4.0):
        self.z_threshold = float(z_threshold)
        self.n = 0
        self.mean = 0.0
        self.M2 = 0.0  # sum of squares of differences from the current mean

    def _std(self) -> float:
        if self.n < 2:
            return 0.0
        var = self.M2 / (self.n - 1)
        return math.sqrt(var)

    def process_one(self, x: dict) -> AnomalyResult:
        value = float(x["value"])

        # score based on current stats BEFORE updating with this point
        std = self._std()
        if self.n < 10 or std == 0.0:
            score = 0.0
            is_anomaly = False
        else:
            z = (value - self.mean) / std
            score = abs(float(z))
            is_anomaly = score >= self.z_threshold

        # update running stats (Welford)
        self.n += 1
        delta = value - self.mean
        self.mean += delta / self.n
        delta2 = value - self.mean
        self.M2 += delta * delta2

        return AnomalyResult(score=score, is_anomaly=is_anomaly)
