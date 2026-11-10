"""Render a book-doc HTML page or PDF to PNG slices for visual checking.

HTML: headless Firefox screenshots the page at 1000 px wide, in light and in dark mode, and cuts
it into slices of 1300 px. PDF: each page (or the pages given) at 150 dpi.
Usage:
  uv run --no-project --with pillow --with pymupdf python shoot.py <page.html|doc.pdf> <out_dir> [first-last]
Prints the PNG paths. Read them with the Read tool. Snap Firefox cannot read /tmp, so the page is
copied into a folder under $HOME first, and that folder is removed afterwards.
"""
import os
import shutil
import subprocess
import sys
import tempfile

src, out = os.path.realpath(sys.argv[1]), os.path.realpath(sys.argv[2])
os.makedirs(out, exist_ok=True)
paths = []
if src.endswith(".pdf"):
    import pymupdf
    doc = pymupdf.open(src)
    first, last = 1, doc.page_count
    if len(sys.argv) > 3:
        first, last = (int(v) for v in sys.argv[3].split("-"))
    for n in range(first, last + 1):
        p = os.path.join(out, f"pdf-p{n:02d}.png")
        doc[n - 1].get_pixmap(dpi=150).save(p)
        paths.append(p)
else:
    from PIL import Image
    work = tempfile.mkdtemp(prefix="book-doc-shot-", dir=os.path.expanduser("~"))
    try:
        for theme in ("light", "dark"):
            page = os.path.join(work, f"{theme}.html")
            html = open(src).read()
            if theme == "dark":
                html = html.replace('<html lang="en">', '<html lang="en" data-theme="dark">', 1)
            open(page, "w").write(html)
            prof = os.path.join(work, f"prof-{theme}")
            os.makedirs(prof)
            shot = os.path.join(work, f"{theme}.png")
            subprocess.run(["firefox", "--headless", "--no-remote", "--profile", prof, "--window-size", "1000,24000",
                            "--screenshot", shot, "file://" + page], check=True, timeout=120,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            im = Image.open(shot).convert("RGB")
            px, h = im.load(), im.height
            bottom = h - 1
            while bottom > 0 and all(px[x, bottom] == px[5, bottom] for x in range(0, 1000, 20)):
                bottom -= 1
            for i, y in enumerate(range(0, bottom + 1, 1300)):
                p = os.path.join(out, f"html-{theme}-{i:02d}.png")
                im.crop((0, y, 1000, min(bottom + 1, y + 1300))).save(p)
                paths.append(p)
    finally:
        shutil.rmtree(work)
print("\n".join(paths))
