import base64, html, re, os
from common import *
import slides as SL
FD = '/home/user/CASS-VLA/.venv/lib/python3.11/site-packages/metadrive/render_pipeline/data/font/'
def b64(p): return base64.b64encode(open(p, 'rb').read()).decode()
fonts = ''.join(f"@font-face{{font-family:'RobotoE';font-weight:{w};src:url(data:font/ttf;base64,{b64(FD+f)}) format('truetype');}}" for w, f in [(400, 'Roboto-Regular.ttf'), (700, 'Roboto-Bold.ttf')])
def runs(t, base_bold=False):
    t = html.escape(t)
    return re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
def para(p, el):
    size = p.get('size', el['size']); color = p.get('color', el['color']); bold = p.get('bold', el['bold'])
    st = f"font-size:{size}px;color:#{color};font-weight:{700 if bold else 400};margin-bottom:{p.get('gap', 10)}px;"
    cls = 'li' if p.get('bullet') else ''
    return f'<p class="{cls}" style="{st}">{runs(p["t"])}</p>'
def render(e):
    pos = f"left:{e['x']}px;top:{e['y']}px;width:{e['w']}px;"
    k = e['k']
    if k == 'rect':
        return f'<div class="abs" style="{pos}height:{e["h"]}px;background:#{e["fill"]};border-radius:14px;"></div>'
    if k == 'text':
        fill = f"background:#{e['fill']};border-radius:14px;" if e['fill'] else ''
        st = pos + f"height:{e['h']}px;padding:{e['pad']}px;box-sizing:border-box;text-align:{ {'l':'left','c':'center'}[e['align']] };{fill}"
        return f'<div class="abs" style="{st}">' + ''.join(para(p, e) for p in e['paras']) + '</div>'
    if k == 'img':
        if not e['path']: return f'<div class="abs missing" style="{pos}height:{e["h"]}px;">missing {e["name"]}</div>'
        return f'<img class="abs" style="{pos}height:{e["h"]}px;object-fit:contain;" src="data:image/png;base64,{b64(e["path"])}">'
    if k == 'table':
        tot = sum(e['cols']); rows = e['rows']
        h = ''.join(f'<col style="width:{c/tot*100:.2f}%">' for c in e['cols'])
        out = f'<table class="abs" style="{pos}font-size:{e["size"]}px;"><colgroup>{h}</colgroup>'
        for i, r in enumerate(rows):
            out += '<tr style="height:%dpx">' % e['rowh']
            for j, c in enumerate(r):
                al = 'left' if (j == 0 or (len(c) > 18 and not re.match(r'^[+\u2212\-0-9]', c))) else 'center'
                if i == 0:
                    out += f'<th style="background:#{e["hdr_fill"]};text-align:{al}">{runs(c)}</th>'
                else:
                    st = 'font-weight:700;' if (j in e['hl'] or i in e['bold_rows']) else ''
                    if j in e['hl']: st += f'color:#{TEAL};'
                    if j>0 and al=='center': st += 'white-space:nowrap;'
                    out += f'<td style="text-align:{al};{st}">{runs(c)}</td>'
            out += '</tr>'
        return out + '</table>'
def slide_html(i, s):
    dark = s['title'] == 'Title'
    body = ''.join(render(e) for e in s['els'])
    foot = '' if dark else f'<div class="foot">CMPE 249 · CASS-VLA · {"B" if s["backup"] else ""}{i}</div>'
    return f'<section class="slide" id="s{i}" style="background:#{INK if dark else BG}">{body}{foot}</section>'
css = f"""
@page{{size:1920px 1080px;margin:0}}
*{{box-sizing:border-box}} html,body{{margin:0;padding:0;background:#888}}
body{{font-family:'RobotoE',Roboto,Arial,sans-serif;color:#{INK}}}
.slide{{position:relative;width:1920px;height:1080px;overflow:hidden;page-break-after:always;break-after:page;margin:0 auto 20px}}
.abs{{position:absolute}} p{{margin:0;line-height:1.25}}
p.li{{padding-left:1.1em;position:relative}} p.li::before{{content:'';position:absolute;left:.1em;top:.5em;width:.32em;height:.32em;border-radius:50%;background:#{TEAL}}}
table{{border-collapse:collapse}} th,td{{border-bottom:2px solid #{LINE};padding:6px 16px;vertical-align:middle;line-height:1.2}} th{{color:#fff;font-weight:700}}
.foot{{position:absolute;right:100px;bottom:22px;font-size:24px;color:#{GREY}}}
.missing{{background:#fdd;color:#900;font-size:30px}}
@media print{{html,body{{background:none}} .slide{{margin:0}}}}
"""
nums = []; mi = 0; bi = 0
parts = []
for s in SL.slides:
    if s['backup']: bi += 1; n = bi
    else: mi += 1; n = mi
    parts.append(slide_html(n, s))
doc = f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Learned tool selector, CMPE 249</title><style>{fonts}{css}</style></head><body>{"".join(parts)}<script>var h=location.hash.slice(1);if(h){{document.querySelectorAll(".slide").forEach(function(e,i){{if(String(i+1)!==h)e.style.display="none";else e.style.margin=0}})}}</script></body></html>'
open('deck.html', 'w').write(doc)
print(len(SL.slides), 'slides', len(doc)//1024, 'KB')
