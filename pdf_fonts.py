"""Embed the site's own CFF/OpenType handwriting in ReportLab as TrueType.

Conversion is in memory, keeps Unicode mappings and metrics, and runs directly
from the OTF sources so replacing a website font also updates the PDF.
"""

import io
from pathlib import Path

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.ttLib import TTFont as OpenTypeFont
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def register_site_font(name: str, path: Path) -> None:
    with OpenTypeFont(path, recalcTimestamp=False) as source:
        if "glyf" in source:
            pdfmetrics.registerFont(TTFont(name, path))
            return
        glyph_set = source.getGlyphSet()
        units = source["head"].unitsPerEm
        glyphs = {}
        for glyph_name in source.getGlyphOrder():
            pen = TTGlyphPen(glyph_set)
            glyph_set[glyph_name].draw(
                Cu2QuPen(pen, max_err=units / 2000, reverse_direction=True)
            )
            glyphs[glyph_name] = pen.glyph()

        builder = FontBuilder(units, isTTF=True)
        builder.setupGlyphOrder(source.getGlyphOrder())
        builder.setupCharacterMap(source.getBestCmap())
        builder.setupGlyf(glyphs)
        builder.setupHorizontalMetrics(source["hmtx"].metrics)
        header = source["hhea"]
        builder.setupHorizontalHeader(
            ascent=header.ascent, descent=header.descent, lineGap=header.lineGap
        )
        # Keep licensing, naming, embedding permissions, and style information.
        builder.font["name"] = source["name"]
        builder.font["OS/2"] = source["OS/2"]
        builder.setupPost(italicAngle=source["post"].italicAngle)
        builder.font["head"].macStyle = source["head"].macStyle
        builder.font["head"].created = source["head"].created
        builder.font["head"].modified = source["head"].modified
        builder.font.recalcTimestamp = False
        buffer = io.BytesIO()
        builder.save(buffer)
        buffer.seek(0)
        pdfmetrics.registerFont(TTFont(name, buffer))
