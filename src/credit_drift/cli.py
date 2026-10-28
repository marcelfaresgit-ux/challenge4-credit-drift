import argparse
import json
import logging
from datetime import UTC, datetime

from credit_drift.config import LOGS_DIR
from credit_drift.monitoring import demonstrate_contract_failure, run_pipeline


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Pipeline de qualidade de dados e monitoramento de drift em crédito"
    )
    parser.add_argument(
        "command", choices=["run", "demo-contract"], nargs="?", default="run"
    )
    parser.add_argument(
        "--rows", type=int, default=60000, help="Limite de linhas usadas nesta execução"
    )
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    try:
        if args.command == "demo-contract":
            print(demonstrate_contract_failure())
        else:
            print(run_pipeline(max_rows=args.rows))
    except Exception as exc:
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        event = {
            "event": "pipeline_failed",
            "timestamp_utc": datetime.now(UTC).isoformat(),
            "command": args.command,
            "error_type": type(exc).__name__,
            "error": str(exc),
        }
        with (LOGS_DIR / "pipeline_events.jsonl").open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(event, ensure_ascii=False) + "\n")
        logging.exception("Execução falhou")
        raise


if __name__ == "__main__":
    main()
