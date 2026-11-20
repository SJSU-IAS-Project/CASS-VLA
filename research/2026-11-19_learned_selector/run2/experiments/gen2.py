import json, os
H = os.path.dirname(os.path.abspath(__file__))
def tab(fn, title, names=None):
    R = json.load(open(f"{H}/{fn}"))["results"]
    print(f"\n### {title}\n")
    print("| variant | cell | mean acc | diff vs signed [95% CI] | mean unsafe | drop after peak | tool-optimal | shares roi/depth/coll | harm 0.1/0.3/0.5 | benefit 0.1/0.3/0.5 |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for n in R:
        for lv in ("low", "mid", "high"):
            for sp in ("val", "test"):
                r = R[n][f"{sp}/{lv}"]; d = r.get("diff_vs_base")
                df = "-" if not d else f"{d['mean']:+.4f} [{d['ci95'][0]:+.4f}, {d['ci95'][1]:+.4f}]"
                hm = "/".join(str(r["harm"][b]) for b in ("0.1", "0.3", "0.5")); bn = "/".join(str(r["benefit"][b]) for b in ("0.1", "0.3", "0.5"))
                print(f"| {n} | {sp}/{lv} | {r['mean_acc']:.4f} | {df} | {r['mean_unsafe']:.3f} | {r['drop_after_peak']:.4f} | {r['tool_optimal']:.3f} | {r['tool_share']} | {hm} | {bn} |")
tab("res2_AC.json", "A and C (train: v2 + v2_extra + v3_extra, 34,718 rows)")
tab("res2_D.json", "D (same training data)")
if os.path.exists(f"{H}/res2_B.json"): tab("res2_B.json", "B (train: v2 + v2_extra only, 25,036 rows; base = geometry-only signed on the same rows)")
