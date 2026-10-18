"""Summarize tasks_v2 experiment results and create publication-ready figures."""

import csv
import json
import math
import statistics
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parent
RESULTS_DIR = ROOT / "results"
FIGURES_DIR = ROOT / "figures"
TASKS = "tasks_v2"
MODEL = "gpt-5.6-luna"
SETS = ("optimization", "heldout")
BASELINE_RUNS = (0, 101, 102, 103)
FINAL_RUNS = (5, 201, 202, 203)
LOOP_ITERATIONS = (1, 2, 3, 4, 5)

# Okabe-Ito blue and vermilion are distinct in common color-vision deficiencies.
COLORS = {"baseline": "#0072B2", "final": "#D55E00"}
SET_COLORS = {"optimization": "#0072B2", "heldout": "#D55E00"}


def _result_path(iteration, task_set):
    return RESULTS_DIR / (
        f"iter_{iteration}_{TASKS}_{task_set}_{MODEL}.json"
    )


def _read_result(iteration, task_set):
    path = _result_path(iteration, task_set)
    if not path.is_file():
        raise FileNotFoundError(f"Missing result file: {path.relative_to(ROOT)}")
    try:
        result = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"Cannot read {path.relative_to(ROOT)}: {exc}") from exc

    expected = {
        "iteration": iteration,
        "tasks": TASKS,
        "set": task_set,
        "model": MODEL,
    }
    for key, value in expected.items():
        if result.get(key) != value:
            raise ValueError(
                f"Unexpected {key!r} in {path.relative_to(ROOT)}: "
                f"expected {value!r}, found {result.get(key)!r}"
            )

    rate = result.get("pass_rate_generated", result.get("pass_rate"))
    tests_total = result.get("tests_total")
    if not isinstance(rate, (int, float)) or not math.isfinite(rate) or not 0 <= rate <= 1:
        raise ValueError(f"Invalid pass rate in {path.relative_to(ROOT)}: {rate!r}")
    if not isinstance(tests_total, int) or tests_total <= 0:
        raise ValueError(f"Invalid tests_total in {path.relative_to(ROOT)}: {tests_total!r}")
    return {"iteration": iteration, "pass_rate": float(rate), "tests_total": tests_total}


def _load_all_results():
    data = {}
    for task_set in SETS:
        for iteration in sorted(set(BASELINE_RUNS + FINAL_RUNS + LOOP_ITERATIONS)):
            data[(iteration, task_set)] = _read_result(iteration, task_set)
    return data


def _sample_std(values):
    return statistics.stdev(values) if len(values) > 1 else 0.0


def _condition_rows(data):
    rows = []
    for condition, iterations in (("baseline", BASELINE_RUNS), ("final", FINAL_RUNS)):
        for task_set in SETS:
            runs = [data[(iteration, task_set)] for iteration in iterations]
            totals = {run["tests_total"] for run in runs}
            if len(totals) != 1:
                raise ValueError(
                    f"Inconsistent tests_total for {condition}/{task_set}: "
                    f"{sorted(totals)}"
                )
            rates = [run["pass_rate"] for run in runs]
            rows.append({
                "condition": condition,
                "set": task_set,
                "n_runs": len(runs),
                "mean_pass_rate": statistics.mean(rates),
                "std_pass_rate": _sample_std(rates),
                "min": min(rates),
                "max": max(rates),
                "tests_total": runs[0]["tests_total"],
                "run_rates": rates,
            })
    return rows


def _write_summary_csv(rows):
    path = RESULTS_DIR / "summary_final.csv"
    fields = (
        "condition", "set", "n_runs", "mean_pass_rate", "std_pass_rate",
        "min", "max", "tests_total",
    )
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows({field: row[field] for field in fields} for row in rows)
    return path


def _write_curve_csv(data):
    path = RESULTS_DIR / "curve_iterations.csv"
    fields = ("iteration", "optimization_pass_rate", "heldout_pass_rate")
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for iteration in range(6):
            if iteration == 0:
                baseline = {
                    task_set: statistics.mean(
                        data[(run, task_set)]["pass_rate"] for run in BASELINE_RUNS
                    )
                    for task_set in SETS
                }
                rates = baseline
            else:
                rates = {
                    task_set: data[(iteration, task_set)]["pass_rate"]
                    for task_set in SETS
                }
            writer.writerow({
                "iteration": iteration,
                "optimization_pass_rate": rates["optimization"],
                "heldout_pass_rate": rates["heldout"],
            })
    return path


def _style_axis(axis):
    axis.set_ylim(0, 100)
    axis.set_yticks(range(0, 101, 10))
    axis.set_ylabel("Pass rate (%)")
    axis.grid(axis="y", color="#D9D9D9", linewidth=0.7, alpha=0.8)
    axis.set_axisbelow(True)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)


def _save_curve_figure(data):
    iterations = list(range(6))
    fig, axis = plt.subplots(figsize=(8.2, 5.2), constrained_layout=True)
    for task_set in SETS:
        rates = []
        for iteration in iterations:
            if iteration == 0:
                rate = statistics.mean(
                    data[(run, task_set)]["pass_rate"] for run in BASELINE_RUNS
                )
            else:
                rate = data[(iteration, task_set)]["pass_rate"]
            rates.append(rate * 100)
        axis.plot(
            iterations,
            rates,
            marker="o",
            markersize=6,
            linewidth=2.2,
            color=SET_COLORS[task_set],
            label="Optimization set" if task_set == "optimization" else "Held-out set",
        )
    axis.set_title("Pass rate by iteration")
    axis.set_xlabel("Iteration")
    axis.set_xticks(iterations)
    _style_axis(axis)
    axis.legend(frameon=False, loc="best")
    axis.text(
        0.99,
        0.02,
        "Single run per iteration (iteration 0 shows the 4-run baseline mean)",
        transform=axis.transAxes,
        ha="right",
        va="bottom",
        fontsize=8.5,
        color="#444444",
    )
    png_path = FIGURES_DIR / "fig_curve.png"
    pdf_path = FIGURES_DIR / "fig_curve.pdf"
    fig.savefig(png_path, dpi=220)
    fig.savefig(pdf_path)
    plt.close(fig)
    return png_path, pdf_path


def _save_comparison_figure(rows):
    fig, axis = plt.subplots(figsize=(8.2, 5.2), constrained_layout=True)
    centers = {"optimization": 0.0, "heldout": 1.0}
    condition_offsets = {"baseline": -0.18, "final": 0.18}
    bar_width = 0.32
    row_lookup = {(row["condition"], row["set"]): row for row in rows}

    for condition in ("baseline", "final"):
        for task_set in SETS:
            row = row_lookup[(condition, task_set)]
            x = centers[task_set] + condition_offsets[condition]
            rates = row["run_rates"]
            mean = row["mean_pass_rate"] * 100
            std = row["std_pass_rate"] * 100
            axis.bar(
                x,
                mean,
                width=bar_width,
                color=COLORS[condition],
                alpha=0.88,
                edgecolor="white",
                linewidth=0.8,
                yerr=std,
                capsize=4,
                error_kw={"elinewidth": 1.3, "capthick": 1.3, "ecolor": "#222222"},
                label=condition.title() if task_set == SETS[0] else "_nolegend_",
                zorder=2,
            )
            if len(rates) > 1:
                jitter_step = 0.055
                jitters = [
                    (index - (len(rates) - 1) / 2) * jitter_step
                    for index in range(len(rates))
                ]
            else:
                jitters = [0.0]
            axis.scatter(
                [x + jitter for jitter in jitters],
                [rate * 100 for rate in rates],
                s=36,
                color="#FFFFFF",
                edgecolor=COLORS[condition],
                linewidth=1.5,
                zorder=3,
            )

    axis.set_title("Baseline vs final performance")
    axis.set_xlabel("Evaluation set")
    axis.set_xticks([centers[task_set] for task_set in SETS])
    axis.set_xticklabels(["Optimization", "Held-out"])
    _style_axis(axis)
    axis.legend(frameon=False, loc="best", title="Condition")
    png_path = FIGURES_DIR / "fig_baseline_vs_final.png"
    pdf_path = FIGURES_DIR / "fig_baseline_vs_final.pdf"
    fig.savefig(png_path, dpi=220)
    fig.savefig(pdf_path)
    plt.close(fig)
    return png_path, pdf_path


def _print_table(rows):
    columns = (
        ("condition", "Condition"),
        ("set", "Set"),
        ("n_runs", "N"),
        ("mean_pass_rate", "Mean"),
        ("std_pass_rate", "Std"),
        ("min", "Min"),
        ("max", "Max"),
        ("tests_total", "Tests"),
    )
    rendered = []
    for row in rows:
        rendered.append({
            "Condition": row["condition"],
            "Set": row["set"],
            "N": str(row["n_runs"]),
            "Mean": f"{row['mean_pass_rate']:.3f}",
            "Std": f"{row['std_pass_rate']:.3f}",
            "Min": f"{row['min']:.3f}",
            "Max": f"{row['max']:.3f}",
            "Tests": str(row["tests_total"]),
        })
    widths = {
        label: max(len(label), *(len(row[label]) for row in rendered))
        for _, label in columns
    }
    header = " | ".join(label.ljust(widths[label]) for _, label in columns)
    separator = "-+-".join("-" * widths[label] for _, label in columns)
    print(header)
    print(separator)
    for row in rendered:
        print(" | ".join(row[label].ljust(widths[label]) for _, label in columns))
    print("Rates are fractions from 0 to 1; Std is the sample standard deviation.")


def main():
    try:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        FIGURES_DIR.mkdir(parents=True, exist_ok=True)
        data = _load_all_results()
        rows = _condition_rows(data)
        summary_path = _write_summary_csv(rows)
        curve_path = _write_curve_csv(data)
        curve_png, curve_pdf = _save_curve_figure(data)
        compare_png, compare_pdf = _save_comparison_figure(rows)
    except (OSError, ValueError, FileNotFoundError) as exc:
        print(f"Analysis failed: {exc}", file=sys.stderr)
        return 1

    _print_table(rows)
    print(f"Wrote {summary_path.relative_to(ROOT)}")
    print(f"Wrote {curve_path.relative_to(ROOT)}")
    print(f"Wrote {curve_png.relative_to(ROOT)} and {curve_pdf.relative_to(ROOT)}")
    print(f"Wrote {compare_png.relative_to(ROOT)} and {compare_pdf.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
