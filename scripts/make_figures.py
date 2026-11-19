"""Paper figures as vector PDFs, from eval_baselines.py (and ablations.py) output.

    python scripts/make_figures.py --eval out/eval/test.json --out paper/figures
    python scripts/make_figures.py --eval out/eval/val_vlm.json --ablations out/eval/ablations/val.json --out paper/figures

Writes pareto_acc.pdf, pareto_unsafe.pdf, families.pdf and, with --ablations, ablations.pdf. Every mark is
vector and fonts are embedded as TrueType (pdf.fonttype 42), as the final report requires. Each method
keeps one colour and one line style in every figure; line styles keep the curves apart in grayscale print.
The x axis is total calls per decision: tool calls plus, for VLM selectors, one VLM call per decision.
"""
import argparse
import json
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

plt.rcParams.update({"pdf.fonttype": 42, "ps.fonttype": 42, "font.size": 8, "axes.titlesize": 8.5, "legend.fontsize": 7.5,
                     "font.family": "DejaVu Sans", "axes.linewidth": 0.6})

INK, MUTED, GRID, SURFACE, NEUTRAL = "#0b0b0b", "#52514e", "#e6e5e0", "#ffffff", "#8a8984"
COLUMN, PAGE = 3.5, 7.16          # IEEE single- and double-column widths, inches

# Fixed method -> (label, colour, line style). Colours are the validated categorical slots, in order;
# a method keeps its slot whether or not the others are plotted.
METHODS = {
    "plandiscrim_geometry": ("PlanDiscrim (geometry)", "#2a78d6", "-"),
    "scene_only_learned": ("Scene-only learned", "#eb6834", "--"),
    "uncertainty_margin": ("Ranker margin", "#1baf7a", "-."),
    "random": ("Random tool", "#eda100", ":"),
    "oracle": ("Oracle selector", "#e87ba4", (0, (1, 1, 4, 1))),
    "plandiscrim_geom_vlm": ("PlanDiscrim (geometry + VLM)", "#008300", (0, (5, 1.5))),
    "plandiscrim_vlm_only": ("PlanDiscrim (VLM only)", "#6250d6", (0, (3, 1, 1, 1, 1, 1))),
    "vlm_prompted": ("VLM prompted choice", "#e34948", (0, (2, 2))),
}
LEVELS = ("low", "mid", "high")


def style(ax):
    ax.set_facecolor(SURFACE)
    ax.grid(axis="y", color=GRID, linewidth=0.6)
    ax.set_axisbelow(True)
    ax.tick_params(colors=MUTED, length=2, width=0.6)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(MUTED)


def pareto(report, which, path):
    """which=0: top-1 accuracy, which=1: unsafe-pick rate."""
    fig, axes = plt.subplots(1, 3, figsize=(PAGE, 2.5), sharey=True, facecolor=SURFACE)
    for ax, level in zip(axes, LEVELS):
        r = report[level]
        offset = r.get("cost_offset", {})
        for key, (label, color, ls) in METHODS.items():
            if key not in r["curves"]:
                continue
            x = [b + offset.get(key, 0.0) for b in r["budgets"]]
            ax.plot(x, [pt[which] for pt in r["curves"][key]], color=color, linestyle=ls, linewidth=1.4, label=label)
        none_y = r["no_tool"]["acc" if which == 0 else "unsafe"]
        always_y = r["always_on"]["acc" if which == 0 else "unsafe"]
        ax.plot([0], [none_y], "o", color=NEUTRAL, markersize=4.5, markeredgecolor=SURFACE, markeredgewidth=0.8, label="No tool", zorder=5)
        ax.plot([r["always_on"]["cost"]], [always_y], "s", color=INK, markersize=4.5, markeredgecolor=SURFACE, markeredgewidth=0.8,
                label="Always-on (all 3 tools)", zorder=5)
        ax.annotate(f"{always_y:.2f}", (r["always_on"]["cost"], always_y), textcoords="offset points", xytext=(-4, 5), ha="right", color=MUTED, fontsize=7)
        ax.set_title(f"{level.capitalize()} tool noise", color=INK, loc="left")
        ax.set_xlabel("Calls per decision", color=MUTED)
        ax.set_xlim(-0.05, r["always_on"]["cost"] + 0.15)
        style(ax)
    axes[0].set_ylabel("Top-1 accuracy" if which == 0 else "Unsafe top-1 rate", color=MUTED)
    axes[0].set_ylim(0, None)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=min(len(labels), 5), frameon=False, labelcolor=INK, handlelength=3.0)
    rows = (len(labels) + 4) // 5
    fig.tight_layout(rect=(0, 0.07 * rows + 0.02, 1, 1))
    fig.savefig(path, facecolor=SURFACE, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


def families(report, path, level="mid"):
    fams = report[level]["families"]
    names = sorted(fams)
    bars = (("no_tool", "No tool", NEUTRAL), ("uncertainty_b50", "Ranker margin", METHODS["uncertainty_margin"][1]),
            ("plandiscrim_b50", "PlanDiscrim (geometry)", METHODS["plandiscrim_geometry"][1]), ("oracle", "Oracle selector", METHODS["oracle"][1]))
    fig, ax = plt.subplots(figsize=(COLUMN, 2.6), facecolor=SURFACE)
    h = 0.8 / len(bars)
    for j, (key, label, color) in enumerate(bars):
        y = [i + (j - (len(bars) - 1) / 2) * h for i in range(len(names))]
        ax.barh(y, [fams[n][key] for n in names], height=h, color=color, edgecolor=SURFACE, linewidth=0.8, label=label)
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels([n.replace("_", " ") for n in names], color=INK)
    ax.invert_yaxis()
    ax.set_xlabel(f"Top-1 accuracy, 0.5 calls/decision, {level} noise", color=MUTED)
    ax.set_xlim(0, 1)
    style(ax)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    ax.legend(loc="lower left", bbox_to_anchor=(-0.02, 1.0), ncol=2, frameon=False, labelcolor=INK, columnspacing=1.0)
    fig.tight_layout()
    fig.savefig(path, facecolor=SURFACE, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


def ablations(abl, path, level="mid"):
    """Change in mean top-1 accuracy (over budgets 0-1) against the reference selector, with 95% seed-bootstrap
    intervals. Rows without a like-for-like reference (the reference itself, the unit-cost sanity check and
    the tie-tolerant metric) stay in the JSON but are not plotted."""
    rows = [(a["label"], a["levels"][level]) for a in abl["ablations"]
            if "delta_vs_ref" in a["levels"][level] and a["name"] != "unit_cost_aware"]
    fig, ax = plt.subplots(figsize=(COLUMN, 0.26 * len(rows) + 0.75), facecolor=SURFACE)
    y = list(range(len(rows)))
    d = [r["delta_vs_ref"] for _, r in rows]
    lo = [r["delta_vs_ref"] - r["delta_ci95"][0] for _, r in rows]
    hi = [r["delta_ci95"][1] - r["delta_vs_ref"] for _, r in rows]
    ax.axvline(0, color=MUTED, linewidth=0.8)
    ax.errorbar(d, y, xerr=[lo, hi], fmt="o", color=METHODS["plandiscrim_geometry"][1], ecolor=METHODS["plandiscrim_geometry"][1],
                elinewidth=1.2, capsize=0, markersize=4.5, markeredgecolor=SURFACE, markeredgewidth=0.8)
    ax.set_yticks(y)
    ax.set_yticklabels([label for label, _ in rows], color=INK)
    ax.invert_yaxis()
    ref = next(a["levels"][level]["auc"] for a in abl["ablations"] if a["levels"][level].get("reference"))
    ax.set_xlabel(f"Change in accuracy vs reference ({ref:.3f}), {level} noise", color=MUTED)
    style(ax)
    ax.grid(axis="y", visible=False)
    ax.grid(axis="x", color=GRID, linewidth=0.6)
    fig.tight_layout()
    fig.savefig(path, facecolor=SURFACE, bbox_inches="tight", pad_inches=0.02)
    plt.close(fig)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--eval", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--metric", default="correct", choices=("correct", "correct_tol"))
    p.add_argument("--ablations", default=None)
    args = p.parse_args()
    with open(args.eval) as f:
        report = json.load(f)[args.metric]
    os.makedirs(args.out, exist_ok=True)
    written = []
    for name, which in (("pareto_acc.pdf", 0), ("pareto_unsafe.pdf", 1)):
        pareto(report, which, os.path.join(args.out, name))
        written.append(name)
    families(report, os.path.join(args.out, "families.pdf"))
    written.append("families.pdf")
    if args.ablations:
        with open(args.ablations) as f:
            ablations(json.load(f), os.path.join(args.out, "ablations.pdf"))
        written.append("ablations.pdf")
    print("wrote " + ", ".join(os.path.join(args.out, w) for w in written))


if __name__ == "__main__":
    main()
