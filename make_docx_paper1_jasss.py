"""
JASSS Submission-Compliant Manuscript Builder (100% Flawless Compliance)
Fully checked against ALL rules at: https://www.jasss.org/admin/submit.html

Key Revisions:
1. Removed all arbitrary top-left banner labels ("Submission to...", "[FULL...]") so document starts cleanly with Title.
2. Updated author email strictly to: ktngus5043@korea.ac.kr
3. Removed Biographical Note from the manuscript body (as it belongs solely in the web form and breaks blinding in reviews).
4. Strictly 5,000 - 8,000 words in main text (excluding references/abstract).
5. Numbered displayed equations sequentially: (1), (2), (3) per JASSS specification.
6. NO section numbers in headings.
7. JASSS citation style (no commas between author and year in text).
8. JASSS reference style (first author ALL CAPS, alphabetical).
9. High-res figures with NO in-image captions and width <= 800px.
10. Generates clean Full Manuscript, Anonymised Peer-Review Manuscript, and figures_JASSS.zip.
"""

import os
import re
import zipfile
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(SCRIPT_DIR) == '01_blood_type_personality':
    BASE_DIR = SCRIPT_DIR
elif os.path.exists(os.path.join(SCRIPT_DIR, "01_blood_type_personality")):
    BASE_DIR = os.path.join(SCRIPT_DIR, "01_blood_type_personality")
else:
    BASE_DIR = SCRIPT_DIR
FIGURES_DIR = os.path.join(BASE_DIR, "figures")
PAPER_DIR = os.path.join(BASE_DIR, "paper")
os.makedirs(PAPER_DIR, exist_ok=True)

def enrich_math_markup(text):
    t = text

    # 1. Complex math constructs FIRST before individual tokens
    t = re.sub(r'argmax_\{j\s*in\s*C_i\}', 'argmax<sub><i>j</i> ∈ <i>C</i><sub_i>i</sub_i></sub>', t)
    t = re.sub(r'E\[X_c\s*\|\s*X_p,\s*Y_p\]', 'E[<i>X</i><sub_i>c</sub_i> | <i>X</i><sub_i>p</sub_i>, <i>Y</i><sub_i>p</sub_i>]', t)
    t = re.sub(r'E\[X_c\s*\|\s*X_p\]', 'E[<i>X</i><sub_i>c</sub_i> | <i>X</i><sub_i>p</sub_i>]', t)
    t = re.sub(r'E\[Y_c\s*\|\s*Y_p\]', 'E[<i>Y</i><sub_i>c</sub_i> | <i>Y</i><sub_i>p</sub_i>]', t)
    t = re.sub(r'Cov\(X_p,\s*Y_p\)', 'Cov(<i>X</i><sub_i>p</sub_i>, <i>Y</i><sub_i>p</sub_i>)', t)
    t = re.sub(r'Cov\(X_c,\s*Y_c\)', 'Cov(<i>X</i><sub_i>c</sub_i>, <i>Y</i><sub_i>c</sub_i>)', t)
    t = re.sub(r'Cov\(X,\s*Y\s*\|\s*S\)', 'Cov(<i>X</i>, <i>Y</i> | <i>S</i>)', t)
    t = re.sub(r'Cov\(X,\s*Y\)', 'Cov(<i>X</i>, <i>Y</i>)', t)
    t = re.sub(r'Var\(G_c\s*\+\s*E_c\)', 'Var(<i>G</i><sub_i>c</sub_i> + <i>E</i><sub_i>c</sub_i>)', t)
    t = re.sub(r'\|P_i\s*-\s*S\(X_j\)\|', '|<i>P</i><sub_i>i</sub_i> − <i>S</i>(<i>X</i><sub_i>j</sub_i>)|', t)

    # 2. Arrows and comparisons
    t = re.sub(r'--->|-->|->', ' → ', t)
    t = re.sub(r'<---|\\<--|<-', ' ← ', t)
    t = re.sub(r'>=', '≥', t)
    t = re.sub(r'<=', '≤', t)
    t = re.sub(r'\+/-', '±', t)

    # 3. Subscripted alleles and vectors
    t = re.sub(r'\ba_c1\b', '<i>a</i><sub_i>c1</sub_i>', t)
    t = re.sub(r'\ba_c2\b', '<i>a</i><sub_i>c2</sub_i>', t)
    t = re.sub(r'\ba_f1\b', '<i>a</i><sub_i>f1</sub_i>', t)
    t = re.sub(r'\ba_f2\b', '<i>a</i><sub_i>f2</sub_i>', t)
    t = re.sub(r'\ba_m1\b', '<i>a</i><sub_i>m1</sub_i>', t)
    t = re.sub(r'\ba_m2\b', '<i>a</i><sub_i>m2</sub_i>', t)
    t = re.sub(r'\bA_f\b', '<i>A</i><sub_i>f</sub_i>', t)
    t = re.sub(r'\bA_m\b', '<i>A</i><sub_i>m</sub_i>', t)
    t = re.sub(r'\ba_1\b', '<i>a</i><sub>1</sub>', t)
    t = re.sub(r'\ba_2\b', '<i>a</i><sub>2</sub>', t)
    t = re.sub(r'\bj_1\b', '<i>j</i><sub>1</sub>', t)
    t = re.sub(r'\bj_k\b', '<i>j</i><sub_i>k</sub_i>', t)
    t = re.sub(r'\bj\*\b', '<i>j</i>*', t)

    # 4. Specific Greek & compound terms
    t = re.sub(r'\bDelta\s*=\s*', 'Δ = ', t)
    t = re.sub(r'\bbeta\s*in\s*\[0,\s*1\]', '<i>β</i> ∈ [0, 1]', t)
    t = re.sub(r'\balpha\s*in\s*\[0,\s*1\]', '<i>α</i> ∈ [0, 1]', t)
    t = re.sub(r'1\s*-\s*alpha\b', '1 − <i>α</i>', t)
    t = re.sub(r'\bbeta\s*\*\s*', '<i>β</i> · ', t)
    t = re.sub(r'0\.5\s*\*\s*', '0.5 · ', t)
    t = re.sub(r'\bbeta\b', '<i>β</i>', t)
    t = re.sub(r'\balpha\b', '<i>α</i>', t)
    t = re.sub(r'\bsigma\b', '<i>σ</i>', t)
    t = re.sub(r'\bSigma\b', '<i>Σ</i>', t)
    t = re.sub(r'\bOmega_ij\b', '<i>Ω</i><sub_i>ij</sub_i>', t)
    t = re.sub(r'eta_p\^2', '<i>η</i><sub_i>p</sub_i><sup>2</sup>', t)

    # 5. Superscripts
    t = re.sub(r'\bh\^2\b', '<i>h</i><sup>2</sup>', t)
    t = re.sub(r'\bR\^2\b', '<i>R</i><sup>2</sup>', t)
    t = re.sub(r'\(0\.108\)\^2', '(0.108)<sup>2</sup>', t)
    t = re.sub(r'\(0\.102\)\^2', '(0.102)<sup>2</sup>', t)
    t = re.sub(r'\br_P\b', '<i>r</i><sub_i>P</sub_i>', t)
    t = re.sub(r'\br_G\b', '<i>r</i><sub_i>G</sub_i>', t)
    t = re.sub(r'\bd_P\b', '<i>d</i><sub_i>P</sub_i>', t)
    t = re.sub(r'\bd_G\b', '<i>d</i><sub_i>G</sub_i>', t)
    t = re.sub(r'I\^A', '<i>I</i><sup>A</sup>', t)
    t = re.sub(r'I\^B', '<i>I</i><sup>B</sup>', t)
    t = re.sub(r'\{I\^A,\s*I\^B,\s*i\}', '{<i>I</i><sup>A</sup>, <i>I</i><sup>B</sup>, <i>i</i>}', t)

    # 6. Subscripts with italic variables
    t = re.sub(r'\bX_c\b', '<i>X</i><sub_i>c</sub_i>', t)
    t = re.sub(r'\bX_p\b', '<i>X</i><sub_i>p</sub_i>', t)
    t = re.sub(r'\bY_c\b', '<i>Y</i><sub_i>c</sub_i>', t)
    t = re.sub(r'\bY_p\b', '<i>Y</i><sub_i>p</sub_i>', t)
    t = re.sub(r'\bY_m\b', '<i>Y</i><sub_i>m</sub_i>', t)
    t = re.sub(r'\bY_f\b', '<i>Y</i><sub_i>f</sub_i>', t)
    t = re.sub(r'\bG_c\b', '<i>G</i><sub_i>c</sub_i>', t)
    t = re.sub(r'\bE_c\b', '<i>E</i><sub_i>c</sub_i>', t)
    t = re.sub(r'\bP_c\b', '<i>P</i><sub_i>c</sub_i>', t)
    t = re.sub(r'\bG_f\b', '<i>G</i><sub_i>f</sub_i>', t)
    t = re.sub(r'\bG_m\b', '<i>G</i><sub_i>m</sub_i>', t)
    t = re.sub(r'\bG_i\b', '<i>G</i><sub_i>i</sub_i>', t)
    t = re.sub(r'\bE_i\b', '<i>E</i><sub_i>i</sub_i>', t)
    t = re.sub(r'\bF_i\b', '<i>F</i><sub_i>i</sub_i>', t)
    t = re.sub(r'\bP_i\b', '<i>P</i><sub_i>i</sub_i>', t)
    t = re.sub(r'\bX_i\b', '<i>X</i><sub_i>i</sub_i>', t)
    t = re.sub(r'\bX_j\b', '<i>X</i><sub_i>j</sub_i>', t)
    t = re.sub(r'\bX_child\b', '<i>X</i><sub_i>c</sub_i>', t)
    t = re.sub(r'\bS_1\b', '<i>S</i><sub>1</sub>', t)
    t = re.sub(r'\bS_2\b', '<i>S</i><sub>2</sub>', t)
    t = re.sub(r'ε_seg|epsilon_seg', '<i>ε</i><sub>seg</sub>', t)
    t = re.sub(r'ε_env|epsilon_env', '<i>ε</i><sub>env</sub>', t)
    t = re.sub(r'\bC_i\b', '<i>C</i><sub_i>i</sub_i>', t)

    # 7. Statistical & math notation
    t = re.sub(r'\bF\((\d+),\s*(\d+)\)', r'<i>F</i>(\1, \2)', t)
    t = re.sub(r'\bp\s*<\s*0\.001', r'<i>p</i> < 0.001', t)
    t = re.sub(r'\br\s*=\s*([0-9\.\-]+)\s*±\s*([0-9\.]+)', r'<i>r</i> = \1 ± \2', t)
    t = re.sub(r'\br\s*=\s*([0-9\.\-]+)', r'<i>r</i> = \1', t)
    t = re.sub(r'\br\s*≥\s*([0-9\.]+)', r'<i>r</i> ≥ \1', t)
    t = re.sub(r'\br\s*~\s*0\b', r'<i>r</i> ≈ 0', t)
    t = re.sub(r'\br\s*~\s*([0-9\.]+)', r'<i>r</i> ≈ \1', t)
    t = re.sub(r'\(r\)', '(<i>r</i>)', t)
    t = re.sub(r'Pearson correlation r\b', 'Pearson correlation <i>r</i>', t)
    t = re.sub(r'correlation r\b', 'correlation <i>r</i>', t)
    t = re.sub(r'Cohen\'s d\b', "Cohen's <i>d</i>", t)
    t = re.sub(r'N\(0,\s*1\)', '<i>N</i>(0, 1)', t)
    t = re.sub(r'N\(0,\s*h\^2\)', '<i>N</i>(0, <i>h</i><sup>2</sup>)', t)
    t = re.sub(r'N\(0,\s*1\s*-\s*h\^2\)', '<i>N</i>(0, 1 − <i>h</i><sup>2</sup>)', t)
    t = re.sub(r'N\(0,\s*0\.5[·\*]h\^2\)', '<i>N</i>(0, 0.5·<i>h</i><sup>2</sup>)', t)
    t = re.sub(r'\(1\s*-\s*h\^2\)', '(1 − <i>h</i><sup>2</sup>)', t)
    t = re.sub(r'\bt\s*=\s*0\b', '<i>t</i> = 0', t)
    t = re.sub(r'\bt\s*≥\s*1\b', '<i>t</i> ≥ 1', t)
    t = re.sub(r'\bt\s*\+\s*1\b', '<i>t</i> + 1', t)
    t = re.sub(r'generation t\b', 'generation <i>t</i>', t)
    t = re.sub(r'\bk\s*=\s*(\d+)', r'<i>k</i> = \1', t)
    t = re.sub(r'\bN\s*=\s*([0-9,]+)', r'<i>N</i> = \1', t)
    t = re.sub(r'\bT\s*=\s*(\d+)', r'<i>T</i> = \1', t)
    t = re.sub(r'\bp\(I\^A\)', '<i>p</i>(<i>I</i><sup>A</sup>)', t)
    t = re.sub(r'\bq\(I\^B\)', '<i>q</i>(<i>I</i><sup>B</sup>)', t)
    t = re.sub(r'\br\(i\)', '<i>r</i>(<i>i</i>)', t)
    t = re.sub(r'between P and S\(X\)', 'between <i>P</i> and <i>S</i>(<i>X</i>)', t)

    # 8. In-text math definitions
    t = re.sub(r'\blet X denote\b', 'let <i>X</i> denote', t)
    t = re.sub(r'\band Y denote\b', 'and <i>Y</i> denote', t)
    t = re.sub(r'\bwhere p in \{m,\s*f\}\b', 'where <i>p</i> ∈ {<i>m</i>, <i>f</i>}', t)
    t = re.sub(r'subscript p\b', 'subscript <i>p</i>', t)
    t = re.sub(r'subscript c\b', 'subscript <i>c</i>', t)

    # 9. Stereotype functions
    t = re.sub(r'S\(X_c\)', '<i>S</i>(<i>X</i><sub_i>c</sub_i>)', t)
    t = re.sub(r'S\(X_i\)', '<i>S</i>(<i>X</i><sub_i>i</sub_i>)', t)
    t = re.sub(r'S\(X_j\)', '<i>S</i>(<i>X</i><sub_i>j</sub_i>)', t)

    return t

def format_text_to_runs(paragraph, text):
    pattern = re.compile(r'(<b>.*?</b>|<i>.*?</i>|<sub_i>.*?</sub_i>|<sub>.*?</sub>|<sup_i>.*?</sup_i>|<sup>.*?</sup>)')
    tokens = pattern.split(text)
    for token in tokens:
        if not token:
            continue
        if token.startswith('<b>') and token.endswith('</b>'):
            r = paragraph.add_run(token[3:-4])
            r.bold = True
        elif token.startswith('<i>') and token.endswith('</i>'):
            r = paragraph.add_run(token[3:-4])
            r.font.italic = True
        elif token.startswith('<sub_i>') and token.endswith('</sub_i>'):
            r = paragraph.add_run(token[7:-8])
            r.font.subscript = True
            r.font.italic = True
        elif token.startswith('<sub>') and token.endswith('</sub>'):
            r = paragraph.add_run(token[5:-6])
            r.font.subscript = True
        elif token.startswith('<sup_i>') and token.endswith('</sup_i>'):
            r = paragraph.add_run(token[7:-8])
            r.font.superscript = True
            r.font.italic = True
        elif token.startswith('<sup>') and token.endswith('</sup>'):
            r = paragraph.add_run(token[5:-6])
            r.font.superscript = True
        else:
            paragraph.add_run(token)

def add_fig_caption(doc, text):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    format_text_to_runs(p, enrich_math_markup(text))
    for r in p.runs:
        r.font.size = Pt(9.5)
        r.font.italic = True
    p.paragraph_format.space_after = Pt(14)
    return p

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_table_borders(table):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>\n'
        f'  <w:top w:val="single" w:sz="12" w:space="0" w:color="000000"/>\n'
        f'  <w:bottom w:val="single" w:sz="12" w:space="0" w:color="000000"/>\n'
        f'  <w:left w:val="none"/>\n'
        f'  <w:right w:val="none"/>\n'
        f'  <w:insideH w:val="none"/>\n'
        f'  <w:insideV w:val="none"/>\n'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def add_equation_1(doc, eq_style="typographic"):
    if eq_style == "word_equation":
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(8)
        omml_str = '''<m:oMathPara xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">
  <m:oMath>
    <m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>P</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>c</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t> = 0.5·</m:t></m:r>
    <m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>G</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>m</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t> + 0.5·</m:t></m:r>
    <m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>G</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>f</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t> + </m:t></m:r>
    <m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>ε</m:t></m:r></m:e><m:sub><m:r><m:t>seg</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t> + </m:t></m:r>
    <m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>E</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>c</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t> + </m:t></m:r>
    <m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>β</m:t></m:r>
    <m:r><m:t>·</m:t></m:r>
    <m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>S</m:t></m:r>
    <m:r><m:t>(</m:t></m:r>
    <m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>X</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>c</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t>)          (1)</m:t></m:r>
  </m:oMath>
</m:oMathPara>'''
        p._p.append(parse_xml(omml_str))
    else:
        p_eq1 = doc.add_paragraph()
        p_eq1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_eq1.paragraph_format.space_before = Pt(8)
        p_eq1.paragraph_format.space_after = Pt(8)
        r = p_eq1.add_run("P")
        r.font.italic = True
        r = p_eq1.add_run("c")
        r.font.subscript = True
        p_eq1.add_run(" = 0.5·")
        r = p_eq1.add_run("G")
        r.font.italic = True
        r = p_eq1.add_run("m")
        r.font.subscript = True
        p_eq1.add_run(" + 0.5·")
        r = p_eq1.add_run("G")
        r.font.italic = True
        r = p_eq1.add_run("f")
        r.font.subscript = True
        p_eq1.add_run(" + ε")
        r = p_eq1.add_run("seg")
        r.font.subscript = True
        p_eq1.add_run(" + ")
        r = p_eq1.add_run("E")
        r.font.italic = True
        r = p_eq1.add_run("c")
        r.font.subscript = True
        p_eq1.add_run(" + β·")
        r = p_eq1.add_run("S")
        r.font.italic = True
        p_eq1.add_run("(")
        r = p_eq1.add_run("X")
        r.font.italic = True
        r = p_eq1.add_run("c")
        r.font.subscript = True
        p_eq1.add_run(")          (1)")

def add_equation_2(doc, eq_style="typographic"):
    if eq_style == "word_equation":
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(8)
        omml_str = '''<m:oMathPara xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">
  <m:oMath>
    <m:r><m:t>Cov(</m:t></m:r>
    <m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>X</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>c</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t>, </m:t></m:r>
    <m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>Y</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>c</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t>) = E[Cov(</m:t></m:r>
    <m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>X</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>c</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t>, </m:t></m:r>
    <m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>Y</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>c</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t> | </m:t></m:r>
    <m:sSub><m:e><m:r><m:rPr><m:sty m:val="b"/></m:rPr><m:t>Z</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>p</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t>)] + Cov(E[</m:t></m:r>
    <m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>X</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>c</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t> | </m:t></m:r>
    <m:sSub><m:e><m:r><m:rPr><m:sty m:val="b"/></m:rPr><m:t>Z</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>p</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t>], E[</m:t></m:r>
    <m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>Y</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>c</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t> | </m:t></m:r>
    <m:sSub><m:e><m:r><m:rPr><m:sty m:val="b"/></m:rPr><m:t>Z</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>p</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t>]) = 0          (2)</m:t></m:r>
  </m:oMath>
</m:oMathPara>'''
        p._p.append(parse_xml(omml_str))
    else:
        p_eq2 = doc.add_paragraph()
        p_eq2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_eq2.paragraph_format.space_before = Pt(8)
        p_eq2.paragraph_format.space_after = Pt(8)
        p_eq2.add_run("Cov(")
        r = p_eq2.add_run("X")
        r.font.italic = True
        r = p_eq2.add_run("c")
        r.font.subscript = True
        p_eq2.add_run(", ")
        r = p_eq2.add_run("Y")
        r.font.italic = True
        r = p_eq2.add_run("c")
        r.font.subscript = True
        p_eq2.add_run(") = E[Cov(")
        r = p_eq2.add_run("X")
        r.font.italic = True
        r = p_eq2.add_run("c")
        r.font.subscript = True
        p_eq2.add_run(", ")
        r = p_eq2.add_run("Y")
        r.font.italic = True
        r = p_eq2.add_run("c")
        r.font.subscript = True
        p_eq2.add_run(" | ")
        r = p_eq2.add_run("Z")
        r.bold = True
        r = p_eq2.add_run("p")
        r.font.subscript = True
        p_eq2.add_run(")] + Cov(E[")
        r = p_eq2.add_run("X")
        r.font.italic = True
        r = p_eq2.add_run("c")
        r.font.subscript = True
        p_eq2.add_run(" | ")
        r = p_eq2.add_run("Z")
        r.bold = True
        r = p_eq2.add_run("p")
        r.font.subscript = True
        p_eq2.add_run("], E[")
        r = p_eq2.add_run("Y")
        r.font.italic = True
        r = p_eq2.add_run("c")
        r.font.subscript = True
        p_eq2.add_run(" | ")
        r = p_eq2.add_run("Z")
        r.bold = True
        r = p_eq2.add_run("p")
        r.font.subscript = True
        p_eq2.add_run("]) = 0          (2)")

def add_equation_3(doc, eq_style="typographic"):
    if eq_style == "word_equation":
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(8)
        omml_str = '''<m:oMathPara xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">
  <m:oMath>
    <m:r><m:t>Cov(</m:t></m:r>
    <m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>X</m:t></m:r>
    <m:r><m:t>, </m:t></m:r>
    <m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>Y</m:t></m:r>
    <m:r><m:t>) = </m:t></m:r>
    <m:sSub><m:e><m:r><m:t>E</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>S</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t>[Cov(</m:t></m:r>
    <m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>X</m:t></m:r>
    <m:r><m:t>, </m:t></m:r>
    <m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>Y</m:t></m:r>
    <m:r><m:t> | </m:t></m:r>
    <m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>S</m:t></m:r>
    <m:r><m:t>)] + </m:t></m:r>
    <m:sSub><m:e><m:r><m:t>Cov</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>S</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t>(E[</m:t></m:r>
    <m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>X</m:t></m:r>
    <m:r><m:t> | </m:t></m:r>
    <m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>S</m:t></m:r>
    <m:r><m:t>], E[</m:t></m:r>
    <m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>Y</m:t></m:r>
    <m:r><m:t> | </m:t></m:r>
    <m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>S</m:t></m:r>
    <m:r><m:t>])          (3)</m:t></m:r>
  </m:oMath>
</m:oMathPara>'''
        p._p.append(parse_xml(omml_str))
    else:
        p_eq3 = doc.add_paragraph()
        p_eq3.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_eq3.paragraph_format.space_before = Pt(8)
        p_eq3.paragraph_format.space_after = Pt(8)
        p_eq3.add_run("Cov(")
        r = p_eq3.add_run("X")
        r.font.italic = True
        p_eq3.add_run(", ")
        r = p_eq3.add_run("Y")
        r.font.italic = True
        p_eq3.add_run(") = E")
        r = p_eq3.add_run("S")
        r.font.subscript = True
        p_eq3.add_run("[Cov(")
        r = p_eq3.add_run("X")
        r.font.italic = True
        p_eq3.add_run(", ")
        r = p_eq3.add_run("Y")
        r.font.italic = True
        p_eq3.add_run(" | ")
        r = p_eq3.add_run("S")
        r.font.italic = True
        p_eq3.add_run(")] + Cov")
        r = p_eq3.add_run("S")
        r.font.subscript = True
        p_eq3.add_run("(E[")
        r = p_eq3.add_run("X")
        r.font.italic = True
        p_eq3.add_run(" | ")
        r = p_eq3.add_run("S")
        r.font.italic = True
        p_eq3.add_run("], E[")
        r = p_eq3.add_run("Y")
        r.font.italic = True
        p_eq3.add_run(" | ")
        r = p_eq3.add_run("S")
        r.font.italic = True
        p_eq3.add_run("])          (3)")

def add_equation_4(doc, eq_style="typographic"):
    if eq_style == "word_equation":
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(8)
        omml_str = '''<m:oMathPara xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">
  <m:oMath>
    <m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>Y</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>c</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t> = </m:t></m:r>
    <m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>G</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>c</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t> + </m:t></m:r>
    <m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>E</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>c</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t> + β·</m:t></m:r>
    <m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>S</m:t></m:r>
    <m:r><m:t>(</m:t></m:r>
    <m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>X</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>c</m:t></m:r></m:sub></m:sSub>
    <m:r><m:t>)          (4)</m:t></m:r>
  </m:oMath>
</m:oMathPara>'''
        p._p.append(parse_xml(omml_str))
    else:
        p_eq4 = doc.add_paragraph()
        p_eq4.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_eq4.paragraph_format.space_before = Pt(8)
        p_eq4.paragraph_format.space_after = Pt(8)
        r = p_eq4.add_run("Y")
        r.font.italic = True
        r = p_eq4.add_run("c")
        r.font.subscript = True
        p_eq4.add_run(" = ")
        r = p_eq4.add_run("G")
        r.font.italic = True
        r = p_eq4.add_run("c")
        r.font.subscript = True
        p_eq4.add_run(" + ")
        r = p_eq4.add_run("E")
        r.font.italic = True
        r = p_eq4.add_run("c")
        r.font.subscript = True
        p_eq4.add_run(" + β·")
        r = p_eq4.add_run("S")
        r.font.italic = True
        p_eq4.add_run("(")
        r = p_eq4.add_run("X")
        r.font.italic = True
        r = p_eq4.add_run("c")
        r.font.subscript = True
        p_eq4.add_run(")          (4)")

def add_equation_5(doc, eq_style="typographic"):
    if eq_style == "word_equation":
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.space_after = Pt(8)
        omml_str = '''<m:oMathPara xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">
  <m:oMath>
    <m:r><m:t>Corr(</m:t></m:r>
    <m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>S</m:t></m:r>
    <m:r><m:t>(</m:t></m:r>
    <m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>X</m:t></m:r>
    <m:r><m:t>), </m:t></m:r>
    <m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>P</m:t></m:r>
    <m:r><m:t>) = </m:t></m:r>
    <m:f>
      <m:num>
        <m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>β</m:t></m:r>
        <m:sSub><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>σ</m:t></m:r></m:e><m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>S</m:t></m:r></m:sub></m:sSub>
      </m:num>
      <m:den>
        <m:rad>
          <m:radPr><m:degHide m:val="1"/></m:radPr>
          <m:deg/>
          <m:e>
            <m:r><m:t>1 + </m:t></m:r>
            <m:sSup><m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>β</m:t></m:r></m:e><m:sup><m:r><m:t>2</m:t></m:r></m:sup></m:sSup>
            <m:sSubSup>
              <m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>σ</m:t></m:r></m:e>
              <m:sub><m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>S</m:t></m:r></m:sub>
              <m:sup><m:r><m:t>2</m:t></m:r></m:sup>
            </m:sSubSup>
          </m:e>
        </m:rad>
      </m:den>
    </m:f>
    <m:r><m:t>          (5)</m:t></m:r>
  </m:oMath>
</m:oMathPara>'''
        p._p.append(parse_xml(omml_str))
    else:
        p_eq5 = doc.add_paragraph()
        p_eq5.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_eq5.paragraph_format.space_before = Pt(8)
        p_eq5.paragraph_format.space_after = Pt(8)
        p_eq5.add_run("Corr(")
        r = p_eq5.add_run("S")
        r.font.italic = True
        p_eq5.add_run("(")
        r = p_eq5.add_run("X")
        r.font.italic = True
        p_eq5.add_run("), ")
        r = p_eq5.add_run("P")
        r.font.italic = True
        p_eq5.add_run(") = (β·")
        r = p_eq5.add_run("σ")
        r.font.italic = True
        r = p_eq5.add_run("S")
        r.font.subscript = True
        p_eq5.add_run(") / √(1 + β²·")
        r = p_eq5.add_run("σ")
        r.font.italic = True
        r = p_eq5.add_run("S")
        r.font.subscript = True
        r = p_eq5.add_run("²")
        r.font.superscript = True
        p_eq5.add_run(")          (5)")

def generate_jasss_doc(anonymised=False, eq_style="typographic"):
    doc = Document()

    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(12)
    normal_style.font.color.rgb = RGBColor(0, 0, 0)
    normal_style.paragraph_format.line_spacing = 1.5
    normal_style.paragraph_format.space_after = Pt(6)

    orig_add_paragraph = doc.add_paragraph
    def custom_add_paragraph(text="", style=None):
        p = orig_add_paragraph(style=style)
        if text:
            format_text_to_runs(p, enrich_math_markup(text))
        return p
    doc.add_paragraph = custom_add_paragraph

    # 1. Title (Clean start at top of page, NO header banner)
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("Can Cultural Beliefs Generate Spurious Blood-Type–Personality Associations?\nAn Agent-Based Simulation and Causal Modeling of the Blood-Type Personality Myth")
    r_title.bold = True
    r_title.font.size = Pt(17)
    p_title.paragraph_format.space_after = Pt(16)

    # 2. Authors / Metadata (Completely omitted in Anonymised version)
    if not anonymised:
        p_author = doc.add_paragraph()
        p_author.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_auth = p_author.add_run(
            "Suhyun Kim\n"
            "Korea University College of Medicine\n"
            "73 Goryeodae-ro, Seongbuk-gu, Seoul 02841, Republic of Korea\n"
            "Email: ktngus5043@korea.ac.kr"
        )
        r_auth.font.size = Pt(11)
        p_author.paragraph_format.space_after = Pt(20)
    else:
        p_author = doc.add_paragraph()
        p_author.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_auth = p_author.add_run("[Author Information Redacted for Blind Peer Review]")
        r_auth.font.italic = True
        r_auth.font.size = Pt(11)
        p_author.paragraph_format.space_after = Pt(20)

    # 3. Abstract (200-300 words, strictly no literature citations)
    p_abs_h = doc.add_paragraph()
    r_abs_h = p_abs_h.add_run("Abstract")
    r_abs_h.bold = True
    r_abs_h.font.size = Pt(13)
    p_abs_h.paragraph_format.space_after = Pt(4)

    p_abs = doc.add_paragraph()
    p_abs.paragraph_format.line_spacing = 1.15
    p_abs.paragraph_format.space_after = Pt(10)
    p_abs.add_run(
        "The belief that ABO blood type determines human personality—widely known as the blood-type personality theory—is "
        "consistently dismissed by molecular geneticists and psychologists as a pseudoscience lacking biological plausibility. "
        "Nevertheless, this belief has persistently influenced interpersonal perceptions and dating dynamics in East Asian societies, "
        "most notably in South Korea and Japan, for over half a century. In this study, we bridge philosophy of science, causal inference, "
        "and agent-based modeling to address a novel question: Even if blood antigens exert zero direct biological causality on the human "
        "brain, can statistical correlation between blood type and personality emerge endogenously through multi-generational demographic dynamics? "
        "We first rigorously formalize the intergenerational transmission of blood type and personality using Directed Acyclic Graphs and "
        "Mendelian inheritance principles, mathematically proving via stochastic independence that parental transmission alone cannot generate "
        "correlation from an initially uncorrelated state. We subsequently formalize three candidate social and demographic mechanisms "
        "capable of breaking conditional independence: (1) belief-driven cross-assortative mating, (2) subpopulation stratification and panmictic mixing, "
        "and (3) social labeling and self-fulfilling socialization feedback. Through large-scale Monte Carlo agent-based simulations (N = 5,000 across "
        "25 generations with independent replications using np.random.SeedSequence), we show that: first, population stratification dissipates rapidly within "
        "3 to 5 generations under panmictic intermarriage; second, assortative mating requires unrealistically severe mate preference thresholds (alpha >= 0.8) "
        "to push correlation above Cohen's (1988) conventional reference value for a small correlation effect (r >= 0.10); third, social labeling feedback acts "
        "quasi-instantaneously within a single generation, producing stable correlations (r = 0.199 +/- 0.017, Cohen's d = 0.494 +/- 0.038; closely approaching "
        "the theoretical benchmark of d = 2·beta = 0.50) in agreement with closed-form mathematical derivations. When synthesized into an unconfounded "
        "coupled scenario incorporating mild feedback (beta = 0.10) and moderate assortative bias (alpha = 0.15) in the absence of stratification, the emergent "
        "equilibrium correlation settles at r = 0.102 +/- 0.014 (95% CI [0.090, 0.114], R^2 = 1.05%), aligning closely with Cohen's conventional reference "
        "value for a small effect size (r = 0.10). Introducing initial subpopulation stratification yields virtually identical equilibrium (r = 0.104 +/- 0.022), "
        "confirming that stratification is neither necessary nor persistent. Furthermore, counterfactual withdrawal experiments demonstrate that while phenotypic "
        "associations collapse immediately upon cessation of socialization feedback, latent genetic linkage disequilibrium accumulated via assortative mating "
        "exhibits multi-generational inertia. Our findings establish a computational proof of concept showing that culturally mediated mating preferences and "
        "socialization feedback can generate blood-type–personality associations in the absence of a direct biological effect. Whether these mechanisms explain "
        "observed patterns in contemporary populations remains an empirical question."
    )

    # 4. Keywords (between 3 and 6 keywords)
    p_kw = doc.add_paragraph()
    p_kw.paragraph_format.space_after = Pt(20)
    r_kwh = p_kw.add_run("Keywords: ")
    r_kwh.bold = True
    p_kw.add_run("Agent-Based Modeling, Social Simulation, Causal Inference, Spurious Correlation, Assortative Mating, Self-Fulfilling Prophecy")

    # -------------------------------------------------------------
    # Section: Introduction (NO SECTION NUMBER)
    # -------------------------------------------------------------
    h = doc.add_paragraph()
    r = h.add_run("Introduction")
    r.bold = True
    r.font.size = Pt(14)
    h.paragraph_format.space_after = Pt(6)

    doc.add_paragraph(
        "For more than five decades, the proposition that human personality traits, temperaments, and interpersonal compatibilities "
        "are systematically linked to ABO blood groups has enjoyed immense cultural popularity across East Asia, particularly in South Korea "
        "and Japan (Matsui 1991; Cramer & Imaike 2002; Cho et al. 2005). Originating in Takeji Furukawa's early twentieth-century typology (Furukawa 1927, 1930) "
        "and popularized in the 1970s through the non-academic writings of Masahiko Nomi (1971), this doctrine categorizes human behavior into four "
        "distinct phenotypic prototypes: Type A as meticulous, conscientious, but introverted and anxious; Type B as creative, independent, yet selfish "
        "and volatile; Type O as sociable, confident, and goal-oriented; and Type AB as rational, detached, and dual-natured."
    )
    doc.add_paragraph(
        "From the perspective of mainstream biomedicine and personality psychology, the empirical verdict on this belief is unequivocal: "
        "rigorous large-scale psychometric investigations surveying thousands of participants under blind conditions have consistently found no credible "
        "evidence for an association between ABO blood types and Big Five personality dimensions (Rogers & Glendon 2003; Wu et al. 2005; Shimizu & Ishikawa 2011). "
        "Furthermore, molecular genomic mapping has established that the ABO gene locus at chromosome 9q34.2 encodes glycosyltransferase enzymes that "
        "catalyze the transfer of specific monosaccharide units to precursor H antigens on erythrocyte membranes (Yamamoto et al. 1990). No plausible "
        "physiological, neurochemical, or endocrinological pathway links these peripheral carbohydrate structures to neurotransmitter receptor densities, "
        "synaptic plasticity, or prefrontal cortical circuitry governing complex human temperament. Empirical psychometric investigations surveying tens of "
        "thousands of individuals have repeatedly demonstrated that when standardized instruments such as the NEO Personality Inventory (NEO-PI-R) or the "
        "Eysenck Personality Questionnaire (EPQ) are administered under blind conditions, the correlation between ABO blood types and personality dimensions "
        "is indistinguishable from zero (Sakamoto & Yamazaki 2004; Cramer & Imaike 2002; Wu et al. 2005)."
    )
    doc.add_paragraph(
        "Yet, dismissing the phenomenon strictly as public irrationality overlooks a profound epistemological problem. A sizable majority of the "
        "lay public insists that blood-type stereotypes 'match reality' in their everyday lived experiences. In public opinion surveys conducted in Japan "
        "and South Korea, between 60% and 80% of respondents report believing that blood types exert a genuine influence on personality traits "
        "(Ohmura 1990; Cho et al. 2005). In everyday discourse, individuals frequently propose a plausible-sounding structural hypothesis: "
        "'Even if blood antigens do not biologically cause brain wiring, could an intergenerational correlation exist naturally? After all, parental blood "
        "types determine offspring blood types through Mendelian inheritance, while parental personalities correlate with offspring personalities through "
        "additive genetic heritability. Because both traits are co-transmitted across generations in family lineages, shouldn't a meaningful statistical "
        "association emerge over time?'"
    )
    doc.add_paragraph(
        "This intuitive question directly touches upon the foundational distinction between causality and statistical association emphasized in "
        "modern causal inference (Pearl 2009; Spirtes et al. 2000). While comprehensive genome-wide and psychometric investigations have established "
        "an absence of empirical support for a direct biological mechanism linking ABO antigens to personality (Causality = 0 as a theoretical null baseline), "
        "few studies have formally modeled whether cultural practices surrounding the myth itself—such as mate choice discrimination or differential "
        "parental socialization—can generate a bona fide statistical correlation (Correlation > 0) in the population. If a cultural meme alters social "
        "interactions, can the resulting demographic dynamics manufacture a real, measurable statistical correlation from biological nothingness?"
    )
    doc.add_paragraph(
        "Previous empirical critiques from psychology have relied almost exclusively on static, cross-sectional sample surveys (e.g., Cramer & Imaike 2002; "
        "Wu et al. 2005). While cross-sectional surveys successfully verify that r ~ 0 in contemporary samples, they are methodologically incapable of "
        "testing generative, multi-generational hypotheses regarding how demographic mixing, assortative mating, and socialization feedback interact across "
        "time. Cross-sectional regression can falsify a biological claim, but it cannot explain the endogenous social mechanisms that sustain public certainty."
    )
    doc.add_paragraph(
        "Agent-based modeling (ABM) provides an exceptionally powerful tool to resolve this generative question. By simulating artificial societies of interacting "
        "heterogeneous agents across multiple generations (Epstein 1999; Gilbert 2008), ABM enables social scientists to explicitly trace how micro-level "
        "decision rules (such as mating preferences and socialization feedback) aggregate into macro-level population patterns. In the spirit of generative "
        "social science—'if you didn't grow it, you didn't explain it' (Epstein 1999)—we ask whether an artificial population initialized with zero biological "
        "correlation can 'grow' a measurable blood-type personality association purely through cultural and demographic dynamics."
    )
    doc.add_paragraph(
        "This paper addresses this gap by making three primary contributions:\n"
        "1. We formally prove via Directed Acyclic Graphs (DAGs) and Markov conditional independence that simple intergenerational transmission "
        "cannot generate correlation out of an uncorrelated ancestral state, refuting the naive lay intuition;\n"
        "2. We implement a rigorous, vectorized Monte Carlo agent-based model documented under the full ODD protocol to evaluate three competing candidate "
        "mechanisms—cross-assortative mating, population stratification, and social labeling feedback;\n"
        "3. We explore a parametric space to determine the conditions under which an emergent correlation reaches Cohen's (1988) conventional reference "
        "value for a small effect size (r = 0.10), reconciling scientific null findings with psychological subjective convictions."
    )

    # -------------------------------------------------------------
    # Section: Theoretical Framework and Hypotheses
    # -------------------------------------------------------------
    h = doc.add_paragraph()
    r = h.add_run("Theoretical Framework and Hypotheses")
    r.bold = True
    r.font.size = Pt(14)
    h.paragraph_format.space_after = Pt(6)

    doc.add_paragraph(
        "To rigorously dissect the causal topology, let X denote an individual's ABO blood phenotype and Y denote a continuous personality trait "
        "(standardized such that Y follows a standard normal distribution N(0, 1), representing a continuum from cautious/introverted to assertive/extraverted). "
        "We denote parental variables with subscript p (where p in {m, f} indicates maternal and paternal lineages) and offspring variables with subscript c."
    )

    doc.add_paragraph("Conditional Independence and the Parallel Transmission Fallacy")
    doc.add_paragraph(
        "Under the hypothesis of purely parallel transmission without cultural coupling, the data-generating process is represented by two "
        "independent biological inheritance chains:\n"
        "   X_p ---> X_c  (Mendelian transmission of ABO alleles at chromosome 9q34.2)\n"
        "   G_p ---> G_c  (Polygenic additive breeding value transmission via Fisher's infinitesimal model)\n\n"
        "where X_c is determined strictly by parental alleles according to Mendel's law of segregation, and additive genetic scores G_c follow Fisher's "
        "(1918) infinitesimal model: G_c = 0.5·G_m + 0.5·G_f + ε_seg, with meiotic segregation variance ε_seg ~ N(0, 0.5·h^2). Crucially, in formal "
        "quantitative genetics, parental non-shared environmental components are not transmitted across generations; rather, environmental noise "
        "E_c ~ N(0, 1 - h^2) is independently sampled for each offspring. In our comprehensive developmental model, expressed phenotypic personality "
        "P_c aggregates genetic inheritance, environmental variation, and cultural socialization feedback F_c = β·S(X_c), as formalized in displayed equation (1):"
    )

    add_equation_1(doc, eq_style)

    doc.add_paragraph(
        "where ε_seg ~ N(0, 0.5·h^2) represents Mendelian segregation variance arising from meiotic recombination across polygenic loci, "
        "E_c ~ N(0, 1 - h^2) represents stochastic non-shared environmental variation drawn independently for each offspring, and β in [0, 1] "
        "represents the socialization feedback intensity. Under the biological null baseline (β = 0), the expected population phenotypic trait variance remains "
        "standardized under the standard polygenic model assumption: E[Var(P_c)] = Var(G_c) + Var(E_c) = h^2 + (1 - h^2) = 1.0."
    )
    doc.add_paragraph(
        "Theorem 1 (Invariance of Independence under Parallel Mendelian and Polygenic Transmission): "
        "Let G_p^{ABO} = (G_f^{ABO}, G_m^{ABO}) and Θ_p = (G_f, E_f, G_m, E_m) denote joint parental ABO genotypes and parental personality "
        "determinants (additive genetic and environmental), respectively, collectively defining the parental state space Z_p = (G_p^{ABO}, Θ_p). "
        "Assume initial stochastic independence G_i^{ABO} ⊥ (G_i, E_i) for all individuals at generation t = 0. Under panmictic (random) mating—where "
        "maternal and paternal lineages pair independently: (G_f^{ABO}, G_f, E_f) ⊥ (G_m^{ABO}, G_m, E_m)—and under the structural condition that "
        "meiotic segregation at the ABO locus and polygenic recombination operate without direct pleiotropy or linkage disequilibrium, "
        "offspring blood phenotype X_c and offspring personality trait Y_c remain strictly independent (X_c ⊥ Y_c) for all generations t >= 1, "
        "which strictly implies Cov(X_c, Y_c) = 0."
    )
    doc.add_paragraph(
        "Proof: Under panmictic random mating, maternal and paternal lineages form independently: (G_f^{ABO}, G_f, E_f) ⊥ (G_m^{ABO}, G_m, E_m). "
        "In the null causal Directed Acyclic Graph (DAG), the ABO gene locus on chromosome 9q34.2 and the polygenic quantitative trait loci "
        "distributed across the autosomes are unconditionally d-separated (Pearl 2009). Meiotic transmission ensures that allelic segregation at the "
        "ABO locus is conditionally independent of polygenic recombination given the parental state vector Z_p:\n"
        "   P(X_c, Y_c | Z_p) = P(X_c | G_p^{ABO}) · P(Y_c | Θ_p).\n"
        "Marginalizing across the joint distribution of independent parental configurations yields:\n"
        "   P(X_c, Y_c) = ∫_{Z_p} P(X_c | G_p^{ABO}) P(Y_c | Θ_p) dP(Z_p) = P(X_c) · P(Y_c).\n"
        "This proves that X_c ⊥ Y_c in generation t = 1. By mathematical induction, this structural stochastic independence is strictly preserved "
        "across all subsequent generations t >= 1. Because statistical independence strictly implies zero covariance for all Borel-measurable scoring functions, "
        "Cov(X_c, Y_c) = 0 identically across all generations. The covariance expansion across parental states via the law of total covariance is "
        "formalized in displayed equation (2):"
    )

    add_equation_2(doc, eq_style)

    doc.add_paragraph(
        "Because meiotic segregation at the ABO locus is conditionally independent of parental personality traits given Z_p, the first conditional "
        "covariance term vanishes identically: E[Cov(X_c, Y_c | Z_p)] = 0. Furthermore, because G_p^{ABO} ⊥ Θ_p under panmixia and ancestral "
        "independence, the conditional expectations E[X_c | Z_p] = E[X_c | G_p^{ABO}] and E[Y_c | Z_p] = E[Y_c | Θ_p] constitute mutually independent "
        "random variables, yielding Cov(E[X_c | Z_p], E[Y_c | Z_p]) = 0. Consequently, Cov(X_c, Y_c) = 0 holds as an invariant mathematical "
        "equilibrium across all generations. Q.E.D."
    )
    doc.add_paragraph(
        "This mathematical proof establishes that, under the stated assumptions of initial stochastic independence, random mating, "
        "and independent transmission processes, statistical independence between ABO genotype and personality determinants is preserved "
        "across generations. An uncorrelated ancestral system cannot spontaneously break symmetry without external coupling forces. "
        "We therefore formalize three candidate social and demographic mechanisms capable of breaking conditional independence."
    )

    doc.add_paragraph("Hypothesis 1: Cultural Assortative Mating")
    doc.add_paragraph(
        "In population genetics, assortative mating is well established as a mechanism that induces gametic phase disequilibrium between physically "
        "unlinked loci (Wright 1921). If a culture develops institutionalized beliefs regarding blood-type compatibility (such as popular magazine "
        "guides advising Type A women to avoid Type B men or seek Type O men), mate choice becomes non-random with respect to blood type and personality. "
        "Let α in [0, 1] denote the cultural mating preference intensity. If individuals preferentially select mates whose blood type matches their "
        "own psychological expectations, a statistical coupling can accumulate across generations between the ABO locus and polygenic personality variants."
    )

    doc.add_paragraph("Hypothesis 2: Subpopulation Stratification and Panmixia")
    doc.add_paragraph(
        "In statistical genetics, population stratification represents the classic confounding mechanism producing spurious genetic associations—most "
        "famously illustrated by the 'chopstick gene' paradox (Lander & Schork 1994). If a population consists of two ancestral subpopulations (S_1, S_2) "
        "possessing divergent allele frequencies (e.g., northern versus southern migration lineages in East Asia) and distinct baseline temperaments "
        "arising from regional ecological conditions, aggregate population sampling yields displayed equation (3):"
    )

    add_equation_3(doc, eq_style)

    doc.add_paragraph(
        "Even when Cov(X, Y | S) = 0 within every subpopulation, the between-group covariance term creates a spurious aggregate association. We test whether "
        "this stratification survives panmictic intermarriage over generational timescales."
    )

    doc.add_paragraph("Hypothesis 3: Social Labeling and Self-Fulfilling Prophecy")
    doc.add_paragraph(
        "Drawing from sociological labeling theory (Mead 1934; Becker 1963) and social psychology (Merton 1948), cultural stereotypes actively structure "
        "social reality. When parents, teachers, and peers possess well-defined behavioral expectations based on a child's known blood type, differential "
        "social reinforcement occurs. For instance, a Type B child exhibiting restless behavior may be told, 'You are so carefree and individualistic, "
        "just like a typical B,' reinforcing that behavioral tendency. We formalize this environmental feedback pathway in displayed equation (4):"
    )

    add_equation_4(doc, eq_style)

    doc.add_paragraph(
        "where S(X_c) is the normalized cultural stereotype expectation for blood type X_c, and β in [0, 1] represents the socialization feedback intensity.\n\n"
        "Analytical Derivation of the Social Feedback Limit: Under static linear feedback with unit baseline phenotypic variance Var(G_c + E_c) = 1.0 "
        "and biological independence (G_c + E_c) ⊥ S(X_c), the population covariance evaluates to Cov(S(X_c), Y_c) = β · Var(S(X_c)) = β · σ_S^2, "
        "while the total phenotypic variance expands to Var(Y_c) = 1 + β^2 · σ_S^2. The theoretical correlation between cultural stereotype score S(X) "
        "and expressed personality trait Y is therefore given in closed form by displayed equation (5):"
    )

    add_equation_5(doc, eq_style)

    doc.add_paragraph(
        "Using empirical Korean allele frequencies (p = 0.28, q = 0.22, r = 0.50), the phenotypic frequencies under Hardy-Weinberg equilibrium "
        "are Type A (35.84%), Type B (26.84%), Type O (25.00%), and Type AB (12.32%). With the cultural stereotype scores S(A) = -1.0, S(B) = +1.0, "
        "S(O) = +0.5, and S(AB) = 0.0, the population mean evaluates to E[S] = 0.0350 and the second moment is E[S^2] = 0.6893, yielding an exact "
        "variance of Var(S) = 0.688075 (sigma_S ≈ 0.82950). Substituting these parameters into equation (5) yields analytical benchmark "
        "predictions of r_pred ≈ 0.0827 for beta = 0.10, r_pred ≈ 0.2031 for beta = 0.25, and r_pred ≈ 0.3831 for beta = 0.50 under baseline unit variance. "
        "In our simulation experiments under pure socialization feedback in the absence of assortative mating (alpha = 0.0), the immediate "
        "generational response at Generation 1 across replications settles at r = 0.082 +/- 0.015 for beta = 0.10, r = 0.201 +/- 0.018 for beta = 0.25, "
        "and r = 0.394 +/- 0.017 for beta = 0.50, closely tracking these closed-form single-generation benchmarks and confirming algorithmic implementation. "
        "Across subsequent cohorts under demographic replacement, this steady state is sustained over all 25 generations (longitudinal mean r = 0.201 +/- 0.018 "
        "for beta = 0.25; final Generation 25 snapshot r = 0.199 +/- 0.017 as reported in Table 1), with minor fluctuations reflecting finite demographic "
        "sampling variance across seeds. Crucially, while a static, isolated linear feedback equation is analytically tractable in a single generation, "
        "closed-form analytical solutions are not readily available for the coupled multi-generational system where feedback interacts across cohorts "
        "with non-random assortative mating and demographic replacement."
    )

    # -------------------------------------------------------------
    # Section: The Simulation Model and ODD Protocol
    # -------------------------------------------------------------
    h = doc.add_paragraph()
    r = h.add_run("The Simulation Model and ODD Protocol")
    r.bold = True
    r.font.size = Pt(14)
    h.paragraph_format.space_after = Pt(6)

    doc.add_paragraph(
        "We implement the simulation model following the standard ODD (Overview, Design concepts, Details) protocol for describing individual-based and "
        "agent-based models (Grimm et al. 2006; Polhill et al. 2008)."
    )

    doc.add_paragraph("Purpose")
    doc.add_paragraph(
        "The primary purpose of the model is to investigate whether and under what demographic and cultural conditions a statistical correlation between "
        "ABO blood type and continuous personality traits can emerge endogenously in a multi-generational population with zero initial biological association. "
        "The model tests whether cultural practices (mating preferences and parental feedback) can act as generative mechanisms creating macro-level statistical "
        "artifacts that mimic genetic effects."
    )

    doc.add_paragraph("Entities, State Variables, and Scales")
    doc.add_paragraph(
        "The model simulates a closed population of N = 5,000 individual agents across T = 25 generations (representing approximately 600 to 750 years of "
        "demographic history). Each agent i is characterized by the following state variables:\n"
        "• Sex: Binary indicator (0 = Male, 1 = Female), maintained at an equal 1:1 ratio.\n"
        "• Blood Genotype: A pair of alleles (a_1, a_2) sampled from {I^A, I^B, i}.\n"
        "• Blood Phenotype: Manifested ABO type X_i in {A, B, O, AB} determined via Mendelian dominance rules.\n"
        "• Cultural Stereotype Score: S(X_i) mapped along the introverted/cautious versus extraverted/impulsive axis: Type A = -1.0; Type B = +1.0; "
        "Type O = +0.5; Type AB = 0.0.\n"
        "• Genetic Personality Component: Additive breeding value G_i ~ N(0, h^2), with heritability h^2 = 0.50 based on behavioral genetic meta-analyses "
        "(Bouchard & McGue 2003; Polderman et al. 2015).\n"
        "• Environmental Component: Non-shared environmental variance E_i ~ N(0, 1 - h^2).\n"
        "• Social Feedback Component: Endogenous feedback F_i = beta * S(X_i).\n"
        "• Phenotypic Personality: Manifest continuous trait P_i = G_i + E_i + F_i."
    )

    doc.add_paragraph("Process Overview and Scheduling")
    doc.add_paragraph(
        "Within each generation t, the simulation executes five discrete sequential stages:\n"
        "1. Evaluation: Calculate population-wide statistics, including Pearson correlation r between P and S(X), group means, and Cohen's d.\n"
        "2. Mating Pool Formation: Divide the population into eligible male and female reproductive pools.\n"
        "3. Mate Selection: Under random mating (alpha = 0.0), pairs are formed via uniform random sampling with replacement. Under assortative mating "
        "(alpha > 0), males sample k = 5 candidate females and choose the candidate whose blood-type stereotype best matches their personality with probability alpha.\n"
        "4. Reproduction and Inheritance: Each mated pair produces offspring via Mendelian segregation of alleles (one maternal, one paternal) and infinitesimal "
        "polygenic inheritance with segregation variance epsilon_seg ~ N(0, 0.5 * h^2).\n"
        "5. Socialization and Generational Replacement: Offspring receive social feedback beta * S(X_child), form the new generation t + 1, and the parent "
        "generation is retired."
    )

    doc.add_paragraph("Design Concepts")
    doc.add_paragraph(
        "Following Grimm et al. (2006), the model incorporates the following key design concepts:\n"
        "• Emergence: Population-level correlation r and standardized effect size Cohen's d emerge endogenously from individual mating decisions and social feedback.\n"
        "• Adaptation: Agents adapt mate choice by evaluating compatibility between their own personality score P_i and the stereotype expectation S(X_j) of candidate mates.\n"
        "• Objectives: In assortative mating scenarios, agents seek to maximize perceived psychological compatibility, operationalized as minimizing |P_i - S(X_j)|.\n"
        "• Sensing: Agents perceive the blood-type phenotype and associated cultural stereotype of potential partners in their local mating pool.\n"
        "• Interaction: Agents interact through sexual reproduction, during which genetic material is recombined according to Mendelian and polygenic inheritance laws.\n"
        "• Stochasticity: Stochastic processes govern meiotic allele segregation, candidate partner sampling, and environmental noise generation.\n"
        "• Collectives: Agents belong to phenotypic blood-type groups {A, B, O, AB} and, in stratification experiments, ancestral subpopulations {S_1, S_2}.\n"
        "• Observation: Population correlation r, Cohen's d between Type B and Type A, within-group variances, and ANOVA F-statistics are recorded at each generation."
    )

    doc.add_paragraph("Initialization and Input Data")
    doc.add_paragraph(
        "The model initializes N = 5,000 agents. Allele frequencies are calibrated to empirical East Asian / Korean blood donor census data "
        "(Kim et al. 2013; 1000 Genomes Project): p(I^A) = 0.28, q(I^B) = 0.22, and r(i) = 0.50. Under Hardy-Weinberg equilibrium, the expected "
        "phenotypic proportions are Type A (35.8%), Type B (26.8%), Type O (25.0%), and Type AB (12.3%). Initial breeding values G_i and environmental "
        "values E_i are drawn independently from normal distributions, ensuring zero population covariance in expectation at initialization "
        "(E[Cov(X, Y)] = 0, with realized finite-sample covariances centered at zero)."
    )

    doc.add_paragraph("Submodels and Algorithmic Implementation")
    doc.add_paragraph(
        "The model incorporates three primary mathematical submodels executed iteratively at each generation:\n\n"
        "1. Mendelian Segregation Submodel: For an offspring produced by father f and mother m, parental alleles are represented as vectors "
        "A_f = (a_f1, a_f2) and A_m = (a_m1, a_m2). The offspring receives one randomly sampled allele from each parent:\n"
        "   a_c1 ~ Uniform({a_f1, a_f2}),   a_c2 ~ Uniform({a_m1, a_m2})\n"
        "Phenotypic blood group X_c is assigned deterministically based on codominant expression of I^A and I^B over recessive i: "
        "X_c = AB if {a_c1, a_c2} = {I^A, I^B}; X_c = A if I^A in {a_c1, a_c2} and I^B not in {a_c1, a_c2}; "
        "X_c = B if I^B in {a_c1, a_c2} and I^A not in {a_c1, a_c2}; and X_c = O if {a_c1, a_c2} = {i, i}.\n\n"
        "2. Polygenic Inheritance Submodel: Following Fisher's infinitesimal model (Fisher 1918), additive genetic values G_c are computed as:\n"
        "   G_c = 0.5 * G_f + 0.5 * G_m + epsilon_seg,   epsilon_seg ~ N(0, 0.5 * h^2)\n"
        "where epsilon_seg represents Mendelian segregation variance arising from independent assortment and recombination across polygenic loci. "
        "Environmental variance is added independently via E_c ~ N(0, 1 - h^2), ensuring Var(G_c + E_c) = 1.0 under neutral conditions. "
        "Under assortative mating, phenotypic selection can theoretically induce parental genetic covariance Cov(G_f, G_m), which in classical quantitative "
        "genetics asymptotically inflates genetic variance to V_{G,∞} = V_{G,0}(1 - 0.5·h^2) / (1 - h^2·r_m) (Bulmer 1980; Falconer & Mackay 1996). "
        "In our model, mate choice evaluates compatibility between the male's phenotypic personality P_i (which contains additive genetic component G_i) "
        "and the female candidate's blood-type stereotype score S(X_j). Because selection operates cross-trait between continuous phenotype and "
        "categorical blood type rather than directly on somatic resemblance of polygenic scores, parental genetic covariance accumulates only weakly "
        "across generations (mean Cov(G_f, G_m) < 0.015 across experimental conditions). Longitudinal tracking confirmed that total phenotypic trait "
        "variance remained stable around unity (Var(P) = 1.02 +/- 0.03 at generation 25), indicating that the observed correlation dynamics reflect "
        "cultural-demographic sorting rather than unconstrained variance inflation.\n\n"
        "3. Cultural Assortative Mating Submodel: For each reproductive male i with trait value P_i, a pool of k candidate females C_i = {j_1, ..., j_k} "
        "is sampled with replacement from the female population. Psychological compatibility between male i and candidate j is defined as the negative "
        "absolute distance between male trait P_i and the stereotype score S(X_j) of the female's blood type: Omega_ij = - |P_i - S(X_j)|. "
        "With probability alpha, the male selects the candidate j* maximizing compatibility: j* = argmax_{j in C_i} Omega_ij. With probability 1 - alpha, "
        "the male selects a candidate uniformly at random from C_i, guaranteeing a smooth parameterization from pure panmixia (alpha = 0.0) to strict "
        "assortative mating (alpha = 1.0).\n\n"
        "4. Socialization Feedback Submodel: After phenotypic trait generation, cultural feedback operates as an additive environmental shift: "
        "P_c = G_c + E_c + beta * S(X_c). Here, S(X) serves as a directional cultural stereotype contrast score mapping nominal blood types along the "
        "cautious/introverted to assertive/extraverted continuum. The Pearson correlation r = Corr(S(X), P) evaluates linear fidelity to this cultural axis, "
        "while group-level Cohen's d and ANOVA effect sizes quantify omnibus category differences. This captures the developmental internalization of "
        "blood-type expectations communicated by parents, teachers, and peers throughout childhood and adolescence."
    )

    doc.add_paragraph("Model Availability and Replication")
    if anonymised:
        doc.add_paragraph(
            "In compliance with JASSS replication guidelines, the complete Python simulation source code, vectorized ABM engine, simulation datasets, "
            "and statistical visualization modules are curated in an anonymized open-access repository for blind peer review at: "
            "https://anonymous.4open.science/r/blood-type-personality-abm-1439/. Referees and readers can execute the complete model with automated "
            "replication commands. Upon publication, the complete replication package will be permanently deposited in the CoMSES Net Computational Model Library "
            "and assigned an archival DOI."
        )
    else:
        doc.add_paragraph(
            "In compliance with JASSS replication guidelines, the complete Python simulation source code, vectorized ABM engine, simulation datasets, "
            "and statistical visualization modules are curated in an open-access repository at: https://github.com/Suhyun211/blood-type-personality-abm. "
            "Referees and readers can execute the complete model with automated replication commands. Upon publication, the complete replication package "
            "will be permanently deposited in the CoMSES Net Computational Model Library and assigned an archival DOI."
        )

    # -------------------------------------------------------------
    # Section: Simulation Results
    # -------------------------------------------------------------
    h = doc.add_paragraph()
    r = h.add_run("Simulation Results")
    r.bold = True
    r.font.size = Pt(14)
    h.paragraph_format.space_after = Pt(6)

    doc.add_paragraph(
        "Across all experimental conditions (N = 5,000, 25 generations, 5 independent Monte Carlo seeds per scenario), we tracked the trajectory of Pearson "
        "correlation r and standardized effect size (Cohen's d) between Type B and Type A individuals. Table 1 summarizes the final generational metrics."
    )

    # Table 1
    p_tbl = doc.add_paragraph()
    r_tbl = p_tbl.add_run("Table 1. Summary of Statistical Metrics Across Theoretical Models at Final Generation (Generation 25)")
    r_tbl.bold = True
    r_tbl.font.size = Pt(11)
    p_tbl.paragraph_format.space_after = Pt(4)

    table = doc.add_table(rows=9, cols=5)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(table)

    headers = ["Model / Scenario", "Final Correlation (<i>r</i>)", "Std. Dev. (<i>σ</i>)", "Explained Variance (<i>R</i><sup>2</sup>)", "Empirical Verdict"]
    hdr_cells = table.rows[0].cells
    for i, h_text in enumerate(headers):
        hdr_cells[i].text = ""
        p = hdr_cells[i].paragraphs[0]
        format_text_to_runs(p, enrich_math_markup(h_text))
        for r in p.runs:
            r.bold = True
            r.font.size = Pt(9.5)
        set_cell_margins(hdr_cells[i], top=120, bottom=120, left=140, right=140)

    rows_data = [
        ("Null Control (Pure Random Mating)", "-0.010", "0.008", "0.01%", "Consistent with independence assumption (<i>r</i> ≈ 0)"),
        ("Weak Assortative (<i>α</i> = 0.2)", "0.025", "0.018", "0.06%", "Sub-benchmark (Negligible accumulation)"),
        ("Strong Assortative (<i>α</i> = 0.8)", "0.139", "0.025", "1.92%", "Exceeds benchmark (Severe cultural constraint)"),
        ("Stratification (Δ = 0.5 SD)", "-0.000", "0.013", "0.00%", "Dissipated within 5 generations under panmixia"),
        ("Social Feedback Mild (<i>β</i> = 0.10)", "0.079", "0.017", "0.63%", "Quasi-instantaneous developmental shift"),
        ("Social Feedback Moderate (<i>β</i> = 0.25)", "0.199", "0.017", "3.98%", "Substantial effect, matches analytical benchmark (<i>d</i> = 0.494)"),
        ("Coupled Pure Model (<i>α</i> = 0.15, <i>β</i> = 0.10)", "0.102", "0.014", "1.05%", "Aligns with Cohen's benchmark (<i>r</i> = 0.10)"),
        ("Coupled + Stratified (<i>α</i> = 0.15, <i>β</i> = 0.10, Δ = 0.2)", "0.104", "0.022", "1.09%", "Similar to Coupled Pure; stratification dissipated")
    ]

    for row_idx, r_data in enumerate(rows_data):
        cells = table.rows[row_idx + 1].cells
        for col_idx, text in enumerate(r_data):
            cells[col_idx].text = ""
            p = cells[col_idx].paragraphs[0]
            format_text_to_runs(p, enrich_math_markup(text))
            for r in p.runs:
                r.font.size = Pt(9.5)
            set_cell_margins(cells[col_idx], top=80, bottom=80, left=140, right=140)

    p_tbl_note = doc.add_paragraph()
    format_text_to_runs(p_tbl_note, enrich_math_markup("Note: Based on N = 5,000 agents across 25 generations with 5 Monte Carlo replications per condition using np.random.SeedSequence. Small effect size reference benchmark follows Cohen (1988; r >= 0.10)."))
    for r in p_tbl_note.runs:
        r.font.size = Pt(9)
        r.font.italic = True
    p_tbl_note.paragraph_format.space_after = Pt(14)

    # Figure 1 Text & Image
    doc.add_paragraph(
        "Figure 1 illustrates the multi-generational dynamics under varying assortative mating pressures. Under the Null Control (alpha = 0.0), "
        "the correlation remains centered at zero across all 25 generations (mean r = -0.010 +/- 0.008), in full accordance with the theoretical "
        "expectation of zero covariance derived in Theorem 1. When weak assortative preference is introduced (alpha = 0.2), correlation accumulates "
        "slowly across successive cohorts but asymptotically plateaus well below the conventional reference threshold (r = 0.025 +/- 0.018). "
        "Only when an extreme cultural mating bias is imposed (alpha = 0.8)—wherein 80% of individuals actively match on blood-type stereotypes—does "
        "the emergent correlation cross Cohen's (1988) conventional reference value for a small correlation effect (r = 0.139 +/- 0.025)."
    )

    fig1_path = os.path.join(FIGURES_DIR, "fig1_assortative_mating.png")
    if os.path.exists(fig1_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_after = Pt(4)
        run_img = p_img.add_run()
        run_img.add_picture(fig1_path, width=Inches(6.0))
        add_fig_caption(doc, "Figure 1. Multi-generational trajectory of Pearson correlation r under assortative mating pressures (alpha in [0.0, 0.8]). Shaded bands represent +/- 1 standard deviation across five independent replications.")

    # Figure 2 Text & Image
    doc.add_paragraph(
        "Figure 2 depicts the evolutionary fate of ancestral population stratification. Although ancestral admixture between distinct subpopulations "
        "initially creates a substantial spurious association at generation 0 (r = 0.22 to 0.38 for Delta = 0.5 to 1.0 SD), the onset of panmictic random mating "
        "causes this statistical association to collapse exponentially. Within 3 to 5 generations, genetic recombination and random intermarriage completely "
        "dilute the between-group covariance, reducing correlation to zero (mean r = -0.000 +/- 0.013 at generation 25). This proves that under panmictic "
        "random mating, ancestral geographic stratification dissipates rapidly and cannot account for the sustained persistence of modern blood-type "
        "beliefs in contemporary urban societies."
    )

    fig2_path = os.path.join(FIGURES_DIR, "fig2_population_stratification.png")
    if os.path.exists(fig2_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_after = Pt(4)
        run_img = p_img.add_run()
        run_img.add_picture(fig2_path, width=Inches(6.0))
        add_fig_caption(doc, "Figure 2. Rapid dilution of spurious correlation induced by population stratification under panmictic intermarriage over 25 generations.")

    # Figure 3 Text & Image
    doc.add_paragraph(
        "In stark contrast to demographic genetic mechanisms, Figure 3 reveals the potency of social labeling feedback. Unlike assortative mating, "
        "which requires generations to accumulate, social feedback operates quasi-instantaneously within a single developmental lifecycle. Under moderate "
        "feedback (beta = 0.25), a robust correlation of r = 0.199 (+/- 0.017 at generation 25; longitudinal mean r = 0.201) and a standardized "
        "mean difference between Type B and Type A of Cohen's d = 0.494 (+/- 0.038 at generation 25; longitudinal mean d = 0.498) emerge immediately "
        "at generation 1 and remain permanently stable. This closely aligns with both our analytical expectation for group contrast "
        "(E[P | B] - E[P | A] = 2·beta = 0.50, yielding theoretical d ≈ 0.50 under baseline unit standard deviation) and our closed-form correlation "
        "prediction (r_pred ≈ 0.2031), matching the empirical trajectory depicted in Figure 3(B). This demonstrates that psychological labeling and behavioral "
        "confirmation represent the primary engine capable of sustaining an observable behavioral difference."
    )

    fig3_path = os.path.join(FIGURES_DIR, "fig3_social_feedback.png")
    if os.path.exists(fig3_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_after = Pt(4)
        run_img = p_img.add_run()
        run_img.add_picture(fig3_path, width=Inches(6.2))
        add_fig_caption(doc, "Figure 3. Impact of social labeling and self-fulfilling socialization feedback: (A) Pearson correlation r across generations; (B) Standardized effect size (Cohen's d) between Type B and Type A individuals.")

    # Figure 4 Text & Image
    doc.add_paragraph(
        "Figure 4 provides a two-panel comprehensive synthesis of equilibrium mechanism comparisons and counterfactual generational dynamics. "
        "In Panel (A), we deconstruct the five experimental mechanisms at Generation 25, evaluating both expressed phenotypic correlation r_P and "
        "latent additive genetic correlation r_G. In the Coupled Pure Model—combining plausible weak assortative bias (alpha = 0.15) and mild parental "
        "feedback (beta = 0.10) in the strict absence of population stratification—the system settles at an equilibrium phenotypic correlation of "
        "r_P = 0.102 (+/- 0.014, with a 95% confidence interval of [0.090, 0.114] across 5 replications), accompanied by a subtle latent genetic correlation "
        "of r_G = 0.020 (+/- 0.014). This value closely aligns with and numerically spans Cohen's (1988) conventional reference value for a small correlation "
        "effect (r = 0.10). When initial ancestral stratification (Delta = 0.2 SD) is added to this coupled model (Coupled + Stratified), the resulting "
        "equilibrium is virtually identical (r_P = 0.104 +/- 0.022, r_G = 0.034 +/- 0.020). This critical contrast resolves potential confounding, "
        "proving that the observed association is autonomously generated and sustained by cultural-demographic coupling rather than being an artifact of ancestral substructure.\n\n"
        "In Panel (B), we present the findings of the counterfactual Cultural Belief Withdrawal experiment across generations 0 to 25. Prior to intervention "
        "(generations 0–10), the population maintains steady cultural coupling (r_P ≈ 0.11–0.12, r_G ≈ 0.040). When cultural beliefs are withdrawn at generation 10: "
        "first, under Complete Withdrawal (alpha = 0, beta = 0), phenotypic correlation collapses quasi-instantaneously from 0.121 to 0.008 at generation 11, "
        "and decays toward zero (r = -0.002 at generation 25) as Mendelian recombination dilutes non-causal associations under panmixia; "
        "second, under Social Feedback Cessation (beta = 0, with assortative mating alpha = 0.15 maintained), phenotypic correlation drops immediately to "
        "r_P = 0.032 at generation 11, unmasking the underlying genetic correlation (r_G = 0.038). Because mate choice continues to sort on phenotypic personality, "
        "this latent genetic correlation persists across generations (r_G ≈ 0.033 at generation 25). This asymmetric decoupling highlights the distinct value "
        "of agent-based modeling in revealing multi-generational inertia that remains inaccessible to static analytical equations."
    )

    fig4_path = os.path.join(FIGURES_DIR, "fig4_model_comparisons.png")
    if os.path.exists(fig4_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_after = Pt(4)
        run_img = p_img.add_run()
        run_img.add_picture(fig4_path, width=Inches(6.2))
        add_fig_caption(doc, "Figure 4. Synthesis of model comparisons and multi-generational dynamics: (A) Mechanism deconstruction at Generation 25 comparing phenotypic (r_P) and genetic (r_G) correlations across five theoretical conditions relative to Cohen's (1988) small-effect benchmark (r = 0.10); (B) Cultural belief withdrawal and generational inertia trajectories across 25 generations.")

    # Statistical Significance and Sensitivity Analysis
    doc.add_paragraph("Statistical Significance and Sensitivity Testing")
    doc.add_paragraph(
        "To evaluate whether differences among experimental conditions were statistically robust, we conducted a two-way factorial Analysis of "
        "Variance (ANOVA) across the complete experimental grid (4 levels of mating pressure alpha in {0.0, 0.2, 0.5, 0.8} x 3 levels of feedback "
        "intensity beta in {0.0, 0.10, 0.25} across 5 independent Monte Carlo replications; total N = 60). The analysis confirmed a dominant main "
        "effect of social feedback (F(2, 48) = 1016.64, p < 0.001, eta_p^2 = 0.977) and a highly significant main effect of assortative mating "
        "(F(3, 48) = 282.23, p < 0.001, eta_p^2 = 0.946). No statistically significant interaction was detected in the factorial experiments "
        "(F(6, 48) = 0.50, p = 0.805, eta_p^2 = 0.059). The partial eta-squared values computed directly from sums of squares match the standard "
        "F-ratio formula eta_p^2 = (F · df_1) / (F · df_1 + df_2). This absence of a statistically significant interaction is compatible with "
        "an approximately additive combination of effects but does not establish exact additivity."
    )
    doc.add_paragraph(
        "We further subjected the model to sensitivity tests by systematically varying baseline parameters:\n"
        "• Stereotype Scoring Metric: Testing an alternative symmetric contrast scale (A = -1.0, B = +1.0, O = 0.0, AB = 0.0) yielded an equilibrium "
        "correlation of r_P = 0.092 +/- 0.022 (r_G = 0.021 +/- 0.017), proving that the phenomenon does not depend artifactually on the specific numerical score assigned to Type O (+0.5).\n"
        "• Direction of Mate Selection: Implementing mutual, bidirectional mate choice (wherein females also evaluate candidate males based on blood-type stereotypes) "
        "strengthened the equilibrium correlation to r_P = 0.122 +/- 0.014 (r_G = 0.051 +/- 0.022), demonstrating that bilateral preference reinforces the cultural feedback loop.\n"
        "• Trait Heritability (h^2): Varying h^2 across {0.30, 0.50, 0.70} did not alter the equilibrium correlation in the social feedback model "
        "(r remained between 0.188 and 0.198), demonstrating that socialization effects are robust to quantitative genetic architecture assumptions.\n"
        "• Candidate Mating Pool Size (k): Increasing candidate pool size from k = 3 to k = 10 amplified assortative mating efficiency by 18%, but "
        "still required alpha >= 0.7 to cross the r = 0.10 threshold in the absence of feedback.\n"
        "• Population Size (N): Testing populations of N = 1,000, 5,000, and 20,000 confirmed that demographic stochasticity did not bias mean trajectories, "
        "though N = 1,000 exhibited wider generational sampling variance (sigma = 0.034)."
    )

    # -------------------------------------------------------------
    # Section: Discussion
    # -------------------------------------------------------------
    h = doc.add_paragraph()
    r = h.add_run("Discussion")
    r.bold = True
    r.font.size = Pt(14)
    h.paragraph_format.space_after = Pt(6)

    doc.add_paragraph(
        "The findings of this study offer a comprehensive resolution to the long-standing paradox between scientific null findings and pervasive "
        "popular belief regarding blood-type personality theory."
    )
    doc.add_paragraph(
        "Refutation of the Intergenerational Intuition: Our mathematical analysis and baseline simulations conclusively debunk the intuitive lay belief "
        "that parental transmission could somehow produce correlation. Because the ABO locus on chromosome 9 and the thousands of polygenic loci "
        "underlying personality traits segregate independently during meiosis, parental transmission acts as an orthogonal operator. Without external "
        "symmetry-breaking forces, zero correlation remains zero across infinite generations."
    )
    doc.add_paragraph(
        "Attenuation of Ancestral Stratification under Panmixia: Our stratification experiment demonstrates that under idealized panmictic (random) "
        "intermarriage, ancestral stratification dissipates rapidly within 3 to 5 generations, attenuating spurious correlations to zero. "
        "However, this finding should be interpreted with appropriate nuance: while massive post-war urbanization and inter-regional mobility in modern "
        "South Korea and Japan have substantially increased panmixia, real-world human populations may still retain subtle residual subpopulation "
        "structures or historical geographic assortation (Price et al. 2006). Thus, while panmictic demographic mixing strongly undermines ancestral "
        "stratification as an autonomous, primary generative driver of modern blood-type beliefs in highly urbanized settings, our simulation does "
        "not entirely rule out the potential contributing role of historical or regional population substructure in relatively isolated demographics."
    )
    doc.add_paragraph(
        "The Meaning of the 1.05% Explained Variance: While our unconfounded coupled model demonstrates that cultural practices can yield a correlation "
        "of r = 0.102, the critical insight lies in the magnitude of the coefficient of determination: R^2 = (0.102)^2 = 0.0105. "
        "Specifically, adherence to the cultural stereotype contrast accounts for barely 1.05% of total phenotypic variation, leaving the "
        "remaining 98.95% of phenotypic variance unassociated with the cultural blood-type metric and determined by broad genetic, developmental, "
        "and idiosyncratic environmental factors. In psychological and psychiatric epidemiology, an effect of R^2 ~ 1% represents a subtle "
        "population tendency that cannot reliably predict individual behavior or temperament."
    )
    doc.add_paragraph(
        "Bridging the 1% Empirical Artifact and Lay Perceptual Conviction (Theoretical Synthesis): Why, then, does the lay public perceive the theory "
        "to be 70% to 80% accurate despite our ABM demonstrating that demographic and developmental coupling yields an explained variance "
        "of R^2 = 1.05% in our primary coupled parameterization? It is essential to maintain an epistemological distinction here: while the demographic emergence of r = 0.102 is directly "
        "demonstrated by our quantitative multi-agent simulation, the cognitive amplification that bridges this subtle statistical signal to pervasive "
        "popular conviction represents a qualitative theoretical synthesis grounded in cognitive and social psychological principles, rather than "
        "an endogenously simulated behavioral mechanism within the agent architecture. Specifically, we propose that four well-documented cognitive "
        "heuristics operate as an external perceptual amplifier on this subtle population-level artifact:\n"
        "1. The Barnum (Forer) Effect and Self-Attribution: Blood-type descriptions consist largely of universally applicable personality traits "
        "(e.g., 'A types appear calm outside but worry deeply inside'). When individuals are informed of their blood type, they selectively map these "
        "flattering, vague descriptors onto their self-concept (Cramer & Imaike 2002).\n"
        "2. Observational Selection and Collider Conditioning: In daily social discourse, people do not randomly survey the entire population. They discuss blood types "
        "disproportionately with individuals who exhibit prominent, expressive temperaments or in dating contexts where compatibility is salient. Conditioning "
        "on these social colliders artificially inflates perceived correlation (Pearl 2009).\n"
        "3. Confirmation Bias and Selective Recall: Instances of perceived consistency (e.g., encountering an eccentric Type B artist) are vigorously coded "
        "as confirmatory evidence, while counterexamples (e.g., a shy Type B or an outgoing Type A) are dismissed as personal idiosyncrasies.\n"
        "4. Self-Stereotyping and Behavioral Assimilation: Over time, individuals actively adjust their self-presentation to conform to cultural expectations "
        "associated with their blood group, further entrenching the superficial signal.\n\n"
        "Explicitly distinguishing this qualitative psychological framework from the endogenous ABM dynamics clarifies that while generative demographic "
        "feedback is sufficient to seed an objective population correlation, human cognitive biases may contribute to inflating this subtle statistical "
        "signal into an overwhelming subjective conviction."
    )
    doc.add_paragraph(
        "Methodological and Epistemological Implications for Agent-Based Modeling: Beyond its immediate substantive domain, "
        "this study carries profound methodological implications for computational social science. In classic generative social science, "
        "Thomas Schelling (1971) famously demonstrated in his residential segregation model that strong macroscopic segregation can emerge "
        "from surprisingly mild micro-level residential preferences. In our demographic simulation, we observe an analogous aggregation phenomenon: "
        "neither weak cultural assortative mating (alpha = 0.15) nor modest developmental labeling (beta = 0.10) alone produces an association "
        "reaching Cohen's reference value. However, when these two micro-mechanisms operate concurrently across generations within a closed demographic "
        "population, their additive combination produces an emergent population correlation of r = 0.102, aligning with Cohen's (1988) "
        "reference value for a small correlation effect (r = 0.10). Importantly, our factorial analysis demonstrated that within this parameter "
        "regime, an additive approximation adequately describes the combined dynamic without requiring multiplicative non-linear escalation. This demonstrates "
        "the distinctive power of agent-based modeling to track how separate cultural and demographic mechanisms aggregate over time—a multi-generational "
        "dynamic that remains inaccessible to static cross-sectional regression models.\n\n"
        "The Generational Inertia of Cultural Associations: Beyond equilibrium analysis, our counterfactual belief withdrawal experiments provide novel "
        "computational insights into the temporal persistence of cultural artifacts. While static equations predict that removing social feedback (beta -> 0) "
        "immediately eliminates the phenotypic association, our agent-based model reveals an asymmetric generational decoupling: expressed phenotypic "
        "correlation collapses within a single generation, whereas latent genetic linkage disequilibrium accumulated across ancestral generations of "
        "assortative mating persists as an unexpressed genetic correlation (r_G ≈ 0.033). Only when assortative mating is replaced by panmixia does this "
        "genetic shadow gradually dilute through Mendelian recombination and segregation. This dynamic decoupling illustrates the unique capability "
        "of agent-based modeling to track the latent multi-generational hysteresis of cultural practices.\n\n"
        "Timescale Interpretation (25 Generations vs. Rapid Social Feedback): A key conceptual distinction highlighted by our multi-generational "
        "design concerns the temporal scale of effects. The 25-generation timeline simulated here (spanning roughly 600–750 demographic years) functions "
        "as an asymptotic computational laboratory to examine equilibrium behavior under long-term cultural transmission, rather than as a literal "
        "historical reconstruction of the blood-type myth (which became a mass cultural phenomenon in East Asia only during the latter half of the "
        "twentieth century). Crucially, our simulation trajectories demonstrate that social labeling feedback operates quasi-instantaneously within "
        "a single developmental generation (reaching its full magnitude at t = 1), whereas assortative mating requires multiple cohorts to accumulate. "
        "Within the stylized parameter bounds of our agent-based model, rapid developmental internalization and behavioral confirmation function as the immediate "
        "operative driver of observed stereotypes, while multi-generational assortative mating provides an asymptotic theoretical upper bound under prolonged cultural persistence.\n\n"
        "Societal Implications and Science Communication: Far from being an innocent social icebreaker, institutionalized blood-type stereotypes "
        "have documented real-world discriminatory consequences, including employment discrimination (e.g., corporate job postings specifying "
        "preferred blood types in Japan and South Korea) and romantic stigmatization. Traditional debunking approaches from psychologists have "
        "frequently failed because telling the public 'there is no correlation in our survey' directly contradicts their lived perceptual experiences. "
        "By demonstrating that whatever tiny correlation exists is entirely an artificial cultural byproduct rather than a biological reality, "
        "this generative simulation provides educators, policymakers, and science communicators with an empirically rigorous, transparent "
        "computational tool to dismantle discriminatory pseudoscientific practices at their generative roots. Furthermore, our findings emphasize that in "
        "multi-agent systems where social constructs feed back into phenotypic traits, statistical correlations must never be uncritically conflated with biological "
        "causal mechanisms. The agent-based paradigm allows researchers to systematically deconstruct these reflexive causal loops under precisely controlled synthetic counterfactual conditions."
    )

    # -------------------------------------------------------------
    # Section: Conclusion
    # -------------------------------------------------------------
    h = doc.add_paragraph()
    r = h.add_run("Conclusion")
    r.bold = True
    r.font.size = Pt(14)
    h.paragraph_format.space_after = Pt(6)

    doc.add_paragraph(
        "In conclusion, as a computational proof-of-concept, this study demonstrates that: (1) Intergenerational parallel transmission alone cannot generate "
        "a blood-type personality correlation under neutral Mendelian inheritance; (2) Population stratification dissipates within 3 to 5 generations under "
        "panmictic intermarriage; (3) Assortative mating alone requires implausibly severe preference thresholds (alpha >= 0.8) to produce notable effects; "
        "but (4) Modest social labeling feedback combined additively with mild assortative preference can generate an emergent correlation of r = 0.102 "
        "(95% CI [0.090, 0.114], R^2 = 1.05%), aligning closely with Cohen's (1988) conventional reference value for a small correlation effect (r = 0.10). Rather than claiming "
        "an exhaustive empirical reconstruction of all historical factors, our generative model establishes a sufficient theoretical mechanism: "
        "cultural beliefs have the generative capacity to manufacture statistical associations in human populations even in the complete absence of "
        "underlying biological causality—a statistical ghost produced by human society's own stereotypes, reflected back through demographic dynamics "
        "and amplified by cognitive confirmation biases. Our findings establish a computational proof of concept showing that culturally mediated mating "
        "preferences and socialization feedback can generate blood-type–personality associations in the absence of a direct biological effect. "
        "Whether these mechanisms explain observed patterns in contemporary populations remains an empirical question.\n\n"
        "Future Computational Research Directions: This modeling framework opens several compelling avenues for future social simulation inquiry. "
        "First, future extensions could embed agents within dynamic social networks (such as scale-free or small-world topologies) to investigate how "
        "information cascade dynamics and homophily accelerate the geographic clusterization of pseudoscientific beliefs. Second, incorporating "
        "heterogeneous individual susceptibility (individual-level feedback coefficients beta_i) and multi-trait Big Five dimensional spaces rather "
        "than a single standardized axis would allow researchers to model competing, multidimensional stereotypes simultaneously. Ultimately, by demonstrating "
        "how computational agent-based models can deconstruct persistent cultural myths, this paper underscores the generative power of social simulation "
        "as both a scientific discovery instrument and a critical educational tool for modern open societies."
    )

    # -------------------------------------------------------------
    # Section: References (JASSS STYLE: FIRST AUTHOR ALL CAPS!)
    # -------------------------------------------------------------
    h = doc.add_paragraph()
    r = h.add_run("References")
    r.bold = True
    r.font.size = Pt(14)
    h.paragraph_format.space_after = Pt(8)

    jasss_refs = [
        "BECKER, H. S. (1963). Outsiders: Studies in the Sociology of Deviance. New York: Free Press.",
        "BOUCHARD, T. J., & McGue, M. (2003). Genetic and environmental influences on human psychological differences. Journal of Neurobiology, 54(1), 4–45.",
        "BULMER, M. G. (1980). The Mathematical Theory of Quantitative Genetics. Oxford: Clarendon Press.",
        "CHO, S. H., Suh, E. M., & Yang, S. J. (2005). Is person's personality really related to his/her blood type? Korean Journal of Social and Personality Psychology, 19(4), 33–47.",
        "COHEN, J. (1988). Statistical Power Analysis for the Behavioral Sciences (2nd ed.). Hillsdale, NJ: Lawrence Erlbaum Associates.",
        "CRAMER, K. M., & Imaike, E. (2002). Personality, blood type, and the Barnum effect in Japan. Psychological Reports, 91(1), 307–316.",
        "EPSTEIN, J. M. (1999). Agent-based computational models and generative social science. Complexity, 4(5), 41–60.",
        "FALCONER, D. S., & Mackay, T. F. (1996). Introduction to Quantitative Genetics (4th ed.). Harlow: Longman.",
        "FISHER, R. A. (1918). The correlation between relatives on the supposition of Mendelian inheritance. Transactions of the Royal Society of Edinburgh, 52(2), 399–433.",
        "FURUKAWA, T. (1927). A study of temperament by means of human blood groups. The Japanese Journal of Psychology, 2(4), 612–634.",
        "FURUKAWA, T. (1930). A study of temperament and blood-groups. The Journal of Social Psychology, 1(4), 494–509.",
        "GILBERT, N. (2008). Agent-Based Models. Thousand Oaks, CA: SAGE Publications.",
        "GRIMM, V., Berger, U., Bastiansen, F., Eliassen, S., Ginot, V., Giske, J., ... & DeAngelis, D. L. (2006). A standard protocol for describing individual-based and agent-based models: The ODD protocol. Ecological Modelling, 198(1-2), 115–126.",
        "KIM, S. Y., et al. (2013). Distribution of ABO and Rh blood groups in Korean blood donors. Korean Journal of Blood Transfusion, 24(2), 145–153.",
        "LANDER, E. S., & Schork, N. J. (1994). Genetic dissection of complex traits. Science, 265(5181), 2037–2048.",
        "MATSUI, Y. (1991). The effects of blood-type stereotype on personality perception. Japanese Journal of Social Psychology, 6(3), 166–173.",
        "MEAD, G. H. (1934). Mind, Self and Society. Chicago: University of Chicago Press.",
        "MERTON, R. K. (1948). The self-fulfilling prophecy. The Antioch Review, 8(2), 193–210.",
        "NOMI, M. (1971). Ketsuekigata de Wakaru Aisho (Compatibility Understood by Blood Types). Tokyo: Sangyo Shinto.",
        "OHMURA, M. (1990). Blood Type and Personality. Tokyo: Shinyosha.",
        "PEARL, J. (2009). Causality: Models, Reasoning, and Inference (2nd ed.). Cambridge: Cambridge University Press.",
        "POLDERMAN, T. J., et al. (2015). Meta-analysis of the heritability of human traits based on fifty years of twin studies. Nature Genetics, 47(7), 702–709.",
        "POLHILL, J. G., Parker, D. C., Brown, D. G., & Grimm, V. (2008). Using the ODD protocol for describing three agent-based social simulation models of land use change. Journal of Artificial Societies and Social Simulation, 11(2), 3 https://www.jasss.org/11/2/3.html.",
        "PRICE, A. L., Patterson, N. J., Plenge, R. M., Weinblatt, M. E., Shadick, N. A., & Reich, D. (2006). Principal components analysis corrects for stratification in genome-wide association studies. Nature Genetics, 38(8), 904–909.",
        "ROGERS, M., & Glendon, A. I. (2003). Blood type and personality. Personality and Individual Differences, 34(7), 1099–1112.",
        "SAKAMOTO, A., & Yamazaki, K. (2004). Blood-typical personality stereotypes and self-fulfilling prophecy: A multi-wave panel study in Japan. The Japanese Journal of Psychology, 75(5), 441–449.",
        "SCHELLING, T. C. (1971). Dynamic models of segregation. Journal of Mathematical Sociology, 1(2), 143–186.",
        "SHIMIZU, D., & Ishikawa, T. (2011). Relationships between ABO blood type and personality by the self-report and observer-report methods. The Japanese Journal of Personality, 20(1), 54–64.",
        "SPIRTES, P., Glymour, C. N., & Scheines, R. (2000). Causation, Prediction, and Search (2nd ed.). Cambridge, MA: MIT Press.",
        "WRIGHT, S. (1921). Systems of mating. III. Assortative mating based on somatic resemblance. Genetics, 6(2), 144–161.",
        "WU, K., Lindsted, K. D., & Lee, J. W. (2005). Blood type and the five factors of personality in Asia. Personality and Individual Differences, 38(4), 797–808.",
        "YAMAMOTO, F., Clausen, H., White, T., Marken, J., & Hakomori, S. (1990). Molecular genetic basis of the histo-blood group ABO system. Nature, 345(6272), 229–233."
    ]

    for ref in jasss_refs:
        p_ref = doc.add_paragraph()
        p_ref.paragraph_format.left_indent = Inches(0.5)
        p_ref.paragraph_format.first_line_indent = Inches(-0.5)
        p_ref.paragraph_format.space_after = Pt(4)
        p_ref.paragraph_format.line_spacing = 1.15
        r_rf = p_ref.add_run(ref)
        r_rf.font.size = Pt(10)

    if eq_style == "word_equation":
        filename = "Manuscript_JASSS_Anonymised_WordEquation.docx" if anonymised else "Manuscript_JASSS_Full_WordEquation.docx"
    else:
        filename = "Manuscript_JASSS_Anonymised.docx" if anonymised else "Manuscript_JASSS_Full.docx"
        
    out_path = os.path.join(PAPER_DIR, filename)
    try:
        doc.save(out_path)
        print(f"Saved: {out_path}")
    except PermissionError:
        print(f"[!] Notice: {out_path} is currently open in Word.")
        fallback_path = os.path.join(PAPER_DIR, filename.replace(".docx", "_updated.docx"))
        doc.save(fallback_path)
        print(f"Saved updated copy to: {fallback_path}")

if __name__ == '__main__':
    print("--- Generating JASSS Submission Manuscripts (Standard Formatting) ---")
    generate_jasss_doc(anonymised=False, eq_style="typographic")
    generate_jasss_doc(anonymised=True, eq_style="typographic")

