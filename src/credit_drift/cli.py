import argparse
import logging

from credit_drift.events import record_event
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
        record_event(
            "pipeline_failed",
            command=args.command,
            error_type=type(exc).__name__,
            error=str(exc),
            status="failed",
        )
        logging.exception("Execução falhou")
        raise


if __name__ == "__main__":
    main()
