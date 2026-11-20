"""Merge per-level eval_triggers.py outputs into one file with the structure of a single run.

    python scripts/merge_trigger_runs.py --out out/v3_eval/triggers_final.json out/v3_eval/final/triggers_final_{low,mid,high}.json
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from eval_triggers import LEVELS, hypotheses  # noqa: E402


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("runs", nargs="+")
    args = p.parse_args()
    runs = [json.load(open(f)) for f in args.runs]
    for r in runs[1:]:
        assert r["n_train"] == runs[0]["n_train"] and r["report_budgets"] == runs[0]["report_budgets"], "runs differ in training data"
    res = {k: v for r in runs for k, v in r["results"].items()}
    splits = list(dict.fromkeys(k.split("/")[0] for k in res))
    levels = [lv for lv in LEVELS if all(f"{s}/{lv}" in res for s in splits)]
    out = dict(runs[0])
    out["results"] = {f"{s}/{lv}": res[f"{s}/{lv}"] for s in splits for lv in levels}
    out["hypotheses"] = hypotheses(out["results"], splits, levels)
    json.dump(out, open(args.out, "w"), indent=1)
    print(json.dumps(out["hypotheses"]))


if __name__ == "__main__":
    main()
