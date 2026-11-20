import json, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.lines import Line2D

R = "/home/user/CASS-VLA"
OUT = f"{R}/research/2026-11-19_learned_selector/deliverables/figures"
J = lambda p: json.load(open(f"{R}/{p}"))
BG, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"
C = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]   # validated slots 1-4
MK = ["o", "s", "^", "D"]
plt.rcParams.update({"font.size": 15, "axes.titlesize": 18, "axes.labelsize": 16, "xtick.labelsize": 14,
    "ytick.labelsize": 14, "legend.fontsize": 14, "figure.facecolor": BG, "axes.facecolor": BG,
    "savefig.facecolor": BG, "text.color": INK, "axes.labelcolor": INK2, "xtick.color": INK2,
    "ytick.color": INK2, "axes.edgecolor": "#b9b8b3", "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.8, "axes.axisbelow": True,
    "svg.fonttype": "none", "font.family": "DejaVu Sans"})

def save(fig, name):
    for ext in ("png", "svg"):
        fig.savefig(f"{OUT}/{name}.{ext}", dpi=200)
    plt.close(fig)

METH = ["signed", "frozen", "signed_scene", "uncertainty_margin"]
LAB = {"signed": "signed", "frozen": "frozen", "signed_scene": "signed_scene", "uncertainty_margin": "uncertainty_margin"}
G = J("out/v4_eval/final_geom.json")
X = [b / 20 for b in range(21)]   # budget b = calls per decision for selectors (one tool call on a fraction b of decisions)

def pareto(level, key, ylabel, name, title, ao_key):
    fig, ax = plt.subplots(figsize=(13.33, 7.5))
    r = G["results"][f"final/{level}"]
    for i, m in enumerate(METH):
        ax.plot(X, r[m][key], color=C[i], marker=MK[i], ms=7, lw=2.5, label=LAB[m])
    ao = r["always_on"][ao_key]
    ax.axhline(ao, color=INK2, ls="--", lw=1.8, label="always_on level")
    ax.plot([3], [ao], marker="*", ms=20, color=INK, ls="", label="always_on (3 calls)", zorder=5, clip_on=False)
    ax.axvline(0.6, color=INK2, ls=":", lw=2)
    ax.text(1.1, 0.35 if key == "curve" else 0.55, "dotted line: 0.6 calls\n(P4 budget)", transform=ax.get_xaxis_transform(), color=INK2, fontsize=14, va="center")
    ax.text(0.15, ao, "always_on level", color=INK2, fontsize=14, va="bottom", transform=matplotlib.transforms.blended_transform_factory(ax.transAxes, ax.transData), ha="left") if False else None
    ax.set_xlim(0, 3.1); ax.set_xlabel("calls per decision (selectors: budget, max 1; always_on: 3)")
    ax.set_ylabel(ylabel); ax.set_title(title, loc="left", color=INK)
    ax.legend(loc="lower right" if key == "curve" else "upper right", frameon=False, ncol=1)
    fig.tight_layout(); save(fig, name)

for lv in ("low", "mid", "high"):
    pareto(lv, "curve", "decision accuracy", f"f1_pareto_{lv}",
           f"Accuracy vs calls per decision, {lv} noise (second final, n=4,922)", "mean_acc")
for lv in ("mid", "high"):
    pareto(lv, "unsafe_curve", "unsafe rate (lower is better)", f"f2_unsafe_{lv}",
           f"Unsafe rate vs calls per decision, {lv} noise (second final, n=4,922)", "mean_unsafe")

# f3 P4
fig, axs = plt.subplots(1, 2, figsize=(13.33, 7.0))
P4 = G["hypotheses"]["final"]["P4"]["cells"]
lvls = ["low", "mid", "high"]
for ax, (k, ck, ttl, mline, side) in zip(axs, [("acc_diff", "acc_diff_ci95", "Accuracy: signed minus always_on", -0.01, "margin -0.01: CI lower bound must stay above"),
                                     ("unsafe_diff", "unsafe_diff_ci95", "Unsafe rate: signed minus always_on", 0.01, "margin +0.01: CI upper bound must stay below")]):
    for i, lv in enumerate(lvls):
        c = P4[lv]; lo, hi = c[ck]
        ax.errorbar(c[k], i, xerr=[[c[k] - lo], [hi - c[k]]], fmt="o", color=C[0], ms=11, lw=2.5, capsize=6)
        ax.text(c[k], i - 0.2, f"{c[k]:+.3f} [{lo:+.3f}, {hi:+.3f}]", ha="center", va="top", fontsize=13, color=INK, bbox=dict(fc=BG, ec="none", pad=1.5), zorder=6)
    ax.axvline(0, color=INK2, lw=1.5)
    ax.axvline(mline, color=C[1], lw=2.5, ls="--")
    ax.axvspan(mline, -0.1 if mline < 0 else 0.1, color=C[1], alpha=0.10)
    ax.set_yticks(range(3)); ax.set_yticklabels([f"{l} noise" for l in lvls]); ax.set_ylim(2.6, -0.7); ax.tick_params(axis="x", labelsize=13)
    ax.set_title(ttl, loc="left", fontsize=16); ax.set_xlabel(f"difference at 0.6 calls (95% CI)\n{side}", fontsize=14)
    ax.grid(axis="y", visible=False)
    ax.set_xlim(-0.1, 0.1); ax.set_xticks([-0.1, -0.05, 0, 0.05, 0.1])
fig.suptitle("P4: non-inferiority to always_on at 0.6 calls (shaded = failing zone)", x=0.01, ha="left", fontsize=18)
fig.tight_layout(rect=(0, 0, 1, 0.94)); save(fig, "f3_p4")

# f4 forest
T = J("out/v3_eval/triggers_final.json")["results"]
S4 = J("out/v3_eval/final/s4_signed.json")["results"]["signed_mse_abstain"]
rows = []  # (label, mean, lo, hi, group) ; group None -> header
def hdr(t): rows.append((t, None, None, None, 0))
hdr("First final (n=4,903)")
for h, k, nm in (("H1", "plandiscrim_vs_uncertainty_margin", "plandiscrim - uncert. margin"),
                 ("H2", "plandiscrim_vs_scene_only", "plandiscrim - scene_only"),
                 ("S1", "plandiscrim_flip_vs_plandiscrim", "flip - plandiscrim")):
    for lv in lvls:
        c = T[f"final/{lv}"]["comparisons"][k]; rows.append((f"{h} {nm}, {lv}", c["mean_diff"], *c["ci95_by_seed"], 1))
for lv in lvls:
    c = S4[f"final/{lv}/plandiscrim"]["diff_vs_frozen"]
    rows.append((f"S4 signed - frozen, {lv}" + (" (not tested)" if lv == "low" else ""), c["mean"], *c["ci95"], 1))
hdr("Second final (n=4,922)")
H = G["hypotheses"]["final"]
for h, nm in (("P1", "signed - frozen"), ("P2", "signed - signed_scene"), ("P3", "signed - uncert. margin")):
    for lv in lvls:
        if lv in H[h]["cells"]:
            c = H[h]["cells"][lv]; rows.append((f"{h} {nm}, {lv}", c["mean_diff"], *c["ci95"], 2))
for lv in lvls:
    c = H["P4"]["cells"][lv]; rows.append((f"P4 accuracy vs always_on @0.6, {lv}", c["acc_diff"], *c["acc_diff_ci95"], 2))
for lv in lvls:
    c = H["P4"]["cells"][lv]; rows.append((f"P4 unsafe vs always_on @0.6, {lv}", c["unsafe_diff"], *c["unsafe_diff_ci95"], 2))
fig, ax = plt.subplots(figsize=(13.33, 11))
n = len(rows)
for i, (l, m, lo, hi, g) in enumerate(rows):
    if m is None:
        ax.text(-0.135, i, l, fontweight="bold", fontsize=15, va="center", color=INK); continue
    col = C[0] if g == 1 else C[1]
    ax.errorbar(m, i, xerr=[[m - lo], [hi - m]], fmt="o" if g == 1 else "s", color=col, ms=8, lw=2.2, capsize=4)
    ax.text(-0.135, i, l, va="center", fontsize=13, color=INK)
ax.axvline(0, color=INK, lw=1.5)
ax.set_ylim(n - 0.3, -0.8); ax.set_yticks([]); ax.set_xlim(-0.135, 0.125)
ax.grid(axis="y", visible=False)
ax.set_xlabel("difference (accuracy, or unsafe rate for P4 unsafe rows) with 95% CI; positive favors the first method, except P4 unsafe where negative is safer")
ax.xaxis.label.set_fontsize(12)
ax.set_title("All pre-registered differences with 95% CIs, both final tests", loc="left")
ax.legend(handles=[Line2D([], [], marker="o", color=C[0], ls="", ms=9, label="first final"),
                   Line2D([], [], marker="s", color=C[1], ls="", ms=9, label="second final")], loc="lower right", frameon=False)
ax.spines["left"].set_visible(False)
fig.tight_layout(); save(fig, "f4_hypotheses")

# f5 harm
fig, ax = plt.subplots(figsize=(13.33, 7.5))
bud = ["0.1", "0.2", "0.3", "0.5"]
for i, m in enumerate(["signed", "frozen", "uncertainty_margin"]):
    ci = [0, 1, 3][i]
    v = [G["results"]["final/mid"][m]["harm"][b] for b in bud]
    ax.plot(range(4), v, color=C[ci], marker=MK[ci], ms=10, lw=2.8, label=m)
    for x, y in enumerate(v):
        ax.annotate(f"{y:.3f}", (x, y), textcoords="offset points", xytext=(0, 14 if m != "signed" else -26), ha="center", fontsize=13, color=INK)
ax.set_xticks(range(4)); ax.set_xticklabels(bud); ax.set_xlim(-0.3, 3.3)
ax.set_xlabel("budget (fraction of decisions allowed a call)"); ax.set_ylabel("harm rate (lower is better)")
ax.set_title("Harm rate by budget, mid noise (second final)", loc="left")
ax.set_ylim(-0.045, 0.43); ax.legend(frameon=False, loc="upper right")
fig.tight_layout(); save(fig, "f5_harm")

# f6 gap split
A = J("research/2026-11-19_learned_selector/analysis2/results.json")["cells"]
fig, ax = plt.subplots(figsize=(13.33, 8.5))
cells = ["val/low", "val/mid", "val/high", "test/low", "test/mid", "test/high"]
y = 0; yt, yl = [], []
for c in cells:
    for b in (0.2, 0.5):
        e = [x for x in A[c]["q2"]["plandiscrim"] if abs(x["budget"] - b) < 1e-9][0]
        gap, bw = e["gap_exp_acc"], e["b_wrong_tool"]; sa = (gap - bw) / gap; sb = bw / gap
        ax.barh(y, sa, color=C[0], height=0.7, edgecolor=BG, linewidth=2)
        ax.barh(y, sb, left=sa, color=C[1], height=0.7, edgecolor=BG, linewidth=2)
        ax.text(sa / 2, y, f"{sa:.0%}", ha="center", va="center", color="white", fontsize=14, fontweight="bold")
        ax.text(sa + sb / 2, y, f"{sb:.0%}", ha="center", va="center", color=INK, fontsize=14, fontweight="bold")
        ax.text(1.01, y, f"gap {gap:.3f}", va="center", fontsize=13, color=INK2)
        yt.append(y); yl.append(f"{c}, budget {b}"); y += 1
    y += 0.4
ax.set_yticks(yt); ax.set_yticklabels(yl); ax.set_ylim(y - 0.2, -0.7); ax.set_xlim(0, 1.15)
ax.set_xticks([0, .25, .5, .75, 1]); ax.set_xticklabels(["0%", "25%", "50%", "75%", "100%"])
ax.grid(axis="y", visible=False); ax.set_xlabel("share of the gap to the ceiling (expected accuracy)")
ax.set_title("Gap to the ceiling: wrong decisions vs wrong tool (plandiscrim, seed 0; exploratory, val/test)", loc="left", fontsize=15)
ax.legend(handles=[plt.Rectangle((0, 0), 1, 1, color=C[0]), plt.Rectangle((0, 0), 1, 1, color=C[1])],
          labels=["(a) wrong decisions", "(b) wrong tool"], loc="upper center", bbox_to_anchor=(0.45, -0.09), ncol=2, frameon=False)
fig.tight_layout(); save(fig, "f6_gap_split")

# f7 vlm
files = [("real", "vlm_extra_train"), ("shuffle", "vlm_control_shuffle"), ("shuffle_family", "vlm_control_shuffle_family"), ("family", "vlm_control_family")]
fig, ax = plt.subplots(figsize=(13.33, 8))
off = [-0.27, -0.09, 0.09, 0.27]
for j, (nm, f) in enumerate(files):
    d = J(f"out/v2_eval/{f}.json")["results"]
    for i, c in enumerate(cells):
        ax.plot(d[c]["geometry_vlm"]["mean_acc"] - d[c]["geometry"]["mean_acc"], i + off[j], MK[j], color=C[j], ms=11,
                label=nm if i == 0 else None, mec=BG)
ax.axvline(0, color=INK, lw=1.5)
ax.set_yticks(range(6)); ax.set_yticklabels(cells); ax.set_ylim(5.6, -0.6); ax.grid(axis="y", visible=False)
ax.set_xlabel("mean accuracy, geometry+VLM minus geometry (one run per cell, no CIs)")
ax.set_title("VLM gain over geometry and its controls (exploratory)", loc="left")
ax.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=4, title="VLM features:", title_fontsize=14)
fig.tight_layout(); save(fig, "f7_vlm_controls")

# f0 pipeline
fig, ax = plt.subplots(figsize=(13.33, 5.5)); ax.axis("off"); ax.set_xlim(0, 100); ax.set_ylim(0, 40)
def box(x, w, txt, fill, y=12, h=16):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.5", fc=fill, ec="#b9b8b3", lw=1.5))
    ax.text(x + w / 2, y + h / 2, txt, ha="center", va="center", fontsize=15, color=INK)
def arrow(x0, x1, y=20):
    ax.add_patch(FancyArrowPatch((x0, y), (x1, y), arrowstyle="-|>", mutation_scale=22, lw=2.2, color=INK2))
box(1, 17, "scene +\nK candidate\nplans", "#e8f0fb"); arrow(19.2, 23)
box(23.5, 17, "selector\n(signed MLP,\ngain > 0 and\nwithin budget)", "#e8f0fb"); arrow(41.7, 46)
box(46.5, 17, "one tool\n(roi, depth,\ncollision) or\nnone", "#fdeee7"); arrow(64.7, 69)
box(69.5, 13, "ranker", "#e7f6f0"); arrow(83.2, 86.5)
box(87, 12.5, "decision", "#e7f6f0")
ax.text(93.2, 8, "scored against\nthe oracle decision", ha="center", va="top", fontsize=14, color=INK2)
ax.text(1, 36, "Selector pipeline: spend a limited call budget on the decisions where a tool helps", fontsize=18, color=INK, va="center")
ax.text(55, 8, "a call costs 1; always_on = 3 calls per decision", ha="center", va="top", fontsize=14, color=INK2)
fig.tight_layout(); save(fig, "f0_pipeline")
