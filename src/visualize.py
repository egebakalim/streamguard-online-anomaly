# src/visualize.py
from __future__ import annotations

from pathlib import Path
import pandas as pd
import plotly.graph_objects as go

REPO_ROOT = Path(__file__).resolve().parents[1]
OUT_DIR = REPO_ROOT / "outputs"
ALERTS_CSV = OUT_DIR / "alerts.csv"
PLOT_HTML = OUT_DIR / "stream_plot.html"


def make_plot() -> None:
    if not ALERTS_CSV.exists():
        raise FileNotFoundError(
            f"Missing {ALERTS_CSV}. Run: python -m src.stream"
        )

    df = pd.read_csv(ALERTS_CSV)

    fig = go.Figure()

    # normal points
    normal = df[df["is_anomaly"] == 0]
    fig.add_trace(
        go.Scatter(
            x=normal["t"],
            y=normal["value"],
            mode="markers",
            name="Normal",
            marker=dict(size=5, color="steelblue"),
        )
    )

    # anomalies
    anomalies = df[df["is_anomaly"] == 1]
    fig.add_trace(
        go.Scatter(
            x=anomalies["t"],
            y=anomalies["value"],
            mode="markers",
            name="Anomaly",
            marker=dict(size=8, color="crimson", symbol="x"),
        )
    )

    # drift marker
    fig.add_vline(
        x=300,
        line_dash="dash",
        line_color="gray",
        annotation_text="Drift starts",
        annotation_position="top",
    )

    fig.update_layout(
        title="StreamGuard — Online Anomaly Detection",
        xaxis_title="Time (t)",
        yaxis_title="Value",
        template="plotly_white",
    )

    OUT_DIR.mkdir(exist_ok=True, parents=True)
    fig.write_html(str(PLOT_HTML))
    print(f"Wrote plot: {PLOT_HTML}")


def main():
    make_plot()


if __name__ == "__main__":
    main()
