"""Vector figures for the VoI selector and the on-device VLM study (paper/figures/*.pdf).

    python scripts/voi_figures.py --voi-eval out/voi_eval/val.json --split val --ablations out/voi_eval/val_ablations.json \
        --yesno out/vlm_yesno/eval.json --latency out/voi_eval/latency.json --out paper/figures

Writes voi_pareto_acc.pdf, voi_pareto_unsafe.pdf (accuracy and unsafe rate against calls per decision, one panel per
noise level; always-on is a reference line at 3 calls), voi_ablations.pdf (change against abl_reference with its
seed-bootstrap interval), vlm_yesno_auroc.pdf and latency.pdf. Styling comes from make_figures.py.
"""
import argparse
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_figures import COLUMN, INK, MUTED, NEUTRAL, PAGE, plt, style  # noqa: E402

LEVELS = ("low", "mid", "high")
BUDGETS = np.round(np.arange(0.0, 1.0001, 0.05), 2)
SERIES = {
    "signed": ("Learned selector (signed, Max)", "#2a78d6", "-"),
    "voi": ("VoI, abstains when VoI <= 0", "#e34948", "-"),
    "voi_budget": ("VoI, budget only", "#e34948", (0, (4, 1.5))),
    "voi_fitted": ("VoI, fitted priors", "#eb6834", "--"),
    "voi_vlm": ("VoI + VLM prior", "#6250d6", (0, (3, 1, 1, 1))),
    "uncertainty_margin": ("Ranker margin", "#1baf7a", "-."),
}


def pareto(report, split, which, path):
    fig, axes = plt.subplots(1, 3, figsize=(PAGE, 2.3), sharey=True)
    key = "curve" if which == "acc" else "unsafe_curve"
    for ax, lv in zip(axes, LEVELS):
        style(ax)
        per = report["results"].get(f"{split}/{lv}", {})
        for m, (label, color, ls) in SERIES.items():
            if m in per and per[m].get(key):
                x = BUDGETS + per[m].get("cost_offset", 0.0)
                ax.plot(x, per[m][key], color=color, linestyle=ls, linewidth=1.4, label=label)
        if "always_on" in per:
            y = per["always_on"]["mean_acc" if which == "acc" else "mean_unsafe"]
            ax.axhline(y, color=NEUTRAL, linewidth=0.9, linestyle=":", label="Always-on (3 calls)")
        ax.set_title(f"{lv} tool noise", color=INK)
        ax.set_xlabel("Calls per decision", color=MUTED)
    axes[0].set_ylabel("Top-1 accuracy" if which == "acc" else "Unsafe top-1 rate", color=MUTED)
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=4, frameon=False, bbox_to_anchor=(0.5, -0.02))
    fig.tight_layout(rect=(0, 0.14, 1, 1))
    fig.savefig(path)
    plt.close(fig)


def ablations(report, split, path, ref="abl_reference"):
    names = sorted({k.split("_minus_")[0] for tag, c in report["comparisons"].items() if tag.startswith(split) for k in c if k.endswith(f"_minus_{ref}")})
    fig, axes = plt.subplots(1, 3, figsize=(PAGE, 0.35 * len(names) + 0.9), sharey=True)
    for ax, lv in zip(axes, LEVELS):
        style(ax)
        comp = report["comparisons"].get(f"{split}/{lv}", {})
        for i, n in enumerate(names):
            c = comp.get(f"{n}_minus_{ref}")
            if c:
                ax.errorbar(c["mean_diff"], i, xerr=[[c["mean_diff"] - c["ci95"][0]], [c["ci95"][1] - c["mean_diff"]]], fmt="o", color="#2a78d6",
                            markersize=3, elinewidth=1, capsize=2)
        ax.axvline(0, color=MUTED, linewidth=0.6)
        ax.set_title(f"{lv} tool noise", color=INK)
        ax.set_xlabel("Change in mean accuracy", color=MUTED)
    axes[0].set_yticks(range(len(names)))
    axes[0].set_yticklabels([n.replace("abl_", "").replace("_", " ") for n in names])
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def yesno(ev, path):
    qs = list(ev["questions"])
    fig, ax = plt.subplots(figsize=(COLUMN, 0.32 * len(qs) + 0.8))
    style(ax)
    for i, q in enumerate(qs):
        v = ev["questions"][q]
        if v.get("auroc") is None:
            continue
        lo, hi = v["ci95"] or [v["auroc"], v["auroc"]]
        ax.errorbar(v["auroc"], i, xerr=[[v["auroc"] - lo], [hi - v["auroc"]]], fmt="o", color="#6250d6", markersize=3, elinewidth=1, capsize=2)
    ax.axvline(0.5, color=MUTED, linewidth=0.6, linestyle=":")
    ax.set_yticks(range(len(qs)))
    ax.set_yticklabels(qs)
    ax.set_xlim(0.3, 1.0)
    ax.set_xlabel("AUROC (0.5 = chance)", color=MUTED)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def latency(entries, path):
    names = list(entries)
    fig, ax = plt.subplots(figsize=(COLUMN, 0.3 * len(names) + 0.8))
    style(ax)
    ax.barh(range(len(names)), [entries[n] for n in names], color="#2a78d6", height=0.6)
    for i, n in enumerate(names):
        ax.text(entries[n], i, f" {entries[n]:.3g} s", va="center", color=INK, fontsize=7)
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names)
    ax.set_xscale("log")
    ax.set_xlabel("Seconds on an Apple Silicon Mac (log scale)", color=MUTED)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--voi-eval", default=None)
    p.add_argument("--split", default="val")
    p.add_argument("--ablations", default=None)
    p.add_argument("--yesno", default=None)
    p.add_argument("--latency", default=None, help="JSON {label: seconds}")
    p.add_argument("--out", required=True)
    a = p.parse_args()
    os.makedirs(a.out, exist_ok=True)
    if a.voi_eval:
        r = json.load(open(a.voi_eval))
        pareto(r, a.split, "acc", os.path.join(a.out, "voi_pareto_acc.pdf"))
        pareto(r, a.split, "unsafe", os.path.join(a.out, "voi_pareto_unsafe.pdf"))
    if a.ablations:
        ablations(json.load(open(a.ablations)), a.split, os.path.join(a.out, "voi_ablations.pdf"))
    if a.yesno:
        yesno(json.load(open(a.yesno)), os.path.join(a.out, "vlm_yesno_auroc.pdf"))
    if a.latency:
        latency(json.load(open(a.latency)), os.path.join(a.out, "latency.pdf"))
    print("wrote figures to", a.out)


if __name__ == "__main__":
    main()
