from pathlib import Path
import json

import matplotlib.pyplot as plt
import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[1]

LOG_DIR = ROOT_DIR / "logs"
REPORT_DIR = ROOT_DIR / "reports"
FIGURE_DIR = REPORT_DIR / "figures"

EXPERIMENT_FILE = LOG_DIR / "experiments.csv"
FINAL_TEST_FILE = LOG_DIR / "final_test.json"

FIGURE_FILE = FIGURE_DIR / "model_validation_rmse.png"
REPORT_FILE = REPORT_DIR / "model_comparison.md"


def find_column(df, *possible_names):
    """
    Find the first existing column name.

    This allows the visualization script to work with
    validation_rmse or val_rmse style column names.
    """
    for name in possible_names:
        if name in df.columns:
            return name

    raise KeyError(
        f"Could not find any of these columns: {possible_names}"
    )


def load_experiments():
    if not EXPERIMENT_FILE.exists():
        raise FileNotFoundError(
            "logs/experiments.csv was not found. "
            "Run the experiment pipeline first."
        )

    df = pd.read_csv(EXPERIMENT_FILE)

    if "status" in df.columns:
        df = df[df["status"].astype(str).str.lower() == "success"]

    if df.empty:
        raise ValueError("No successful experiments were found.")

    return df


def load_final_test():
    if not FINAL_TEST_FILE.exists():
        raise FileNotFoundError(
            "logs/final_test.json was not found. "
            "Run the experiment pipeline first."
        )

    with open(FINAL_TEST_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def create_rmse_chart(df, rmse_col):
    FIGURE_DIR.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(10, 6))

    bars = plt.bar(
        df["run_id"].astype(str),
        df[rmse_col].astype(float)
    )

    plt.title("Validation RMSE Comparison")
    plt.xlabel("Experiment Run")
    plt.ylabel("Validation RMSE")

    for bar, value in zip(bars, df[rmse_col]):
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height(),
            f"{float(value):.2f}",
            ha="center",
            va="bottom"
        )

    plt.tight_layout()
    plt.savefig(FIGURE_FILE, dpi=200)
    plt.close()


def create_model_report(
    df,
    final_test,
    mae_col,
    rmse_col,
    r2_col
):
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    ranked = df.sort_values(rmse_col, ascending=True)
    best = ranked.iloc[0]

    lines = []

    lines.append("# Model Comparison Report")
    lines.append("")
    lines.append(
        "Báo cáo này được sinh tự động từ "
        "`logs/experiments.csv` và `logs/final_test.json`."
    )
    lines.append("")

    lines.append("## 1. Experiment Results")
    lines.append("")
    lines.append(
        "| Run ID | Model | Validation MAE | "
        "Validation RMSE | Validation R2 |"
    )
    lines.append(
        "|---|---|---:|---:|---:|"
    )

    for _, row in df.iterrows():
        lines.append(
            f"| {row['run_id']} "
            f"| {row['model']} "
            f"| {float(row[mae_col]):.4f} "
            f"| {float(row[rmse_col]):.4f} "
            f"| {float(row[r2_col]):.4f} |"
        )

    lines.append("")
    lines.append("## 2. Validation RMSE Visualization")
    lines.append("")
    lines.append(
        "![Validation RMSE Comparison]"
        "(figures/model_validation_rmse.png)"
    )
    lines.append("")

    lines.append("## 3. Best Model Selection")
    lines.append("")
    lines.append(
        "Tiêu chí chính để chọn best model là "
        "**Validation RMSE**, trong đó giá trị càng thấp càng tốt."
    )
    lines.append("")
    lines.append(f"- Best Run: **{best['run_id']}**")
    lines.append(f"- Model: **{best['model']}**")
    lines.append(
        f"- Validation MAE: **{float(best[mae_col]):.4f}**"
    )
    lines.append(
        f"- Validation RMSE: **{float(best[rmse_col]):.4f}**"
    )
    lines.append(
        f"- Validation R2: **{float(best[r2_col]):.4f}**"
    )
    lines.append("")

    lines.append("## 4. Final Test Evaluation")
    lines.append("")
    lines.append(
        "Sau khi best configuration được chọn bằng validation set, "
        "model cuối được train lại trên Train + Validation và "
        "sau đó mới đánh giá trên Test Set."
    )
    lines.append("")

    lines.append(
        f"- Selected Run: "
        f"**{final_test.get('selected_run', 'N/A')}**"
    )
    lines.append(
        f"- Model: **{final_test.get('model', 'N/A')}**"
    )
    lines.append(
        f"- Test MAE: "
        f"**{float(final_test.get('test_mae', 0)):.4f}**"
    )
    lines.append(
        f"- Test MSE: "
        f"**{float(final_test.get('test_mse', 0)):.4f}**"
    )
    lines.append(
        f"- Test RMSE: "
        f"**{float(final_test.get('test_rmse', 0)):.4f}**"
    )
    lines.append(
        f"- Test R2: "
        f"**{float(final_test.get('test_r2', 0)):.4f}**"
    )
    lines.append("")

    lines.append("## 5. Conclusion")
    lines.append("")
    lines.append(
        "Model được chọn dựa trên validation data, "
        "không sử dụng test set để tune hyperparameter."
    )
    lines.append("")
    lines.append(
        "Final test chỉ được sử dụng sau khi best configuration "
        "đã được xác định."
    )

    REPORT_FILE.write_text(
        "\n".join(lines),
        encoding="utf-8"
    )


def main():
    print("=" * 60)
    print("MODEL RESULT VISUALIZATION")
    print("=" * 60)

    experiments = load_experiments()
    final_test = load_final_test()

    mae_col = find_column(
        experiments,
        "validation_mae",
        "val_mae"
    )

    rmse_col = find_column(
        experiments,
        "validation_rmse",
        "val_rmse"
    )

    r2_col = find_column(
        experiments,
        "validation_r2",
        "val_r2"
    )

    create_rmse_chart(
        experiments,
        rmse_col
    )

    create_model_report(
        experiments,
        final_test,
        mae_col,
        rmse_col,
        r2_col
    )

    best = experiments.loc[
        experiments[rmse_col].astype(float).idxmin()
    ]

    print(f"Experiments: {len(experiments)}")
    print(f"Best Run: {best['run_id']}")
    print(f"Best Model: {best['model']}")
    print(
        f"Validation RMSE: "
        f"{float(best[rmse_col]):.4f}"
    )

    print()
    print(f"Figure saved to:")
    print(FIGURE_FILE)

    print()
    print(f"Report saved to:")
    print(REPORT_FILE)

    print("=" * 60)


if __name__ == "__main__":
    main()
