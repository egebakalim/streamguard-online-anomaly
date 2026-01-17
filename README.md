# streamguard-online-anomaly

Online anomaly detection on a live-like numeric stream with automated drift monitoring.

This project demonstrates:
- online (streaming) anomaly detection
- distribution drift detection over time
- reproducible monitoring artifacts
- basic automated tests


## Install

```bash
pip install -r requirements.txt
```

Run the stream

```bash
python -m src.stream
```

This:

- simulates a live numeric data stream

- flags anomalous events in real time

- writes results to outputs/alerts.csv

- prints [ALERT] lines when anomalies are detected

## Generate monitoring report

```bash
python -m src.report
```

This generates an HTML drift monitoring report at:

outputs/drift_report.html

The report compares:
- a reference window (t < 300)
- a current window (t ≥ 300)

and highlights distribution shift using summary statistics and effect size
(Cohen’s d).

## Visualize anomalies

```bash
python -m src.visualize
```

This generates an interactive plot at:

outputs/stream_plot.html

- Blue points represent normal behavior.
- Red X markers represent detected anomalies.
- A vertical line marks the onset of drift.

## Run tests

```bash
python -m pytest
```