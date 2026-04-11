"""
GAMMA Three-Way Comparison Visualizer
---------------------------------------
Compares three configurations against each other:
  1. A default/baseline run
  2. The best result from a slevel sweep (lowest runtime)
  3. The best result from a PE sweep (lowest runtime)

Automatically finds the best from each sweep folder by scanning CSVs
and picking the one with the lowest runtime.

Usage:
    python plot_three_way_comparison.py \
        --default_csv   ./gamma_results/default_result_c.csv \
        --sl_dir        ./gamma_results_sweep_slevel \
        --pe_dir        ./gamma_results_sweep_pe

    python plot_three_way_comparison.py \
        --default_csv   ./gamma_results/default_result_c.csv \
        --sl_dir        ./gamma_results_sweep_slevel \
        --pe_dir        ./gamma_results_sweep_pe \
        --outdir        ./plots
"""

import os
import re
import argparse
import glob
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib.patches as mpatches
import numpy as np

# ── CLI Arguments ─────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="GAMMA three-way comparison plot")
parser.add_argument("--default_csv", type=str, required=True,
                    help="Path to the default/baseline result CSV")
parser.add_argument("--sl_dir", type=str, required=True,
                    help="Folder containing slevel sweep CSVs")
parser.add_argument("--pe_dir", type=str, required=True,
                    help="Folder containing PE sweep CSVs")
parser.add_argument("--outdir", type=str, default=None,
                    help="Where to save the plot (default: current directory)")
args = parser.parse_args()

outdir = args.outdir if args.outdir else "."
os.makedirs(outdir, exist_ok=True)

# ── Helper: load all CSVs from a folder into a DataFrame ─────────────────────
def load_folder(folder, id_pattern, id_label):
    """Load all CSVs in folder, extract an ID field via regex, return DataFrame."""
    csv_files = glob.glob(os.path.join(folder, "*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in: {folder}")
    records = []
    for filepath in csv_files:
        filename = os.path.basename(filepath)
        match = re.search(id_pattern, filename)
        if not match:
            print(f"  Skipping {filename} (pattern not found)")
            continue
        df = pd.read_csv(filepath)
        if df.empty:
            continue
        row = df.iloc[0]
        record = {
            id_label:   match.group(1) if id_label != "sl" else f"{match.group(1)}-{match.group(2)}",
            "runtime":  float(row["runtime"]),
            "area":     float(row["area"]),
            "pe_ratio": float(row["pe_area_ratio"]) * 100,
            "L1":       float(row["L1_size"]),
            "L2":       float(row["L2_size"]),
            "reward":   float(row["reward"]) if "reward" in row else None,
        }
        records.append(record)
    if not records:
        raise ValueError(f"No valid CSVs parsed from: {folder}")
    return pd.DataFrame(records)

# ── Load default ──────────────────────────────────────────────────────────────
print("\nLoading default CSV...")
df_default = pd.read_csv(args.default_csv)
row = df_default.iloc[0]

# Extract label info from filename
fname = os.path.basename(args.default_csv)
sl_match = re.search(r'SL-(\d+-\d+)', fname)
ep_match = re.search(r'GEN-(\d+)', fname)
pe_match = re.search(r'FixedPE-(\d+)', fname)
sl_str = sl_match.group(1) if sl_match else "?"
ep_str = ep_match.group(1) if ep_match else "?"
pe_str = pe_match.group(1) if pe_match else "?"

default = {
    "label":    f"Default\n(SL {sl_str}, {ep_str} ep, {pe_str} PE)",
    "runtime":  float(row["runtime"]),
    "area":     float(row["area"]),
    "pe_ratio": float(row["pe_area_ratio"]) * 100,
    "L1":       float(row["L1_size"]),
    "L2":       float(row["L2_size"]),
    "color":    "#ff6b6b",
}
print(f"  Default: runtime={default['runtime']:,.0f}, area={default['area']:,.0f}")

# ── Load SL sweep — pick best runtime ─────────────────────────────────────────
print("\nLoading SL sweep...")
df_sl = load_folder(args.sl_dir, r'SL-(\d+)-(\d+)', "sl")
best_sl_row = df_sl.loc[df_sl["runtime"].idxmin()]
best_sl = {
    "label":    f"Best SL\n(SL {best_sl_row['sl']}, {ep_str} ep, {pe_str} PE)",
    "runtime":  best_sl_row["runtime"],
    "area":     best_sl_row["area"],
    "pe_ratio": best_sl_row["pe_ratio"],
    "L1":       best_sl_row["L1"],
    "L2":       best_sl_row["L2"],
    "color":    "#00f5c4",
}
print(f"  Best SL: SL={best_sl_row['sl']}, runtime={best_sl['runtime']:,.0f}, area={best_sl['area']:,.0f}")

# ── Load PE sweep — pick best runtime ─────────────────────────────────────────
print("\nLoading PE sweep...")
df_pe = load_folder(args.pe_dir, r'FixedPE-(\d+)', "pe")
best_pe_row = df_pe.loc[df_pe["runtime"].idxmin()]

# Extract epoch/sl from pe sweep filenames for label
pe_csv_files = glob.glob(os.path.join(args.pe_dir, "*.csv"))
pe_ep, pe_sl = ep_str, sl_str
if pe_csv_files:
    pf = os.path.basename(pe_csv_files[0])
    m1 = re.search(r'GEN-(\d+)', pf)
    m2 = re.search(r'SL-(\d+-\d+)', pf)
    if m1: pe_ep = m1.group(1)
    if m2: pe_sl = m2.group(1)

best_pe = {
    "label":    f"Best PE\n(SL {pe_sl}, {pe_ep} ep, {int(best_pe_row['pe'])} PE)",
    "runtime":  best_pe_row["runtime"],
    "area":     best_pe_row["area"],
    "pe_ratio": best_pe_row["pe_ratio"],
    "L1":       best_pe_row["L1"],
    "L2":       best_pe_row["L2"],
    "color":    "#6bcbff",
}
print(f"  Best PE: PE={int(best_pe_row['pe'])}, runtime={best_pe['runtime']:,.0f}, area={best_pe['area']:,.0f}")

configs = [default, best_sl, best_pe]

# ── Plot Style ────────────────────────────────────────────────────────────────
BG    = "#0f1923"
PANEL = "#131f2e"
MUTED = "#64748b"

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

# ── Figure ────────────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(18, 13), facecolor=BG)
fig.suptitle("Default vs Best SL vs Best PE  —  VGG16 Layer 1",
             fontsize=15, fontweight="bold", color="#e0e8f0", y=0.98)

# Summary cards
card_ax = fig.add_axes([0.03, 0.84, 0.94, 0.10])
card_ax.set_facecolor(BG)
card_ax.axis("off")

comparisons = [
    ("Best SL vs Default",  configs[1], configs[0]),
    ("Best PE vs Default",  configs[2], configs[0]),
    ("Best PE vs Best SL",  configs[2], configs[1]),
]

for i, (title, a, b) in enumerate(comparisons):
    x0 = 0.02 + i * 0.325
    rect = mpatches.FancyBboxPatch((x0, 0.05), 0.30, 0.88,
        boxstyle="round,pad=0.02", linewidth=1,
        edgecolor="#2a3a4a", facecolor="#131f2e",
        transform=card_ax.transAxes)
    card_ax.add_patch(rect)
    speedup = b["runtime"] / a["runtime"]
    area_change = (a["area"] - b["area"]) / b["area"] * 100
    card_ax.text(x0 + 0.15, 0.80, title,
                 ha="center", va="center", fontsize=8.5, color="#8899aa",
                 transform=card_ax.transAxes)
    card_ax.text(x0 + 0.15, 0.45,
                 f"{speedup:,.1f}× faster runtime",
                 ha="center", va="center", fontsize=12, fontweight="bold",
                 color=a["color"], transform=card_ax.transAxes)
    sign = "+" if area_change > 0 else ""
    card_ax.text(x0 + 0.15, 0.18,
                 f"{sign}{area_change:.0f}% area change",
                 ha="center", va="center", fontsize=8.5,
                 color="#ff6b6b" if area_change > 0 else "#00f5c4",
                 transform=card_ax.transAxes)

# Bar charts
x_pos   = np.arange(len(configs))
xlabels = [c["label"] for c in configs]
colors  = [c["color"] for c in configs]
BW      = 0.45

def bar_chart(ax, key, title, ylabel, higher_better=False):
    vals = [c[key] for c in configs]
    bars = ax.bar(x_pos, vals, width=BW, color=colors,
                  edgecolor=BG, linewidth=1.0, zorder=3)
    ax.xaxis.grid(False)
    ax.set_title(title, color="#e0e8f0", fontsize=10, fontweight="bold", pad=8)
    ax.set_ylabel(ylabel, fontsize=8)
    ax.set_xticks(x_pos)
    ax.set_xticklabels(xlabels, fontsize=7.5)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
    best_idx = vals.index(min(vals)) if not higher_better else vals.index(max(vals))
    rng = max(vals) - min(vals) if max(vals) != min(vals) else max(vals)
    for i, (bar, val) in enumerate(zip(bars, vals)):
        is_best = (i == best_idx)
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + rng * (0.08 if is_best else 0.01),
                f"{val:,.0f}", ha="center", va="bottom",
                fontsize=7, color=colors[i] if is_best else "#8899aa")

    for spine in ax.spines.values():
        spine.set_edgecolor("#2a3a4a")

axes = [fig.add_subplot(2, 3, i + 1) for i in range(5)]
fig.add_subplot(2, 3, 6).set_visible(False)

bar_chart(axes[0], "runtime",  "Runtime (cycles)",     "Cycles",   higher_better=False)
bar_chart(axes[1], "area",     "Total Area (µm²)",     "µm²",      higher_better=False)
bar_chart(axes[2], "pe_ratio", "PE Area Ratio (%)",    "%",        higher_better=True)
bar_chart(axes[3], "L1",       "L1 Buffer (elements)", "Elements", higher_better=False)
bar_chart(axes[4], "L2",       "L2 Buffer (elements)", "Elements", higher_better=False)

axes[2].set_ylim(0, 110)

plt.subplots_adjust(top=0.81, bottom=0.08, hspace=0.55, wspace=0.38,
                    left=0.06, right=0.97)

# ── Save ──────────────────────────────────────────────────────────────────────
out_path = os.path.join(outdir, "three_way_comparison.png")
plt.savefig(out_path, dpi=150, bbox_inches="tight", facecolor=BG)
print(f"\nSaved plot to: {out_path}")
