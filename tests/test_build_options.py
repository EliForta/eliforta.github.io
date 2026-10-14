"""Build CLI coverage for the optional compressed PDF and freshness checks."""

import io
import tempfile
import unittest
from contextlib import ExitStack, redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

import build
import build_pdf


class BuildOptionsTests(unittest.TestCase):
    def setUp(self):
        self.stack = ExitStack()
        self.addCleanup(self.stack.close)
        self.root = Path(self.stack.enter_context(tempfile.TemporaryDirectory()))
        self.pdf_path = self.root / "output" / "pdf" / "ef-portfolio.pdf"
        self.compressed_path = self.pdf_path.with_stem("ef-portfolio-compressed")
        self.index = self.root / "index.html"
        self.stack.enter_context(patch.object(build, "ROOT", self.root))
        self.stack.enter_context(patch.object(build_pdf, "OUTPUT_PATH", self.pdf_path))
        self.stack.enter_context(patch.object(build_pdf, "COMPRESSED_OUTPUT_PATH", self.compressed_path))
        self.stack.enter_context(patch.object(build, "load_projects", return_value=[{"slug": "example"}]))
        self.stack.enter_context(patch.object(build, "build_outputs", return_value={self.index: "site"}))
        self.stack.enter_context(patch.object(
            build_pdf, "render_portfolio_pdf",
            side_effect=lambda projects, *, compress_images=False: b"compressed" if compress_images else b"regular",
        ))

    def run_build(self, *options):
        output, errors = io.StringIO(), io.StringIO()
        with patch("sys.argv", ["build.py", *options]), redirect_stdout(output), redirect_stderr(errors):
            result = build.main()
        return result, output.getvalue(), errors.getvalue()

    def test_regular_build_does_not_create_or_check_optional_pdf(self):
        self.assertEqual(self.run_build()[0], 0)
        self.assertEqual(self.pdf_path.read_bytes(), b"regular")
        self.assertFalse(self.compressed_path.exists())
        self.compressed_path.write_bytes(b"stale optional copy")
        self.assertEqual(self.run_build("--check")[0], 0)
        self.assertEqual(self.compressed_path.read_bytes(), b"stale optional copy")

    def test_option_generates_both_pdfs_and_checks_them(self):
        self.assertEqual(self.run_build("--compressed-pdf")[0], 0)
        self.assertEqual(self.pdf_path.read_bytes(), b"regular")
        self.assertEqual(self.compressed_path.read_bytes(), b"compressed")
        self.assertEqual(self.run_build("--check", "--compressed-pdf")[0], 0)

    def test_check_detects_missing_and_stale_compressed_pdf_without_writing(self):
        self.run_build()
        for contents in (None, b"stale"):
            with self.subTest(contents=contents):
                if contents is not None:
                    self.compressed_path.write_bytes(contents)
                result, _, errors = self.run_build("--check", "--compressed-pdf")
                self.assertEqual(result, 1)
                self.assertIn("output/pdf/ef-portfolio-compressed.pdf", errors)
                self.assertIn("Run: python3 build.py --compressed-pdf", errors)
                if contents is None:
                    self.assertFalse(self.compressed_path.exists())
                else:
                    self.assertEqual(self.compressed_path.read_bytes(), contents)

    def test_check_still_detects_stale_regular_pdf_with_option(self):
        self.run_build("--compressed-pdf")
        self.pdf_path.write_bytes(b"stale regular copy")
        result, _, errors = self.run_build("--check", "--compressed-pdf")
        self.assertEqual(result, 1)
        self.assertIn("- output/pdf/ef-portfolio.pdf", errors)
        self.assertNotIn("- output/pdf/ef-portfolio-compressed.pdf", errors)
        self.assertEqual(self.pdf_path.read_bytes(), b"stale regular copy")


if __name__ == "__main__":
    unittest.main()
