import json
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports" / "generated"
METRICS = REPORTS / "metrics.json"
DRIFT = REPORTS / "drift_statistics.csv"
EVENTS = ROOT / "logs" / "pipeline_events.jsonl"

st.set_page_config(page_title="Credit Model Monitoring", layout="wide")
st.title("Observabilidade do Credit Scoring")
st.caption("Painel local para métricas operacionais, performance e drift do cenário simulado.")

if not METRICS.exists() or not DRIFT.exists():
    st.info("Execute .\\scripts\\run_pipeline.ps1 para gerar os relatórios e métricas.")
    st.stop()

metrics = json.loads(METRICS.read_text(encoding="utf-8"))
drift = pd.read_csv(DRIFT)
events = []
if EVENTS.exists():
    for line in EVENTS.read_text(encoding="utf-8").splitlines():
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue

col1, col2, col3, col4 = st.columns(4)
col1.metric("Linhas na referência", f"{metrics['reference_rows']:,}")
col2.metric("Linhas em produção", f"{metrics['production_rows']:,}")
col3.metric("Testes com drift", metrics["drifted_feature_tests"])
col4.metric("Duração do pipeline", f"{metrics['pipeline_duration_seconds']} s")

left, right = st.columns(2)
left.subheader("Saúde do modelo")
left.write({"ROC AUC baseline": metrics["baseline_metrics"]["roc_auc"],
            "ROC AUC em produção simulada": metrics["production_metrics"]["roc_auc"],
            "Brier baseline": metrics["baseline_metrics"]["brier_score"],
            "Brier produção": metrics["production_metrics"]["brier_score"],
            "Taxa alvo referência": metrics["reference_default_rate"],
            "Taxa alvo produção": metrics["production_default_rate"]})
right.subheader("Testes estatísticos")
right.dataframe(drift, use_container_width=True, hide_index=True)

st.subheader("Histórico de execuções e alertas")
completed = pd.DataFrame(
    event for event in events if event.get("event") == "pipeline_completed"
)
if not completed.empty:
    completed["timestamp_utc"] = pd.to_datetime(
        completed["timestamp_utc"], utc=True, errors="coerce"
    )
    completed = completed.dropna(subset=["timestamp_utc"]).sort_values("timestamp_utc")
    history = completed.set_index("timestamp_utc")[["drifted_feature_tests"]]
    st.line_chart(history, y="drifted_feature_tests")
    st.dataframe(
        completed[["timestamp_utc", "reference_rows", "production_rows",
                   "drifted_feature_tests", "pipeline_duration_seconds",
                   "validation_status"]],
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("O histórico será exibido após novas execuções do pipeline.")

st.subheader("Falhas e rejeições de validação")
validation_events = [
    event for event in events
    if event.get("event") in {"pipeline_failed", "contract_rejected_invalid_batch"}
]
if validation_events:
    failures = pd.DataFrame(validation_events)
    failures["timestamp_utc"] = pd.to_datetime(
        failures["timestamp_utc"], utc=True, errors="coerce"
    )
    st.dataframe(
        failures[[column for column in
                  ["timestamp_utc", "event", "command", "error_type", "error"]
                  if column in failures]],
        use_container_width=True,
        hide_index=True,
    )
else:
    st.success("Nenhuma falha ou rejeição registrada no log local.")

report = REPORTS / "evidently_data_drift.html"
if report.exists():
    st.download_button(
        "Baixar relatório HTML do Evidently",
        data=report.read_bytes(),
        file_name=report.name,
        mime="text/html",
    )
st.caption(
    "Data/concept drift da produção é simulado; os dados originais "
    "não contêm uma série temporal."
)
