#!/usr/bin/env python3
"""Create the print-native portfolio PDF from the project TOML data.

The PDF is composed with ReportLab flowables and selectable text. It does not
print, screenshot, or otherwise depend on the generated website.
"""

from __future__ import annotations

import io
import os
import re
import shutil
import subprocess
from itertools import product
from functools import lru_cache
from html import escape
from pathlib import Path

from PIL import Image as PILImage
from PIL import ImageOps
import reportlab
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from pdf_fonts import register_site_font

from reportlab.platypus import (
    BaseDocTemplate,
    Flowable,
    Frame,
    Indenter,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.flowables import _listWrapOn


ROOT = Path(__file__).resolve().parent
OUTPUT_PATH = ROOT / "output" / "pdf" / "ef-portfolio.pdf"

PAGE_WIDTH, PAGE_HEIGHT = LETTER
MARGIN_X = 0.67 * inch
MARGIN_TOP = 0.95 * inch
MARGIN_BOTTOM = 0.65 * inch
CONTENT_WIDTH = PAGE_WIDTH - (2 * MARGIN_X)
MIN_COMPACT_GALLERY_CELL_WIDTH = 2 * inch

PAPER = colors.HexColor("#fcfcfb")
INK = colors.HexColor("#292b27")
MUTED = colors.HexColor("#73756f")
PRINT_MUTED = colors.HexColor("#60635d")
RULE = colors.HexColor("#dedfd9")
SURFACE = colors.HexColor("#f3f4f0")

MOTION_EXTENSIONS = {".gif", ".mp4", ".mov", ".m4v", ".webm", ".avi"}
VIDEO_EXTENSIONS = MOTION_EXTENSIONS - {".gif"}


def _register_fonts() -> tuple[str, str]:
    for name in ("EF-Regular", "EF-Bold", "Icons"):
        register_site_font(name, ROOT / "assets" / "fonts" / f"{name}.otf")
    pdfmetrics.registerFontFamily(
        "EF-Regular", normal="EF-Regular", bold="EF-Bold",
        italic="EF-Regular", boldItalic="EF-Bold",
    )
    pdfmetrics.registerFontFamily(
        "EF-Bold", normal="EF-Bold", bold="EF-Bold",
        italic="EF-Bold", boldItalic="EF-Bold",
    )
    font_dir = Path(reportlab.__file__).resolve().parent / "fonts"
    pdfmetrics.registerFont(TTFont("EF-Body", font_dir / "Vera.ttf"))
    pdfmetrics.registerFont(TTFont("EF-Body-Bold", font_dir / "VeraBd.ttf"))
    pdfmetrics.registerFontFamily(
        "EF-Body", normal="EF-Body", bold="EF-Body-Bold",
        italic="EF-Body", boldItalic="EF-Body-Bold",
    )
    return "EF-Regular", "EF-Bold"


FONT_REGULAR, FONT_BOLD = _register_fonts()
BODY_FONT = "EF-Body"
HAND_CHARACTERS = set(pdfmetrics.getFont(FONT_REGULAR).face.charToGlyph) & set(
    pdfmetrics.getFont(FONT_BOLD).face.charToGlyph
)
BODY_CHARACTERS = set(pdfmetrics.getFont(BODY_FONT).face.charToGlyph)


def _text(value: object) -> str:
    """Normalize TOML copy for print and escape ReportLab paragraph markup."""
    normalized = str(value or "").replace("\u00a0", " ")
    normalized = normalized.replace("\u2014", " - ").replace("\u2013", "-").replace("\u2011", "-")
    normalized = re.sub(r"[ \t]+", " ", normalized)
    output = []
    for char in normalized.strip():
        if char == "\n":
            output.append("<br/>")
        elif ord(char) in HAND_CHARACTERS:
            output.append(escape(char))
        elif ord(char) in BODY_CHARACTERS:
            output.append(f'<font name="{BODY_FONT}">{escape(char)}</font>')
        else:
            raise ValueError(f"PDF fonts do not contain {char!r} (U+{ord(char):04X}).")
    return "".join(output)


def _plain(value: object) -> str:
    normalized = str(value or "").replace("\u00a0", " ")
    return normalized.replace("\u2014", " - ").replace("\u2013", "-").replace("\u2011", "-").strip()


def _style(name, font, size, leading, color=INK, **kwargs):
    return ParagraphStyle(name, fontName=font, fontSize=size, leading=leading,
                          textColor=color, **kwargs)


STYLES = {
    "kicker": _style("Kicker", BODY_FONT, 7.5, 11, MUTED, spaceAfter=5, keepWithNext=True),
    "cover_title": _style("CoverTitle", FONT_BOLD, 34, 42, spaceAfter=8),
    "cover_deck": _style("CoverDeck", BODY_FONT, 10, 16, MUTED),
    "project_title": _style("ProjectTitle", FONT_BOLD, 30, 38, spaceAfter=6, keepWithNext=True),
    "project_meta": _style("ProjectMeta", BODY_FONT, 8.5, 13, PRINT_MUTED),
    "section_title": _style("SectionTitle", FONT_BOLD, 17.5, 23, spaceAfter=8, keepWithNext=True),
    "body": _style("Body", BODY_FONT, 10, 15.5, PRINT_MUTED, spaceAfter=8),
    "small": _style("Small", BODY_FONT, 8.2, 12, PRINT_MUTED),
    "small_bold": _style("SmallBold", FONT_BOLD, 16, 20, spaceAfter=3),
    "caption": _style("Caption", FONT_REGULAR, 11.5, 15, PRINT_MUTED),
    "motion": _style("Motion", BODY_FONT, 7.4, 10.5, PRINT_MUTED),
    "note_title": _style("NoteTitle", FONT_REGULAR, 13, 16, spaceAfter=5),
    "quote": _style("Quote", FONT_REGULAR, 23, 30, alignment=TA_CENTER),
}


def _styles(theme="paper"):
    if theme != "dark":
        return STYLES
    secondary = {"body", "small", "caption", "motion", "project_meta", "kicker"}
    return {key: ParagraphStyle(
        f"{style.name}Dark", parent=style,
        textColor=colors.HexColor("#c6c8c0") if key in secondary else PAPER,
    ) for key, style in STYLES.items()}


class InvariantCanvas(canvas.Canvas):
    """A compressed, reproducible canvas suitable for build freshness checks."""

    def __init__(self, *args, **kwargs):
        kwargs["invariant"] = 1
        kwargs.setdefault("pageCompression", 1)
        kwargs.setdefault("initialFontName", FONT_REGULAR)
        kwargs.setdefault("initialFontSize", 9)
        kwargs.setdefault("initialLeading", 12)
        kwargs.setdefault("lang", "en")
        super().__init__(*args, **kwargs)


class ProjectAnchor(Flowable):
    def __init__(self, slug: str, title: str) -> None:
        super().__init__()
        self.slug = slug
        self.title = title
        self.width = 0
        self.height = 0

    def draw(self) -> None:
        key = f"project-{self.slug}"
        self.canv.bookmarkPage(key)
        self.canv.addOutlineEntry(self.title, key, level=0, closed=False)


def _asset_path(value: object) -> Path | None:
    source = str(value or "")
    if not source or source.startswith(("http://", "https://", "data:")):
        return None
    relative = Path(source.lstrip("/"))
    if ".." in relative.parts:
        return None
    direct = ROOT / relative
    if direct.is_file():
        return direct
    shorthand = ROOT / "assets" / "images" / relative
    return shorthand if shorthand.is_file() else None


@lru_cache(maxsize=128)
def _prepared_image(path_string: str) -> tuple[bytes, int, int]:
    """Keep transparent CAD artwork on the paper and photos compact."""
    source_file = path_string
    if Path(path_string).suffix.lower() in VIDEO_EXTENSIONS:
        ffmpeg = shutil.which("ffmpeg")
        if not ffmpeg:
            raise RuntimeError("PDF video stills require ffmpeg. Install it before building the PDF.")
        result = subprocess.run(
            [ffmpeg, "-v", "error", "-i", path_string, "-vf",
             "thumbnail=30,scale=1280:1280:force_original_aspect_ratio=decrease",
             "-frames:v", "1", "-threads", "1", "-f", "image2pipe", "-vcodec", "png", "pipe:1"],
            check=True, capture_output=True, timeout=60,
        )
        source_file = io.BytesIO(result.stdout)
    with PILImage.open(source_file) as source:
        source.seek(0)
        image = ImageOps.exif_transpose(source).convert("RGBA")
        # About 180-250 dpi at these printed sizes, without oversized uploads.
        image.thumbnail((1280, 1280), PILImage.Resampling.LANCZOS)
        output = io.BytesIO()
        if image.getextrema()[3][0] < 255:
            image.save(output, format="PNG", optimize=True)
        else:
            image.convert("RGB").save(output, format="JPEG", quality=90, optimize=True)
        return output.getvalue(), image.width, image.height


def _table(rows, widths, **kwargs):
    table = Table(rows, colWidths=widths, hAlign="LEFT", **kwargs)
    table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return table


def _position(value):
    words = str(value or "50% 50%").split()
    positions = {"left": 0, "top": 0, "center": .5, "right": 1, "bottom": 1}
    def fraction(word):
        if word in positions:
            return positions[word]
        try:
            return max(0, min(1, float(word.rstrip("%")) / 100))
        except ValueError:
            return .5
    if len(words) == 1:
        return (.5, fraction(words[0])) if words[0] in {"top", "bottom"} else (fraction(words[0]), .5)
    return fraction(words[0]), fraction(words[1])


class MediaFrame(Flowable):
    def __init__(self, path, item, width, max_height):
        super().__init__()
        data, pw, ph = _prepared_image(str(path.resolve()))
        self.image = ImageReader(io.BytesIO(data))
        self.width = width
        ratios = {"landscape": 3/2, "portrait": 4/5, "square": 1, "wide": 16/9}
        ratio = ratios.get(item.get("ratio"), pw / ph)
        zoom = max(.01, float(item.get("scale", 1)))
        natural = item.get("ratio", "natural") == "natural"
        layout_scale = min(zoom, 1) if natural else 1
        layout_width = width*layout_scale
        self.height = min(max_height, layout_width / ratio)
        fit = item.get("fit", "cover" if item.get("ratio") in ratios else "contain")
        scale = max(layout_width / pw, self.height / ph) if fit == "cover" else min(layout_width / pw, self.height / ph)
        self.render_width, self.render_height = pw * scale * zoom/layout_scale, ph * scale * zoom/layout_scale
        self.position = _position(item.get("position"))
        self.background = item.get("background")
        from build import has_elevated_image_surface
        self.elevated = has_elevated_image_surface(item) and (
            not data.startswith(b"\x89PNG") or item.get("surface") == "elevated"
        )
        # A natural image's caption should sit under the actual image, rather
        # than under empty space left by the print height limit.
        self.frame_width = min(width, self.render_width) if natural else width
        self.frame_x = (width-self.frame_width)*self.position[0]

    def draw(self):
        c = self.canv
        c.saveState()
        if self.elevated:
            # Graduated translucent contours give photos a soft lift at print
            # resolution without rasterizing the photograph or its caption.
            c.saveState()
            c.setFillColor(colors.HexColor("#1f221c"))
            for spread in (4, 3.5, 3, 2.5, 2, 1.5, 1, .5):
                c.setFillAlpha(.012)
                c.roundRect(self.frame_x-spread, -1.5-spread,
                            self.frame_width+2*spread, self.height+2*spread,
                            3.5+spread, fill=1, stroke=0)
            c.restoreState()
        clip = c.beginPath()
        if self.elevated:
            clip.roundRect(self.frame_x, 0, self.frame_width, self.height, 3.5)
        else:
            clip.rect(0, 0, self.width, self.height)
        c.clipPath(clip, stroke=0)
        if self.background:
            c.setFillColor(colors.HexColor(self.background))
            c.rect(0, 0, self.width, self.height, fill=1, stroke=0)
        px, py = self.position
        c.drawImage(self.image, (self.width-self.render_width)*px,
                    (self.height-self.render_height)*(1-py),
                    self.render_width, self.render_height, mask="auto")
        c.restoreState()


class Tilted(Flowable):
    """The same slight, alternating image tilt as the site's galleries."""
    def __init__(self, content, width, angle):
        super().__init__()
        self.content, self.width, self.angle = content, width, angle

    def wrap(self, availWidth, availHeight):
        _, self.content_height = self.content.wrap(self.width, 10000)
        self.height = self.content_height + 8
        return self.width, self.height

    def draw(self):
        self.canv.saveState()
        self.canv.translate(self.width/2, self.height/2)
        self.canv.rotate(self.angle)
        self.content.drawOn(self.canv, -self.width/2, -self.content_height/2)
        self.canv.restoreState()


def _motion_note(source):
    extension = Path(str(source or "")).suffix.lower()
    if extension == ".gif":
        return "Animation - first frame shown."
    if extension in VIDEO_EXTENSIONS:
        return "Video still - motion on the website."
    return ""


def _media_item(item, width, max_height, styles=None, angle=0):
    styles = styles or STYLES
    source = item.get("src", "")
    path = _asset_path(source)
    if item.get("placeholder") or path is None:
        label = item.get("placeholder") or _motion_note(source) or "Media available on the website."
        visual = _table([[Paragraph(_text(label), styles["caption"])]], [width],
                        rowHeights=[min(max_height, 1.2*inch)])
        visual.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), SURFACE if styles is STYLES else colors.HexColor("#343631")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ]))
    else:
        visual = MediaFrame(path, item, width, max_height)
    rows = [[visual]]
    caption_inset = visual.frame_x if isinstance(visual, MediaFrame) else 0
    if item.get("caption"):
        rows.extend([[Spacer(1, 5)], [Paragraph(_text(item["caption"]), styles["caption"])]])
    if _motion_note(source) and path is not None:
        rows.extend([[Spacer(1, 4)], [Paragraph(_text(_motion_note(source)), styles["motion"])]])
    card = _table(rows, [width])
    if len(rows) > 1 and isinstance(visual, MediaFrame) and visual.frame_width < width:
        card.setStyle(TableStyle([
            ("LEFTPADDING", (0, 1), (-1, -1), caption_inset),
            ("RIGHTPADDING", (0, 1), (-1, -1), width-visual.frame_width-caption_inset),
        ]))
    return Tilted(card, width, angle) if angle else card


def _paragraphs(value: object, style: ParagraphStyle | None = None) -> list[Paragraph]:
    if value is None:
        return []
    values = value if isinstance(value, list) else [value]
    output: list[Paragraph] = []
    for item in values:
        for block in re.split(r"\n\s*\n", str(item)):
            if block.strip():
                output.append(Paragraph(_text(block), style or STYLES["body"]))
    return output


def _section_heading(section, styles=None):
    styles = styles or STYLES
    heading = []
    if section.get("eyebrow"):
        heading.append(Paragraph(_text(section["eyebrow"]), styles["kicker"]))
    if section.get("title"):
        heading.append(Paragraph(_text(section["title"]), styles["section_title"]))
    return heading


def _section_images(section):
    images = section.get("images", [])
    if isinstance(images, dict):
        images = [images]
    return [{"src": item} if isinstance(item, str) else dict(item) for item in images]


def _compact_gallery_columns(image_count, width=CONTENT_WIDTH, gap=16):
    """Add columns only while every gallery cell remains useful at print size."""
    columns_by_width = int((width + gap) // (MIN_COMPACT_GALLERY_CELL_WIDTH + gap))
    return max(1, min(4, image_count, columns_by_width))


def _gallery(
    images,
    columns,
    width=CONTENT_WIDTH,
    layout="grid",
    styles=None,
    max_image_height=2.5 * inch,
    row_gap=12,
):
    if not images:
        return Spacer(1, 0)
    columns = max(1, min(columns, 4, len(images)))
    gap = 16
    cell_width = (width - gap * (columns - 1)) / columns
    cells = [_media_item(item, cell_width, max_image_height, styles,
                         angle=0 if layout == "filmstrip" else (-.7, .9, -.35)[i % 3])
             for i, item in enumerate(images)]
    widths = [value for i in range(columns) for value in ([cell_width, gap] if i < columns-1 else [cell_width])]
    rows = []
    if layout == "collage":
        # Balanced natural-height columns, in the same down-column order as CSS.
        # Bound each panel to three images per column so a gallery can paginate.
        for start in range(0, len(cells), columns*3):
            panel = cells[start:start+columns*3]
            heights = [cell.wrap(cell_width, 10000)[1]+12 for cell in panel]
            groups, cursor = [], 0
            for column in range(columns):
                remaining_columns = columns-column
                target = sum(heights[cursor:]) / remaining_columns
                group, height = [], 0
                while cursor < len(panel):
                    if group and (len(panel)-cursor < remaining_columns or
                                  abs(height-target) < abs(height+heights[cursor]-target)):
                        break
                    group.extend([panel[cursor], Spacer(1, 12)])
                    height += heights[cursor]
                    cursor += 1
                groups.append(group)
            row = []
            for i, group in enumerate(groups):
                row.append(group)
                if i < columns-1:
                    row.append("")
            rows.append(row)
    else:
        for start in range(0, len(cells), columns):
            row = []
            for i in range(columns):
                row.append(cells[start+i] if start+i < len(cells) else "")
                if i < columns-1:
                    row.append("")
            rows.append(row)
    table = _table(rows, widths)
    table.setStyle(TableStyle([("BOTTOMPADDING", (0, 0), (-1, -1), row_gap)]))
    return table


class AnnotatedImage(Flowable):
    """Uncropped drawing with handwritten side notes and native dashed leaders."""
    def __init__(self, path, notes, width, note_side, styles, background=PAPER):
        super().__init__()
        self.width, self.notes, self.side = width, notes, note_side
        self.background = background
        self.note_width = width * .31
        self.image_width = width * .62 if notes else width
        data, pw, ph = _prepared_image(str(path.resolve()))
        self.image = ImageReader(io.BytesIO(data))
        self.image_height = min(240, self.image_width * ph/pw)
        self.image_width = self.image_height * pw/ph
        self.copy = []
        heights = []
        for note in notes:
            parts = [Paragraph(_text(note.get("title", "Detail")), styles["note_title"])]
            parts.extend(_paragraphs(note.get("text"), styles["small"]))
            height = sum(part.wrap(self.note_width, 10000)[1] + part.getSpaceAfter() for part in parts)
            self.copy.append((parts, height))
            heights.append(height)
        self.height = max(self.image_height, sum(heights)+18*max(0, len(notes)-1)) + 8

    def draw(self):
        c = self.canv
        left = self.side != "right"
        ix = self.width-self.image_width if left else 0
        iy = (self.height-self.image_height)/2
        nx = 0 if left else self.width-self.note_width
        c.drawImage(self.image, ix, iy, self.image_width, self.image_height, mask="auto")
        notes_height = sum(height for _, height in self.copy)+18*max(0, len(self.copy)-1)
        top = (self.height+notes_height)/2
        for note, (parts, height) in zip(self.notes, self.copy):
            point = note.get("point", [.5, .5])
            x = ix+float(point[0])*self.image_width
            y = iy+(1-float(point[1]))*self.image_height
            sx = nx+self.note_width+5 if left else nx-5
            sy = top-9
            c.saveState()
            c.setStrokeColor(colors.HexColor("#819074"))
            c.setLineWidth(.65)
            c.setDash(2, 2)
            path = c.beginPath()
            path.moveTo(sx, sy)
            elbow = sx+10 if left else sx-10
            path.curveTo(elbow, sy, elbow, y, x, y)
            c.drawPath(path)
            c.setDash()
            c.setFillColor(self.background)
            c.circle(x, y, 2.3, fill=1, stroke=1)
            c.restoreState()
            text_top = top
            for part in parts:
                _, ph = part.wrap(self.note_width, 10000)
                part.drawOn(c, nx, text_top-ph)
                text_top -= ph+part.getSpaceAfter()
            top -= height+18


class EdgeAnnotatedImage(Flowable):
    """Full-width drawing with horizontal or staggered notes on either edge."""

    def __init__(self, path, notes, width, side, layout, columns, styles, background=PAPER):
        from build import detail_note_edge
        super().__init__()
        self.width, self.background = width, background
        data, pw, ph = _prepared_image(str(path.resolve()))
        self.image = ImageReader(io.BytesIO(data))
        self.image_height = min(240, width * ph / pw)
        self.image_width = self.image_height * pw / ph
        self.groups = {}
        self.placements = []
        for edge in ("top", "bottom"):
            group = [note for note in notes if detail_note_edge(note, side) == edge]
            count = min(columns, len(group)) or 1
            note_width = (width - 18 * (count - 1)) / count
            rows = []
            for start in range(0, len(group), count):
                row = []
                for index, note in enumerate(group[start:start + count]):
                    parts = [Paragraph(_text(note.get("title", "Detail")), styles["note_title"])]
                    parts.extend(_paragraphs(note.get("text"), styles["small"]))
                    height = sum(part.wrap(note_width, 10000)[1] + part.getSpaceAfter() for part in parts)
                    offset = 14 if layout == "staggered" and (start + index) % 2 else 0
                    heading_width = min(note_width, max(
                        pdfmetrics.stringWidth(line, styles["note_title"].fontName, styles["note_title"].fontSize)
                        for line in _plain(note.get("title", "Detail")).split("\n")
                    ))
                    row.append((note, parts, height, offset, heading_width))
                rows.append((row, max(height + offset for _, _, height, offset, _ in row)))
            group_height = sum(height for _, height in rows) + 22 * max(0, len(rows) - 1)
            self.groups[edge] = (rows, group_height, note_width)
        top_height = self.groups["top"][1]
        bottom_height = self.groups["bottom"][1]
        self.image_y = bottom_height + (32 if bottom_height else 0) + 4
        self.height = self.image_y + self.image_height + (32 if top_height else 0) + top_height + 4
        for edge, (rows, group_height, note_width) in self.groups.items():
            cursor = self.height - 4 if edge == "top" else bottom_height + 4
            for row_index, (row, row_height) in enumerate(rows):
                for index, (note, parts, height, offset, heading_width) in enumerate(row):
                    top = cursor - offset if edge == "bottom" else cursor - row_height + height + offset
                    self.placements.append({
                        "note": note, "parts": parts, "height": height, "width": note_width,
                        "x": index * (note_width + 18), "top": top, "edge": edge,
                        "heading_width": heading_width,
                        "later_row": row_index < len(rows) - 1 if edge == "top" else row_index > 0,
                        "rail": cursor - row_height - 8 if edge == "top" else cursor + 8,
                    })
                cursor -= row_height + 22

    def draw(self):
        c = self.canv
        ix, iy = (self.width - self.image_width) / 2, self.image_y
        c.drawImage(self.image, ix, iy, self.image_width, self.image_height, mask="auto")
        for item in self.placements:
            point = item["note"].get("point", [.5, .5])
            x, y = ix + float(point[0]) * self.image_width, iy + (1 - float(point[1])) * self.image_height
            on_top = item["edge"] == "top"
            sx = item["x"] + item["heading_width"] / 2
            sy = item["top"] - item["height"] - 6 if on_top else item["top"] + 6
            elbow_y = iy + self.image_height + 14 if on_top else iy - 14
            c.saveState()
            c.setStrokeColor(colors.HexColor("#819074"))
            c.setLineWidth(.65)
            c.setDash(2, 2)
            path = c.beginPath()
            path.moveTo(sx, sy)
            if item["later_row"]:
                gutter = -8 if sx < self.width / 2 else self.width + 8
                path.lineTo(sx, item["rail"])
                path.lineTo(gutter, item["rail"])
                path.lineTo(gutter, elbow_y)
            else:
                path.lineTo(sx, elbow_y)
            path.lineTo(x, y)
            c.drawPath(path)
            c.setDash()
            c.setFillColor(self.background)
            c.circle(x, y, 2.3, fill=1, stroke=1)
            c.restoreState()
        for item in self.placements:
            top = item["top"]
            for part in item["parts"]:
                _, height = part.wrap(item["width"], 10000)
                part.drawOn(c, item["x"], top - height)
                top -= height + part.getSpaceAfter()


def _details(section, width, styles):
    from build import detail_note_options
    source = section.get("image")
    path = _asset_path(source)
    notes = [note for note in section.get("notes", []) if isinstance(note, dict)]
    if path and Path(str(source)).suffix.lower() not in VIDEO_EXTENSIONS:
        side, layout, columns = detail_note_options(section)
        background = INK if section.get("theme") == "dark" else SURFACE if section.get("theme") == "soft" else PAPER
        if side in {"top", "bottom", "both"}:
            return [EdgeAnnotatedImage(path, notes, width, side, layout, columns, styles, background)]
        return [AnnotatedImage(path, notes, width, side, styles, background)]
    output = [_media_item({"src": source}, width, 240, styles)]
    for note in notes:
        output.append(Paragraph(_text(note.get("title", "Detail")), styles["note_title"]))
        output.extend(_paragraphs(note.get("text"), styles["small"]))
    return output


def _render_section(section, *, gallery_columns=None, gallery_max_height=2.5 * inch):
    from build import normalize_section
    section = normalize_section(section)
    kind = section["type"]
    theme = section.get("theme", "paper")
    styles = _styles(theme)
    width = CONTENT_WIDTH
    if section.get("width") == "reading":
        width *= .76 if kind == "details" else .73
    inset = 16 if theme in {"soft", "dark"} else 0
    inner_width = width-2*inset
    heading = _section_heading(section, styles)
    body = []

    if kind == "text":
        body.extend(_paragraphs(section.get("body"), styles["body"]))
    elif kind == "split":
        copy = heading+_paragraphs(section.get("body"), styles["body"])
        heading = []
        images = _section_images(section)
        if not images and section.get("image"):
            images = [{"src": section["image"], "caption": section.get("image_caption")}]
        gap = 22
        image_width = (inner_width-gap)*.61
        text_width = inner_width-image_width-gap
        if section.get("media_layout") == "grid":
            media = [_gallery(images, 2, image_width, styles=styles)]
        else:
            media = []
            # Keep a complete stack on one page while allowing ample drawing size.
            max_height = min(230, 300/max(1, len(images))-20)
            for item in images:
                media.extend([_media_item(item, image_width, max_height, styles), Spacer(1, 10)])
        left = section.get("image_side") == "left"
        row = [media, "", copy] if left else [copy, "", media]
        widths = [image_width, gap, text_width] if left else [text_width, gap, image_width]
        table = _table([row], widths)
        table.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
        body.append(table)
    elif kind == "gallery":
        images = _section_images(section)
        layout = section.get("layout", "grid")
        columns = (
            min(3, len(images)) if layout == "filmstrip"
            else gallery_columns or section.get("columns", 2)
        )
        body.append(_gallery(
            images, columns, inner_width, layout, styles,
            max_image_height=gallery_max_height,
            row_gap=0 if gallery_columns is not None else 12,
        ))
    elif kind == "details":
        body.extend(_details(section, inner_width, styles))
    elif kind == "image":
        image_width = inner_width*.82 if section.get("style") == "inset" else inner_width
        media = _media_item(section, image_width, 350, styles)
        media.hAlign = "CENTER"
        body.append(media)
    elif kind == "columns":
        items = [item for item in section.get("items", []) if isinstance(item, dict)]
        count = max(1, min(section.get("columns", 3), 4))
        gap = 16
        cell_width = (inner_width-gap*(count-1))/count
        cells = [[Paragraph(_text(item.get("title", "")), styles["note_title"]),
                  *_paragraphs(item.get("text"), styles["body"])] for item in items]
        rows = []
        for start in range(0, len(cells), count):
            row = []
            for i in range(count):
                row.append(cells[start+i] if start+i < len(cells) else "")
                if i < count-1:
                    row.append("")
            rows.append(row)
        if rows:
            widths = [v for i in range(count) for v in ([cell_width, gap] if i < count-1 else [cell_width])]
            body.append(_table(rows, widths))
    elif kind == "quote":
        body.append(Paragraph(_text(section.get("quote", "")), styles["quote"]))
        if section.get("attribution"):
            body.extend([Spacer(1, 10), Paragraph(_text(section["attribution"]),
                         ParagraphStyle("Attribution", parent=styles["small"], alignment=TA_CENTER))])

    content = heading+body
    if not content:
        return []
    if kind == "text":
        # Short reading sections belong with their heading, not on two pages.
        # Long copy can still flow naturally through the document.
        height = sum(part.wrap(inner_width, 10000)[1] + part.getSpaceAfter() for part in content)
        if height < 230:
            content = [KeepTogether(content)]
    space = {"compact": 13, "normal": 22, "generous": 43}.get(section.get("spacing", "normal"), 22)
    if kind == "gallery" and gallery_columns is not None:
        # A dense gallery is selected only to share a page with adjacent
        # content, so it needs less of the normal section-to-section gap.
        space = min(space, 4)
    alignment = section.get("align", "left")
    left_indent = CONTENT_WIDTH-width if alignment == "right" else (CONTENT_WIDTH-width)/2 if kind == "image" else 0
    if theme in {"soft", "dark"}:
        panel = _table([[content]], [width])
        panel.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), INK if theme == "dark" else SURFACE),
            ("LEFTPADDING", (0, 0), (-1, -1), inset),
            ("RIGHTPADDING", (0, 0), (-1, -1), inset),
            ("TOPPADDING", (0, 0), (-1, -1), inset),
            ("BOTTOMPADDING", (0, 0), (-1, -1), inset),
        ]))
        content = [panel]
    # A spacer and the first heading travel together; headings never end a page.
    top = Spacer(1, space)
    top.keepWithNext = True
    return [Indenter(left=left_indent, right=CONTENT_WIDTH-width-left_indent), top,
            *content, Indenter(left=-left_indent, right=-(CONTENT_WIDTH-width-left_indent))]


def _cover(projects):
    intro = [Paragraph('Hi, I\'m Eli<font color="#64754e">.</font>', STYLES["cover_title"]),
             Paragraph(
                 "I am a mechanical engineering student at Lawrence Technological University.<br/>"
                 "This is a small collection of projects I have designed and built.",
                 STYLES["cover_deck"],
             )]
    story = [ProjectAnchor("home", "Selected work"),
             *intro,
             Spacer(1, 24), Paragraph("Selected work", STYLES["section_title"])]
    gap = 28
    cell_width = (CONTENT_WIDTH-gap)/2
    rows = []
    for start in range(0, len(projects), 2):
        row = []
        for column, project in enumerate(projects[start:start+2]):
            thumb = {"src": project.get("thumbnail"), "ratio": "landscape",
                     "fit": project.get("thumbnail_fit", "cover"),
                     "scale": project.get("thumbnail_scale", 1),
                     "position": project.get("thumbnail_position", "50% 50%")}
            if thumb["fit"] != "contain":
                thumb["background"] = project.get("thumbnail_background", "#f3f4f0")
            title = f'<link href="#project-{escape(project["slug"], quote=True)}">{_text(project["title"])}</link>'
            label = _plain(project.get("card_label") or project.get("subtitle"))
            year = _plain(project.get("year"))
            card = [Spacer(1, 10 if column else 0),
                    _media_item(thumb, cell_width, 132, angle=.8 if column else -.7),
                    Spacer(1, 7), Paragraph(title, STYLES["small_bold"]),
                    Paragraph(" &nbsp;&nbsp; ".join(_text(v) for v in (label, year) if v), STYLES["small"]),
                    Spacer(1, 16)]
            if column:
                row.append("")
            row.append(card)
        if len(row) == 1:
            row.extend(["", ""])
        rows.append(row)
    if rows:
        story.append(_table(rows, [cell_width, gap, cell_width]))
    note_text = (
        "This is a PDF copy of my portfolio website. For the best experience, I recommend viewing "
        "the live site, as animations and videos cannot be displayed in this version."
    )
    site_url = os.environ.get("PORTFOLIO_SITE_URL", "").strip() or "https://eliforta.github.io"
    display_url = re.sub(r"^https?://", "", site_url).rstrip("/")
    note = [Paragraph("A note about this PDF", STYLES["small_bold"]),
            Paragraph(_text(note_text), STYLES["body"]),
            Paragraph(
                f'<link href="{escape(site_url, quote=True)}" color="#4d633b">'
                f'<b>{_text(display_url)}</b></link>',
                STYLES["body"],
            )]
    panel = _table([[note]], [CONTENT_WIDTH])
    panel.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), SURFACE),
        ("LINEBEFORE", (0, 0), (0, -1), 2, colors.HexColor("#819074")),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING", (0, 0), (-1, -1), 11),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 11),
    ]))
    story.extend([Spacer(1, 8), panel, PageBreak()])
    return story


def _project(project, index, total):
    story = [ProjectAnchor(project["slug"], project["title"])]
    if project.get("eyebrow"):
        story.append(Paragraph(_text(project["eyebrow"]), STYLES["kicker"]))
    title = f'{_text(project["title"])}<font color="#64754e">.</font>'
    if project.get("year"):
        title += f'  <font name="{FONT_REGULAR}" size="14" color="#73756f">{_text(project["year"])}</font>'
    story.append(Paragraph(title, STYLES["project_title"]))
    if _plain(project.get("subtitle")):
        story.append(Paragraph(_text(project["subtitle"]), STYLES["project_meta"]))
    meta = []
    if project.get("role"):
        meta.append(f'<font color="#292b27">Role</font> &nbsp; {_text(project["role"])}')
    if project.get("tags"):
        meta.append('<font color="#292b27">Focus</font> &nbsp; ' + " · ".join(_text(tag) for tag in project["tags"]))
    if meta:
        # Separate metadata fields remain easy to scan when the focus list wraps.
        story.append(Paragraph(" &nbsp;&nbsp;&nbsp; ".join(meta), STYLES["project_meta"]))
    sections = []
    for section in project.get("sections", []):
        from build import normalize_section
        normalized = normalize_section(section)
        normal = _render_section(normalized)
        variants = [(normal, 0)]
        if normalized["type"] == "gallery" and normalized.get("layout", "grid") != "filmstrip":
            images = _section_images(normalized)
            requested_columns = max(1, min(int(normalized.get("columns", 2)), 4, len(images)))
            gallery_width = CONTENT_WIDTH * (.73 if normalized.get("width") == "reading" else 1)
            compact_columns = _compact_gallery_columns(len(images), gallery_width)
            if compact_columns > requested_columns:
                compact = _render_section(
                    normalized,
                    gallery_columns=compact_columns,
                    gallery_max_height=2 * inch,
                )
                variants.append((compact, compact_columns - requested_columns))
        sections.append({
            "variants": variants,
            # This is a soft relationship. The planner keeps supporting views
            # with the preceding section when space permits, but can break the
            # pair instead of leaving most of a page blank.
            "supporting": not normalized.get("title") and normalized["type"] == "gallery",
        })
    story = _paginate_project(story, sections)
    story.append(PageBreak())
    return story


def _measure(flowables, measuring_canvas):
    expanded = []
    for item in flowables:
        expanded.extend(item._content if isinstance(item, KeepTogether) else [item])
    return _listWrapOn(expanded, CONTENT_WIDTH, measuring_canvas)[1]


def _paginate_project(intro, sections):
    """Fit ordered section variants into the fewest well-filled pages.

    Galleries retain their authored column count unless a denser variant saves
    a page. Untitled supporting views prefer to stay with the preceding copy,
    but that relationship is soft so it cannot create a mostly empty page.
    Native flowables still handle unusually long sections.
    """
    measuring_canvas = InvariantCanvas(io.BytesIO())
    capacity = PAGE_HEIGHT-MARGIN_TOP-MARGIN_BOTTOM-4
    intro_height = _measure(intro, measuring_canvas)
    heights = [
        [_measure(flowables, measuring_canvas) for flowables, _ in section["variants"]]
        for section in sections
    ]
    if not sections or any(min(options) > capacity for options in heights):
        return intro + [part for section in sections for part in section["variants"][0][0]]

    @lru_cache(None)
    def plan(start):
        available = capacity-intro_height if start == 0 else capacity
        best = None
        for end in range(start+1, len(sections)+1):
            if sum(min(options) for options in heights[start:end]) > available:
                break
            choices = [range(len(section["variants"])) for section in sections[start:end]]
            for selected in product(*choices):
                parts = [
                    part
                    for section, choice in zip(sections[start:end], selected)
                    for part in section["variants"][choice][0]
                ]
                height = _measure(parts, measuring_canvas)
                if height > available:
                    continue
                compact_cost = sum(
                    section["variants"][choice][1]
                    for section, choice in zip(sections[start:end], selected)
                )
                supporting_break = int(end < len(sections) and sections[end]["supporting"])
                if end == len(sections):
                    score = (1, compact_cost, supporting_break, (available-height)**2)
                    pages = ((end, selected),)
                else:
                    tail = plan(end)
                    if tail is None:
                        continue
                    score = (
                        1+tail[0][0],
                        compact_cost+tail[0][1],
                        supporting_break+tail[0][2],
                        (available-height)**2+tail[0][3],
                    )
                    pages = ((end, selected),)+tail[1]
                result = (score, pages)
                if best is None or result[0] < best[0]:
                    best = result
        return best

    choice = plan(0)
    if choice is None:
        return intro + [part for section in sections for part in section["variants"][0][0]]
    output, start = list(intro), 0
    for end, selected in choice[1]:
        if start:
            output.append(PageBreak())
        for section, variant in zip(sections[start:end], selected):
            output.extend(section["variants"][variant][0])
        start = end
    return output


class PortfolioDocTemplate(BaseDocTemplate):
    current_project = "Portfolio"

    def afterFlowable(self, flowable):
        if isinstance(flowable, ProjectAnchor):
            self.current_project = "Portfolio" if flowable.slug == "home" else _plain(flowable.title)


def _draw_project_header(c, document):
    # Draw after the page's anchor has identified the project, including its
    # opening page. This label is deliberately plain text with no annotation.
    c.saveState()
    c.setFont(BODY_FONT, 8.5)
    c.setFillColor(PRINT_MUTED)
    c.drawRightString(PAGE_WIDTH-MARGIN_X, PAGE_HEIGHT-36, document.current_project.replace("\n", " "))
    c.restoreState()


def _draw_page(canvas_object, document):
    c = canvas_object
    c.saveState()
    c.setFillColor(PAPER)
    c.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
    c.saveState()
    c.translate(MARGIN_X, PAGE_HEIGHT-43)
    c.rotate(6)
    c.setFillColor(INK)
    c.setFont(FONT_BOLD, 26)
    c.drawString(0, 0, "ef.")
    c.restoreState()
    c.setFont(BODY_FONT, 8)
    c.setFillColor(MUTED)
    c.setStrokeColor(RULE)
    c.setLineWidth(.45)
    c.line(MARGIN_X, 34, PAGE_WIDTH-MARGIN_X, 34)
    c.setFont(BODY_FONT, 7)
    c.drawString(MARGIN_X, 20, "Made by")
    c.setFont(FONT_BOLD, 13)
    c.setFillColor(INK)
    c.drawString(MARGIN_X+34, 19, "ef.")
    c.setFont(FONT_REGULAR, 11)
    c.setFillColor(MUTED)
    c.drawRightString(PAGE_WIDTH-MARGIN_X, 19, f"{c.getPageNumber():02d}")
    c.restoreState()


def render_portfolio_pdf(projects: list[dict]) -> bytes:
    """Render featured TOML projects into deterministic PDF bytes."""
    featured = [project for project in projects if project.get("featured", True)]
    if not featured:
        featured = projects
    buffer = io.BytesIO()
    document = PortfolioDocTemplate(
        buffer,
        pagesize=LETTER,
        rightMargin=MARGIN_X,
        leftMargin=MARGIN_X,
        topMargin=MARGIN_TOP,
        bottomMargin=MARGIN_BOTTOM,
        title="EF - Selected Work",
        author="Eli",
        subject="Portfolio",
        creator="Portfolio TOML PDF builder",
        pageCompression=1,
    )
    document.addPageTemplates(PageTemplate(
        id="portfolio", onPage=_draw_page, onPageEnd=_draw_project_header,
        frames=[Frame(MARGIN_X, MARGIN_BOTTOM, CONTENT_WIDTH,
                      PAGE_HEIGHT-MARGIN_TOP-MARGIN_BOTTOM,
                      leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)],
    ))
    story = _cover(featured)
    for index, project in enumerate(featured, 1):
        story.extend(_project(project, index, len(featured)))
    if story and isinstance(story[-1], PageBreak):
        story.pop()
    document.build(story, canvasmaker=InvariantCanvas)
    return buffer.getvalue()
