"""Builds report.md, report.html and SOURCES_TABLES.md from report.tmpl.md.

Tables are generated from the result files so that no table number is typed by hand.
Run:  python3 build.py        (then report.pdf is made by the chromium command in the appendix)
"""
import base64
import html
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "../../../.."))
RUN = os.path.join(ROOT, "research/2026-11-19_learned_selector")
FIGDIR = os.path.join(RUN, "deliverables/figures")
LV = ("low", "mid", "high")
USED = []  # (table, file, keys)


def load(p):
    return json.load(open(os.path.join(ROOT, p)))


G2 = load("out/v4_eval/final_geom.json")
TF = load("out/v3_eval/triggers_final.json")
S4 = load("out/v3_eval/final/s4_signed.json")
R2 = G2["results"]
R1 = TF["results"]
S4R = S4["results"]["signed_mse_abstain"]
BUD = [round(0.05 * i, 2) for i in range(21)]


def f(x, n=4):
    return f"{x:.{n}f}"


def sg(x, n=4):
    return f"{x:+.{n}f}"


def ci(c, n=4):
    return f"[{c[0]:.{n}f}, {c[1]:.{n}f}]"


def table(head, rows):
    out = ["| " + " | ".join(head) + " |", "|" + "|".join("---" for _ in head) + "|"]
    out += ["| " + " | ".join(str(c) for c in r) + " |" for r in rows]
    return "\n".join(out)


def first_reach(curve, target, up=True):
    for b, v in zip(BUD, curve):
        if (v >= target) if up else (v <= target):
            return b
    return None


def t_final2_means():
    rows = []
    for name in ("signed", "frozen", "signed_scene", "uncertainty_margin"):
        rows.append([name] + [f(R2[f"final/{l}"][name]["mean_acc"]) for l in LV] + [f(R2[f"final/{l}"][name]["mean_unsafe"]) for l in LV])
    rows.append(["always_on (3 calls)"] + [f(R2[f"final/{l}"]["always_on"]["mean_acc"]) for l in LV] + [f(R2[f"final/{l}"]["always_on"]["mean_unsafe"]) for l in LV])
    USED.append(("T-final2-means", "out/v4_eval/final_geom.json", "results.final/<level>.<method>.{mean_acc,mean_unsafe}; always_on mean_acc and mean_unsafe are its constant accuracy and unsafe rate"))
    return table(["Method", "Acc low", "Acc mid", "Acc high", "Unsafe low", "Unsafe mid", "Unsafe high"], rows)


def t_p123():
    H = G2["hypotheses"]["final"]
    rows = []
    for k, desc, lvs in (("P1", "signed minus frozen", ("mid", "high")), ("P2", "signed minus signed_scene", LV), ("P3", "signed minus uncertainty_margin", LV)):
        cells = []
        for l in LV:
            c = H[k]["cells"].get(l)
            cells.append(f"{sg(c['mean_diff'])} {ci(c['ci95'])}" if c else "not part of the hypothesis")
        rows.append([k + ": " + desc, *cells, H[k]["status"]])
    USED.append(("T-P123", "out/v4_eval/final_geom.json", "hypotheses.final.{P1,P2,P3}.cells.<level>.{mean_diff,ci95}, .status"))
    return table(["Hypothesis (pre-registered)", "Low", "Mid", "High", "Verdict"], rows)


def t_p4():
    P = G2["hypotheses"]["final"]["P4"]["cells"]
    rows = []
    for l in LV:
        c = P[l]
        rows.append([l, f"{sg(c['acc_diff'])} {ci(c['acc_diff_ci95'])}", "yes" if c["acc_lower_above_minus_0.01"] else "no",
                     f"{sg(c['unsafe_diff'])} {ci(c['unsafe_diff_ci95'])}", "yes" if c["unsafe_upper_below_plus_0.01"] else "no"])
    USED.append(("T-P4", "out/v4_eval/final_geom.json", "hypotheses.final.P4.cells.<level>.{acc_diff,acc_diff_ci95,unsafe_diff,unsafe_diff_ci95,acc_lower_above_minus_0.01,unsafe_upper_below_plus_0.01}"))
    return table(["Noise", "Accuracy, signed minus always-on", "Lower bound above -0.01", "Unsafe rate, signed minus always-on", "Upper bound below +0.01"], rows)


def t_at06():
    rows = []
    for name in ("signed", "frozen", "signed_scene", "uncertainty_margin"):
        rows.append([name] + [f"{f(R2[f'final/{l}'][name]['at_budget_0.6']['acc'])} / {f(R2[f'final/{l}'][name]['at_budget_0.6']['unsafe'])}" for l in LV])
    rows.append(["always_on (3 calls)"] + [f"{f(R2[f'final/{l}']['always_on']['mean_acc'])} / {f(R2[f'final/{l}']['always_on']['mean_unsafe'])}" for l in LV])
    USED.append(("T-at06", "out/v4_eval/final_geom.json", "results.final/<level>.<method>.at_budget_0.6.{acc,unsafe}; always_on mean_acc, mean_unsafe"))
    return table(["Method at 0.6 calls per decision", "Low (acc / unsafe)", "Mid (acc / unsafe)", "High (acc / unsafe)"], rows)


def t_reach2():
    rows = []
    for name in ("signed", "frozen", "signed_scene", "uncertainty_margin"):
        cells = []
        for l in LV:
            r = R2[f"final/{l}"]
            aa, au = r["always_on"]["mean_acc"], r["always_on"]["mean_unsafe"]
            ba = first_reach(r[name]["curve"], aa)
            bu = first_reach(r[name]["unsafe_curve"], au, up=False)
            both = None
            for b, a_, u_ in zip(BUD, r[name]["curve"], r[name]["unsafe_curve"]):
                if a_ >= aa and u_ <= au:
                    both = b
                    break
            cells.append(" / ".join("not reached" if x is None else f"{x:.2f}" for x in (ba, bu, both)))
        rows.append([name] + cells)
    USED.append(("T-reach2", "out/v4_eval/final_geom.json", "computed here from results.final/<level>.<method>.{curve,unsafe_curve} (21 budgets, step 0.05) against always_on mean_acc and mean_unsafe; first budget at which the curve is at least always-on accuracy, at most its unsafe rate, and both on the same budget"))
    return table(["Method", "Low (acc / unsafe / both)", "Mid (acc / unsafe / both)", "High (acc / unsafe / both)"], rows)


def t_s2():
    rows = []
    for l in LV:
        for name in ("signed", "frozen", "signed_scene", "uncertainty_margin"):
            d = R2[f"final/{l}"][name]
            rows.append([l, name] + [f"{f(d['harm'][b], 3)} / {f(d['benefit'][b], 3)}" for b in ("0.1", "0.2", "0.3", "0.5")])
    USED.append(("T-s2-2", "out/v4_eval/final_geom.json", "results.final/<level>.<method>.{harm,benefit}.<budget>"))
    return table(["Noise", "Method", "0.1", "0.2", "0.3", "0.5"], rows)


def t_fam2():
    fams = list(R2["final/low"]["signed"]["by_family"])
    rows = []
    for fam in fams:
        rows.append([fam] + [f"{f(R2[f'final/{l}']['signed']['by_family'][fam], 3)} / {f(R2[f'final/{l}']['signed_scene']['by_family'][fam], 3)} / {f(R2[f'final/{l}']['uncertainty_margin']['by_family'][fam], 3)}" for l in LV])
    USED.append(("T-fam2", "out/v4_eval/final_geom.json", "results.final/<level>.<method>.by_family.<family> (point estimates, no CIs)"))
    return table(["Family", "Low", "Mid", "High"], rows)


def t_shape2():
    rows = []
    for name in ("signed", "frozen"):
        rows.append([name + ": accuracy at budget 1.0"] + [f(R2[f"final/{l}"][name]["acc_at_1"]) for l in LV])
        rows.append([name + ": drop after the peak"] + [f(R2[f"final/{l}"][name]["drop_after_0.65"]) for l in LV])
        rows.append([name + ": tool-optimal rate"] + [f(R2[f"final/{l}"][name]["tool_optimal"], 3) for l in LV])
        rows.append([name + ": share roi / depth / collision (mid)"] + ["", " / ".join(f(x, 3) for x in R2["final/mid"][name]["tool_share"]), ""])
    USED.append(("T-shape2", "out/v4_eval/final_geom.json", "results.final/<level>.<method>.{acc_at_1,drop_after_0.65,tool_optimal,tool_share}"))
    return table(["Measure", "Low", "Mid", "High"], rows)


def t_first_verdicts():
    C = {l: R1[f"final/{l}"]["comparisons"] for l in LV}
    S = {l: S4R[f"final/{l}/plandiscrim"]["diff_vs_frozen"] for l in LV}
    rows = []
    for key, desc in (("plandiscrim_vs_uncertainty_margin", "H1: plandiscrim minus uncertainty_margin"), ("plandiscrim_vs_scene_only", "H2: plandiscrim minus scene_only"), ("plandiscrim_flip_vs_plandiscrim", "S1: plandiscrim_flip minus plandiscrim")):
        rows.append([desc] + [f"{sg(C[l][key]['mean_diff'])} {ci(C[l][key]['ci95_by_seed'])}" for l in LV])
    rows.append(["S4: signed_mse_abstain minus plandiscrim"] + [f"{sg(S[l]['mean'])} {ci(S[l]['ci95'])}" for l in LV])
    USED.append(("T-first-verdicts", "out/v3_eval/triggers_final.json; out/v3_eval/final/s4_signed.json", "results.final/<level>.comparisons.*.{mean_diff,ci95_by_seed}; hypotheses.final.{H1,H2,S1}; results.signed_mse_abstain.final/<level>/plandiscrim.diff_vs_frozen.{mean,ci95}"))
    return table(["Hypothesis", "Low", "Mid", "High"], rows)


def t_first_means():
    pols = ("random", "uncertainty_margin", "ego_speed", "candidate_spread", "fixed_schedule", "scene_only", "candidate_only", "plandiscrim", "plandiscrim_flip")
    rows = [[p] + [f(R1[f"final/{l}"][p]["mean_acc"]) for l in LV] for p in pols]
    rows.append(["signed_mse_abstain (S4)"] + [f(S4R[f"final/{l}/plandiscrim"]["mean_acc"]) for l in LV])
    rows.append(["fair_ceiling"] + [f(R1[f"final/{l}"]["fair_ceiling"]["mean_acc"]) for l in LV])
    USED.append(("T-first-means", "out/v3_eval/triggers_final.json; out/v3_eval/final/s4_signed.json", "results.final/<level>.<policy>.mean_acc; results.signed_mse_abstain.final/<level>/plandiscrim.mean_acc"))
    return table(["Policy", "Low", "Mid", "High"], rows)


def t_first_h3():
    rows = []
    for l in LV:
        r = R1[f"final/{l}"]
        a, u = r["always_on"]["acc"], r["always_on"]["unsafe"]
        h = r["h3_always_on"]["plandiscrim"]
        both = None
        for b, a_, u_ in zip(BUD, r["plandiscrim"]["curve"], r["plandiscrim"]["unsafe_curve"]):
            if a_ >= a and u_ <= u:
                both = b
                break
        rows.append([l, f"{f(a)} / {f(u)}", f"{h['budget']:.2f}", f"{f(h['acc'])} / {f(h['unsafe'])}", sg(h["unsafe"] - h["always_on_unsafe"]), "not reached" if both is None else f"{both:.2f}"])
    USED.append(("T-first-h3", "out/v3_eval/triggers_final.json", "results.final/<level>.{always_on,h3_always_on.plandiscrim}; the both-matched budget is computed here from plandiscrim.curve and .unsafe_curve (post hoc)"))
    return table(["Noise", "Always-on acc / unsafe", "plandiscrim first matches accuracy at", "its acc / unsafe there", "unsafe minus always-on there", "First budget matching both (post hoc)"], rows)


def t_first_s2():
    rows = []
    for l in LV:
        for p in ("plandiscrim", "scene_only", "uncertainty_margin"):
            b = R1[f"final/{l}"][p]["by_budget"]
            rows.append([l, p] + [f"{f(b[x]['harm_rate'], 3)} / {f(b[x]['benefit_captured'], 3)}" for x in ("0.1", "0.2", "0.3", "0.5")])
    USED.append(("T-first-s2", "out/v3_eval/triggers_final.json", "results.final/<level>.<policy>.by_budget.<budget>.{harm_rate,benefit_captured}"))
    return table(["Noise", "Policy", "0.1", "0.2", "0.3", "0.5"], rows)


def t_first_s4():
    rows = []
    for lab, fn in (("mean accuracy, signed / frozen", lambda l: f"{f(S4R[f'final/{l}/plandiscrim']['mean_acc'])} / {f(R1[f'final/{l}']['plandiscrim']['mean_acc'])}"),
                    ("accuracy at budget 1.0, signed / frozen", lambda l: f"{f(S4R[f'final/{l}/plandiscrim']['acc_at_1.0'])} / {f(R1[f'final/{l}']['plandiscrim']['curve'][-1])}"),
                    ("always-on accuracy", lambda l: f(R1[f"final/{l}"]["always_on"]["acc"])),
                    ("tool-optimal rate, signed", lambda l: f(S4R[f"final/{l}/plandiscrim"]["tool_optimal_rate"], 3))):
        rows.append([lab] + [fn(l) for l in LV])
    USED.append(("T-first-s4", "out/v3_eval/final/s4_signed.json; out/v3_eval/triggers_final.json", "results.signed_mse_abstain.final/<level>/plandiscrim.{mean_acc,acc_at_1.0,tool_optimal_rate}; results.final/<level>.plandiscrim.curve[-1]; .always_on.acc"))
    return table(["Measure", "Low", "Mid", "High"], rows)


def t_fam1():
    fams = list(R1["final/low"]["plandiscrim"]["by_family"])
    rows = [[fam] + [f"{f(R1[f'final/{l}']['plandiscrim']['by_family'][fam], 3)} / {f(R1[f'final/{l}']['scene_only']['by_family'][fam], 3)} / {f(R1[f'final/{l}']['uncertainty_margin']['by_family'][fam], 3)}" for l in LV] for fam in fams]
    USED.append(("T-fam1", "out/v3_eval/triggers_final.json", "results.final/<level>.<policy>.by_family.<family>"))
    return table(["Family", "Low", "Mid", "High"], rows)


def t_counts():
    m2 = load("out/v2_dataset/manifest.json")["counts"]
    m3 = load("out/v3_final_ds/manifest.json")["counts"]["final"]
    m4 = load("out/v4_final_ds/manifest.json")["counts"]["final"]
    fams = list(m4)
    rows = [[fam, sum(m2[s][fam] for s in ("train", "val", "test")), m3[fam], m4[fam]] for fam in fams]
    rows.append(["total", sum(r[1] for r in rows), sum(r[2] for r in rows), sum(r[3] for r in rows)])
    USED.append(("T-counts", "out/v2_dataset/manifest.json; out/v3_final_ds/manifest.json; out/v4_final_ds/manifest.json", "counts.<split>.<family>, summed over train, val and test for the main dataset"))
    return table(["Family", "Main dataset (seeds 100-399)", "First final (760-859)", "Second final (1060-1159)"], rows)


def t_q1():
    V = load("out/v4_eval/final_vlm.json")
    q = V["hypotheses"]["final"]["Q1"]["cells"]
    rows = [["Q1: signed_vlm minus signed (mean accuracy over budgets)"] + [f"{sg(q[l]['mean_diff'])} {ci(q[l]['ci95'])}" for l in LV],
            ["signed_vlm mean accuracy / mean unsafe"] + [f"{f(V['results'][f'final/{l}']['signed_vlm']['mean_acc'])} / {f(V['results'][f'final/{l}']['signed_vlm']['mean_unsafe'])}" for l in LV],
            ["signed mean accuracy / mean unsafe (same run)"] + [f"{f(V['results'][f'final/{l}']['signed']['mean_acc'])} / {f(V['results'][f'final/{l}']['signed']['mean_unsafe'])}" for l in LV],
            ["at 0.6 calls, signed_vlm acc / unsafe"] + [f"{f(V['results'][f'final/{l}']['signed_vlm']['at_budget_0.6']['acc'])} / {f(V['results'][f'final/{l}']['signed_vlm']['at_budget_0.6']['unsafe'])}" for l in LV]]
    USED.append(("T-q1", "out/v4_eval/final_vlm.json", "hypotheses.final.Q1.cells.<level>.{mean_diff,ci95}; results.final/<level>.{signed_vlm,signed}.{mean_acc,mean_unsafe,at_budget_0.6}"))
    return table(["Measure", "Low", "Mid", "High"], rows)


TABLES = {k[2:]: v for k, v in list(globals().items()) if k.startswith("t_") and callable(v)}


def figures_md(name, cap):
    return f"![{cap}](../figures/{name})\n\n*{cap}*"


def render_tmpl():
    t = open(os.path.join(HERE, "report.tmpl.md")).read()
    t = re.sub(r"\{\{T:(\w+)\}\}", lambda m: TABLES[m.group(1)](), t)
    t = re.sub(r"\{\{FIG:([^|}]+)\|([^}]+)\}\}", lambda m: figures_md(m.group(1).strip(), m.group(2).strip()) if os.path.exists(os.path.join(FIGDIR, m.group(1).strip())) else f"*(figure {m.group(1).strip()} is not available yet)*", t)
    return t


# ---------- minimal markdown to html ----------
def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", lambda m: "<code>" + m.group(1) + "</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![*\w])\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", s)
    s = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)", r'<a href="\2">\1</a>', s)
    return s


def img_tag(alt, src, embed):
    orig = src
    p = os.path.normpath(os.path.join(HERE, src))
    if embed and os.path.exists(p):
        ext = os.path.splitext(p)[1][1:].lower().replace("jpg", "jpeg")
        mime = "svg+xml" if ext == "svg" else ext
        src = f"data:image/{mime};base64," + base64.b64encode(open(p, "rb").read()).decode()
    st = ' style="max-height:96mm;max-width:92%"' if 'f4_' in orig else ''
    return f'<img src="{src}" alt="{html.escape(alt)}"{st}>'


def md_to_html(md, embed=True):
    lines = md.split("\n")
    out, i, para, in_list = [], 0, [], None

    def flush():
        nonlocal para
        if para:
            out.append("<p>" + inline(" ".join(para)) + "</p>")
            para = []

    def close_list():
        nonlocal in_list
        if in_list:
            out.append(f"</{in_list}>")
            in_list = None

    while i < len(lines):
        ln = lines[i]
        if ln.startswith("```"):
            flush(); close_list()
            buf = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                buf.append(lines[i]); i += 1
            out.append("<pre><code>" + html.escape("\n".join(buf)) + "</code></pre>")
        elif ln.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[-| ]+\|$", lines[i + 1]):
            flush(); close_list()
            head = [c.strip() for c in ln.strip().strip("|").split("|")]
            rows = []
            i += 2
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            i -= 1
            out.append("<table><thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead><tbody>" +
                       "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows) + "</tbody></table>")
        elif re.match(r"^#{1,4} ", ln):
            flush(); close_list()
            n = len(ln) - len(ln.lstrip("#"))
            out.append(f"<h{n}>{inline(ln[n + 1:])}</h{n}>")
        elif re.match(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$", ln):
            flush(); close_list()
            m = re.match(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$", ln)
            out.append("<figure>" + img_tag(m.group(1), m.group(2), embed))
            # caption on following non-empty line starting with *
            j = i + 1
            while j < len(lines) and not lines[j].strip():
                j += 1
            if j < len(lines) and lines[j].startswith("*") and lines[j].endswith("*"):
                out.append("<figcaption>" + inline(lines[j].strip("*")) + "</figcaption>")
                i = j
            out.append("</figure>")
        elif re.match(r"^\s*[-*] ", ln) or re.match(r"^\s*\d+\. ", ln):
            flush()
            kind = "ol" if re.match(r"^\s*\d+\. ", ln) else "ul"
            if in_list != kind:
                close_list(); out.append(f"<{kind}>"); in_list = kind
            item = re.sub(r"^\s*([-*]|\d+\.) ", "", ln)
            while i + 1 < len(lines) and lines[i + 1].startswith("  ") and not re.match(r"^\s*([-*]|\d+\.) ", lines[i + 1]) and lines[i + 1].strip():
                i += 1; item += " " + lines[i].strip()
            out.append("<li>" + inline(item) + "</li>")
        elif not ln.strip():
            flush(); close_list()
        else:
            close_list(); para.append(ln.strip())
        i += 1
    flush(); close_list()
    return "\n".join(out)


CSS = """
:root{--fg:#1b1f24;--muted:#555d66;--line:#cfd5db;--bg:#fff;--accent:#1a4f8b;--code:#f3f5f7}
@media (prefers-color-scheme:dark){:root:not([data-print]){--fg:#e6e9ec;--muted:#a3abb3;--line:#3a424a;--bg:#14181c;--accent:#7fb2ea;--code:#1f252b}}
*{box-sizing:border-box}
html{background:var(--bg)}
body{font-family:Body,Georgia,serif;color:var(--fg);background:var(--bg);line-height:1.3;font-size:9pt;max-width:178mm;margin:0 auto;padding:14mm 16px}
h1{font-size:20pt;line-height:1.2;margin:0 0 4pt}
h2{font-size:13pt;margin:13pt 0 4pt;border-bottom:1px solid var(--line);padding-bottom:2pt;color:var(--accent);break-after:avoid}
h3{font-size:11.5pt;margin:12pt 0 3pt;break-after:avoid}
h4{font-size:10.5pt;margin:9pt 0 2pt;break-after:avoid}
p{margin:0 0 5pt;orphans:3;widows:3}
.byline{color:var(--muted);margin:0 0 10pt}
table{border-collapse:collapse;width:100%;margin:6pt 0 9pt;font-family:Body,Arial,sans-serif;font-size:7.4pt;break-inside:avoid}
th,td{border:1px solid var(--line);padding:2pt 4pt;text-align:left;vertical-align:top}
th{background:var(--code)}
code{font-family:Mono,monospace;font-size:7.8pt;background:var(--code);padding:0 2px;border-radius:2px;overflow-wrap:anywhere}
pre{background:var(--code);padding:6pt;border:1px solid var(--line);font-size:7pt;white-space:pre-wrap;overflow-wrap:anywhere;break-inside:avoid}
pre code{background:none;padding:0;font-size:7pt}
figure{margin:8pt 0;break-inside:avoid;text-align:center}
figure img{max-width:78%;max-height:54mm;width:auto;height:auto}
figcaption{font-size:8.5pt;color:var(--muted);text-align:left;margin-top:2pt}
ul,ol{margin:0 0 6pt;padding-left:18pt}
li{margin-bottom:2pt}
.tag-pre{font-weight:bold}
@page{size:A4;margin:11mm 12mm}
@media print{html,body{background:#fff}body{max-width:none;padding:0;color:#000}h2{color:#1a4f8b}.pb{break-before:page}}
"""


RF = "/home/user/.cache/uv/git-v1/checkouts/8626af41d3de3b63/85e5dadc/metadrive/render_pipeline/data/font/"
MF = "/home/user/CASS-VLA/.venv/lib/python3.11/site-packages/matplotlib/mpl-data/fonts/ttf/"


def font_css():
    """Embed fonts so the page renders the same on machines (and headless Chromium) without system fonts."""
    out = []
    for fam, path, w, st in (("Body", RF + "Roboto-Regular.ttf", 400, "normal"), ("Body", RF + "Roboto-Bold.ttf", 700, "normal"),
                             ("Body", RF + "Roboto-Italic.ttf", 400, "italic"), ("Body", RF + "Roboto-BoldItalic.ttf", 700, "italic"),
                             ("Mono", MF + "DejaVuSansMono.ttf", 400, "normal"), ("Mono", MF + "DejaVuSansMono-Bold.ttf", 700, "normal")):
        if os.path.exists(path):
            b = base64.b64encode(open(path, "rb").read()).decode()
            out.append(f"@font-face{{font-family:{fam};font-weight:{w};font-style:{st};src:url(data:font/ttf;base64,{b}) format('truetype')}}")
    return "".join(out)


def build():
    md = render_tmpl()
    open(os.path.join(HERE, "report.md"), "w").write(md)
    body = md_to_html(md, embed=True)
    title = re.search(r"^# (.+)$", md, re.M).group(1)
    doc = f'<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><style>{font_css()}{CSS}</style></head><body>\n{body}\n</body></html>\n'
    doc = doc.replace("<p>@@PB@@</p>", '<div class="pb"></div>')
    open(os.path.join(HERE, "report.html"), "w").write(doc)
    with open(os.path.join(HERE, "SOURCES_TABLES.md"), "w") as fh:
        fh.write("# Generated tables and where their numbers come from\n\nMade by `build.py`. Each table is computed from the file and keys below when the report is built.\n\n")
        fh.write(table(["Table id", "File", "Keys"], [[a, f"`{b}`", c] for a, b, c in USED]) + "\n")
    print("built", len(md.split()), "words")


if __name__ == "__main__":
    build()
