# EF portfolio

A static portfolio whose projects are defined entirely by TOML files. The build produces plain HTML, CSS, and JavaScript suitable for any static host, plus a PDF-native version for applications that require an uploaded document.

## Add a project

1. Copy `content/project-template.toml.example` to `content/projects/your-project.toml`.
2. Put the referenced images and silent MP4s in `assets/images/`.
3. Edit the TOML. The order of `[[sections]]` blocks is the order shown on the project page.
4. Run:

   ```sh
   python3 build.py
   ```

That single TOML file controls the home card, metadata, page URL, project navigation, and every page section. `index.html` and `projects/*/index.html` are generated files; do not edit them directly.

The complete, annotated starter file is at [`content/project-template.toml.example`](../content/project-template.toml.example). The live projects in [`content/projects/`](../content/projects/) are smaller real examples.

The hidden `layout-demo` project is linked from the homepage and shows every template and layout option in one place.

## Project fields

These top-level fields define the project and its home-page card:

| Field | Required | Purpose |
| --- | --- | --- |
| `slug` | yes | URL-safe page name, such as `desk-lamp` |
| `order` | no | Sort order; defaults to the end |
| `title` | yes | Project title |
| `subtitle` | no | Optional short line beneath the title |
| `card_label` | no | Home-card category; falls back to `subtitle` |
| `description` | no | Search/meta description |
| `thumbnail` | yes | Image or MP4 path; a root-relative path or a filename in `assets/images/` |
| `thumbnail_alt` | no | Optional accessible description; falls back to the project title |
| `thumbnail_fit` | no | `cover` or `contain` |
| `thumbnail_scale` | no | Fine scale control, normally `1.0` |
| `thumbnail_position` | no | CSS-style focal point, such as `35% 50%` |
| `thumbnail_background` | no | Hex background color |
| `year`, `role`, `tags` | no | Metadata shown below the page title |
| `eyebrow` | no | Small label above the page title |
| `featured` | no | Set `false` to build the page but hide its home card |
| `draft` | no | Set `true` to omit the project from the build |

## Section templates

Every section starts with `[[sections]]` and a `type`. Sections can be repeated and combined in any order.

### `text`

A focused reading block. Blank lines in a multiline `body` become paragraphs.

```toml
[[sections]]
type = "text"
title = "Overview"
width = "reading"
body = """
First paragraph.

Second paragraph.
"""
```

### `split`

Text beside one image, a vertical image stack, or a compact image grid. Changing `image_side` produces both text-left and text-right compositions without needing separate templates.

```toml
[[sections]]
type = "split"
title = "Development"
body = "How the idea became an object."
image_side = "right"       # left | right
media_layout = "stack"     # single | stack | grid

  [[sections.images]]
  src = "assets/images/sketch.jpg"
  alt = "Early form sketch"
  caption = "First direction"

  [[sections.images]]
  src = "assets/images/prototype.jpg"
  alt = "Foam prototype"
```

For compact TOML, the aliases `text-image`, `image-text`, `text-stack`, and
`stack-text` preconfigure the corresponding `split` options. `detail` is an
alias for `details`. A `split` can also use a single `image = "..."` plus
`image_alt`, when a nested `[[sections.images]]` table would be unnecessary.

### `gallery`

An arbitrary image array in a regular grid, asymmetric collage, or horizontal filmstrip.
For the shortest form, `images = ["front.jpg", "detail.jpg"]` is also
accepted; table entries are available when each image needs its own metadata.

```toml
[[sections]]
type = "gallery"
title = "Gallery"
layout = "grid"             # grid | collage | filmstrip
columns = 3                  # 2–4, used by grid and collage

  [[sections.images]]
  src = "assets/images/front.jpg"
  alt = "Front view"
  caption = "Front"
  ratio = "portrait"
```

### `details`

One large image with any number of annotated notes. `point` is `[x, y]`, measured from the image's top-left with values from `0` to `1`.

```toml
[[sections]]
type = "details"
title = "Details"
image = "assets/images/overview.jpg"
image_alt = "Overview with construction details called out"
note_side = "left"              # left | right | top | bottom | both
note_layout = "horizontal"      # horizontal | staggered; for top/bottom/both
note_columns = 3                # 1–4; maximum columns per edge on desktop
align = "right"                 # left | right; most visible with width = "reading"

  [[sections.notes]]
  title = "Quiet hinge"
  text = "The hardware disappears when closed."
  point = [0.68, 0.42]
```

Use `note_side = "top"` or `"bottom"` to place a row of callouts above or below
the image. `note_layout = "staggered"` offsets every other note away from the
image; `"horizontal"` keeps the notes aligned. Long lists wrap into additional
rows, and annotation leaders route around those rows instead of through text.
On smaller screens, these edge layouts reduce to two columns, then one, while
keeping notes on their chosen edge. Left/right layouts still move below the image.

With `note_side = "both"`, points in the upper half of the image get top notes
and points in the lower half get bottom notes. An optional `side` on each note
overrides that automatic placement:

```toml
[[sections]]
type = "detail"
image = "assets/images/overview.jpg"
note_side = "both"
note_layout = "staggered"

  [[sections.notes]]
  title = "Upper detail"
  text = "A callout above the image."
  point = [0.35, 0.25]
  side = "top"                   # top | bottom; optional with note_side = "both"

  [[sections.notes]]
  title = "Lower detail"
  text = "A callout below the image."
  point = [0.65, 0.8]
```

The PDF export uses the same edge, arrangement, and column options.

### `image`

A single image with optional title and caption. `style` can be `inset`, `wide`, or `full`.

```toml
[[sections]]
type = "image"
title = "Final object"
src = "assets/images/hero.jpg"
alt = "The finished object in use"
caption = "Final prototype"
style = "full"
```

### `columns`

Two to four short text blocks for outcomes, facts, phases, or lessons.

```toml
[[sections]]
type = "columns"
title = "Results"
columns = 3

  [[sections.items]]
  title = "40%"
  text = "Less material than the first iteration."
```

### `quote`

A large, centered statement with an optional attribution.

```toml
[[sections]]
type = "quote"
quote = "The simplest version became the strongest."
attribution = "Project reflection"
```

## Shared section and media options

Any section can use:

- `id`: custom anchor; otherwise generated from the title.
- `eyebrow`: small label above the section title.
- `width`: `reading`, `wide`, or `full`.
- `theme`: `paper`, `soft`, or `dark`.
- `spacing`: `compact`, `normal`, or `generous`.

Detail sections also accept `align = "left"` or `align = "right"`. This positions the complete detail view within the page and is most useful with `width = "reading"`; use `note_side` separately to choose which side of the image holds the callouts.

Visible text accepts `\n` in double-quoted TOML strings. It renders as an intentional line break in titles, subtitles, body copy, captions, notes, columns, and quotes:

```toml
title = "One line\nthen another"
body = "First sentence.\nSecond sentence."
```

To press Enter and write the value across source lines, use TOML's triple-quoted form:

```toml
body = """
First line.
Second line.
"""
```

The portfolio loader also accepts a raw line break inside ordinary double quotes for convenience, even though triple quotes are the portable TOML form.

Within `body`, a blank line still starts a separate paragraph.

Images and MP4s within `split` and `gallery` support:

- `src`, optional `alt`, and optional `caption`.
- `ratio`: `natural`, `landscape`, `portrait`, `square`, or `wide`.
- `fit`: `cover` or `contain`.
- `position`: a focal point such as `30% 50%`.
- `scale`: fine zoom control, normally `1.0`.
- `lightbox = false` to disable the enlarged view.
- `dialog_scale` to tune the enlarged view.
- `surface = "flat"` or `surface = "elevated"` to override the automatic image treatment.
- `width` and `height` to reserve the correct image space while loading.
- `placeholder = "Coming soon"` instead of `src` for an intentional empty slot.

Opaque photos, GIFs, and videos automatically receive slightly rounded corners
and a soft shadow. Transparent PNG/SVG artwork stays flat on the page so CAD
drawings and line art retain their cutout appearance.

Any `src` or project `thumbnail` ending in `.mp4` is rendered as GIF-like motion:
it autoplays muted, loops continuously, stays inline on mobile, and shows no playback UI.
MP4s use the same TOML presentation controls as images (`ratio`, `fit`, `position`,
`scale`, captions, and lightbox settings), so no separate markup is needed:

```toml
[[sections.images]]
src = "assets/images/my-project/motion.mp4"
alt = "The mechanism opening and closing"
ratio = "wide"
fit = "cover"
position = "50% 50%"
scale = 1.0
lightbox = true
dialog_scale = 1.0
```

## Build and preview

Python 3.11 or newer is required because TOML support is built in. Install the PDF build dependencies once:

```sh
python3 -m pip install -r requirements.txt
```

Install FFmpeg as well (`brew install ffmpeg` on macOS, or `apt install ffmpeg`
on Debian/Ubuntu). The PDF builder uses it to extract a representative still
from each local video; HTML-only development does not need it.

```sh
python3 build.py
python3 -m http.server 4173 --bind 127.0.0.1
```

The production build creates `output/pdf/ef-portfolio.pdf` directly from the TOML content. The PDF carries the site's handwritten EF headings and captions, signature, paper colors, gently tilted galleries, and dashed side annotations. Its opening page mirrors the homepage's project cards, with clickable project titles. Projects follow the same section order as the site, without inserting an extra thumbnail or SEO description.

Text, links, annotation leaders, and page layout remain native PDF elements; this is not a browser print or a screenshot. `pdf_fonts.py` uses FontTools to convert the site's OpenType outlines to embeddable TrueType in memory, preserving the Unicode mappings and font metrics. Font failures stop the build instead of silently substituting a generic face. Body copy uses an embedded sans-serif font with slightly stronger contrast for print. Animated GIFs use a labeled first frame, and local videos use a labeled representative still extracted by FFmpeg.

The PDF honors reading widths, section alignment and spacing, soft/dark themes, split layouts, natural-height collages, media aspect ratios, fit, focal point, and scale. Photos have rounded corners and soft shadows; transparent artwork stays flat. Captions align with the visible image edges, including images limited by page height. The paginator balances complete sections across each project's pages and keeps untitled galleries with their preceding explanation. Each project page has a plain current-project label in the header. Edit `build_pdf.py` for PDF composition and `pdf_fonts.py` for font embedding; the source content and artwork remain shared with the website.

The prominent opening notice links to `https://eliforta.github.io` by default.
To override the destination for a production build:

```sh
PORTFOLIO_SITE_URL="https://example.com" python3 build.py
```

Then open `http://127.0.0.1:4173`.

For an automatic development loop, use the built-in watcher instead:

```sh
python3 dev.py
```

It builds the HTML immediately (without regenerating the PDF), serves the generated site at `http://127.0.0.1:4173`, watches TOML/templates/assets/CSS/JavaScript for saves, rebuilds after each change, and reloads the open browser page. Use `--port 8080` to choose another port or `--no-live-reload` to keep serving without the browser refresh probe. Stop it with `Ctrl-C`.

For CI, the check command validates TOML, required fields, referenced local images, section types, annotation coordinates, and whether generated pages and the deterministic PDF are current:

```sh
python3 build.py --check
```

To run the PDF regression checks (embedded fonts, selectable content, project links, alternate layouts, and reproducible output):

```sh
python3 -m pip install -r requirements-dev.txt
python3 -m unittest discover -s tests -v
```

The output remains compatible with GitHub Pages and other static hosts. Run the build before publishing, or add `python3 build.py` to the host's build command.

## GitHub Pages publishing

The source lives on the `site` branch. A push to that branch runs
`.github/workflows/pages.yml`, builds an HTML-only artifact in `_site/`, and deploys
it with GitHub Pages. The `main` branch is intentionally empty so the default
repository view exposes neither the source tree nor this guide.

After creating the GitHub repository, open **Settings → Pages** and set the build
source to **GitHub Actions**. The workflow publishes only the generated HTML,
styles, JavaScript, fonts, images, `.nojekyll`, and `robots.txt`; source TOML,
templates, Python scripts, tests, and this documentation are not part of the
public Pages artifact.

Every generated HTML page includes a `noindex` robots directive. `robots.txt`
also opts out of known AI training and user-agent crawlers while allowing search
crawlers to fetch the HTML and observe `noindex`. These are voluntary crawler
directives, not access control: a public static site can still be downloaded by
a crawler that ignores them.

## Site-wide editing

- Edit the home intro and structural HTML in `templates/index.html`.
- Edit project-page structure in `templates/project.html`.
- Edit layout, themes, and section templates in `styles.css`.
- Edit lightbox and annotation behavior in `script.js`.
- Edit only TOML when adding or changing project content.

## Compact project styling

Sections use 38px of spacing by default (32px on mobile), with 22px for related compact blocks. Transparent CAD images sit directly on the page. Soft/dark section surfaces and generous spacing remain opt-in; the layout lab labels those optional examples.

A collage uses natural-height masonry columns. Set `columns = 2`, `3`, or `4` to choose the desktop count; mobile uses two. Images and captions stay together, and reading/tab order runs down each column. PNG and GIF dimensions are inferred during the build to reserve space before loading. Other formats can supply explicit `width` and `height`.

For a smaller supporting annotated view, use `width = "reading"` and `spacing = "compact"`. An untitled view immediately after another detail view reads as its continuation. The annotation coordinates still refer to the complete source image.
