import json, os
D = os.path.dirname(os.path.abspath(__file__))
V = ["signed_mse_abstain","signed_mse_noabstain","signed_huber_abstain","signed_mse_abstain_toolw","cal_control_80pct","cal_isotonic","cal_platt","softmax_none","pairwise_rank"]
cells = [f"{s}/{l}" for s in ("val","test") for l in ("low","mid","high")]
for fs in ("plandiscrim","scene_only"):
    print(f"\n### Feature set: {fs}\n")
    print("| variant | " + " | ".join(cells) + " | mean unsafe mid(val/test) | drop after 0.65 (mid val/test) |")
    print("|---|" + "---|"*(len(cells)+2))
    fr = json.load(open(D+"/res_frozen.json"))
    print("| frozen MLP (acc) | " + " | ".join(f"{fr[c+'/'+fs]['mean_acc']:.4f}" for c in cells) + " | " + " / ".join(f"{fr[f'{s}/mid/{fs}']['mean_unsafe']:.3f}" for s in ("val","test")) + " | " + " / ".join(f"{max(fr[f'{s}/mid/{fs}']['curve'][13:])-fr[f'{s}/mid/{fs}']['curve'][-1]:.3f}" for s in ("val","test")) + " |")
    for v in V:
        R = json.load(open(f"{D}/res_{v}.json"))
        if not all(f"{c}/{fs}" in R for c in cells): continue
        row = [f"{R[c+'/'+fs]['diff_vs_frozen']['mean']:+.4f} [{R[c+'/'+fs]['diff_vs_frozen']['ci95'][0]:+.4f},{R[c+'/'+fs]['diff_vs_frozen']['ci95'][1]:+.4f}]" for c in cells]
        print(f"| {v} | " + " | ".join(row) + " | " + " / ".join(f"{R[f'{s}/mid/{fs}']['mean_unsafe']:.3f}" for s in ("val","test")) + " | " + " / ".join(f"{R[f'{s}/mid/{fs}']['drop_after_0.65']:.3f}" for s in ("val","test")) + " |")
print("\n### Harm rate / benefit captured, plandiscrim, mid noise, val then test (budgets 0.1 / 0.2 / 0.3 / 0.5)\n")
print("| variant | split | harm 0.1 | 0.2 | 0.3 | 0.5 | benefit 0.1 | 0.2 | 0.3 | 0.5 |\n|---|---|---|---|---|---|---|---|---|---|")
for v in ["frozen"]+V:
    R = json.load(open(f"{D}/res_{v}.json"))
    for s in ("val","test"):
        r = R.get(f"{s}/mid/plandiscrim")
        if not r: continue
        b = r["by_budget"]
        print(f"| {v} | {s} | " + " | ".join(str(b[k]["harm_rate"]) for k in ("0.1","0.2","0.3","0.5")) + " | " + " | ".join(str(b[k]["benefit_captured"]) for k in ("0.1","0.2","0.3","0.5")) + " |")
print("\n### Tool-optimal rate (share of decisions with a positive-gain tool where the chosen tool is the best one) and tool shares roi/depth/collision, plandiscrim\n")
print("| variant | cell | tool-optimal | shares |\n|---|---|---|---|")
for v in ["frozen","signed_mse_abstain","signed_mse_abstain_toolw"]:
    R = json.load(open(f"{D}/res_{v}.json"))
    for c in cells:
        r = R[c+"/plandiscrim"]
        print(f"| {v} | {c} | {r.get('tool_optimal_rate')} | {r.get('tool_share')} |")
print("\n### Curves (plandiscrim, test/mid, budgets 0.5 to 1.0 step 0.05)\n")
for v in ["frozen","signed_mse_abstain","signed_mse_abstain_toolw","pairwise_rank"]:
    R = json.load(open(f"{D}/res_{v}.json")); print(f"- {v}: " + " ".join(f"{x:.3f}" for x in R["test/mid/plandiscrim"]["curve"][10:]))
