import json, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(f"{HERE}/h3_posthoc.json"))
COL = {"plandiscrim": "#2a78d6", "signed_mse_abstain": "#eb6834", "scene_only": "#1baf7a", "uncertainty_margin": "#6250d6"}
NAME = {"plandiscrim": "plandiscrim", "signed_mse_abstain": "signed_mse_abstain", "scene_only": "scene_only", "uncertainty_margin": "uncertainty_margin"}
fig, ax = plt.subplots(2, 3, figsize=(12, 6.6), sharex=True, dpi=130)
for j, lv in enumerate(("low", "mid", "high")):
    for i, key in enumerate(("acc_diff", "unsafe_diff")):
        a = ax[i, j]
        a.axhline(0, color="#52514e", lw=1)
        for m in COL:
            c = d[lv]["methods"][m]["curve05"]
            x = c["budget"]
            a.plot(x, c[key], color=COL[m], lw=2, marker="o", ms=3.5, label=NAME[m])
            if key == "unsafe_diff" and m in ("plandiscrim", "signed_mse_abstain"):
                a.fill_between(x, [v[0] for v in c["unsafe_diff_ci"]], [v[1] for v in c["unsafe_diff_ci"]], color=COL[m], alpha=0.13, lw=0)
        a.grid(axis="y", color="#e3e2de", lw=0.8)
        for s in ("top", "right"):
            a.spines[s].set_visible(False)
        if i == 0:
            a.set_title(f"{lv} noise", loc="left", fontsize=11)
            a.set_ylim(-0.25, 0.1)
        else:
            a.set_ylim(-0.06, 0.22)
            a.set_xlabel("budget (calls per decision; always_on = 3)")
        if j == 0:
            a.set_ylabel("accuracy minus always_on" if i == 0 else "unsafe rate minus always_on\n(lower is safer)")
ax[0, 0].legend(frameon=False, fontsize=8.5, loc="lower right")
fig.suptitle("Post hoc, first final split (seeds 760-859): difference from always_on by budget; bands are 95% seed-bootstrap CIs of the unsafe difference", fontsize=9.5, x=0.01, ha="left")
fig.tight_layout(rect=(0, 0, 1, 0.96))
fig.savefig(f"{HERE}/h3_posthoc.png")
