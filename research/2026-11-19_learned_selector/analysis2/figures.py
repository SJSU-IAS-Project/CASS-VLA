import json
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
r = json.load(open("results.json"))["cells"]
INK, SEC, SURF, GRID = "#0b0b0b", "#52514e", "#fcfcfb", "#e6e5e1"
LV = {"low": "#86b6ef", "mid": "#2a78d6", "high": "#104281"}
plt.rcParams.update({"font.size": 10, "axes.edgecolor": SEC, "text.color": INK, "axes.labelcolor": SEC, "xtick.color": SEC, "ytick.color": SEC,
                     "figure.facecolor": SURF, "axes.facecolor": SURF})
def clean(ax):
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    ax.grid(axis="y", color=GRID, lw=0.8); ax.set_axisbelow(True)

# Figure 1: by rank bin, test (solid) and val (dashed)
fig, ax = plt.subplots(1, 2, figsize=(10, 3.8), constrained_layout=True)
labels = ["0-20", "20-40", "40-65", "65-80", "80-100"]
for lv, col in LV.items():
    for split, ls in (("test", "-"), ("val", "--")):
        q = r[f"{split}/{lv}"]["q1_by_rank"][:5]
        ax[0].plot(labels, [b["mean_ge_chosen"] for b in q], ls, color=col, marker="o", ms=5, lw=2, label=f"{lv} noise, {split}")
        ax[1].plot(labels, [b["frac_chosen_negative"] for b in q], ls, color=col, marker="o", ms=5, lw=2)
ax[0].axhline(0, color=SEC, lw=1); ax[0].set_ylabel("mean expected gain of the chosen tool"); ax[1].set_ylabel("share of calls with negative expected gain")
for a in ax: a.set_xlabel("rank of decision by predicted score (% of decisions)"); clean(a); a.axvline(2.5, color=SEC, lw=1, ls=":")
ax[0].set_title("Gain turns negative past rank 65%", loc="left", fontsize=11); ax[1].set_title("Harmful calls become common", loc="left", fontsize=11)
ax[0].legend(frameon=False, fontsize=8, ncol=2, loc="upper right")
fig.savefig("fig_late_ranks.png", dpi=150)

# Figure 2: permutation importance
def avg(nm, lv, k):
    return np.mean([r[f"{s}/{lv}"]["q3"][nm]["importance"][k]["drop"] for s in ("val", "test")])
keys = [k for k in r["val/mid"]["q3"]["plandiscrim"]["importance"]]
groups = [k for k in keys if k.startswith("GROUP:")]
groups.sort(key=lambda k: -avg("plandiscrim", "mid", k))
feats = sorted([k for k in keys if not k.startswith("GROUP:")], key=lambda k: -avg("plandiscrim", "mid", k))[:10]
fig, ax = plt.subplots(1, 2, figsize=(12, 4.6), constrained_layout=True, gridspec_kw=dict(width_ratios=[1, 1]))
for a, ks, title in ((ax[0], groups, "Feature groups (plandiscrim)"), (ax[1], feats, "Top 10 single features")):
    y = np.arange(len(ks))[::-1]
    for off, lv in ((0.19, "mid"), (-0.19, "high")):
        v = [avg("plandiscrim", lv, k) for k in ks]
        a.barh(y + off, v, height=0.36, color=LV[lv], label=f"{lv} noise")
        for yy, vv in zip(y + off, v): a.text(vv + 0.001, yy, f"{vv:.3f}", va="center", fontsize=7.5, color=SEC)
    a.set_yticks(y); a.set_yticklabels([k.replace("GROUP:", "").replace("_", " ") if k.startswith("GROUP:") else k for k in ks])
    a.set_xlabel("accuracy drop when shuffled (val and test mean)"); a.set_title(title, loc="left", fontsize=11)
    for s in ("top", "right"): a.spines[s].set_visible(False)
    a.grid(axis="x", color=GRID, lw=0.8); a.set_axisbelow(True)
ax[0].legend(frameon=False, loc="lower right")
fig.savefig("fig_permutation.png", dpi=150)
