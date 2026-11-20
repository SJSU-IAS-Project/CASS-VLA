"""Shared slide spec and number loading for build_html.py and build_pptx.py.
Coordinates are in a 1920x1080 px space. Every number comes from a file; the src field of each slide feeds SOURCES.md."""
import json, os, re
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
FIGDIR = os.path.join(HERE, '..', 'figures')
G = json.load(open(os.path.join(ROOT, 'out/v4_eval/final_geom.json')))
R = G['results']
H = G['hypotheses']['final']
LV = ['low', 'mid', 'high']
INK, GREY, TEAL, RUST, LINE, PANEL, BG = '14213D', '566274', '0B7A75', 'B4440E', 'D3D9E1', 'EEF2F6', 'FFFFFF'

def f3(x): return f'{x:.3f}'.replace('-', '−')
def f4(x): return f'{x:.4f}'.replace('-', '−')
def sg(x, n=3):
    s = f'{x:+.{n}f}'
    return s.replace('-', '−')
def ci(c, n=3):
    return '[' + ', '.join(f'{v:.{n}f}'.replace('-', '−') for v in c) + ']'

def figpath(name):
    p = os.path.join(FIGDIR, name)
    return p if os.path.exists(p) else None

# ---- element constructors ----
def T(x, y, w, h, paras, size=36, color=INK, bold=False, align='l', fill=None, pad=0, anchor='t', font=None):
    """paras: list of str or dict(t, size, color, bold, bullet, gap). **x** marks bold runs."""
    ps = []
    for p in paras:
        if isinstance(p, str): p = {'t': p}
        ps.append(p)
    return dict(k='text', x=x, y=y, w=w, h=h, paras=ps, size=size, color=color, bold=bold, align=align, fill=fill, pad=pad, anchor=anchor)
def RECT(x, y, w, h, fill=PANEL, line=None):
    return dict(k='rect', x=x, y=y, w=w, h=h, fill=fill, line=line)
def TABLE(x, y, w, cols, rows, size=30, rowh=64, hl=None, firstcol_left=True, hdr_fill=INK, bold_rows=(), colors=None):
    """cols: relative widths; rows[0] is the header. hl: column indexes drawn in teal bold."""
    return dict(k='table', x=x, y=y, w=w, cols=cols, rows=rows, size=size, rowh=rowh, hl=hl or [], hdr_fill=hdr_fill, bold_rows=list(bold_rows), colors=colors or {})
def IMG(x, y, w, h, name):
    return dict(k='img', x=x, y=y, w=w, h=h, name=name, path=figpath(name))

def frame(title, eyebrow=None):
    els = []
    if eyebrow:
        els.append(T(100, 48, 1500, 40, [eyebrow], size=26, color=GREY))
    els.append(T(100, 86, 1720, 120, [title], size=58, bold=True, anchor='t'))
    return els

slides = []
def slide(title, eyebrow, els, src, backup=False, notes=''):
    slides.append(dict(title=title, eyebrow=eyebrow, els=frame(title, eyebrow) + els, src=src, backup=backup, notes=notes))

def bullets(items, size=38, gap=22):
    out = []
    for it in items:
        if isinstance(it, str): it = {'t': it}
        d = dict(size=size, bullet=True, gap=gap); d.update(it); out.append(d)
    return out

def stat(x, y, w, h, label, big, sub, color=TEAL):
    return [RECT(x, y, w, h, PANEL),
            T(x + 36, y + 24, w - 72, 50, [label], size=30, color=GREY, bold=True),
            T(x + 36, y + 84, w - 72, 110, [big], size=88, color=color, bold=True),
            T(x + 36, y + 200, w - 72, h - 210, sub, size=30, color=INK)]
