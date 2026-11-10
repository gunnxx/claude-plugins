# Figures that survive both renderers

Every figure is an inline `<svg>` in the HTML page. `html2tex.py` turns it into TikZ at the same
coordinates, so a figure that is clean in the browser is clean in the PDF only if it leaves room
for Computer Modern, which sets text a little wider than Source Serif and JetBrains Mono. The rules
below come from that constraint.

## Contents
1. What the converter understands
2. Layout
3. Text width budget
4. Arrows
5. Recipes for common diagrams
6. Checking

## 1. What the converter understands

Use only these elements. Anything else is skipped and will be missing from the PDF.

| Element | Attributes read | Notes |
| --- | --- | --- |
| `rect` | `x y width height rx class` | class picks the style |
| `line` | `x1 y1 x2 y2 class marker-start marker-end` | a marker on either end becomes an arrow tip |
| `polyline` | `points class marker-*` | for right-angle routes |
| `text` | `x y font-size text-anchor class` | one line per element, no `tspan` |
| `g` | `font-size text-anchor class` | inherited by children |

Classes (styled in the template's CSS and in `macros.sty`):

- boxes: `box` (neutral), `box-r` (first host, blue), `box-b` (second host, orange), `host-robot`, `host-brain` (large containers), `wire` (green band), `lan` (purple band), `dashed` (external or optional), `bar-a`, `bar-b` (timeline bars)
- lines: `arrow` (request, solid), `arrow-ret` (answer, dashed), `life` (lifeline or divider, dotted)
- text: `t-title` (bold), `t-mono` (identifier), `t-muted` (secondary line, grey)
- `class="halo"` on the `<svg>` itself puts a solid backing behind every label. Use it for sequence diagrams, where lifelines run behind arrow labels.

The colour names are semantic in the guide this skill came from (robot and brain). Reuse them for
any two-sided system, such as client and server, and say in the prose which colour is which.

Every `<svg>` carries `viewBox`, `role="img"`, a `<title>`, and its own marker id
(`ah1`, `ah2`, ...), since ids must be unique across the page.

## 2. Layout

- Width 900 to 1100 units. The PDF maps the viewBox width onto 16.5 cm, so 1000 units is
  about 0.165 mm per unit, and a 13 unit font is about 6 pt in print. Do not go below 11 units.
- Put everything on a grid you compute before writing. Write the coordinates down first
  (columns at x = 35 and 205, rows every 34 units), then write the elements. Ad hoc placement is
  how labels end up overlapping.
- A box holding one label is 26 to 30 units tall. A box with a title and a muted second line is
  60 to 70 units tall, title baseline at top + 26, second line at top + 46.
- Text baseline for a one-line box of height h is y + h/2 + 4.5 at font 13.
- Leave 10 units between any text and any box edge, line, or other text.

## 3. Text width budget

Estimate a label's width before placing it, with the PDF's wider fonts:

- serif: characters x font-size x 0.55
- mono (`t-mono`): characters x font-size x 0.62

A label must fit inside its box, or inside the gap between the two things its arrow joins, with
10 units to spare on each side. When it does not, in this order: split it into a title line and
a muted second line, shorten it, widen the gap, or lower the font one step. A 22 character label
at font 12 needs about 145 units, which is why lanes in a sequence diagram sit 150 units apart.

## 4. Arrows

- End an arrow 2 units short of the box edge it points at (`x2 = box_x - 2`), so the tip
  touches the border instead of entering it. Start it on the edge it leaves.
- Horizontal and vertical lines only, plus a polyline for an L-shaped route. A diagonal is allowed
  when no straight route exists, and then its label sits beside it with `text-anchor="end"` on the
  left side or `start` on the right side, at a y where you have checked the line's x.
- Arrow labels sit above a horizontal arrow (baseline 8 units above it) or beside a vertical one
  (10 units to its side). Two-line labels put the muted line 14 units below the first, both above
  the arrow.
- Bidirectional channels use both markers on one line. Request and answer pairs use two lines,
  25 units apart, solid then dashed.

## 5. Recipes for common diagrams

- **Deployment overview.** Two host boxes side by side with a 230 unit channel gap between them.
  Containers as a two-column grid of small boxes inside each host. Channels as labelled
  horizontal arrows in the gap, each with a title line and a muted line.
- **Planes or layers.** Full-width bands stacked vertically, 30 to 40 units apart. A band that
  exists on one side only is half width. Each band has a centred title and muted detail lines.
- **Sequence diagram.** Header boxes 120 wide, lanes 150 apart, dotted lifelines to the bottom,
  one message every 50 units, numbered labels (`1. sound`), self-actions as small boxes centred
  on the lifeline, `class="halo"` on the svg.
- **Loop or pipeline.** Six boxes 200 by 60 in two rows of three, 100 units between columns,
  arrows clockwise, labels on the arrows.
- **Data flow across a boundary.** A dashed horizontal divider with the two side names at its
  right end, components above and below, and a caption saying that every arrow crossing the
  divider crosses the boundary.
- **Timing.** A time axis with an arrow at the right, bars for intervals, dotted vertical markers
  for instants, and marker labels below the axis staggered by 16 units when two are close.

## 6. Checking

Screenshot the page and the PDF with `scripts/shoot.py` and look at every figure in both. In each,
check that no text touches a line or box edge, every arrow tip lands on the box it names, and
every label is inside its box. Fix the coordinates in the HTML, then rebuild the PDF, since the
PDF is generated from the HTML.
