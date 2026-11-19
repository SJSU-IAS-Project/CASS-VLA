"""Decision-change and abstention labels (refined proposal section 3) for one retained oracle record."""
import numpy as np

from cassvla.planning.features import selector_features
from cassvla.planning.ranker import rank
from cassvla.planning.tools import LEVELS, TOOLS, TOOL_FNS, base_observation, merge

TIE_SCORE = 1.0


def _spearman(order, oracle_order):
    pos = {n: i for i, n in enumerate(oracle_order)}
    a = np.arange(len(order), dtype=float)
    b = np.array([pos[n] for n in order], dtype=float)
    if len(a) < 2:
        return 1.0
    return float(np.corrcoef(a, b)[0, 1])


def _outcome(rec, ranked):
    top = ranked["top1"]
    m = rec["metrics"]
    tied = m[top]["safe"] == m[rec["c_star"]]["safe"] and m[rec["c_star"]]["score"] - m[top]["score"] <= TIE_SCORE
    return dict(top1=top, correct=top == rec["c_star"], correct_tol=bool(tied), unsafe=not m[top]["safe"], margin=round(min(ranked["margin"], 1e6), 3),
                spearman=round(_spearman(ranked["order"], rec["oracle_order"]), 3))


def label_record(rec, levels=None):
    base = base_observation(rec)
    base_rank = rank(rec, base)
    out = dict(family=rec["family"], seed=rec["seed"], t_dec=rec["t_dec"], c_star=rec["c_star"], n_safe=rec["n_safe"],
               n_cand=len(rec["candidates"]), oracle_order=rec["oracle_order"],
               safe={n: bool(m["safe"]) for n, m in rec["metrics"].items()},
               no_tool=_outcome(rec, base_rank), features=selector_features(rec, base, base_rank), levels={})
    for level in levels or LEVELS:
        responses = {t: TOOL_FNS[t](rec, level) for t in TOOLS}
        tools = {t: _outcome(rec, rank(rec, merge(base, [responses[t]]))) for t in TOOLS}
        always = _outcome(rec, rank(rec, merge(base, list(responses.values()))))
        change = {t: bool(tools[t]["correct"] and not out["no_tool"]["correct"]) for t in TOOLS}
        change_tol = {t: bool(tools[t]["correct_tol"] and not out["no_tool"]["correct_tol"]) for t in TOOLS}
        out["levels"][level] = dict(tools=tools, always_on=always, decision_change=change, abstain=not any(change.values()),
                                    decision_change_tol=change_tol, abstain_tol=not any(change_tol.values()))
    return out
