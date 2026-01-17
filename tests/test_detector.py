from src.detector import OnlineZScoreDetector


def test_anomaly_flags_spike():
    det = OnlineZScoreDetector(z_threshold=4.0)

    # warm up with normal-ish variation
    for i in range(300):
        det.process_one({"value": (i % 10) * 0.1})  # small variation

    # big spike should be anomaly
    res = det.process_one({"value": 10.0})
    assert res.is_anomaly is True
    assert res.score >= 4.0
