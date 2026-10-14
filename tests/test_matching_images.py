"""Matching media frames share geometry across HTML and PDF output."""

import copy
import io
import tempfile
import unittest
from pathlib import Path

from PIL import Image
from pypdf import PdfReader
from reportlab.pdfgen.canvas import Canvas

from build import ROOT, BuildError, render_section, section_images, validate_project
from build_pdf import MediaFrame, _section_images


class MatchingImageTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(dir=ROOT / "tmp")
        self.addCleanup(self.directory.cleanup)
        folder = Path(self.directory.name)
        self.first = folder / "first.jpg"
        self.next = folder / "next.png"
        Image.new("RGB", (800, 400), "red").save(self.first)
        Image.new("RGB", (300, 600), "blue").save(self.next)
        self.section = {"type": "gallery", "images": [
            {"src": self.first.relative_to(ROOT).as_posix(), "scale": .5},
            {"src": self.next.relative_to(ROOT).as_posix(), "match_first": True,
             "ratio": "portrait", "scale": .2, "fit": "contain", "position": "25% 50%"},
            {"src": self.next.relative_to(ROOT).as_posix(), "ratio": "square"},
        ]}

    def test_natural_jpeg_reference_and_opt_in_do_not_mutate_content(self):
        original = copy.deepcopy(self.section)
        items = section_images(self.section)
        self.assertEqual(items[1]["_matching_frame"], {"ratio": 2, "scale": .5, "natural": True})
        self.assertNotIn("_matching_frame", items[2])
        self.assertEqual(self.section, original)
        self.assertEqual(items, _section_images(self.section))

    def test_matching_html_for_split_and_gallery_keeps_own_fit_and_position(self):
        for kind in ("gallery", "split"):
            markup = render_section({**self.section, "type": kind}, 0, "Test", set())
            self.assertEqual(markup.count("ratio--matched"), 2)
            self.assertEqual(markup.count("--image-layout-width:50%;--image-frame-ratio:2"), 2)
            self.assertIn("--image-fit:contain", markup)
            self.assertIn("--image-position:25% 50%", markup)
            self.assertIn("ratio--square", markup)

    def test_pdf_frames_match_even_when_limited_by_page_height(self):
        items = section_images(self.section)
        for max_height in (400, 70):
            frames = [MediaFrame(path, item, 400, max_height)
                      for path, item in zip((self.first, self.next), items)]
            first, next_frame = frames
            self.assertEqual(first.frame_width, next_frame.frame_width)
            self.assertEqual(first.height, next_frame.height)
            self.assertAlmostEqual(next_frame.frame_width / next_frame.height, 2)
            self.assertLessEqual(next_frame.render_width, next_frame.frame_width)
            self.assertLessEqual(next_frame.render_height, next_frame.height)

    def test_preset_ratio_uses_full_frame_regardless_of_reduced_scale(self):
        self.section["images"][0].update(ratio="wide", scale=.3)
        items = section_images(self.section)
        self.assertEqual(items[1]["_matching_frame"], {"ratio": 16 / 9, "scale": 1, "natural": False})

    def test_own_cover_and_zoom_are_clipped_inside_matching_pdf_frame(self):
        self.section["images"][1].update(fit="cover", scale=2)
        item = section_images(self.section)[1]
        frame = MediaFrame(self.next, item, 400, 400)
        self.assertEqual((frame.frame_width, frame.height), (200, 100))
        self.assertGreater(frame.render_height, frame.height)
        output = io.BytesIO()
        canvas = Canvas(output)
        frame.drawOn(canvas, 40, 40)
        canvas.save()
        self.assertEqual(len(PdfReader(io.BytesIO(output.getvalue())).pages), 1)

    def test_explicit_dimensions_support_video_svg_and_remote_references(self):
        for source in ("movie.mp4", "drawing.svg", "https://example.com/photo.jpg"):
            items = section_images({"images": [
                {"src": source, "width": 640, "height": 480},
                {"src": "next.jpg", "match_first": True},
            ]})
            self.assertAlmostEqual(items[1]["_matching_frame"]["ratio"], 4 / 3)

    def test_unknown_reference_dimensions_have_an_actionable_error(self):
        self.section["images"][0] = {"src": "https://example.com/photo.jpg"}
        with self.assertRaisesRegex(BuildError, "width and height"):
            section_images(self.section)
        errors = self.validate()
        self.assertTrue(any("match_first needs" in error for error in errors), errors)

    def validate(self):
        return validate_project({"slug": "test", "title": "Test",
                                 "thumbnail": self.first.relative_to(ROOT).as_posix(),
                                 "sections": [self.section]}, Path("test.toml"))

    def test_invalid_setting_and_self_reference_are_reported(self):
        self.section["images"][1]["match_first"] = "true"
        self.assertTrue(any("must be true or false" in error for error in self.validate()))
        self.section["images"][0]["match_first"] = True
        self.assertTrue(any("only available after" in error for error in self.validate()))

    def test_disabled_setting_leaves_media_independent(self):
        self.section["images"][1]["match_first"] = False
        self.assertFalse(any("_matching_frame" in item for item in section_images(self.section)))


if __name__ == "__main__":
    unittest.main()
