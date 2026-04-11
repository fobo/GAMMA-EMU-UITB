"""
GAMMA PE Sweep Visualizer
--------------------------
Reads all result CSVs from a folder, extracts the PE count from the
filename, and generates bar charts comparing each metric across
different PE configurations.

Usage:
    python plot_pe_sweep.py --results_dir ./gamma_results_sweep_pe
    python plot_pe_sweep.py --results_dir ./gamma_results_sweep_pe --outdir ./plots
"""

import os
import re
import argparse
import glob
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

# ── CLI Arguments ─────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Plot GAMMA PE sweep results")
parser.add_argument("--results_dir", type=str, default=".",
                    help="Folder containing result CSV files")
parser.add_argument("--outdir", type=str, default=None,
                    help="Where to save the plot (default: same as results_dir)")
args = parser.parse_args()

results_dir = args.results_dir
outdir = args.outdir if args.outdir else results_dir
os.makedirs(outdir, exist_ok=True)

# ── Load CSVs ─────────────────────────────────────────────────────────────────
import pandas as pd

csv_files = glob.glob(os.path.join(results_dir, "*.csv"))
if not csv_files:
    raise FileNotFoundError(f"No CSV files found in: {results_dir}")

records = []
for filepath in csv_files:
    filename = os.path.basename(filepath)

    # Extract FixedPE-<n> from filename
    match = re.search(r'FixedPE-(\d+)', filename)
    if not match:
        print(f"  Skipping {filename} (no FixedPE-<n> found)")
        continue

    pe = int(match.group(1))
    df = pd.read_csv(filepath)
    if df.empty:
        print(f"  Skipping {filename} (empty)")
        continue

    row = df.iloc[0]
    records.append({
        "pe":       pe,
        "runtime":  float(row["runtime"]),
        "area":     float(row["area"]),
        "pe_ratio": float(row["pe_area_ratio"]) * 100,
        "L1_size":  float(row["L1_size"]),
        "L2_size":  float(row["L2_size"]),
        "reward":   float(row["reward"]) if "reward" in row.index else None,
    })

if not records:
    raise ValueError("No valid CSV files could be parsed.")

data = pd.DataFrame(records).sort_values("pe").reset_index(drop=True)
print(f"\nLoaded {len(data)} runs:")
print(data[["pe", "reward", "runtime", "area", "pe_ratio", "L1_size", "L2_size"]].to_string(index=False))
print()

# ── Plot Style ────────────────────────────────────────────────────────────────
BG      = "#0f1923"
PANEL   = "#131f2e"
ACCENT  = "#00f5c4"
MUTED   = "#64748b"
PALETTE = ["#6bcbff", "#00f5c4", "#ffd93d", "#ff9f43", "#ff6b6b", "#a78bfa",
           "#e0e8f0", "#84cc16", "#f97316"]

plt.rcParams.update({
    "figure.facecolor": BG,
    "axes.facecolor":   PANEL,
    "axes.edgecolor":   "#2a3a4a",
    "axes.labelcolor":  "#8899aa",
    "axes.grid":        True,
    "grid.color":       "#1e2d3d",
    "grid.linestyle":   "--",
    "grid.linewidth":   0.7,
    "xtick.color":      "#e0e8f0",
    "ytick.color":      "#8899aa",
    "text.color":       "#e0e8f0",
    "font.family":      "monospace",
})

x       = np.arange(len(data))
xlabels = [str(p) for p in data["pe"].tolist()]
colors  = [PALETTE[i % len(PALETTE)] for i in range(len(data))]
BW      = 0.55

# ── Bar chart helper ──────────────────────────────────────────────────────────
def bar_chart(ax, values, title, ylabel, higher_better=False):
    bars = ax.bar(x, values, width=BW, color=colors,
                  edgecolor=BG, linewidth=1.0, zorder=3)
    ax.xaxis.grid(False)
    ax.set_title(title, color="#e0e8f0", fontsize=10, fontweight="bold", pad=8)
    ax.set_ylabel(ylabel, fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels(xlabels, fontsize=9)
    ax.set_xlabel("Number of PEs", fontsize=8)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))

    best_idx = values.index(min(values)) if not higher_better else values.index(max(values))
    for i, (bar, val) in enumerate(zip(bars, values)):
        is_best = (i == best_idx)
        label_y = bar.get_height() * (1.09 if is_best else 1.01)
        ax.text(bar.get_x() + bar.get_width() / 2, label_y,
                f"{val:,.0f}", ha="center", va="bottom",
                fontsize=7, color=ACCENT if is_best else "#8899aa")



    for spine in ax.spines.values():
        spine.set_edgecolor("#2a3a4a")

# ── Figure ────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(17, 12), facecolor=BG)
fig.suptitle("PE Count Sweep  —  VGG16 Layer 1",
             fontsize=15, fontweight="bold", color="#e0e8f0", y=0.98)

axes = [fig.add_subplot(2, 3, i + 1) for i in range(6)]

bar_chart(axes[0], data["runtime"].tolist(),  "Runtime (cycles)",     "Cycles",   higher_better=False)
bar_chart(axes[1], data["area"].tolist(),     "Total Area (µm²)",     "µm²",      higher_better=False)
bar_chart(axes[2], data["pe_ratio"].tolist(), "PE Area Ratio (%)",    "%",        higher_better=True)
bar_chart(axes[3], data["L1_size"].tolist(),  "L1 Buffer (elements)", "Elements", higher_better=False)
bar_chart(axes[4], data["L2_size"].tolist(),  "L2 Buffer (elements)", "Elements", higher_better=False)
reward_vals = data["reward"].tolist() if "reward" in data.columns and data["reward"].notna().all() else None
if reward_vals:
    bar_chart(axes[5], reward_vals, "Reward (higher = better)", "Value", higher_better=True)

axes[2].set_ylim(0, 110)

plt.subplots_adjust(top=0.92, bottom=0.08, hspace=0.55, wspace=0.38,
                    left=0.06, right=0.97)

# ── Save ──────────────────────────────────────────────────────────────────────
out_path = os.path.join(outdir, "pe_sweep_results.png")
plt.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=BG)
print(f"Saved plot to: {out_path}")
