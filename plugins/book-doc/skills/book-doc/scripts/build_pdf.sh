#!/usr/bin/env bash
# Build the PDF from a book-doc HTML page.
# Usage: build_pdf.sh <page.html> <out_dir>
# Writes <out_dir>/latex/{main.tex,macros.sty,main.pdf}. Uses a local pdflatex when present,
# else the texlive/texlive:latest-medium Docker image. Fails on any LaTeX error or overfull box.
set -euo pipefail
[ $# -eq 2 ] || { echo "usage: build_pdf.sh <page.html> <out_dir>" >&2; exit 2; }
page=$(realpath "$1"); out=$(realpath -m "$2")
[ -f "$page" ] || { echo "no such page: $page" >&2; exit 2; }
here=$(dirname "$(realpath "$0")")
mkdir -p "$out/latex"
cp "$here/../assets/latex/macros.sty" "$out/latex/"
uv run --no-project --with beautifulsoup4 python "$here/html2tex.py" "$page" "$out/latex/main.tex"
cd "$out/latex"
run='pdflatex -interaction=nonstopmode -halt-on-error main.tex >/dev/null && pdflatex -interaction=nonstopmode -halt-on-error main.tex > build.log'
if command -v pdflatex >/dev/null; then
  sh -c "$run" || { grep -A3 '^!' main.log >&2; exit 1; }
else
  docker run --rm -u "$(id -u):$(id -g)" -v "$PWD":/w -w /w texlive/texlive:latest-medium sh -c "$run" \
    || { grep -A3 '^!' main.log >&2; exit 1; }
fi
if grep -q 'Overfull' build.log; then grep -A2 'Overfull' build.log >&2; echo "overfull boxes: narrow the table widths in html2tex.py or shorten the line" >&2; exit 1; fi
echo "built $out/latex/main.pdf"
