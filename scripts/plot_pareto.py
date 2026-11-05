"""Accuracy against query budget, one panel per noise level, from eval_baselines.py output.

    python scripts/plot_pareto.py --eval out/eval/test.json --out docs/baseline_pareto.png
"""
import argparse
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

SERIES = (("plandiscrim_geometry", "PlanDiscrim, geometry only", "#2a78d6", "-", 2.6),
          ("scene_only_learned", "Scene-only learned", "#eb6834", "--", 2.0),
          ("uncertainty_margin", "Ranker margin", "#1baf7a", "-.", 2.0),
          ("random", "Random tool", "#eda100", ":", 2.0),
          ("oracle", "Oracle selector", "#e87ba4", (0, (1, 1, 4, 1)), 2.0))
INK, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--eval", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--metric", default="correct")
    args = p.parse_args()
    with open(args.eval) as f:
        report = json.load(f)[args.metric]
    fig, axes = plt.subplots(1, 3, figsize=(11, 4.2), sharey=True, facecolor=SURFACE)
    for ax, level in zip(axes, ("low", "mid", "high")):
        r = report[level]
        for key, label, color, style, width in SERIES:
            ax.plot(r["budgets"], [pt[0] for pt in r["curves"][key]], color=color, linestyle=style, linewidth=width, label=label)
        ax.axhline(r["always_on"]["acc"], color=MUTED, linewidth=1.2)
        ax.text(0.98, r["always_on"]["acc"] + 0.008, f"Always-on, 3 calls: {r['always_on']['acc']:.2f}", color=MUTED, fontsize=9, ha="right")
        ax.set_title(f"{level.capitalize()} tool noise", color=INK, fontsize=11, loc="left")
        ax.set_xlabel("Tool calls per decision", color=MUTED)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 0.8)
        ax.set_facecolor(SURFACE)
        ax.grid(axis="y", color=GRID, linewidth=0.8)
        ax.tick_params(colors=MUTED, length=0)
        for side in ("top", "right", "left"):
            ax.spines[side].set_visible(False)
        ax.spines["bottom"].set_color(GRID)
    axes[0].set_ylabel("Top-1 accuracy", color=MUTED)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=5, frameon=False, fontsize=9.5, labelcolor=INK, handlelength=3.2)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    fig.savefig(args.out, dpi=150, facecolor=SURFACE)


if __name__ == "__main__":
    main()
