#!/usr/bin/env python3
"""Build the static portfolio and print-native PDF from project TOML files.

The generated index and project pages can be served from any static host,
including GitHub Pages. The production entry point also generates a PDF;
``dev.py`` intentionally calls the HTML-only helpers for fast live reloads.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import math
import re
import struct
import sys
import tomllib
from pathlib import Path
from urllib.parse import quote, urlsplit


ROOT = Path(__file__).resolve().parent
CONTENT_DIR = ROOT / "content" / "projects"
TEMPLATE_DIR = ROOT / "templates"
ALLOWED_TYPES = {
    "text", "split", "gallery", "details", "detail", "image", "columns", "quote",
    "text-image", "image-text", "text-stack", "stack-text",
}
TYPE_ALIASES = {
    "detail": "details",
    "text-image": "split",
    "image-text": "split",
    "text-stack": "split",
    "stack-text": "split",
}
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CSS_COLOR_RE = re.compile(r"^#[0-9a-fA-F]{3,8}$")
CSS_POSITION_RE = re.compile(r"^[0-9.]+%(?:\s+[0-9.]+%){1,2}$|^(?:center|left|right|top|bottom)(?:\s+(?:center|left|right|top|bottom))?$")
VIDEO_EXTENSIONS = {".mp4"}
TRANSPARENT_VECTOR_EXTENSIONS = {".svg"}


class BuildError(Exception):
    pass


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def visible_text(value: object) -> str:
    """Escape visible copy while preserving intentional newline characters."""
    normalized = str(value).replace("\r\n", "\n").replace("\r", "\n")
    return esc(normalized).replace("\n", "<br>")


def _escaped_at(source: str, index: int) -> bool:
    backslashes = 0
    index -= 1
    while index >= 0 and source[index] == "\\":
        backslashes += 1
        index -= 1
    return backslashes % 2 == 1


def allow_raw_string_newlines(source: str) -> str:
    """Make raw newlines in ordinary double-quoted values TOML-compatible.

    TOML normally requires either ``\n`` or triple quotes. This compatibility
    pass promotes only an ordinary quoted string that reaches a physical
    newline before its closing quote. Valid strings and multiline strings are
    copied byte-for-byte.
    """
    output: list[str] = []
    index = 0
    length = len(source)
    while index < length:
        if source.startswith('"""', index):
            end = index + 3
            while end < length:
                if source.startswith('"""', end) and not _escaped_at(source, end):
                    end += 3
                    break
                end += 1
            output.append(source[index:end])
            index = end
            continue
        if source.startswith("'''", index):
            end = source.find("'''", index + 3)
            end = length if end < 0 else end + 3
            output.append(source[index:end])
            index = end
            continue
        if source[index] == "#":
            end = source.find("\n", index)
            end = length if end < 0 else end
            output.append(source[index:end])
            index = end
            continue
        if source[index] == "'":
            end = source.find("'", index + 1)
            end = length if end < 0 else end + 1
            output.append(source[index:end])
            index = end
            continue
        if source[index] != '"':
            output.append(source[index])
            index += 1
            continue

        end = index + 1
        while end < length and source[end] != "\n":
            if source[end] == '"' and not _escaped_at(source, end):
                break
            end += 1
        if end < length and source[end] == '"':
            output.append(source[index:end + 1])
            index = end + 1
            continue

        closing = end + 1
        while closing < length:
            if source[closing] == '"' and not _escaped_at(source, closing):
                break
            closing += 1
        if closing >= length:
            output.append(source[index:])
            break
        output.append('"""')
        output.append(source[index + 1:closing])
        output.append('"""')
        index = closing + 1
    return "".join(output)


def slugify(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return value or "section"


def paragraphs(value: object, class_name: str = "rich-text") -> str:
    if value is None:
        return ""
    parts: list[str] = []
    values = value if isinstance(value, list) else [value]
    for item in values:
        if not isinstance(item, str):
            raise BuildError("text content must be a string or an array of strings")
        parts.extend(part.strip() for part in re.split(r"\n\s*\n", item) if part.strip())
    rendered = "".join(f"<p>{visible_text(part)}</p>" for part in parts)
    return f'<div class="{class_name}">{rendered}</div>' if rendered else ""


def public_url(value: str, prefix: str = "../../") -> str:
    if value.startswith(("https://", "http://", "data:", "/")):
        return value
    value = asset_source(value)
    return prefix + quote(value, safe="/@:+~,-._")


def asset_source(value: str) -> str:
    """Return the repository-relative asset path, supporting a short filename."""
    if value.startswith(("https://", "http://", "data:", "/")):
        return value
    path = Path(value)
    if ".." in path.parts:
        return value
    if (ROOT / path).is_file():
        return value
    shorthand = Path("assets/images") / path
    if (ROOT / shorthand).is_file():
        return shorthand.as_posix()
    return value


def local_asset_exists(value: str) -> bool:
    if value.startswith(("https://", "http://", "data:", "/")):
        return True
    return asset_source(value) != value or (".." not in Path(value).parts and (ROOT / value).is_file())


def is_video_source(value: object) -> bool:
    """Return whether a media source should use the GIF-like video renderer."""
    source = str(value or "")
    if source.lower().startswith("data:video/mp4"):
        return True
    return Path(urlsplit(source).path).suffix.lower() in VIDEO_EXTENSIONS


def is_transparent_art_source(value: object) -> bool:
    """Recognize image formats that should keep floating directly on the page.

    Transparent PNGs cover the portfolio's CAD and line-art assets. SVGs are
    treated conservatively as transparent artwork; opaque raster formats keep
    the subtle framed-photo treatment.
    """
    source = str(value or "")
    if source.lower().startswith("data:image/svg+xml"):
        return True
    if source.startswith(("https://", "http://", "data:", "/")):
        return Path(urlsplit(source).path).suffix.lower() in TRANSPARENT_VECTOR_EXTENSIONS

    resolved = ROOT / asset_source(source)
    suffix = resolved.suffix.lower()
    if suffix in TRANSPARENT_VECTOR_EXTENSIONS:
        return True
    if suffix != ".png":
        return False

    try:
        with resolved.open("rb") as image_file:
            if image_file.read(8) != b"\x89PNG\r\n\x1a\n":
                return False
            while True:
                length_bytes = image_file.read(4)
                if len(length_bytes) != 4:
                    return False
                length = struct.unpack(">I", length_bytes)[0]
                chunk_type = image_file.read(4)
                chunk_data = image_file.read(length)
                image_file.read(4)  # CRC
                if chunk_type == b"IHDR" and len(chunk_data) >= 10:
                    if chunk_data[9] in {4, 6}:
                        return True
                elif chunk_type == b"tRNS":
                    return True
                elif chunk_type in {b"IDAT", b"IEND"}:
                    return False
    except OSError:
        return False


def has_elevated_image_surface(item: dict) -> bool:
    """Return whether this visual should receive rounded corners and a shadow."""
    surface = item.get("surface", "auto")
    if surface in {False, "flat", "transparent"}:
        return False
    if surface in {True, "elevated", "framed"}:
        return True
    return is_video_source(item.get("src")) or not is_transparent_art_source(item.get("src"))


def image_dimensions(item: dict) -> str:
    width, height = item.get("width"), item.get("height")
    if isinstance(width, int) and width > 0 and isinstance(height, int) and height > 0:
        return f' width="{width}" height="{height}"'
    # Reserve natural image space before lazy loading, including in masonry
    # columns. PNG/GIF cover the project's renders, photos, and animations.
    src = str(item.get("src", ""))
    if src and not src.startswith(("http:", "https:", "data:", "/")) and ".." not in Path(src).parts:
        try:
            with (ROOT / asset_source(src)).open("rb") as image_file:
                header = image_file.read(24)
            if header.startswith(b"\x89PNG\r\n\x1a\n") and len(header) == 24:
                width = int.from_bytes(header[16:20], "big")
                height = int.from_bytes(header[20:24], "big")
            elif header[:6] in (b"GIF87a", b"GIF89a") and len(header) >= 10:
                width = int.from_bytes(header[6:8], "little")
                height = int.from_bytes(header[8:10], "little")
            else:
                return ""
            if width > 0 and height > 0:
                return f' width="{width}" height="{height}"'
        except OSError:
            pass
    return ""


def normalized_image_scale(item: dict) -> float:
    try:
        scale = min(4.0, max(0.1, float(item.get("scale", 1))))
    except (TypeError, ValueError):
        scale = 1
    return scale if math.isfinite(scale) else 1


def image_style(item: dict) -> str:
    fit = item.get("fit", "cover")
    if fit not in {"cover", "contain"}:
        fit = "cover"
    scale = normalized_image_scale(item)
    # Scaling via transform alone leaves the natural media frame at its
    # original height. Keep scale-ups as a crop/zoom, but let scale-downs
    # reduce the natural frame itself so stacked media keeps a stable rhythm.
    layout_scale = min(scale, 1)
    layout_width = f"{layout_scale * 100:g}%"
    transform_scale = scale / layout_scale
    position = str(item.get("position", "50% 50%"))
    if not CSS_POSITION_RE.fullmatch(position):
        position = "50% 50%"
    return esc(
        f"--image-fit:{fit};--image-scale:{transform_scale:g};"
        f"--image-layout-width:{layout_width};--image-position:{position}"
    )


def render_visual(
    item: dict,
    url: str,
    alt: str,
    *,
    class_name: str = "",
    loading: str = "lazy",
) -> str:
    """Render an image or a silent MP4 using the same TOML presentation fields."""
    classes = f' class="{esc(class_name)}"' if class_name else ""
    attrs = image_dimensions(item)
    style = image_style(item)
    if is_video_source(item.get("src")):
        accessibility = f' aria-label="{esc(alt)}"' if alt else ' aria-hidden="true"'
        preload = "auto" if loading == "eager" else "metadata"
        return (
            f'<video{classes} src="{esc(url)}"{accessibility}{attrs} autoplay muted loop playsinline '
            f'preload="{preload}" disablepictureinpicture disableremoteplayback style="{style}">'
            "Your browser does not support embedded MP4 video.</video>"
        )
    return (
        f'<img{classes} src="{esc(url)}" alt="{esc(alt)}"{attrs} loading="{loading}" '
        f'style="{style}">'
    )


def normalize_section(section: dict) -> dict:
    """Normalize friendly type aliases and compact single-image split syntax."""
    normalized = dict(section)
    original_kind = str(normalized.get("type", ""))
    kind = TYPE_ALIASES.get(original_kind, original_kind)
    normalized["type"] = kind
    if original_kind in {"text-image", "image-text", "text-stack", "stack-text"}:
        normalized.setdefault("image_side", "left" if original_kind in {"image-text", "stack-text"} else "right")
        normalized.setdefault("media_layout", "stack" if original_kind in {"text-stack", "stack-text"} else "single")
    if kind == "split" and not normalized.get("images"):
        if normalized.get("image"):
            image = normalized["image"]
            if isinstance(image, str):
                image = {"src": image, "alt": normalized.get("image_alt", ""), "caption": normalized.get("image_caption")}
            elif isinstance(image, dict):
                image = dict(image)
            else:
                image = None
            if image:
                normalized["images"] = [image]
        elif normalized.get("src"):
            normalized["images"] = [{"src": normalized["src"], "alt": normalized.get("alt", ""), "caption": normalized.get("caption")}]
    return normalized


def section_images(section: dict) -> list[dict]:
    images = section.get("images", [])
    if isinstance(images, dict):
        images = [images]
    if not isinstance(images, list):
        return []
    normalized: list[dict] = []
    for item in images:
        if isinstance(item, str):
            # String arrays stay concise; authors can use tables whenever they
            # need a hand-written alt, caption, crop, or lightbox setting.
            label = re.sub(r"[-_]+", " ", Path(item).stem).strip().capitalize()
            normalized.append({"src": item, "alt": label})
        elif isinstance(item, dict):
            normalized.append(item)
    return normalized


def render_heading(section: dict, section_id: str) -> str:
    title = section.get("title")
    eyebrow = section.get("eyebrow")
    if not title and not eyebrow:
        return ""
    eyebrow_html = f'<p class="section-eyebrow">{visible_text(eyebrow)}</p>' if eyebrow else ""
    title_html = f'<h2 id="{esc(section_id)}-title">{visible_text(title)}</h2>' if title else ""
    return f'<header class="section-heading">{eyebrow_html}{title_html}</header>'


def render_media(item: dict, project_title: str, classes: str = "") -> str:
    caption = item.get("caption")
    ratio = item.get("ratio", "natural")
    if ratio not in {"natural", "landscape", "portrait", "square", "wide"}:
        ratio = "natural"
    figure_classes = f"media-item ratio--{ratio} {classes}".strip()
    caption_html = f"<figcaption>{visible_text(caption)}</figcaption>" if caption else ""

    if item.get("placeholder"):
        label = visible_text(item["placeholder"])
        return (
            f'<figure class="{figure_classes} media-placeholder">'
            f'<div class="media-frame"><span>{label}</span></div>{caption_html}</figure>'
        )

    src = str(item.get("src", ""))
    alt = str(item.get("alt", ""))
    url = public_url(src)
    loading = "eager" if item.get("eager") else "lazy"
    visual = render_visual(item, url, alt, loading=loading)
    lightbox = item.get("lightbox", True)
    frame_class = "media-frame media-surface--elevated" if has_elevated_image_surface(item) else "media-frame"
    frame_style = esc(f"--image-layout-width:{min(normalized_image_scale(item), 1) * 100:g}%")
    if lightbox:
        dialog_scale = item.get("dialog_scale", 1)
        frame = (
            f'<a class="{frame_class}" href="{esc(url)}" data-lightbox '
            f'data-title="{esc(caption or project_title)}" data-dialog-scale="{esc(dialog_scale)}" '
            f'style="{frame_style}">{visual}</a>'
        )
    else:
        frame = f'<div class="{frame_class}" style="{frame_style}">{visual}</div>'
    return f'<figure class="{figure_classes}">{frame}{caption_html}</figure>'


def section_classes(section: dict, kind: str) -> str:
    theme = section.get("theme", "paper")
    if theme not in {"paper", "soft", "dark"}:
        theme = "paper"
    width = section.get("width", "wide")
    if width not in {"reading", "wide", "full"}:
        width = "wide"
    spacing = section.get("spacing", "normal")
    if spacing not in {"compact", "normal", "generous"}:
        spacing = "normal"
    classes = f"project-section section--{kind} theme--{theme} width--{width} spacing--{spacing}"
    if kind == "details":
        align = section.get("align", "left")
        align = align if align in {"left", "right"} else "left"
        classes += f" align--{align}"
    return classes


def detail_note_options(section: dict) -> tuple[str, str, int]:
    """Share annotation layout defaults between the website and PDF."""
    side = section.get("note_side", "left")
    side = side if side in {"left", "right", "top", "bottom", "both"} else "left"
    layout = section.get("note_layout", "horizontal")
    layout = layout if layout in {"horizontal", "staggered"} else "horizontal"
    columns = section.get("note_columns", 3)
    columns = columns if type(columns) is int and 1 <= columns <= 4 else 3
    return side, layout, columns


def detail_note_edge(note: dict, side: str) -> str:
    """For both edges, use an explicit side or the point's nearest edge."""
    if side != "both":
        return side
    if note.get("side") in {"top", "bottom"}:
        return note["side"]
    return "top" if float(note.get("point", [.5, .5])[1]) < .5 else "bottom"


def render_section(section: dict, index: int, project_title: str, used_ids: set[str]) -> str:
    section = normalize_section(section)
    kind = str(section.get("type", ""))
    proposed_id = str(section.get("id") or slugify(str(section.get("title") or f"section-{index + 1}")))
    section_id = proposed_id
    suffix = 2
    while section_id in used_ids:
        section_id = f"{proposed_id}-{suffix}"
        suffix += 1
    used_ids.add(section_id)
    heading = render_heading(section, section_id)
    labelled = f' aria-labelledby="{esc(section_id)}-title"' if section.get("title") else ""
    classes = section_classes(section, kind)

    if kind == "text":
        content = heading + paragraphs(section.get("body"))

    elif kind == "split":
        side = section.get("image_side", "right")
        side = side if side in {"left", "right"} else "right"
        layout = section.get("media_layout", "single")
        layout = layout if layout in {"single", "stack", "grid"} else "single"
        images = section_images(section)
        media = "".join(render_media(item, project_title) for item in images)
        copy = heading + paragraphs(section.get("body"))
        split_classes = f"split-layout media--{esc(side)}"
        split_style = ""
        if (
            layout == "single"
            and len(images) == 1
            and images[0].get("ratio", "natural") == "natural"
            and normalized_image_scale(images[0]) < 1
        ):
            # A reduced natural image should reduce its grid track as well as its
            # frame. Otherwise the invisible remainder of the media column steals
            # usable line length from the adjacent copy.
            media_share = (1.35 / (0.85 + 1.35)) * normalized_image_scale(images[0]) * 100
            split_classes += " split-layout--compact-media"
            split_style = f' style="--split-media-share:{media_share:g}%"'
        content = (
            f'<div class="{split_classes}"{split_style}>'
            f'<div class="split-copy">{copy}</div>'
            f'<div class="split-media media-layout--{esc(layout)}">{media}</div></div>'
        )

    elif kind == "gallery":
        layout = section.get("layout", "grid")
        layout = layout if layout in {"grid", "collage", "filmstrip"} else "grid"
        columns = section.get("columns", 3 if layout == "collage" else 2)
        columns = columns if isinstance(columns, int) and 2 <= columns <= 4 else 2
        images = "".join(render_media(item, project_title) for item in section_images(section))
        content = heading + f'<div class="project-gallery gallery--{layout}" style="--gallery-columns:{columns}">{images}</div>'

    elif kind == "details":
        side, layout, columns = detail_note_options(section)
        item = {
            "src": section.get("image", ""),
            "alt": section.get("image_alt", ""),
            "width": section.get("image_width"),
            "height": section.get("image_height"),
            "fit": section.get("image_fit", "contain"),
            "scale": section.get("image_scale", 1),
        }
        groups = {edge: [] for edge in ("left", "right", "top", "bottom")}
        for note in section.get("notes", []):
            point = note.get("point", [0.5, 0.5])
            point_attr = esc(f"[{float(point[0]):g},{float(point[1]):g}]")
            groups[detail_note_edge(note, side)].append(
                f'<li class="view-note" data-point="{point_attr}"><h3>{visible_text(note.get("title", "Detail"))}</h3>'
                f'<p>{visible_text(note.get("text", ""))}</p></li>'
            )
        image = render_visual(
            item,
            public_url(str(item["src"])),
            str(item["alt"]),
            class_name=(
                "annotated-image media-surface--elevated"
                if has_elevated_image_surface(item)
                else "annotated-image"
            ),
        )
        if side in {"top", "bottom", "both"}:
            def edge_notes(edge):
                notes = groups[edge]
                if not notes:
                    return ""
                count = min(columns, len(notes))
                return (f'<ul class="view-notes view-notes--{edge}" style="--note-columns:{count}">'
                        f'{"".join(notes)}</ul>')

            content = (
                heading + f'<div class="annotated-view notes--{side} note-layout--{layout}">'
                f'{edge_notes("top")}{image}{edge_notes("bottom")}'
                '<svg class="annotation-lines" aria-hidden="true"></svg></div>'
            )
        else:
            content = (
                heading + f'<div class="annotated-view notes--{side}">{image}'
                f'<ul class="view-notes">{"".join(groups[side])}</ul>'
                '<svg class="annotation-lines" aria-hidden="true"></svg></div>'
            )

    elif kind == "image":
        style = section.get("style", "wide")
        style = style if style in {"inset", "wide", "full"} else "wide"
        item = {
            "src": section.get("src", ""), "alt": section.get("alt", ""),
            "caption": section.get("caption"), "ratio": section.get("ratio", "natural"),
            "fit": section.get("fit", "cover"), "position": section.get("position", "50% 50%"),
            "scale": section.get("scale", 1), "width": section.get("image_width"),
            "height": section.get("image_height"), "lightbox": section.get("lightbox", True),
            "surface": section.get("surface", "auto"),
        }
        content = heading + render_media(item, project_title, f"standalone-image image-style--{style}")

    elif kind == "columns":
        columns = section.get("columns", 3)
        columns = columns if isinstance(columns, int) and 2 <= columns <= 4 else 3
        items = "".join(
            f'<article class="column-item"><h3>{visible_text(item.get("title", ""))}</h3>{paragraphs(item.get("text"))}</article>'
            for item in section.get("items", [])
        )
        content = heading + f'<div class="content-columns" style="--content-columns:{columns}">{items}</div>'

    elif kind == "quote":
        attribution = section.get("attribution")
        cite = f"<cite>{visible_text(attribution)}</cite>" if attribution else ""
        content = heading + f'<blockquote><p>{visible_text(section.get("quote", ""))}</p>{cite}</blockquote>'

    else:
        raise BuildError(f"unknown section type: {kind}")

    return f'        <section class="{classes}" id="{esc(section_id)}"{labelled}>\n          {content}\n        </section>'


def validate_image(item: dict, context: str, errors: list[str]) -> None:
    if item.get("placeholder"):
        return
    src = item.get("src")
    if not isinstance(src, str) or not src:
        errors.append(f"{context}: image needs a src (or placeholder)")
        return
    if not local_asset_exists(src):
        errors.append(f"{context}: image does not exist: {src}")
    if "position" in item and (not isinstance(item["position"], str) or not CSS_POSITION_RE.fullmatch(item["position"])):
        errors.append(f"{context}: position must be a CSS percentage or keyword position")


def validate_project(project: dict, source: Path) -> list[str]:
    errors: list[str] = []
    label = source.name
    for field in ("slug", "title", "thumbnail"):
        if not isinstance(project.get(field), str) or not project[field].strip():
            errors.append(f"{label}: missing required string '{field}'")
    slug = project.get("slug", "")
    if slug and not SLUG_RE.fullmatch(slug):
        errors.append(f"{label}: slug must use lowercase letters, numbers, and hyphens")
    thumbnail = project.get("thumbnail")
    if isinstance(thumbnail, str) and thumbnail and not local_asset_exists(thumbnail):
        errors.append(f"{label}: thumbnail does not exist: {thumbnail}")
    background = project.get("thumbnail_background", "#f3f4f0")
    if not isinstance(background, str) or not CSS_COLOR_RE.fullmatch(background):
        errors.append(f"{label}: thumbnail_background must be a hex color")
    position = project.get("thumbnail_position", "50% 50%")
    if not isinstance(position, str) or not CSS_POSITION_RE.fullmatch(position):
        errors.append(f"{label}: thumbnail_position must be a CSS percentage or keyword position")
    tags = project.get("tags")
    if tags is not None and (not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags)):
        errors.append(f"{label}: tags must be an array of strings")
    sections = project.get("sections", [])
    if not isinstance(sections, list) or not sections:
        errors.append(f"{label}: add at least one [[sections]] block")
        return errors
    for index, section in enumerate(sections, 1):
        context = f"{label}, section {index}"
        if not isinstance(section, dict):
            errors.append(f"{context}: section must be a TOML table")
            continue
        section = normalize_section(section)
        kind = section.get("type")
        if kind not in ALLOWED_TYPES:
            errors.append(f"{context}: type must be one of {', '.join(sorted(ALLOWED_TYPES))}")
            continue
        if kind in {"split", "gallery"}:
            images = section_images(section)
            if not images:
                errors.append(f"{context}: add at least one [[sections.images]] block")
            for image_index, item in enumerate(images, 1):
                validate_image(item, f"{context}, image {image_index}", errors)
        elif kind == "image":
            validate_image(section, context, errors)
        elif kind == "details":
            validate_image({"src": section.get("image"), "alt": section.get("image_alt")}, context, errors)
            if section.get("note_side", "left") not in {"left", "right", "top", "bottom", "both"}:
                errors.append(f"{context}: note_side must be left, right, top, bottom, or both")
            if section.get("note_layout", "horizontal") not in {"horizontal", "staggered"}:
                errors.append(f"{context}: note_layout must be horizontal or staggered")
            columns = section.get("note_columns", 3)
            if type(columns) is not int or not 1 <= columns <= 4:
                errors.append(f"{context}: note_columns must be an integer from 1 to 4")
            notes = section.get("notes", [])
            if not isinstance(notes, list):
                errors.append(f"{context}: notes must be an array of tables")
                notes = []
            for note_index, note in enumerate(notes, 1):
                if not isinstance(note, dict):
                    errors.append(f"{context}, note {note_index}: note must be a TOML table")
                    continue
                if "side" in note and note["side"] not in {"top", "bottom"}:
                    errors.append(f"{context}, note {note_index}: side must be top or bottom")
                point = note.get("point")
                valid = isinstance(point, list) and len(point) == 2 and all(isinstance(n, (int, float)) and 0 <= n <= 1 for n in point)
                if not valid:
                    errors.append(f"{context}, note {note_index}: point must be two numbers from 0 to 1")
        elif kind == "columns":
            items = section.get("items")
            if not isinstance(items, list) or not items:
                errors.append(f"{context}: add at least one [[sections.items]] block")
            elif any(not isinstance(item, dict) for item in items):
                errors.append(f"{context}: items must be an array of tables")
    return errors


def load_projects() -> list[dict]:
    projects: list[dict] = []
    errors: list[str] = []
    for source in sorted(CONTENT_DIR.glob("*.toml")):
        try:
            raw = source.read_text(encoding="utf-8")
            try:
                project = tomllib.loads(raw)
            except tomllib.TOMLDecodeError:
                project = tomllib.loads(allow_raw_string_newlines(raw))
        except tomllib.TOMLDecodeError as exc:
            errors.append(f"{source.name}: invalid TOML: {exc}")
            continue
        project["_source"] = source
        if not project.get("draft", False):
            errors.extend(validate_project(project, source))
            projects.append(project)
    slugs = [project.get("slug") for project in projects]
    for slug in sorted({slug for slug in slugs if slugs.count(slug) > 1}):
        errors.append(f"duplicate project slug: {slug}")
    if errors:
        raise BuildError("\n".join(f"- {error}" for error in errors))
    return sorted(projects, key=lambda item: (item.get("order", 9999), item["title"].lower()))


def render_card(project: dict, position: int) -> str:
    fit = project.get("thumbnail_fit", "cover")
    fit = fit if fit in {"contain", "cover"} else "cover"
    try:
        scale = min(4.0, max(0.1, float(project.get("thumbnail_scale", 1))))
    except (TypeError, ValueError):
        scale = 1
    if not math.isfinite(scale):
        scale = 1
    position_value = str(project.get("thumbnail_position", "50% 50%"))
    background = project.get("thumbnail_background", "#f3f4f0")
    year = project.get("year")
    year_html = f'<span class="card-year">{visible_text(year)}</span>' if year else ""
    thumbnail_item = {
        "src": project["thumbnail"],
        "fit": fit,
        "scale": scale,
        "position": position_value,
    }
    elevated_surface = has_elevated_image_surface(thumbnail_item)
    # A transform changes the artwork without changing its layout box. For
    # contained, transparent cutouts, let scale-downs reduce the box too so the
    # caption gap stays constant. Cropped/elevated images keep a fixed surface.
    layout_scale = scale if fit == "contain" and not elevated_surface and scale < 1 else 1
    transform_scale = scale / layout_scale
    desktop_ratio = 1.4 / layout_scale
    mobile_ratio = 1.5 / layout_scale
    style = esc(
        f"--thumb-fit:{fit};--thumb-scale:{transform_scale:g};"
        f"--thumb-position:{position_value};--thumb-bg:{background};"
        f"--thumb-art-ratio:{desktop_ratio:g};--thumb-art-ratio-mobile:{mobile_ratio:g}"
    )
    thumbnail = render_visual(
        thumbnail_item,
        public_url(project["thumbnail"], "./"),
        str(project.get("thumbnail_alt", project["title"])),
        class_name="project-thumbnail",
        loading="eager" if position <= 2 else "lazy",
    )
    art_class = f"project-art project-art--{fit}"
    if elevated_surface:
        art_class += " media-surface--elevated"
    return f'''          <article class="project">
            <a class="project-link" href="./projects/{esc(project['slug'])}/" aria-label="Explore {esc(project['title'])}">
              <div class="{art_class}" style="{style}">
                {thumbnail}
                <span class="view-drawing" aria-hidden="true">Explore project <svg viewBox="0 0 20 20" fill="none"><path d="M5 15 15 5M5 5h10v10"/></svg></span>
              </div>
              <div class="project-caption">
                <div><h3>{visible_text(project['title'])}</h3><p class="card-meta"><span>{visible_text(project.get('card_label') or project.get('subtitle', ''))}</span>{year_html}</p></div>
                <span class="project-arrow" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none"><path d="M5 12h14m-6-6 6 6-6 6"/></svg></span>
              </div>
            </a>
          </article>'''


def render_project(project: dict) -> str:
    template = (TEMPLATE_DIR / "project.html").read_text(encoding="utf-8")
    used_ids: set[str] = set()
    sections = "\n\n".join(
        render_section(section, index, project["title"], used_ids)
        for index, section in enumerate(project["sections"])
    )
    meta_items = []
    if project.get("role"):
        meta_items.append(f'<li><span>Role</span>{visible_text(project["role"])}</li>')
    if project.get("tags"):
        tags = project["tags"] if isinstance(project["tags"], list) else [project["tags"]]
        meta_items.append(f'<li><span>Focus</span>{visible_text(" · ".join(str(tag) for tag in tags))}</li>')
    meta = f'<ul class="project-meta">{"".join(meta_items)}</ul>' if meta_items else ""
    eyebrow = f'<p class="eyebrow">{visible_text(project["eyebrow"])}</p>' if project.get("eyebrow") else ""
    year = project.get("year")
    project_year = f'<p class="project-year" aria-label="Year {esc(year)}">{visible_text(year)}</p>' if year else ""
    subtitle = project.get("subtitle", "")
    subtitle_html = f'<p class="project-subtitle">{visible_text(subtitle)}</p>' if str(subtitle).strip() else ""
    replacements = {
        "DOCUMENT_TITLE": esc(f'{project["title"]} — EF'),
        "DESCRIPTION": esc(project.get("description") or project.get("subtitle") or project["title"]),
        "EYEBROW": eyebrow,
        "TITLE": visible_text(project["title"]),
        "PROJECT_YEAR": project_year,
        "SUBTITLE": subtitle_html,
        "PROJECT_META": meta,
        "SECTIONS": sections,
    }
    for token, value in replacements.items():
        template = template.replace("{{" + token + "}}", value)
    return '<!-- Generated by build.py. Edit content/projects/*.toml, not this file. -->\n' + template


def build_outputs(projects: list[dict]) -> dict[Path, str]:
    featured = [project for project in projects if project.get("featured", True)]
    index_template = (TEMPLATE_DIR / "index.html").read_text(encoding="utf-8")
    cards = "\n\n".join(render_card(project, position) for position, project in enumerate(featured, 1))
    index_html = index_template.replace("{{PROJECT_CARDS}}", cards)
    outputs = {ROOT / "index.html": '<!-- Generated by build.py. Edit templates/index.html or content/projects/*.toml. -->\n' + index_html}
    for project in projects:
        outputs[ROOT / "projects" / project["slug"] / "index.html"] = render_project(project)
    style_version = hashlib.sha256((ROOT / "styles.css").read_bytes()).hexdigest()[:12]
    return {path: contents.replace("{{STYLE_VERSION}}", style_version) for path, contents in outputs.items()}


def prune_generated_pages(outputs: dict[Path, str]) -> None:
    """Remove stale pages only when they were previously generated by this script."""
    expected_pages = {path.resolve() for path in outputs if path.parent.parent.resolve() == (ROOT / "projects").resolve()}
    projects_root = ROOT / "projects"
    if not projects_root.is_dir():
        return
    for page in projects_root.glob("*/index.html"):
        if page.resolve() in expected_pages:
            continue
        try:
            generated = page.read_text(encoding="utf-8").startswith("<!-- Generated by build.py.")
        except OSError:
            continue
        if generated:
            page.unlink()
            try:
                page.parent.rmdir()
            except OSError:
                pass


def write_outputs(outputs: dict[Path, str]) -> None:
    """Write generated files and prune only stale pages previously generated here."""
    for path, contents in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(contents, encoding="utf-8")
    prune_generated_pages(outputs)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate content and verify generated pages are current")
    args = parser.parse_args()
    try:
        projects = load_projects()
        outputs = build_outputs(projects)
        try:
            from build_pdf import OUTPUT_PATH as pdf_path
            from build_pdf import render_portfolio_pdf
        except ImportError as exc:
            raise BuildError(
                "PDF dependencies are missing. Run: python3 -m pip install -r requirements.txt"
            ) from exc
        try:
            pdf_bytes = render_portfolio_pdf(projects)
        except Exception as exc:
            raise BuildError(f"PDF build failed: {exc}") from exc
    except (BuildError, OSError) as exc:
        print(f"Build failed:\n{exc}", file=sys.stderr)
        return 1

    if args.check:
        stale = [path for path, expected in outputs.items() if not path.exists() or path.read_text(encoding="utf-8") != expected]
        if not pdf_path.exists() or pdf_path.read_bytes() != pdf_bytes:
            stale.append(pdf_path)
        if stale:
            print("Generated files are out of date:", file=sys.stderr)
            for path in stale:
                print(f"- {path.relative_to(ROOT)}", file=sys.stderr)
            print("Run: python3 build.py", file=sys.stderr)
            return 1
        print(f"OK: {len(projects)} projects validated; generated pages and PDF are current.")
        return 0

    write_outputs(outputs)
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    pdf_path.write_bytes(pdf_bytes)
    print(f"Built {len(projects)} projects, the home page, and {pdf_path.relative_to(ROOT)}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
