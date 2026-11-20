import json, sys
R = json.load(open(sys.argv[1]))["results"]
for n in R:
    for tag in sorted(R[n]):
        r = R[n][tag]; d = r.get("diff_vs_base", {})
        h = " ".join(f"{b}:{r['harm'][b]}/{r['benefit'][b]}" for b in ("0.1", "0.3", "0.5"))
        print(f"{n:20s} {tag:10s} acc {r['mean_acc']:.4f} d {d.get('mean','-')} {d.get('ci95','')} unsafe {r['mean_unsafe']} drop {r['drop_after_peak']} topt {r['tool_optimal']} sh {r['tool_share']}")
