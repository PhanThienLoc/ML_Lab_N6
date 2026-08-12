"""Command-line entry point for reproducibly generating TV1 artifacts."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.pipeline import prepare_data


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the leakage-safe Olist TV1 handoff.")
    parser.add_argument("--raw-dir", default="data/raw", help="Directory containing the four Olist CSV files.")
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
    split = prepared["metadata"]["temporal_split"]
    print("TV1 pipeline completed.")
    print(f"Processed rows: {len(prepared['processed_dataset'])}")
    print("Target-month splits:")
    for name, details in split.items():
        print(f"  {name}: {details['target_month_start']}..{details['target_month_end']} ({details['rows']} rows)")
    print(f"Model features: {len(prepared['metadata']['feature_names'])}")


if __name__ == "__main__":
    main()
