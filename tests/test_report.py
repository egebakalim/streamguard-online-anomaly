from pathlib import Path
import pandas as pd

from src.report import make_report

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "outputs"
ALERTS_CSV = OUT_DIR / "alerts.csv"
REPORT_HTML = OUT_DIR / "drift_report.html"


def test_report_generation(tmp_path):
    # prepare minimal fake alerts file
    OUT_DIR.mkdir(exist_ok=True, parents=True)

    df = pd.DataFrame(
        {
            "t": list(range(10)),
            "value": [0.0] * 5 + [5.0] * 5,
            "score": [0.0] * 10,
            "is_anomaly": [0] * 10,
        }
    )
    df.to_csv(ALERTS_CSV, index=False)

    make_report()

    assert REPORT_HTML.exists()
    assert REPORT_HTML.stat().st_size > 100
