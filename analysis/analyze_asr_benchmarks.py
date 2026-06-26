from __future__ import annotations

import json
import math
from pathlib import Path

import matplotlib.font_manager as fm
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RESULT_DIR = ROOT / "result"
OUTPUT_DIR = ROOT / "analysis" / "outputs"
ASSET_DIR = ROOT / "blog" / "assets"
DOCS_ASSET_DIR = ROOT / "docs" / "assets"
INTERACTIVE_DATA_DIR = ROOT / "blog" / "interactive" / "data"
DOCS_DATA_DIR = ROOT / "docs" / "data"
RNG_SEED = 20260625

SINGLE_SPEAKER_MODELS = {
    "aws_transcribe": {
        "label": "AWS Transcribe",
        "path": RESULT_DIR / "result_3922.csv",
    },
    "whisper_base": {
        "label": "Whisper base",
        "path": RESULT_DIR / "openai_whisper_base_result_3922.csv",
    },
    "whisper_medium": {
        "label": "Whisper medium",
        "path": RESULT_DIR / "openai_whisper_medium_result_3922.csv",
    },
    "whisper_large": {
        "label": "Whisper large",
        "path": RESULT_DIR / "openai_whisper_large_result_3922.csv",
    },
}

CALL_CENTER_PROVIDER_COLUMNS = {
    "aws": "AWS",
    "azure": "Azure",
    "clova": "Clova",
    "gcp": "GCP",
}

CALL_CENTER_SCENARIOS = [
    "PB bond order",
    "Startup business loan",
    "Auto insurance surcharge",
]


def ensure_dirs() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_ASSET_DIR.mkdir(parents=True, exist_ok=True)
    INTERACTIVE_DATA_DIR.mkdir(parents=True, exist_ok=True)
    DOCS_DATA_DIR.mkdir(parents=True, exist_ok=True)


def configure_matplotlib() -> None:
    font_candidates = [
        "/System/Library/Fonts/AppleSDGothicNeo.ttc",
        "/Library/Fonts/AppleGothic.ttf",
    ]
    for path in font_candidates:
        if Path(path).exists():
            fm.fontManager.addfont(path)
            plt.rcParams["font.family"] = fm.FontProperties(fname=path).get_name()
            break
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["figure.dpi"] = 160
    plt.rcParams["savefig.dpi"] = 220


def read_result_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    unnamed = [col for col in df.columns if str(col).startswith("Unnamed") or col == ""]
    if unnamed:
        df = df.drop(columns=unnamed)
    return df


def bootstrap_mean_ci(values: pd.Series, rounds: int = 2000) -> tuple[float, float]:
    arr = values.dropna().to_numpy(dtype=float)
    if len(arr) == 0:
        return math.nan, math.nan
    rng = np.random.default_rng(RNG_SEED)
    samples = rng.choice(arr, size=(rounds, len(arr)), replace=True).mean(axis=1)
    return float(np.quantile(samples, 0.025)), float(np.quantile(samples, 0.975))


def bootstrap_delta_ci(a: pd.Series, b: pd.Series, rounds: int = 2000) -> tuple[float, float]:
    arr = (a - b).dropna().to_numpy(dtype=float)
    if len(arr) == 0:
        return math.nan, math.nan
    rng = np.random.default_rng(RNG_SEED)
    samples = rng.choice(arr, size=(rounds, len(arr)), replace=True).mean(axis=1)
    return float(np.quantile(samples, 0.025)), float(np.quantile(samples, 0.975))


def load_single_speaker_long() -> pd.DataFrame:
    frames = []
    file_name_sets = {}
    for model_id, spec in SINGLE_SPEAKER_MODELS.items():
        df = read_result_csv(spec["path"])
        required = ["file_name", "ground_truth", "word_lenth", "transcribe_sentence", "cer"]
        missing = [col for col in required if col not in df.columns]
        if missing:
            raise ValueError(f"{spec['path']} is missing columns: {missing}")
        file_name_sets[model_id] = set(df["file_name"].dropna())
        frames.append(
            df[required]
            .assign(
                model_id=model_id,
                model=spec["label"],
                text_length=lambda x: pd.to_numeric(x["word_lenth"], errors="coerce"),
                cer=lambda x: pd.to_numeric(x["cer"], errors="coerce"),
            )
            .drop(columns=["word_lenth"])
        )
    expected_model_id, expected_files = next(iter(file_name_sets.items()))
    for model_id, files in file_name_sets.items():
        if files != expected_files:
            missing = sorted(expected_files - files)[:5]
            extra = sorted(files - expected_files)[:5]
            raise ValueError(
                f"{model_id} file_name set does not match {expected_model_id}; "
                f"missing examples={missing}, extra examples={extra}"
            )
    return pd.concat(frames, ignore_index=True)


def summarize_single_speaker(single_long: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (model_id, model), g in single_long.groupby(["model_id", "model"], sort=False):
        ci_low, ci_high = bootstrap_mean_ci(g["cer"])
        length_cer_spearman = g["text_length"].rank().corr(g["cer"].rank(), method="pearson")
        rows.append(
            {
                "model_id": model_id,
                "model": model,
                "n": len(g),
                "mean_cer": g["cer"].mean(),
                "mean_cer_ci95_low": ci_low,
                "mean_cer_ci95_high": ci_high,
                "median_cer": g["cer"].median(),
                "std_cer": g["cer"].std(ddof=1),
                "p75_cer": g["cer"].quantile(0.75),
                "p90_cer": g["cer"].quantile(0.90),
                "p95_cer": g["cer"].quantile(0.95),
                "p99_cer": g["cer"].quantile(0.99),
                "max_cer": g["cer"].max(),
                "perfect_rate": (g["cer"] == 0).mean(),
                "pass_1pct_rate": (g["cer"] <= 0.01).mean(),
                "pass_3pct_rate": (g["cer"] <= 0.03).mean(),
                "pass_5pct_rate": (g["cer"] <= 0.05).mean(),
                "pass_10pct_rate": (g["cer"] <= 0.10).mean(),
                "over_10pct_rate": (g["cer"] > 0.10).mean(),
                "over_20pct_rate": (g["cer"] > 0.20).mean(),
                "length_cer_pearson": g["text_length"].corr(g["cer"], method="pearson"),
                "length_cer_spearman": length_cer_spearman,
            }
        )
    return pd.DataFrame(rows).sort_values("mean_cer")


def build_single_wide(single_long: pd.DataFrame) -> pd.DataFrame:
    base_cols = ["file_name", "ground_truth", "text_length"]
    base = single_long[base_cols].drop_duplicates("file_name")
    pivot = single_long.pivot(index="file_name", columns="model_id", values="cer").reset_index()
    return base.merge(pivot, on="file_name", how="left")


def threshold_pass_rates(single_long: pd.DataFrame) -> pd.DataFrame:
    thresholds = [0, 0.01, 0.03, 0.05, 0.10, 0.15, 0.20]
    rows = []
    for (model_id, model), g in single_long.groupby(["model_id", "model"], sort=False):
        for threshold in thresholds:
            rows.append(
                {
                    "model_id": model_id,
                    "model": model,
                    "cer_threshold": threshold,
                    "pass_rate": (g["cer"] <= threshold).mean(),
                }
            )
    return pd.DataFrame(rows)


def paired_deltas(single_wide: pd.DataFrame) -> pd.DataFrame:
    model_ids = list(SINGLE_SPEAKER_MODELS.keys())
    rows = []
    for left in model_ids:
        for right in model_ids:
            if left == right:
                continue
            delta = single_wide[left] - single_wide[right]
            ci_low, ci_high = bootstrap_delta_ci(single_wide[left], single_wide[right])
            rows.append(
                {
                    "left_model_id": left,
                    "left_model": SINGLE_SPEAKER_MODELS[left]["label"],
                    "right_model_id": right,
                    "right_model": SINGLE_SPEAKER_MODELS[right]["label"],
                    "mean_delta_cer_left_minus_right": delta.mean(),
                    "mean_delta_ci95_low": ci_low,
                    "mean_delta_ci95_high": ci_high,
                    "left_better_count": int((delta < 0).sum()),
                    "right_better_count": int((delta > 0).sum()),
                    "tie_count": int((delta == 0).sum()),
                    "left_better_rate_excluding_ties": (
                        (delta < 0).sum() / ((delta != 0).sum())
                        if int((delta != 0).sum()) > 0
                        else math.nan
                    ),
                }
            )
    return pd.DataFrame(rows)


def length_bin_summary(single_long: pd.DataFrame) -> pd.DataFrame:
    bins = [0, 20, 30, 40, 50, 10_000]
    labels = ["<=20", "21-30", "31-40", "41-50", "51+"]
    labeled = single_long.copy()
    labeled["length_bin"] = pd.cut(labeled["text_length"], bins=bins, labels=labels)
    summary = (
        labeled.groupby(["model_id", "model", "length_bin"], observed=True)
        .agg(n=("cer", "size"), mean_cer=("cer", "mean"), median_cer=("cer", "median"), perfect_rate=("cer", lambda s: (s == 0).mean()))
        .reset_index()
    )
    return summary


def worst_examples(single_long: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (model_id, model), g in single_long.groupby(["model_id", "model"], sort=False):
        top = g.sort_values("cer", ascending=False).head(20).copy()
        top["model_id"] = model_id
        top["model"] = model
        rows.append(top)
    return pd.concat(rows, ignore_index=True)[
        ["model_id", "model", "file_name", "text_length", "cer", "ground_truth", "transcribe_sentence"]
    ]


def disagreement_examples(single_long: pd.DataFrame, single_wide: pd.DataFrame) -> pd.DataFrame:
    cols = list(SINGLE_SPEAKER_MODELS.keys())
    wide = single_wide.copy()
    wide["best_cer"] = wide[cols].min(axis=1)
    wide["worst_cer"] = wide[cols].max(axis=1)
    wide["cer_spread"] = wide["worst_cer"] - wide["best_cer"]
    wide["best_models"] = wide[cols].apply(
        lambda row: ", ".join(SINGLE_SPEAKER_MODELS[col]["label"] for col in cols if row[col] == row.min()),
        axis=1,
    )
    wide["worst_models"] = wide[cols].apply(
        lambda row: ", ".join(SINGLE_SPEAKER_MODELS[col]["label"] for col in cols if row[col] == row.max()),
        axis=1,
    )
    transcripts = (
        single_long.pivot(index="file_name", columns="model_id", values="transcribe_sentence")
        .add_prefix("transcript_")
        .reset_index()
    )
    return (
        wide.merge(transcripts, on="file_name", how="left")
        .sort_values("cer_spread", ascending=False)
        .head(30)
    )


def quality_gate_policy_simulation(single_long: pd.DataFrame) -> pd.DataFrame:
    policies = {
        "strict": {"pass": 0.03, "review": 0.10},
        "balanced": {"pass": 0.05, "review": 0.15},
        "lenient": {"pass": 0.10, "review": 0.20},
    }
    rows = []
    for (model_id, model), g in single_long.groupby(["model_id", "model"], sort=False):
        for policy, bounds in policies.items():
            cer = g["cer"]
            rows.append(
                {
                    "model_id": model_id,
                    "model": model,
                    "policy": policy,
                    "pass_threshold": bounds["pass"],
                    "review_threshold": bounds["review"],
                    "pass_rate": (cer <= bounds["pass"]).mean(),
                    "review_rate": ((cer > bounds["pass"]) & (cer <= bounds["review"])).mean(),
                    "block_rate": (cer > bounds["review"]).mean(),
                }
            )
    return pd.DataFrame(rows)


def load_call_center_long() -> pd.DataFrame:
    frames = []
    for basis, path in [
        ("hangul ground truth", RESULT_DIR / "cs_hangul_result.csv"),
        ("numeric ground truth", RESULT_DIR / "cs_number_result.csv"),
    ]:
        df = read_result_csv(path)
        if len(df) != len(CALL_CENTER_SCENARIOS):
            raise ValueError(
                f"{path} has {len(df)} rows, but {len(CALL_CENTER_SCENARIOS)} call-center scenarios are configured"
            )
        df["scenario"] = CALL_CENTER_SCENARIOS[: len(df)]
        for provider_id, provider in CALL_CENTER_PROVIDER_COLUMNS.items():
            col = f"cer_{provider_id}"
            if col not in df.columns:
                raise ValueError(f"{path} is missing {col}")
            frames.append(
                df[["scenario", col]]
                .rename(columns={col: "cer"})
                .assign(provider_id=provider_id, provider=provider, basis=basis)
            )
    return pd.concat(frames, ignore_index=True)


def summarize_call_center(call_long: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (basis, provider_id, provider), g in call_long.groupby(["basis", "provider_id", "provider"], sort=False):
        rows.append(
            {
                "basis": basis,
                "provider_id": provider_id,
                "provider": provider,
                "n": len(g),
                "mean_cer": g["cer"].mean(),
                "median_cer": g["cer"].median(),
                "min_cer": g["cer"].min(),
                "max_cer": g["cer"].max(),
                "pass_10pct_rate": (g["cer"] <= 0.10).mean(),
                "over_20pct_rate": (g["cer"] > 0.20).mean(),
            }
        )
    return pd.DataFrame(rows).sort_values(["basis", "mean_cer"])


def model_win_counts(single_wide: pd.DataFrame) -> pd.DataFrame:
    model_ids = list(SINGLE_SPEAKER_MODELS.keys())
    rows = []
    for model_id in model_ids:
        values = single_wide[model_ids]
        rows.append(
            {
                "model_id": model_id,
                "model": SINGLE_SPEAKER_MODELS[model_id]["label"],
                "best_or_tied_count": int((values[model_id] == values.min(axis=1)).sum()),
                "sole_best_count": int(((values[model_id] == values.min(axis=1)) & (values.eq(values.min(axis=1), axis=0).sum(axis=1) == 1)).sum()),
                "worst_or_tied_count": int((values[model_id] == values.max(axis=1)).sum()),
                "sole_worst_count": int(((values[model_id] == values.max(axis=1)) & (values.eq(values.max(axis=1), axis=0).sum(axis=1) == 1)).sum()),
            }
        )
    return pd.DataFrame(rows).sort_values("sole_best_count", ascending=False)


def percent_axis(ax) -> None:
    ax.yaxis.set_major_formatter(lambda x, pos: f"{x * 100:.0f}%")


def save_chart(fig: plt.Figure, filename: str, **kwargs) -> None:
    for directory in [ASSET_DIR, DOCS_ASSET_DIR]:
        fig.savefig(directory / filename, **kwargs)


def plot_single_mean(summary: pd.DataFrame) -> None:
    plot_df = summary.sort_values("mean_cer")
    labels = plot_df["model"].tolist()
    y = plot_df["mean_cer"].to_numpy()
    low = y - plot_df["mean_cer_ci95_low"].to_numpy()
    high = plot_df["mean_cer_ci95_high"].to_numpy() - y
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    colors = ["#2E7D32", "#558B2F", "#1565C0", "#6D4C41"]
    ax.bar(labels, y, yerr=np.vstack([low, high]), color=colors[: len(labels)], capsize=4)
    ax.set_title("Single-speaker Korean ASR: mean CER with 95% bootstrap CI")
    ax.set_ylabel("CER")
    percent_axis(ax)
    ax.grid(axis="y", alpha=0.25)
    ax.set_axisbelow(True)
    for idx, value in enumerate(y):
        ax.text(idx, value + 0.002, f"{value * 100:.2f}%", ha="center", va="bottom", fontsize=9)
    fig.tight_layout()
    save_chart(fig, "single_speaker_mean_cer.png")
    plt.close(fig)


def plot_thresholds(thresholds: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    for model_id, g in thresholds.groupby("model_id", sort=False):
        ax.plot(g["cer_threshold"], g["pass_rate"], marker="o", label=SINGLE_SPEAKER_MODELS[model_id]["label"])
    ax.set_title("Pass rate by CER threshold")
    ax.set_xlabel("Allowed CER threshold")
    ax.set_ylabel("Pass rate")
    percent_axis(ax)
    ax.xaxis.set_major_formatter(lambda x, pos: f"{x * 100:.0f}%")
    ax.grid(alpha=0.25)
    ax.legend(frameon=False, ncols=2)
    fig.tight_layout()
    save_chart(fig, "single_speaker_threshold_pass_rates.png")
    plt.close(fig)


def plot_distribution(single_long: pd.DataFrame) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(10, 6), sharex=True, sharey=True)
    bins = np.linspace(0, 0.35, 36)
    for ax, (model_id, g) in zip(axes.ravel(), single_long.groupby("model_id", sort=False)):
        ax.hist(g["cer"], bins=bins, color="#4E79A7", alpha=0.85)
        ax.axvline(g["cer"].mean(), color="#C0392B", linestyle="--", linewidth=1.2, label="mean")
        ax.set_title(SINGLE_SPEAKER_MODELS[model_id]["label"])
        ax.grid(axis="y", alpha=0.2)
    fig.suptitle("CER distribution is zero-heavy and long-tailed")
    for ax in axes[-1, :]:
        ax.set_xlabel("CER")
        ax.xaxis.set_major_formatter(lambda x, pos: f"{x * 100:.0f}%")
    for ax in axes[:, 0]:
        ax.set_ylabel("Utterances")
    fig.tight_layout()
    save_chart(fig, "single_speaker_cer_distribution.png")
    plt.close(fig)


def plot_length_bins(length_summary: pd.DataFrame) -> None:
    order = ["<=20", "21-30", "31-40", "41-50", "51+"]
    fig, ax = plt.subplots(figsize=(8.5, 4.8))
    for model_id, g in length_summary.groupby("model_id", sort=False):
        g = g.set_index("length_bin").reindex(order).reset_index()
        ax.plot(g["length_bin"], g["mean_cer"], marker="o", label=SINGLE_SPEAKER_MODELS[model_id]["label"])
    ax.set_title("Mean CER by reference sentence length")
    ax.set_xlabel("Reference text length")
    ax.set_ylabel("Mean CER")
    percent_axis(ax)
    ax.grid(alpha=0.25)
    ax.legend(frameon=False, ncols=2)
    fig.tight_layout()
    save_chart(fig, "single_speaker_length_bins.png")
    plt.close(fig)


def plot_call_center(call_long: pd.DataFrame) -> None:
    summary = summarize_call_center(call_long)
    fig, ax = plt.subplots(figsize=(8.8, 4.8))
    providers = list(CALL_CENTER_PROVIDER_COLUMNS.values())
    bases = ["hangul ground truth", "numeric ground truth"]
    width = 0.36
    x = np.arange(len(providers))
    for i, basis in enumerate(bases):
        g = summary[summary["basis"] == basis].set_index("provider").reindex(providers)
        offset = (i - 0.5) * width
        ax.bar(x + offset, g["mean_cer"], width=width, label=basis)
        for xi, value in zip(x + offset, g["mean_cer"]):
            ax.text(xi, value + 0.005, f"{value * 100:.1f}%", ha="center", va="bottom", fontsize=8)
    ax.set_title("Financial call-center samples: mean CER by provider")
    ax.set_xticks(x)
    ax.set_xticklabels(providers)
    ax.set_ylabel("Mean CER")
    percent_axis(ax)
    ax.grid(axis="y", alpha=0.25)
    ax.set_axisbelow(True)
    ax.legend(frameon=False)
    fig.tight_layout()
    save_chart(fig, "call_center_provider_mean_cer.png")
    plt.close(fig)


def plot_call_center_heatmap(call_long: pd.DataFrame) -> None:
    bases = ["hangul ground truth", "numeric ground truth"]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.8), sharey=True)
    for ax, basis in zip(axes, bases):
        pivot = (
            call_long[call_long["basis"] == basis]
            .pivot(index="scenario", columns="provider", values="cer")
            .reindex(index=CALL_CENTER_SCENARIOS, columns=list(CALL_CENTER_PROVIDER_COLUMNS.values()))
        )
        im = ax.imshow(pivot.to_numpy(), cmap="RdYlGn_r", vmin=0, vmax=0.50)
        ax.set_title(basis)
        ax.set_xticks(np.arange(len(pivot.columns)), labels=pivot.columns)
        ax.set_yticks(np.arange(len(pivot.index)), labels=pivot.index)
        ax.tick_params(axis="x", rotation=30)
        for i in range(pivot.shape[0]):
            for j in range(pivot.shape[1]):
                value = pivot.iloc[i, j]
                ax.text(j, i, f"{value * 100:.1f}%", ha="center", va="center", fontsize=8)
    fig.suptitle("Call-center CER heatmap by scenario")
    fig.colorbar(im, ax=axes.ravel().tolist(), fraction=0.035, pad=0.02)
    save_chart(fig, "call_center_scenario_heatmap.png", bbox_inches="tight")
    plt.close(fig)


def plot_quality_gate_policy(policy: pd.DataFrame) -> None:
    balanced = policy[policy["policy"] == "balanced"].copy()
    balanced = balanced.set_index("model").loc[
        ["Whisper large", "Whisper medium", "AWS Transcribe", "Whisper base"]
    ].reset_index()
    fig, ax = plt.subplots(figsize=(8.8, 4.8))
    bottom = np.zeros(len(balanced))
    colors = {"pass_rate": "#2E7D32", "review_rate": "#F9A825", "block_rate": "#C62828"}
    labels = {"pass_rate": "pass", "review_rate": "review", "block_rate": "block"}
    for col in ["pass_rate", "review_rate", "block_rate"]:
        ax.bar(balanced["model"], balanced[col], bottom=bottom, color=colors[col], label=labels[col])
        bottom += balanced[col].to_numpy()
    ax.set_title("Balanced ASR quality gate: pass <=5%, review <=15%, block >15% CER")
    ax.set_ylabel("Share of utterances")
    percent_axis(ax)
    ax.grid(axis="y", alpha=0.2)
    ax.set_axisbelow(True)
    ax.legend(frameon=False, ncols=3, loc="upper center", bbox_to_anchor=(0.5, -0.12))
    fig.tight_layout()
    save_chart(fig, "quality_gate_balanced.png")
    plt.close(fig)


def write_markdown_summary(
    single_summary: pd.DataFrame,
    call_summary: pd.DataFrame,
    policy: pd.DataFrame,
    wins: pd.DataFrame,
) -> None:
    def pct(x: float) -> str:
        return f"{x * 100:.2f}%"

    lines = [
        "# ASR Benchmark Summary",
        "",
        "Generated from repository data by `analysis/analyze_asr_benchmarks.py`.",
        "",
        "## Single-speaker 3,922 utterances",
        "",
        "| Model | Mean CER | Median CER | Perfect | <=5% CER | >10% CER |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for _, row in single_summary.sort_values("mean_cer").iterrows():
        lines.append(
            f"| {row['model']} | {pct(row['mean_cer'])} | {pct(row['median_cer'])} | {pct(row['perfect_rate'])} | {pct(row['pass_5pct_rate'])} | {pct(row['over_10pct_rate'])} |"
        )

    lines.extend(
        [
            "",
            "## Single-speaker best/worst counts",
            "",
            "| Model | Sole-best count | Best-or-tied count | Sole-worst count |",
            "|---|---:|---:|---:|",
        ]
    )
    for _, row in wins.iterrows():
        lines.append(
            f"| {row['model']} | {row['sole_best_count']} | {row['best_or_tied_count']} | {row['sole_worst_count']} |"
        )

    lines.extend(
        [
            "",
            "## Financial call-center samples",
            "",
            "| Basis | Provider | Mean CER | Median CER | Max CER |",
            "|---|---|---:|---:|---:|",
        ]
    )
    for _, row in call_summary.iterrows():
        lines.append(
            f"| {row['basis']} | {row['provider']} | {pct(row['mean_cer'])} | {pct(row['median_cer'])} | {pct(row['max_cer'])} |"
        )

    lines.extend(
        [
            "",
            "## Balanced quality gate policy",
            "",
            "Pass: CER <= 5%, review: 5% < CER <= 15%, block: CER > 15%.",
            "",
            "| Model | Pass | Review | Block |",
            "|---|---:|---:|---:|",
        ]
    )
    for _, row in policy[policy["policy"] == "balanced"].sort_values("pass_rate", ascending=False).iterrows():
        lines.append(
            f"| {row['model']} | {pct(row['pass_rate'])} | {pct(row['review_rate'])} | {pct(row['block_rate'])} |"
        )

    (OUTPUT_DIR / "model_performance_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def dataframe_records(df: pd.DataFrame) -> list[dict]:
    return json.loads(df.to_json(orient="records", force_ascii=False))


def write_interactive_data(
    single_summary: pd.DataFrame,
    thresholds: pd.DataFrame,
    policy: pd.DataFrame,
    wins: pd.DataFrame,
    length_summary: pd.DataFrame,
    deltas: pd.DataFrame,
    call_long: pd.DataFrame,
    call_summary: pd.DataFrame,
) -> list[Path]:
    payload = {
        "metadata": {
            "project": "job-transcribe",
            "analysis_script": "analysis/analyze_asr_benchmarks.py",
            "rng_seed": RNG_SEED,
            "disclaimer": (
                "2023 public product/open model experiment; not current vendor performance, "
                "not an official benchmark, and not internal performance data."
            ),
            "source_files": {
                "single_speaker": [
                    "result/result_3922.csv",
                    "result/openai_whisper_base_result_3922.csv",
                    "result/openai_whisper_medium_result_3922.csv",
                    "result/openai_whisper_large_result_3922.csv",
                ],
                "call_center": [
                    "result/cs_hangul_result.csv",
                    "result/cs_number_result.csv",
                ],
            },
        },
        "single_speaker": {
            "summary": dataframe_records(single_summary),
            "thresholds": dataframe_records(thresholds),
            "quality_gate_policies": dataframe_records(policy),
            "win_counts": dataframe_records(wins),
            "length_bins": dataframe_records(length_summary),
            "paired_deltas": dataframe_records(deltas),
        },
        "call_center": {
            "observations": dataframe_records(call_long),
            "provider_summary": dataframe_records(call_summary),
        },
    }
    paths = [
        INTERACTIVE_DATA_DIR / "asr-benchmark.json",
        DOCS_DATA_DIR / "asr-benchmark.json",
    ]
    serialized = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    for path in paths:
        path.write_text(serialized, encoding="utf-8")
    return paths


def main() -> None:
    ensure_dirs()
    configure_matplotlib()

    single_long = load_single_speaker_long()
    single_wide = build_single_wide(single_long)
    single_summary = summarize_single_speaker(single_long)
    thresholds = threshold_pass_rates(single_long)
    deltas = paired_deltas(single_wide)
    length_summary = length_bin_summary(single_long)
    worst = worst_examples(single_long)
    disagreement = disagreement_examples(single_long, single_wide)
    policy = quality_gate_policy_simulation(single_long)
    wins = model_win_counts(single_wide)

    call_long = load_call_center_long()
    call_summary = summarize_call_center(call_long)

    single_long.to_csv(OUTPUT_DIR / "single_speaker_long.csv", index=False)
    single_summary.to_csv(OUTPUT_DIR / "single_speaker_model_summary.csv", index=False)
    thresholds.to_csv(OUTPUT_DIR / "single_speaker_threshold_pass_rates.csv", index=False)
    deltas.to_csv(OUTPUT_DIR / "single_speaker_paired_deltas.csv", index=False)
    length_summary.to_csv(OUTPUT_DIR / "single_speaker_length_bins.csv", index=False)
    worst.to_csv(OUTPUT_DIR / "single_speaker_worst_examples.csv", index=False)
    disagreement.to_csv(OUTPUT_DIR / "single_speaker_disagreement_examples.csv", index=False)
    policy.to_csv(OUTPUT_DIR / "quality_gate_policy_simulation.csv", index=False)
    wins.to_csv(OUTPUT_DIR / "single_speaker_model_win_counts.csv", index=False)
    call_long.to_csv(OUTPUT_DIR / "call_center_long.csv", index=False)
    call_summary.to_csv(OUTPUT_DIR / "call_center_provider_summary.csv", index=False)

    plot_single_mean(single_summary)
    plot_thresholds(thresholds)
    plot_distribution(single_long)
    plot_length_bins(length_summary)
    plot_call_center(call_long)
    plot_call_center_heatmap(call_long)
    plot_quality_gate_policy(policy)

    write_markdown_summary(single_summary, call_summary, policy, wins)
    interactive_data_paths = write_interactive_data(
        single_summary,
        thresholds,
        policy,
        wins,
        length_summary,
        deltas,
        call_long,
        call_summary,
    )

    metadata = {
        "single_speaker_rows": int(single_wide.shape[0]),
        "single_speaker_models": [spec["label"] for spec in SINGLE_SPEAKER_MODELS.values()],
        "call_center_rows": int(call_long.shape[0]),
        "call_center_providers": list(CALL_CENTER_PROVIDER_COLUMNS.values()),
        "outputs": sorted(str(path.relative_to(ROOT)) for path in OUTPUT_DIR.glob("*")),
        "assets": sorted(str(path.relative_to(ROOT)) for path in ASSET_DIR.glob("*.png")),
        "docs_assets": sorted(str(path.relative_to(ROOT)) for path in DOCS_ASSET_DIR.glob("*.png")),
        "interactive_data": [str(path.relative_to(ROOT)) for path in interactive_data_paths],
    }
    (OUTPUT_DIR / "run_metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(metadata, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
