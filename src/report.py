# src/report.py
from __future__ import annotations

from pathlib import Path
import math

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "outputs"
ALERTS_CSV = OUT_DIR / "alerts.csv"
REPORT_HTML = OUT_DIR / "drift_report.html"


def _summary_stats(s: pd.Series) -> dict:
    s = s.dropna().astype(float)
    return {
        "count": int(s.shape[0]),
        "mean": float(s.mean()),
        "std": float(s.std(ddof=1)) if s.shape[0] > 1 else 0.0,
        "min": float(s.min()),
        "p25": float(s.quantile(0.25)),
        "p50": float(s.quantile(0.50)),
        "p75": float(s.quantile(0.75)),
        "max": float(s.max()),
    }


def _cohens_d(ref: pd.Series, cur: pd.Series) -> float:
    ref = ref.dropna().astype(float)
    cur = cur.dropna().astype(float)
    if len(ref) < 2 or len(cur) < 2:
        return 0.0
    m1, m2 = ref.mean(), cur.mean()
    s1, s2 = ref.std(ddof=1), cur.std(ddof=1)
    pooled = math.sqrt(((len(ref) - 1) * s1**2 + (len(cur) - 1) * s2**2) / (len(ref) + len(cur) - 2))
    if pooled == 0:
        return 0.0
    return float((m2 - m1) / pooled)


def make_report() -> None:
    if not ALERTS_CSV.exists():
        raise FileNotFoundError(f"Missing {ALERTS_CSV}. Run: python -m src.stream")

    df = pd.read_csv(ALERTS_CSV)

    ref = df[df["t"] < 300]["value"]
    cur = df[df["t"] >= 300]["value"]

    ref_stats = _summary_stats(ref)
    cur_stats = _summary_stats(cur)
    d = _cohens_d(ref, cur)

    # Simple drift rule-of-thumb
    drift_flag = abs(d) >= 0.5  # medium effect size

    html = f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>streamguard drift report</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; }}
    .card {{ border: 1px solid #ddd; border-radius: 12px; padding: 16px; margin-bottom: 16px; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #eee; padding: 8px; text-align: right; }}
    th {{ background: #fafafa; }}
    .flag-yes {{ color: #b00020; font-weight: bold; }}
    .flag-no {{ color: #0a7a0a; font-weight: bold; }}
    .mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; }}
  </style>
</head>
<body>
  <h1>StreamGuard Drift Report</h1>
  <p class="mono">Reference window: t &lt; 300 | Current window: t ≥ 300</p>

  <div class="card">
    <h2>Drift decision</h2>
    <p>Cohen's d (effect size): <span class="mono">{d:.3f}</span></p>
    <p>Drift detected: <span class="{ 'flag-yes' if drift_flag else 'flag-no' }">{str(drift_flag).upper()}</span></p>
    <p style="color:#666;">Rule: drift if |d| ≥ 0.5 (medium shift). This is a simple, explainable baseline.</p>
  </div>

  <div class="card">
    <h2>Summary stats (value)</h2>
    <table>
      <thead>
        <tr><th></th><th>Reference</th><th>Current</th></tr>
      </thead>
      <tbody>
        {''.join([f"<tr><td style='text-align:left'>{k}</td><td>{ref_stats[k]:.4f}</td><td>{cur_stats[k]:.4f}</td></tr>"
                 for k in ['count','mean','std','min','p25','p50','p75','max']])}
      </tbody>
    </table>
  </div>

  <div class="card">
    <h2>What this means</h2>
    <ul>
      <li><b>Anomaly detection</b> flags unusual points live.</li>
      <li><b>Drift detection</b> checks whether "normal" behavior changed over time.</li>
      <li>This report compares two windows and shows if the distribution shifted.</li>
    </ul>
  </div>
</body>
</html>
"""

    OUT_DIR.mkdir(exist_ok=True, parents=True)
    REPORT_HTML.write_text(html, encoding="utf-8")
    print(f"Wrote report: {REPORT_HTML}")


def main():
    make_report()


if __name__ == "__main__":
    main()
