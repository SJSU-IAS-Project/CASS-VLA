import re
from pptx import Presentation
from pptx.util import Emu, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR, MSO_AUTO_SIZE
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml.ns import qn
from lxml import etree
from common import *
import slides as SL
PX = 6350
FONT = 'Arial'
def rgb(h): return RGBColor.from_string(h)
def pt(px): return Pt(px * 0.46)
prs = Presentation(); prs.slide_width = Emu(1920 * PX); prs.slide_height = Emu(1080 * PX)
blank = prs.slide_layouts[6]
def add_runs(p, text, size, color, bold):
    parts = re.split(r'(\*\*.+?\*\*)', text)
    for part in parts:
        if not part: continue
        b = bold
        if part.startswith('**'): part = part[2:-2]; b = True
        r = p.add_run(); r.text = part; r.font.size = pt(size); r.font.bold = b; r.font.name = FONT; r.font.color.rgb = rgb(color)
def bullet(p, size):
    pPr = p._p.get_or_add_pPr(); ind = int(size * 0.9 * PX)
    pPr.set('marL', str(ind)); pPr.set('indent', str(-ind))
    for tag in ('a:buNone', 'a:buChar', 'a:buClr'):
        for e in pPr.findall(qn(tag)): pPr.remove(e)
    clr = etree.SubElement(pPr, qn('a:buClr')); s = etree.SubElement(clr, qn('a:srgbClr')); s.set('val', TEAL)
    bu = etree.SubElement(pPr, qn('a:buChar')); bu.set('char', '•')
def fill_text(tf, e):
    tf.word_wrap = True
    tf.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
    m = Emu(e['pad'] * PX); tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = m
    tf.vertical_anchor = MSO_ANCHOR.TOP
    first = True
    for pa in e['paras']:
        p = tf.paragraphs[0] if first else tf.add_paragraph(); first = False
        size = pa.get('size', e['size']); color = pa.get('color', e['color']); bold = pa.get('bold', e['bold'])
        add_runs(p, pa['t'], size, color, bold)
        p.space_after = pt(pa.get('gap', 10)); p.line_spacing = 1.05
        p.alignment = PP_ALIGN.CENTER if e['align'] == 'c' else PP_ALIGN.LEFT
        if pa.get('bullet'): bullet(p, size)
def add_slide(s):
    sl = prs.slides.add_slide(blank)
    dark = s['title'] == 'Title'
    bg = sl.background.fill; bg.solid(); bg.fore_color.rgb = rgb(INK if dark else BG)
    for e in s['els']:
        k = e['k']
        if k == 'rect':
            sh = sl.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE if (e['w'] < 1900) else MSO_SHAPE.RECTANGLE, Emu(e['x'] * PX), Emu(e['y'] * PX), Emu(e['w'] * PX), Emu(e['h'] * PX))
            if e['w'] < 1900: sh.adjustments[0] = 0.04
            sh.fill.solid(); sh.fill.fore_color.rgb = rgb(e['fill']); sh.line.fill.background(); sh.shadow.inherit = False
        elif k == 'text':
            if e['fill']:
                sh = sl.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Emu(e['x'] * PX), Emu(e['y'] * PX), Emu(e['w'] * PX), Emu(e['h'] * PX))
                sh.adjustments[0] = 0.06; sh.fill.solid(); sh.fill.fore_color.rgb = rgb(e['fill']); sh.line.fill.background(); sh.shadow.inherit = False
            else:
                sh = sl.shapes.add_textbox(Emu(e['x'] * PX), Emu(e['y'] * PX), Emu(e['w'] * PX), Emu(e['h'] * PX))
            fill_text(sh.text_frame, e)
        elif k == 'img':
            if e['path']:
                from struct import unpack
                d = open(e['path'], 'rb').read(24); iw, ih = unpack('>II', d[16:24])
                sc = min(e['w'] / iw, e['h'] / ih); w = iw * sc; h = ih * sc
                sl.shapes.add_picture(e['path'], Emu(int((e['x'] + (e['w'] - w) / 2) * PX)), Emu(int((e['y'] + (e['h'] - h) / 2) * PX)), Emu(int(w * PX)), Emu(int(h * PX)))
        elif k == 'table':
            rows = e['rows']; nr, nc = len(rows), len(rows[0])
            gf = sl.shapes.add_table(nr, nc, Emu(e['x'] * PX), Emu(e['y'] * PX), Emu(e['w'] * PX), Emu(e['rowh'] * nr * PX))
            tb = gf.table
            tblPr = tb._tbl.tblPr
            for a in ('bandRow', 'firstRow'): tblPr.set(a, '0')
            sid = tblPr.find(qn('a:tableStyleId'))
            if sid is not None: sid.text = '{2D5ABB26-0587-4C30-8999-92F81FD0307C}'
            tot = sum(e['cols'])
            for j, c in enumerate(e['cols']): tb.columns[j].width = Emu(int(e['w'] * c / tot * PX))
            for i, r in enumerate(rows):
                tb.rows[i].height = Emu(e['rowh'] * PX)
                for j, c in enumerate(r):
                    cell = tb.cell(i, j); cell.vertical_anchor = MSO_ANCHOR.MIDDLE
                    cell.margin_left = cell.margin_right = Emu(14 * PX); cell.margin_top = cell.margin_bottom = Emu(6 * PX)
                    tf = cell.text_frame; tf.word_wrap = True; p = tf.paragraphs[0]
                    left = (j == 0 or (len(c) > 18 and not re.match(r'^[+−\-0-9]', c)))
                    p.alignment = PP_ALIGN.LEFT if left else PP_ALIGN.CENTER
                    if i == 0:
                        add_runs(p, c, e['size'], 'FFFFFF', True); cell.fill.solid(); cell.fill.fore_color.rgb = rgb(e['hdr_fill'])
                    else:
                        hl = j in e['hl']; add_runs(p, c, e['size'], TEAL if hl else INK, hl or i in e['bold_rows'])
                        cell.fill.solid(); cell.fill.fore_color.rgb = rgb('FFFFFF' if i % 2 else 'F4F6F9')
    if not dark:
        pass
    if s.get('notes'): sl.notes_slide.notes_text_frame.text = s['notes']
    else: sl.notes_slide.notes_text_frame.text = 'Sources: ' + s['src']
    return sl
mi = bi = 0
for s in SL.slides:
    sl = add_slide(s)
    if s['title'] != 'Title':
        if s['backup']: bi += 1; n = f'B{bi}'
        else: mi += 1; n = str(mi)
        tb = sl.shapes.add_textbox(Emu(1300 * PX), Emu(1020 * PX), Emu(520 * PX), Emu(40 * PX)); tf = tb.text_frame
        p = tf.paragraphs[0]; p.alignment = PP_ALIGN.RIGHT; add_runs(p, f'CMPE 249 · CASS-VLA · {n}', 24, GREY, False)
    else: mi += 1
prs.save('deck.pptx'); print('saved', len(prs.slides.__iter__.__self__._sldIdLst))
