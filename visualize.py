"""
GAMMA Results Plotter
---------------------
Reads all result CSVs from a folder, extracts the epoch count from the
filename, and generates four line charts:
  1. Runtime (cycles)
  2. Total Area (um^2)
  3. PE Area Ratio (%)
  4. L1 and L2 Buffer Sizes (elements)

Usage:
    python plot_gamma_results.py --results_dir ./gamma_results
    python plot_gamma_results.py --results_dir ./gamma_results --outdir ./plots
"""

import os
import re
import argparse
import glob
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# ── CLI Arguments ────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Plot GAMMA optimization results")
parser.add_argument("--results_dir", type=str, default="./gamma_results",
                    help="Folder containing result CSV files")
parser.add_argument("--outdir", type=str, default=None,
                    help="Where to save plots (default: same as results_dir)")
args = parser.parse_args()

results_dir = args.results_dir
outdir = args.outdir if args.outdir else results_dir
os.makedirs(outdir, exist_ok=True)

# ── Load CSVs ────────────────────────────────────────────────────────────────
csv_files = glob.glob(os.path.join(results_dir, "*.csv"))
if not csv_files:
    raise FileNotFoundError(f"No CSV files found in: {results_dir}")

records = []
for filepath in csv_files:
    filename = os.path.basename(filepath)

    # Extract epoch count from filename — looks for GEN-<number>
    match = re.search(r'GEN-(\d+)', filename)
    if not match:
        print(f"  Skipping {filename} (no GEN-<n> found in name)")
        continue

    epoch = int(match.group(1))
    df = pd.read_csv(filepath)

    if df.empty:
        print(f"  Skipping {filename} (empty)")
        continue

    row = df.iloc[0]
    records.append({
        "epoch":    epoch,
        "runtime":  float(row["runtime"]),
        "area":     float(row["area"]),
        "pe_ratio": float(row["pe_area_ratio"]) * 100,  # convert to %
        "L1_size":  float(row["L1_size"]),
        "L2_size":  float(row["L2_size"]),
    })

if not records:
    raise ValueError("No valid CSV files could be parsed.")

# Sort by epoch
data = pd.DataFrame(records).sort_values("epoch").reset_index(drop=True)
print(f"\nLoaded {len(data)} runs:\n{data[['epoch','runtime','area','pe_ratio','L1_size','L2_size']].to_string(index=False)}\n")

# ── Plot Style ───────────────────────────────────────────────────────────────
plt.rcParams.update({
    "figure.facecolor":  "#0f1923",
    "axes.facecolor":    "#0f1923",
    "axes.edgecolor":    "#2a3a4a",
    "axes.labelcolor":   "#8899aa",
    "axes.grid":         True,
    "grid.color":        "#1e2d3d",
    "grid.linestyle":    "--",
    "grid.linewidth":    0.7,
    "xtick.color":       "#8899aa",
    "ytick.color":       "#8899aa",
    "text.color":        "#e0e8f0",
    "font.family":       "monospace",
    "legend.facecolor":  "#0f1923",
    "legend.edgecolor":  "#2a3a4a",
})

COLORS = {
    "runtime":  "#00f5c4",
    "area":     "#ff6b6b",
    "pe_ratio": "#ffd93d",
    "L1":       "#6bcbff",
    "L2":       "#a78bfa",
}

def styled_plot(ax, x, y, color, ylabel, title):
    ax.plot(x, y, color=color, linewidth=2, marker="o", markersize=5,
            markerfacecolor=color, markeredgewidth=0)
    ax.fill_between(x, y, alpha=0.08, color=color)
    ax.set_title(title, color="#e0e8f0", fontsize=11, pad=10, fontweight="bold")
    ax.set_xlabel("Epochs", fontsize=9)
    ax.set_ylabel(ylabel, fontsize=9)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(
        lambda v, _: f"{v:,.0f}" if v >= 1000 else f"{v:.2f}".rstrip('0').rstrip('.')
    ))
    for spine in ax.spines.values():
        spine.set_edgecolor("#2a3a4a")

# ── Figure ───────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(14, 9))
fig.suptitle("GAMMA Optimization Results", fontsize=15, fontweight="bold",
             color="#e0e8f0", y=0.98)
fig.patch.set_facecolor("#0f1923")
plt.subplots_adjust(hspace=0.4, wspace=0.35)

x = data["epoch"]

# Chart 1 — Runtime
styled_plot(axes[0, 0], x, data["runtime"], COLORS["runtime"],
            "Cycles", "Runtime (cycles)")

# Chart 2 — Area
styled_plot(axes[0, 1], x, data["area"], COLORS["area"],
            "µm²", "Total Area (µm²)")

# Chart 3 — PE Area Ratio
styled_plot(axes[1, 0], x, data["pe_ratio"], COLORS["pe_ratio"],
            "%", "PE Area Ratio (%)")
axes[1, 0].set_ylim(0, 100)

# Chart 4 — Buffer sizes (two lines)
ax4 = axes[1, 1]
ax4.plot(x, data["L1_size"], color=COLORS["L1"], linewidth=2, marker="o",
         markersize=5, markeredgewidth=0, label="L1 (local)")
ax4.plot(x, data["L2_size"], color=COLORS["L2"], linewidth=2, marker="o",
         markersize=5, markeredgewidth=0, linestyle="--", label="L2 (global)")
ax4.fill_between(x, data["L1_size"], alpha=0.08, color=COLORS["L1"])
ax4.fill_between(x, data["L2_size"], alpha=0.08, color=COLORS["L2"])
ax4.set_title("Buffer Sizes (elements)", color="#e0e8f0", fontsize=11,
              pad=10, fontweight="bold")
ax4.set_xlabel("Epochs", fontsize=9)
ax4.set_ylabel("Elements", fontsize=9)
ax4.legend(fontsize=8)
ax4.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
for spine in ax4.spines.values():
    spine.set_edgecolor("#2a3a4a")

# ── Save ─────────────────────────────────────────────────────────────────────
out_path = os.path.join(outdir, "gamma_results.png")
plt.savefig(out_path, dpi=150, bbox_inches="tight", facecolor="#0f1923")
print(f"Saved plot to: {out_path}")
plt.show()