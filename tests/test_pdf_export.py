"""PDF regressions: typography, content, navigation, and deterministic builds."""

import io
import os
import re
import unittest
from unittest.mock import patch

from pypdf import PdfReader

from build import load_projects
from build_pdf import _compact_gallery_columns, _plain, render_portfolio_pdf


def compact(value):
    return re.sub(r"\s+", " ", _plain(value)).strip()


class PortfolioPDFTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.projects = load_projects()
        with patch.dict(os.environ, {"PORTFOLIO_SITE_URL": ""}):
            cls.pdf = render_portfolio_pdf(cls.projects)
        cls.reader = PdfReader(io.BytesIO(cls.pdf))
        cls.text = compact(" ".join(page.extract_text() for page in cls.reader.pages))

    def test_handwriting_is_embedded_and_unused_icon_font_is_absent(self):
        fonts = {
            str(font.get_object().get("/BaseFont")): font.get_object()
            for page in self.reader.pages
            for font in page["/Resources"]["/Font"].values()
        }
        for face in ("EF-Regular", "EF-Bold"):
            matches = [font for name, font in fonts.items() if name.endswith("+"+face)]
            self.assertTrue(matches, f"Missing original site font: {face}")
            for font in matches:
                self.assertIn("/ToUnicode", font)
                self.assertIn("/FontFile2", font["/FontDescriptor"])
        self.assertFalse(any(name.endswith("+Icons-Regular") for name in fonts))

    def test_project_copy_survives_pagination(self):
        for project in self.projects:
            if not project.get("featured", True):
                self.assertNotIn(compact(project["title"]), self.text)
                continue
            self.assertIn(compact(project["title"]), self.text)
            for section in project["sections"]:
                values = [section.get(key) for key in ("title", "body", "quote", "attribution", "caption")]
                for item in section.get("notes", []) + section.get("items", []):
                    values.extend([item.get("title"), item.get("text")])
                for item in section.get("images", []):
                    if isinstance(item, dict):
                        values.append(item.get("caption"))
                for value in values:
                    if value:
                        self.assertIn(compact(value), self.text)

    def test_cover_links_and_outline_reach_each_project(self):
        featured = [p for p in self.projects if p.get("featured", True)]
        titles = [entry.title for entry in self.reader.outline]
        self.assertEqual(titles, ["Selected work"]+[p["title"] for p in featured])
        project_pages = [self.reader.get_destination_page_number(entry) for entry in self.reader.outline[1:]]
        self.assertTrue(all(page > 0 for page in project_pages))
        links = [a.get_object() for a in self.reader.pages[0].get("/Annots", [])
                 if "/Dest" in a.get_object()]
        self.assertEqual(len(links), len(featured))
        for link, page_number in zip(links, project_pages):
            self.assertEqual(link["/Dest"][0], self.reader.pages[page_number].indirect_reference)

    def test_project_headers_identify_every_page_without_navigation_links(self):
        outlines = self.reader.outline[1:]
        for index, entry in enumerate(outlines):
            start = self.reader.get_destination_page_number(entry)
            end = self.reader.get_destination_page_number(outlines[index+1]) if index+1 < len(outlines) else len(self.reader.pages)
            for page in self.reader.pages[start:end]:
                self.assertEqual(page.extract_text().strip().splitlines()[-1], compact(entry.title))
                for annotation in page.get("/Annots", []):
                    self.assertLess(float(annotation.get_object()["/Rect"][3]), 740)
        self.assertNotIn("All work", self.text)

    def test_cover_matches_site_copy_and_keeps_pdf_notice_on_first_page(self):
        cover = self.reader.pages[0]
        cover_text = compact(cover.extract_text())
        site_intro = (
            "I am a mechanical engineering student at Lawrence Technological University. "
            "This is a small collection of projects I have designed and built."
        )
        self.assertIn(site_intro, cover_text)
        self.assertIn("A note about this PDF", cover_text)
        self.assertIn(
            "This is a PDF copy of my portfolio website. For the best experience, I recommend "
            "viewing the live site, as animations and videos cannot be displayed in this version.",
            cover_text,
        )
        self.assertNotIn("See the work in motion", cover_text)
        urls = [str(a.get_object().get("/A", {}).get("/URI", "")) for a in cover.get("/Annots", [])]
        self.assertIn("https://eliforta.github.io", urls)
        self.assertNotIn("https://www.linkedin.com/in/EliForta", urls)
        self.assertEqual(self.reader.get_destination_page_number(self.reader.outline[1]), 1)

    def test_video_stills_replace_empty_panels(self):
        self.assertIn("Video still - motion on the website.", self.text)
        self.assertNotIn("Video - website only.", self.text)

    def test_layout_avoids_sparse_pages(self):
        # The PDF paginator may densify a gallery only when doing so lets
        # adjacent content share a page. The image-size floor intentionally
        # trades a few pages for legibility while staying below the old
        # 19-page export.
        self.assertLessEqual(len(self.reader.pages), 16)

    def test_compact_galleries_keep_print_legible_cell_widths(self):
        self.assertEqual(_compact_gallery_columns(4), 3)

    def test_export_is_reproducible(self):
        with patch.dict(os.environ, {"PORTFOLIO_SITE_URL": ""}):
            self.assertEqual(self.pdf, render_portfolio_pdf(self.projects))

    def test_optional_layouts_and_live_link(self):
        lab = next(p for p in self.projects if p["slug"] == "layout-demo")
        url = "https://example.com/portfolio"
        with patch.dict(os.environ, {"PORTFOLIO_SITE_URL": url}):
            reader = PdfReader(io.BytesIO(render_portfolio_pdf([lab])))
        text = compact(" ".join(p.extract_text() for p in reader.pages))
        for section in lab["sections"]:
            for key in ("title", "quote", "body"):
                # Gallery body is not a displayed field in the website template.
                if section.get(key) and not (section["type"] == "gallery" and key == "body"):
                    self.assertIn(compact(section[key]), text)
        links = [a.get_object() for page in reader.pages for a in page.get("/Annots", [])]
        self.assertIn(url, [str(link.get("/A", {}).get("/URI", "")) for link in links])


if __name__ == "__main__":
    unittest.main()
