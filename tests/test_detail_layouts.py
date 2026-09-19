"""Detail layouts share note placement across HTML and native PDF output."""

import io
from pathlib import Path
import unittest

from pypdf import PdfReader
from reportlab.pdfgen.canvas import Canvas

from build import detail_note_edge, detail_note_options, render_section, validate_project
from build_pdf import EdgeAnnotatedImage, STYLES, _details


class DetailLayoutTests(unittest.TestCase):
    def section(self, **options):
        return {
            "type": "detail", "image": "project-01.png", "image_alt": "Detail test drawing",
            "notes": [
                {"title": "Upper note", "text": "Upper feature.", "point": [.3, .2]},
                {"title": "Lower note", "text": "Lower feature.", "point": [.7, .8]},
            ], **options,
        }

    def render(self, **options):
        return render_section(self.section(**options), 0, "Test project", set())

    def test_left_and_right_remain_unchanged(self):
        for side in ("left", "right"):
            markup = self.render(note_side=side)
            self.assertIn(f'class="annotated-view notes--{side}"', markup)
            self.assertIn('<ul class="view-notes">', markup)
            self.assertNotIn("note-layout--", markup)

    def test_all_edge_and_arrangement_combinations(self):
        for side in ("top", "bottom", "both"):
            for layout in ("horizontal", "staggered"):
                with self.subTest(side=side, layout=layout):
                    markup = self.render(note_side=side, note_layout=layout)
                    self.assertIn(f'notes--{side} note-layout--{layout}', markup)
                    self.assertEqual(markup.count('class="view-note"'), 2)
                    self.assertEqual("view-notes--top" in markup, side != "bottom")
                    self.assertEqual("view-notes--bottom" in markup, side != "top")
                    if side != "bottom":
                        self.assertLess(markup.index("view-notes--top"), markup.index("annotated-image"))
                    if side != "top":
                        self.assertLess(markup.index("annotated-image"), markup.index("view-notes--bottom"))

    def test_nearest_edge_and_explicit_override(self):
        self.assertEqual(detail_note_edge({"point": [.5, .49]}, "both"), "top")
        self.assertEqual(detail_note_edge({"point": [.5, .5]}, "both"), "bottom")
        self.assertEqual(detail_note_edge({"point": [.5, .8], "side": "top"}, "both"), "top")
        self.assertEqual(detail_note_edge({"point": [.5, .2], "side": "bottom"}, "both"), "bottom")
        self.assertEqual(detail_note_edge({"side": "top"}, "bottom"), "bottom")

    def test_column_count_is_limited_to_available_notes(self):
        self.assertIn("--note-columns:2", self.render(note_side="bottom", note_columns=4))
        self.assertIn("--note-columns:1", self.render(note_side="both", note_columns=4))
        self.assertEqual(detail_note_options({}), ("left", "horizontal", 3))

    def test_empty_edge_groups_are_omitted(self):
        markup = self.render(note_side="both", notes=[{"title": "Top", "point": [.5, .2]}])
        self.assertIn("view-notes--top", markup)
        self.assertNotIn("view-notes--bottom", markup)
        self.assertNotIn("view-notes--", self.render(note_side="both", notes=[]))

    def test_invalid_options_are_reported(self):
        for field, value in (("note_side", "middle"), ("note_layout", "diagonal"),
                             ("note_columns", 0), ("note_columns", True)):
            project = {"slug": "test", "title": "Test", "thumbnail": "project-01.png",
                       "sections": [self.section(**{field: value})]}
            errors = validate_project(project, Path("test.toml"))
            self.assertTrue(any(field in error for error in errors), errors)

    def test_pdf_notes_are_on_the_selected_edge_without_clipping(self):
        for side in ("top", "bottom", "both"):
            for layout in ("horizontal", "staggered"):
                # Several rows exercise the leaders that route around later rows.
                notes = [{"title": f"Note {index}", "text": "An annotated feature.",
                          "point": [.25 + .1 * (index % 3), .2 if index < 4 else .8]}
                         for index in range(8)]
                section = self.section(note_side=side, note_layout=layout, notes=notes, note_columns=3)
                flowable = _details(section, 500, STYLES)[0]
                self.assertIsInstance(flowable, EdgeAnnotatedImage)
                for item in flowable.placements:
                    self.assertGreaterEqual(item["top"] - item["height"], 0)
                    self.assertLessEqual(item["top"], flowable.height)
                    if item["edge"] == "top":
                        self.assertGreater(item["top"] - item["height"], flowable.image_y + flowable.image_height)
                    else:
                        self.assertLess(item["top"], flowable.image_y)
                output = io.BytesIO()
                canvas = Canvas(output, pagesize=(560, flowable.height + 60))
                flowable.drawOn(canvas, 30, 30)
                canvas.save()
                text = PdfReader(io.BytesIO(output.getvalue())).pages[0].extract_text()
                for note in notes:
                    self.assertIn(note["title"], text)


if __name__ == "__main__":
    unittest.main()
