---
name: book-doc
description: Write a self-contained, book-style technical guide as an HTML page with light and dark mode, inline SVG diagrams and KaTeX math, then convert it to LaTeX in the scribe-notes template (header block, Outline, contents, numbered sections) and render the PDF, with both checked visually. Use this whenever the user asks to document, explain or write up how a system, codebase, pipeline, protocol or algorithm works "as a book", "as a guide", "as lecture or scribe notes", "as HTML and PDF" or "with figures and math", or asks to reformat existing notes or a Markdown write-up into that style, even if they name only one of the two formats.
---

# Book-style documentation, HTML and PDF

The result is one HTML page that reads like a chapter of a textbook, and a PDF made from that same
page through LaTeX. A reader who knows the field but not the system should understand it from the
document alone, so the document carries its own vocabulary, figures and worked examples.

Bundled files, paths relative to this skill's folder:

| File | Use |
| --- | --- |
| `assets/template.html` | the page skeleton: theme tokens, dark mode, toggle, header block, Outline, contents, figure and table patterns |
| `assets/latex/macros.sty` | the scribe template header and the TikZ styles of the figures |
| `scripts/html2tex.py` | HTML to `main.tex`, every SVG to TikZ at the same coordinates |
| `scripts/build_pdf.sh` | runs the converter and pdflatex (local, else the TeX Live Docker image) |
| `scripts/lint_prose.py` | finds colons, semicolons and dashes in prose |
| `scripts/shoot.py` | screenshots the page in both themes, and PDF pages, as PNG slices |
| `references/figures.md` | how to draw figures that stay aligned in both renderers. Read it before the first figure |

## 1. Research before writing

Every statement must be traceable to a source the user can open. Read the code, configs, READMEs
and start commands that define the behaviour, not summaries of them. Note the file path behind
each fact as you go, since the reading list at the end is built from those notes. When something
cannot be confirmed, say so in the text, and never fill a gap with a plausible number or name.
For a large codebase, a subagent can map the territory, but read the key files yourself, because
the explanations depend on details a summary drops.

## 2. Plan the outline

Follow the scribe template's order, which the converter relies on:

1. A header block of three rows, each with a left and a right cell. Typically the organization,
   the subject and the version on the left, and the reader, a notes number and the date on the
   right. Use the real date in full (`November 5, 2026`).
2. A title (`h1`).
3. An Outline paragraph that walks through the chapters in order.
4. Contents (the `nav.toc`), then numbered chapters (`h2`) and sections (`h3`).
5. Optionally appendices, as an `h2` whose text begins `Appendix. `.

Order chapters from the outside in: what the system is and its vocabulary, its parts, how the parts
communicate, then the central question the user asked, answered in full, then worked traces of
concrete cases, then cross-cutting rules, then a reading list of source files.

## 3. Write the HTML

Copy `assets/template.html` to the output folder and replace its sample content. Keep the `<head>`,
the CSS tokens, the dark-mode blocks, the toggle script and the class names, since the converter
and the figure styles depend on them. Set `<title>` to a two to four word name.

Write the prose like a book:

- Complete sentences with proper grammar and conjugation, in paragraphs that build on each other.
- No colons, no semicolons and no em or en dashes in prose. Join ideas with a period or a
  conjunction instead. Bold run-in heads end with a period (`<b>Step 3. Transcription.</b>`), and
  captions read `Figure 2. The four planes.` Identifiers, commands and math may contain any
  character, because the lint skips them.
- Define each term before its first use, in a vocabulary list (`dl`) or in the sentence itself.
- Use mathematics where it says something more precisely than words. A bound, a set, a decomposition
  of a vector or a timing budget. Introduce each symbol in the sentence before the display.
  Inline math is `\( ... \)`, display math is `$$ ... $$` on its own line between elements.
- One figure for each idea that has a shape, such as topology, a sequence over time, a loop, a
  boundary or a timeline. Each has a caption sentence and is referred to from the text before it
  appears. Follow `references/figures.md`.
- Tables for parallel facts, such as services, ports or file paths. A table of services uses
  `<table class="svc">` with the columns Service, Module, ROS (or another short flag), Start
  command, What it does. Other tables have two or four columns. The converter sets widths for those
  counts, so check the PDF when you use another count.
- Identifiers in `<code>`. Commands and payloads in `<pre><code>`.
- Numbered and bulleted lists (`ol`, `ul`) are fine and become `enumerate` and `itemize`. Keep
  each `pre` line under about 80 characters, or the PDF build reports an overfull box.
- A double hyphen in a figure label (`up --wait`) goes in a `t-mono` text, because a serif
  font joins the two hyphens into a dash.

## 4. Check the page

```bash
python3 <skill>/scripts/lint_prose.py page.html
uv run --no-project --with pillow --with pymupdf python <skill>/scripts/shoot.py page.html <shots_dir>
```

Fix every line the lint prints. Read each PNG slice, in both themes, and look at every figure and
table. Text must not touch lines or box edges, arrow tips must land on their targets, and tables must
not break identifiers in the middle of a word. Fix and shoot again until all of that holds. The
screenshot folder is scratch, so delete it afterwards.

## 5. Build and check the PDF

```bash
<skill>/scripts/build_pdf.sh page.html <out_dir>
uv run --no-project --with pillow --with pymupdf python <skill>/scripts/shoot.py <out_dir>/latex/main.pdf <shots_dir>
```

The build fails on any LaTeX error or overfull box, and prints it. Common causes:

- An identifier in a caption. The converter already wraps it in `\protect`, so look for a
  `<code>` in a heading instead and move it into the text.
- A table too wide. Shorten the cell text, or adjust the widths in `table_tex` in
  `html2tex.py`, which must sum to about 14.5 cm plus the column padding.
- A figure label touching a line in the PDF only. Computer Modern is wider, so give the label more
  room in the SVG. Do not patch the TikZ, since the next build overwrites it.

Read the PDF pages that hold figures and tables, and fix the HTML until they are clean too.

## 6. Deliver

Put the files where the user asked. When they name no place, use the session's scratchpad. The
delivered set is the HTML page, the PDF, and the `latex/` folder with `main.tex` and `macros.sty`,
so the user can edit and recompile. Report the absolute paths, what the document covers, and
anything you could not verify. If the user later asks to change the content, edit the HTML and run
the build again, so the two formats never drift apart.

When the user gives a different LaTeX template, keep the converter and change only `macros.sty` to
that template's header and fonts, since the body structure (sections, figures, longtables) is
standard LaTeX.
