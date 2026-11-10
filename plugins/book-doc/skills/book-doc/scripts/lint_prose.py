"""List prose lines of a book-doc HTML page that contain a colon, semicolon, en dash or em dash.

Code, preformatted blocks, SVG figures and math are skipped, since identifiers and formulas
may carry those characters. Exit 1 when anything is found.
Usage: python3 lint_prose.py <page.html>
"""
import html
import re
import sys

s = open(sys.argv[1]).read()
body = s[s.index("<main>"):s.index("</main>")]
for pat in (r"<svg.*?</svg>", r"<pre>.*?</pre>", r"<code>.*?</code>", r"\$\$.*?\$\$", r"\\\(.*?\\\)", r"<!--.*?-->"):
    body = re.sub(pat, "", body, flags=re.S)
text = html.unescape(re.sub(r"<[^>]+>", "", body))
bad = [line.strip() for line in text.splitlines() if re.search(r"[:;–—]", line)]
for line in bad:
    print(line[:200])
sys.exit(1 if bad else 0)
