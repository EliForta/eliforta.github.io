"""PDF regressions: typography, content, navigation, and deterministic builds."""

import io
import os
import re
import unittest
from datetime import date
from unittest.mock import patch
from urllib.parse import unquote, urlsplit

from pypdf import PdfReader
from pypdf.generic import ContentStream

from build import ROOT, load_projects
from build_pdf import (
    COMPRESSED_IMAGE_MAX_SIZE, InvariantCanvas, _asset_url,
    _compact_gallery_columns, _media_item, _plain, render_portfolio_pdf,
)


def compact(value):
    return re.sub(r"\s+", " ", _plain(value)).strip()


class PortfolioPDFTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.projects = load_projects()
        with patch.dict(os.environ, {"PORTFOLIO_SITE_URL": ""}):
            cls.pdf = render_portfolio_pdf(cls.projects)
            cls.compressed_pdf = render_portfolio_pdf(cls.projects, compress_images=True)
        cls.reader = PdfReader(io.BytesIO(cls.pdf))
        cls.compressed_reader = PdfReader(io.BytesIO(cls.compressed_pdf))
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
        self.assertEqual(len(links), 2 * len(featured))
        for index, page_number in enumerate(project_pages):
            # Each cover thumbnail and its title reach the same project page.
            for link in links[2*index:2*index+2]:
                self.assertEqual(link["/Dest"][0], self.reader.pages[page_number].indirect_reference)
        cover_urls = [str(a.get_object().get("/A", {}).get("/URI", ""))
                      for a in self.reader.pages[0].get("/Annots", [])]
        self.assertFalse(any("/assets/images/" in url for url in cover_urls))

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
            "I’m a mechanical engineering student at Lawrence Technological University. "
            "Here are some projects I’ve designed, built, and tested, from research hardware to a product I sold."
        )
        self.assertIn(site_intro, cover_text)
        self.assertIn("A note about this PDF", cover_text)
        self.assertIn(
            "This is a PDF copy of my portfolio website. Within each project, click any image to open the original file, "
            "including animations and videos, or view them on the live site for the best experience. "
            "The web version is likely more up to date than this PDF.",
            cover_text,
        )
        self.assertNotIn("See the work in motion", cover_text)
        urls = [str(a.get_object().get("/A", {}).get("/URI", "")) for a in cover.get("/Annots", [])]
        self.assertIn("https://eliforta.github.io", urls)
        self.assertNotIn("https://www.linkedin.com/in/EliForta", urls)
        self.assertEqual(self.reader.get_destination_page_number(self.reader.outline[1]), 1)

    def test_video_stills_replace_empty_panels(self):
        self.assertIn("Video still - click to view.", self.text)
        self.assertNotIn("Video - website only.", self.text)

    def test_cover_date_updates_on_each_build(self):
        for day, label in (
            (date(2031, 2, 3), "February 3, 2031"),
            (date(2032, 11, 14), "November 14, 2032"),
        ):
            with self.subTest(date=day), patch("build_pdf.date") as clock:
                clock.today.return_value = day
                reader = PdfReader(io.BytesIO(render_portfolio_pdf([])))
                self.assertIn(f"Last updated {label}", compact(reader.pages[0].extract_text()))

    def test_animation_stills_are_labeled_and_link_to_the_original(self):
        for source, animated in (
            ("slider/slider.gif", True),
            ("dynamo/dynamo.avif", True),
            ("dynamo/dynamo.png", False),
        ):
            with self.subTest(source=source), patch.dict(os.environ, {"PORTFOLIO_SITE_URL": ""}):
                output = io.BytesIO()
                media = _media_item({"src": source}, 240, 180)
                canvas = InvariantCanvas(output)
                media.wrap(240, 10000)
                media.drawOn(canvas, 40, 400)
                canvas.save()
                page = PdfReader(io.BytesIO(output.getvalue())).pages[0]
                self.assertEqual(
                    "Animation still - first frame shown; click to view." in page.extract_text(),
                    animated,
                )
                self.assertEqual(
                    [str(a.get_object()["/A"]["/URI"]) for a in page["/Annots"]],
                    [f"https://eliforta.github.io/assets/images/{source}"],
                )
        for reader in (self.reader, self.compressed_reader):
            dynamo_page = next(
                page for page in reader.pages
                if any(
                    str(a.get_object().get("/A", {}).get("/URI", "")).endswith("/dynamo/dynamo.avif")
                    for a in page.get("/Annots", [])
                )
            )
            self.assertIn("Animation still - first frame shown; click to view.",
                          compact(dynamo_page.extract_text()))

    def test_every_project_image_links_to_its_original_asset(self):
        urls = set()
        for page_number, page in enumerate(self.reader.pages[1:], 2):
            with self.subTest(page=page_number):
                images = page["/Resources"].get("/XObject", {})
                image_count = sum(
                    operator == b"Do" and images[operands[0]].get("/Subtype") == "/Image"
                    for operands, operator in ContentStream(page.get_contents(), self.reader).operations
                )
                image_links = [
                    a.get_object() for a in page.get("/Annots", [])
                    if str(a.get_object().get("/A", {}).get("/URI", "")).startswith(
                        "https://eliforta.github.io/assets/images/"
                    )
                ]
                self.assertEqual(len(image_links), image_count)
                for link in image_links:
                    url = str(link["/A"]["/URI"])
                    urls.add(url)
                    self.assertEqual(link["/Subtype"], "/Link")
                    self.assertTrue((ROOT / unquote(urlsplit(url).path.lstrip("/"))).is_file())
                    x1, y1, x2, y2 = map(float, link["/Rect"])
                    self.assertGreater(x2, x1)
                    self.assertGreater(y2, y1)
                    self.assertGreaterEqual(x1, 0)
                    self.assertGreaterEqual(y1, 0)
                    self.assertLessEqual(x2, float(page.mediabox.width))
                    self.assertLessEqual(y2, float(page.mediabox.height))
        self.assertIn("https://eliforta.github.io/assets/images/slider/slider7.mp4", urls)

    def test_asset_links_encode_filenames_and_preserve_site_path(self):
        with patch.dict(os.environ, {"PORTFOLIO_SITE_URL": "https://example.com/portfolio/"}):
            self.assertEqual(
                _asset_url(ROOT / "assets" / "images" / "drawing #1?.png"),
                "https://example.com/portfolio/assets/images/drawing%20%231%3F.png",
            )

    def test_compact_galleries_keep_print_legible_cell_widths(self):
        self.assertEqual(_compact_gallery_columns(4), 3)

    def test_export_is_reproducible(self):
        with patch.dict(os.environ, {"PORTFOLIO_SITE_URL": ""}):
            self.assertEqual(self.pdf, render_portfolio_pdf(self.projects))

    def test_compressed_copy_is_smaller_and_keeps_image_transparency(self):
        self.assertLess(len(self.compressed_pdf), len(self.pdf))
        transparent_images = 0
        for original, compressed in zip(self.reader.pages, self.compressed_reader.pages):
            def images(page, reader):
                objects = page["/Resources"].get("/XObject", {})
                return [objects[operands[0]]
                        for operands, operator in ContentStream(page.get_contents(), reader).operations
                        if operator == b"Do" and objects[operands[0]].get("/Subtype") == "/Image"]

            originals = images(original, self.reader)
            compressed_images = images(compressed, self.compressed_reader)
            self.assertEqual(len(originals), len(compressed_images))
            for source, image in zip(originals, compressed_images):
                self.assertLessEqual(image["/Width"], min(source["/Width"], COMPRESSED_IMAGE_MAX_SIZE[0]))
                self.assertLessEqual(image["/Height"], min(source["/Height"], COMPRESSED_IMAGE_MAX_SIZE[1]))
                self.assertEqual("/SMask" in source, "/SMask" in image)
                if "/SMask" in image:
                    transparent_images += 1
                    self.assertEqual(image["/SMask"]["/Width"], image["/Width"])
                    self.assertEqual(image["/SMask"]["/Height"], image["/Height"])
                else:
                    self.assertIn("/DCTDecode", image["/Filter"])
        self.assertGreater(transparent_images, 0)

    def test_compressed_copy_preserves_page_content_and_links(self):
        self.assertEqual(len(self.reader.pages), len(self.compressed_reader.pages))
        self.assertEqual(
            [(entry.title, self.reader.get_destination_page_number(entry)) for entry in self.reader.outline],
            [(entry.title, self.compressed_reader.get_destination_page_number(entry))
             for entry in self.compressed_reader.outline],
        )
        for page_number, (original, compressed) in enumerate(zip(self.reader.pages, self.compressed_reader.pages), 1):
            with self.subTest(page=page_number):
                self.assertEqual(original.extract_text(), compressed.extract_text())

                def drawing_operations(page, reader):
                    return [(operands if operator != b"Do" else ["image"], operator)
                            for operands, operator in ContentStream(page.get_contents(), reader).operations]

                self.assertEqual(drawing_operations(original, self.reader),
                                 drawing_operations(compressed, self.compressed_reader))

                def links(page, reader):
                    page_numbers = {p.indirect_reference: index for index, p in enumerate(reader.pages)}
                    return [(tuple(link["/Rect"]), str(link.get("/A", {}).get("/URI", "")),
                             page_numbers[link["/Dest"][0]] if "/Dest" in link else None)
                            for annotation in page.get("/Annots", [])
                            for link in [annotation.get_object()]]

                self.assertEqual(links(original, self.reader), links(compressed, self.compressed_reader))

    def test_compressed_export_is_reproducible(self):
        with patch.dict(os.environ, {"PORTFOLIO_SITE_URL": ""}):
            self.assertEqual(self.compressed_pdf, render_portfolio_pdf(self.projects, compress_images=True))

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
        urls = [str(link.get("/A", {}).get("/URI", "")) for link in links]
        self.assertIn(url, urls)
        self.assertIn(f"{url}/assets/images/project-01.png", urls)


if __name__ == "__main__":
    unittest.main()
