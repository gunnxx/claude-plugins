"""Convert a book-doc HTML page into a LaTeX main.tex, each inline SVG into TikZ at the same coordinates.

Usage: html2tex.py <page.html> <out/main.tex>
The header block's three rows fill the template header (left cells, then right cells).
The output needs macros.sty from the skill's assets/latex beside it.
"""
import re
import sys
import xml.etree.ElementTree as ET
from html import unescape

from bs4 import BeautifulSoup, NavigableString, Tag

SRC, OUT = sys.argv[1], sys.argv[2]
TEXTWIDTH_CM = 16.5
FONT_SCALE = 1.0  # the SVG font sizes, which keep every label inside its box in Computer Modern

SPECIAL = {"&": r"\&", "%": r"\%", "#": r"\#", "_": r"\_", "~": r"\textasciitilde{}",
           "^": r"\textasciicircum{}", "\\": r"\textbackslash{}", "{": r"\{", "}": r"\}",
           "<": r"\textless{}", ">": r"\textgreater{}"}


def esc(s):
    s = "".join(SPECIAL.get(c, c) for c in s)
    s = re.sub(r'"([^"]*)"', r"``\1''", s)
    return s.replace("--", "-{}-")  # keep a double hyphen, not an en dash


def esc_math_aware(s):
    """Escape prose but keep \\( ... \\) math as written."""
    parts = re.split(r"(\\\(.*?\\\))", s, flags=re.S)
    return "".join(p if p.startswith("\\(") else esc(p) for p in parts)


def code(s):
    s = s.replace("\u200b", "")
    if " " in s.strip():
        return " ".join(code(part) for part in s.split())
    if any(c in s for c in "{}"):
        return r"\texttt{" + esc(s) + "}"
    return r"\code{" + s + "}"


def inline(node):
    out = []
    for ch in node.children:
        if isinstance(ch, NavigableString):
            out.append(esc_math_aware(str(ch)))
        elif ch.name == "code":
            out.append(code(ch.get_text()))
        elif ch.name == "b":
            out.append(r"\textbf{" + inline(ch) + "}")
        elif ch.name == "em":
            out.append(r"\emph{" + inline(ch) + "}")
        elif ch.name == "wbr":
            continue
        elif ch.name == "span":
            out.append(inline(ch))
        else:
            out.append(inline(ch))
    return "".join(out)


# ---------------- SVG to TikZ ----------------
NS = "{http://www.w3.org/2000/svg}"


def svg_to_tikz(svg_html):
    svg_html = re.sub(r"<title[^>]*>.*?</title>", "", svg_html, flags=re.S)
    svg_html = svg_html.replace("<svg ", '<svg xmlns="http://www.w3.org/2000/svg" ', 1)
    root = ET.fromstring(svg_html)
    vb = [float(v) for v in (root.get("viewBox") or root.get("viewbox")).split()]
    scale = TEXTWIDTH_CM / vb[2]
    pt_per_px = scale * 28.4528 * FONT_SCALE
    halo = ",fill=white,inner sep=0.6pt" if "halo" in (root.get("class") or "") else ",inner sep=0pt"
    lines = [rf"\begin{{tikzpicture}}[x={scale:.5f}cm,y=-{scale:.5f}cm]"]

    def walk(el, size, anchor, klass):
        tag = el.tag.replace(NS, "")
        size = float(el.get("font-size", size))
        anchor = el.get("text-anchor", anchor)
        cls = (el.get("class") or "").split()
        if tag in ("defs", "marker"):
            return
        if tag == "rect":
            x, y, w, h = (float(el.get(k)) for k in ("x", "y", "width", "height"))
            rx = float(el.get("rx", 0))
            style = cls[0] if cls else "box"
            style = "dashed-box" if style == "dashed" else style
            rc = f",rounded corners={rx * scale:.3f}cm" if rx else ""
            lines.append(rf"\path[{style}{rc}] ({x:g},{y:g}) rectangle ({x + w:g},{y + h:g});")
        elif tag in ("line", "polyline"):
            if tag == "line":
                pts = [(el.get("x1"), el.get("y1")), (el.get("x2"), el.get("y2"))]
            else:
                pts = [p.split(",") for p in el.get("points").split()]
            start, end = el.get("marker-start"), el.get("marker-end")
            tip = "<->" if start and end else "->" if end else "<-" if start else "-"
            style = {"life": "life", "dashed": "life", "arrow-ret": "arrow-ret"}.get(cls[0] if cls else "", "arrow")
            path = " -- ".join(f"({float(a):g},{float(b):g})" for a, b in pts)
            lines.append(rf"\draw[{style},{tip}] {path};")
        elif tag == "text":
            x, y = float(el.get("x")), float(el.get("y"))
            all_cls = cls + klass
            fs = size * pt_per_px
            font = rf"\fontsize{{{fs:.2f}pt}}{{{fs * 1.15:.2f}pt}}\selectfont"
            if "t-mono" in all_cls:
                font += r"\ttfamily"
            if "t-title" in all_cls:
                font += r"\bfseries"
            color = ",text=figmuted" if "t-muted" in all_cls else ""
            node_anchor = {"middle": "base", "start": "base west", "end": "base east"}[anchor]
            txt = esc("".join(el.itertext()))
            lines.append(rf"\node[anchor={node_anchor}{halo},font={font}{color}] at ({x:g},{y:g}) {{{txt}}};")
            return
        for ch in el:
            walk(ch, size, anchor, cls if tag == "g" else klass)

    for ch in root:
        walk(ch, 16.0, "start", [])
    lines.append(r"\end{tikzpicture}")
    return "\n".join(lines)


# ---------------- document ----------------
html = open(SRC).read()
soup = BeautifulSoup(html, "html.parser")
main = soup.find("main")
body = []
appendix = False


def strip_prefix(text, word):
    return re.sub(rf"^{word} \w+\.\s*", "", text.strip())


def table_tex(wrap):
    table = wrap.find("table")
    rows = [[c for c in tr.find_all(["th", "td"])] for tr in table.find_all("tr")]
    head, data = rows[0], rows[1:]
    cap = table.find("caption")
    cap_tex = inline(cap).strip()
    cap_tex = re.sub(r"^Table \d+\.\s*", "", cap_tex).replace(r"\code{", r"\protect\code{")
    n = len(head)
    if "svc" in (table.get("class") or []):
        spec = r"@{}>{\raggedright}p{2.2cm}>{\raggedright}p{2.5cm}>{\raggedright}p{0.9cm}>{\raggedright}p{3.4cm}>{\raggedright\arraybackslash}p{6.3cm}@{}"
        size = r"\footnotesize\setlength{\tabcolsep}{4pt}"
    else:
        widths = {4: [2.4, 3.2, 3.3, 5.8], 2: [6.4, 8.8]}.get(n, [16.0 / n] * n)
        last = r"\arraybackslash"
        spec = "@{}" + "".join(">{\\raggedright" + (last if i == n - 1 else "") + "}p{" + f"{w}cm" + "}" for i, w in enumerate(widths)) + "@{}"
        size = r"\small"
    hdr = " & ".join(r"\textbf{" + inline(c) + "}" for c in head) + r" \\"
    out = [r"\begingroup" + size, rf"\begin{{longtable}}{{{spec}}}",
           rf"\caption{{{cap_tex}}}\\", r"\toprule", hdr, r"\midrule", r"\endfirsthead",
           r"\toprule", hdr, r"\midrule", r"\endhead"]
    for r in data:
        out.append(" & ".join(inline(c).strip() for c in r) + r" \\")
    out += [r"\bottomrule", r"\end{longtable}", r"\endgroup"]
    return "\n".join(out)


for el in main.children:
    if isinstance(el, NavigableString):
        s = str(el).strip()
        if s.startswith("$$"):
            body.append(r"\[" + s.strip("$").strip() + r"\]")
        continue
    if not isinstance(el, Tag):
        continue
    cls = el.get("class") or []
    if "header-block" in cls or el.name in ("h1", "nav") or "outline" in cls:
        continue
    if el.name == "h2":
        num = el.find("span", class_="num")
        num.extract()
        title = el.get_text().strip()
        if title.startswith("Appendix"):
            body.append(r"\appendix")
            title = title.replace("Appendix. ", "")
        body.append(rf"\section{{{esc(title)}}}")
    elif el.name == "h3":
        el.find("span", class_="num").extract()
        body.append(rf"\subsection{{{esc(el.get_text().strip())}}}")
    elif el.name == "p":
        body.append(inline(el).strip())
    elif el.name == "pre":
        body.append("\\begin{verbatim}\n" + unescape(el.get_text()).strip("\n") + "\n\\end{verbatim}")
    elif el.name in ("ol", "ul"):
        env = "enumerate" if el.name == "ol" else "itemize"
        items = [r"\item " + inline(li).strip() for li in el.find_all("li", recursive=False)]
        body.append(f"\\begin{{{env}}}[leftmargin=1.6em,itemsep=2pt]\n" + "\n".join(items) + f"\n\\end{{{env}}}")
    elif el.name == "dl":
        items = []
        for dt in el.find_all("dt"):
            dd = dt.find_next_sibling("dd")
            items.append(rf"\item[{inline(dt)}] {inline(dd)}")
        body.append("\\begin{description}[leftmargin=1.2em,style=nextline]\n" + "\n".join(items) + "\n\\end{description}")
    elif el.name == "div" and "callout" in cls:
        body.append("\\begin{callout}\n" + "\n\n".join(inline(p).strip() for p in el.find_all("p")) + "\n\\end{callout}")
    elif el.name == "div" and "table-wrap" in cls:
        body.append(table_tex(el))
    elif el.name == "figure":
        svg = str(el.find("svg"))
        cap = re.sub(r"^Figure \d+\.\s*", "", inline(el.find("figcaption")).strip()).replace(r"\code{", r"\protect\code{")
        body.append("\\begin{figure}[htbp]\n\\centering\n" + svg_to_tikz(svg) + f"\n\\caption{{{cap}}}\n\\end{{figure}}")
    else:
        raise SystemExit(f"unhandled element {el.name} {cls}")

outline = inline(main.find("p", class_="outline")).replace(r"\textbf{Outline}", "").strip()
title = esc(main.find("h1").get_text().strip())

rows = [[inline(c).strip() for c in r.find_all("span", recursive=False)] for r in main.find("div", class_="header-block").find_all("div", class_="header-row")]
if len(rows) != 3 or any(len(r) != 2 for r in rows):
    raise SystemExit("header-block must hold three header-row divs of two spans each")
doc = rf"""\documentclass[11pt]{{article}}
\usepackage{{macros}}
\parindent0in
\pagestyle{{plain}}
\thispagestyle{{plain}}
\institution{{{rows[0][0]}}}
\course{{{rows[1][0]}}}
\release{{{rows[2][0]}}}
\scribedby{{{rows[0][1]}}}
\assignment{{{rows[1][1]}}}
\lecturedate{{{rows[2][1]}}}
\doctitle{{{title}}}
\begin{{document}}
\maketitle
\outline{{{outline}}}\par
\tableofcontents
\clearpage

""" + "\n\n".join(body) + "\n\n\\end{document}\n"
open(OUT, "w").write(doc)
print("wrote", OUT, len(doc), "bytes")
