"""Command-line entry point for reproducibly generating TV1 artifacts."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.pipeline import prepare_data


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the Customer Shopping Trends regression handoff.")
    parser.add_argument("--raw-dir", default="data/raw", help="Directory containing shopping_trends.csv.")
    parser.add_argument("--processed-dir", default="data/processed", help="Directory for generated CSV and metadata.")
    parser.add_argument("--report-dir", default="reports", help="Directory for generated TV1 Markdown reports.")
    parser.add_argument("--log-path", default="logs/data_quality.log", help="Generated TV1 data-quality log path.")
    args = parser.parse_args()
    prepared = prepare_data(
        raw_dir=Path(args.raw_dir),
        processed_dir=Path(args.processed_dir),
        report_dir=Path(args.report_dir),
        log_path=Path(args.log_path),
    )
    split = {"train": len(prepared["y_train"]), "validation": len(prepared["y_val"]), "test": len(prepared["y_test"])}
    print("TV1 pipeline completed.")
    print(f"Processed rows: {len(prepared['processed_dataset'])}")
    print("Random row splits (seed=42):")
    for name, rows in split.items():
        print(f"  {name}: {rows} rows")
    print(f"Model features: {len(prepared['metadata']['feature_names'])}")


if __name__ == "__main__":
    main()
