"""HTML image-surface treatment regressions."""

import unittest

from build import has_elevated_image_surface, is_transparent_art_source, render_media, render_section


class ImageSurfaceTests(unittest.TestCase):
    def test_transparent_line_art_stays_flat(self):
        source = "assets/images/actuator/actuator.png"
        self.assertTrue(is_transparent_art_source(source))
        self.assertFalse(has_elevated_image_surface({"src": source}))
        self.assertNotIn("media-surface--elevated", render_media({"src": source}, "Actuator"))

    def test_photos_receive_the_elevated_surface(self):
        for source in (
            "assets/images/actuator/actuator1.jpg",
            "assets/images/slider/slider1.png",
            "assets/images/slider/slider.gif",
        ):
            with self.subTest(source=source):
                self.assertTrue(has_elevated_image_surface({"src": source}))
                self.assertIn("media-surface--elevated", render_media({"src": source}, "Photo"))

    def test_surface_can_be_overridden_for_future_assets(self):
        source = "assets/images/actuator/actuator.png"
        self.assertTrue(has_elevated_image_surface({"src": source, "surface": "elevated"}))
        self.assertFalse(has_elevated_image_surface({"src": "photo.jpg", "surface": "flat"}))

    def test_standalone_image_passes_surface_override_to_media_renderer(self):
        markup = render_section(
            {"type": "image", "src": "assets/images/slider/slider.gif", "surface": "flat"},
            0,
            "Slider",
            set(),
        )
        self.assertNotIn("media-surface--elevated", markup)

    def test_reduced_single_split_image_releases_space_to_copy(self):
        markup = render_section(
            {
                "type": "split",
                "title": "Version 2",
                "body": "More room for this copy.",
                "images": [{"src": "assets/images/actuator/actuator2.jpg", "scale": 0.5}],
            },
            0,
            "Actuator",
            set(),
        )
        self.assertIn("split-layout--compact-media", markup)
        self.assertIn("--split-media-share:30.6818%", markup)

    def test_full_size_split_image_keeps_standard_columns(self):
        markup = render_section(
            {
                "type": "split",
                "images": [{"src": "assets/images/actuator/actuator2.jpg"}],
            },
            0,
            "Actuator",
            set(),
        )
        self.assertNotIn("split-layout--compact-media", markup)


if __name__ == "__main__":
    unittest.main()
