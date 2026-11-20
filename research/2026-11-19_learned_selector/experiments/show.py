import json, sys, glob, os
D = os.path.dirname(os.path.abspath(__file__))
fro = json.load(open(D + "/res_frozen.json"))
names = sys.argv[1:] or sorted(os.path.basename(p)[4:-5] for p in glob.glob(D + "/res_*.json"))
for n in names:
    R = json.load(open(f"{D}/res_{n}.json"))
    for tag in sorted(R):
        sp, lv, fs = tag.split("/")
        r = R[tag]
        bb = r["by_budget"]
        h = " ".join(f"{b}:{bb[b]['harm_rate']}/{bb[b]['benefit_captured']}" for b in ("0.1", "0.2", "0.3", "0.5"))
        d = r.get("diff_vs_frozen", {})
        print(f"{n:22s} {tag:24s} acc {r['mean_acc']:.4f} unsafe {r['mean_unsafe']:.4f} d {d.get('mean','-')} {d.get('ci95','')} peak {r.get('peak_budget','-')} drop {r.get('drop_after_0.65','-')} harm/ben {h}")
