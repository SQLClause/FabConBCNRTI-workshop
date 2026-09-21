# Slides

PowerPoint decks for presenting each module's theory portion, built from Marp-flavored markdown
sources onto this conference's own branded template (`template/*.pptx`) using
[MarpToPptx](https://github.com/jongalloway/MarpToPptx). Unlike stock Marp CLI (which rasterizes
slides as images), MarpToPptx produces a real, editable `.pptx` — every heading, bullet, table, and
code block is a native, selectable PowerPoint shape, styled using the template's own masters and
layouts.

The markdown (`module-XX-slides.md`) stays the source of truth and the file you edit; the `.pptx`
files under `dist/pptx/` are generated output, rebuilt with `./build-slides.sh`.

## Prerequisites (presenter/build-time only, not needed by attendees)

- [.NET 10 SDK](https://dotnet.microsoft.com/download)
- MarpToPptx as a global tool:
  ```bash
  dotnet tool install --global MarpToPptx
  ```
  (`build-slides.sh` falls back to `dnx MarpToPptx`, a no-install run, if `marp2pptx` isn't found on
  PATH — slower per run since it resolves the package fresh each time, but works without the
  `dotnet tool install` step.)

## Build

```bash
cd slides
./build-slides.sh
```

Rebuilds all seven decks into `dist/pptx/module-00.pptx` … `module-06.pptx`.

## Template

`template/EMFCC26_SpeakerPPT_TemplateA_Styled_Accessibility Review_Updated_11Aug.pptx` is the
conference's official speaker template — it supplies every deck's fonts, colors, backgrounds, and
slide layouts. `marp-theme.css` is passed alongside it (`--theme-css`) to style anything the template
doesn't own outright (code blocks, and any layout with no declared placeholders); wherever a slide
uses a template layout with real title/body placeholders, the template's own styling wins.

## Layout cheat-sheet

The template ships 12 slide layouts; only four are used in these decks (the rest were evaluated and
found either redundant or not useful for markdown-driven content — see "Layouts we deliberately don't
use" below). Set the deck-wide default in front matter, override per slide with an HTML comment:

```markdown
---
marp: true
layout: Main Content : Title + Text Box
---

<!-- _layout: Section Break Slide -->
## A one-slide-only override

<!-- layout: Main Content : Title + Visual Data -->
## This override "sticks" until changed again (no leading underscore)
```

| When to use | Layout name | Notes |
|---|---|---|
| The deck's opening title slide — **only the first slide of each deck** | `Template[3]` | Clones the template's own authored branded title slide (background art + the "PRESENTATION TITLE GOES HERE" treatment) rather than a reusable layout — that fancy treatment is authored directly on the template's slide 3, not exposed as a normal layout. See "After generating" below for the one manual step this requires. |
| Every ordinary bulleted content slide | `Main Content : Title + Text Box` | The deck-wide default — has real `title` and `body` placeholders, so text is fully template-styled. |
| Section dividers / "Hands-on lab" transition slides | `Section Break Slide` | Matches the template's own example usage (its authored "Section title" slide uses this layout). Only exposes one placeholder, so keep these slides short — one heading, minimal body text. |
| A slide built around a code-fence diagram, ASCII sketch, or data table | `Main Content : Title + Visual Data` | Code blocks and tables render as standalone native shapes on **any** layout (this is a MarpToPptx feature, not specific to this layout) — using this layout instead of the default just gives the slide the template's "visual data" background/framing to signal "look at this," not different code-block placement. |

### Layouts we deliberately don't use

- **`Dark Content (White Background)`** and the two `Main Content - Dark BKG : ...` variants — these
  layouts have **no declared title/body placeholders** in the template, so MarpToPptx falls back to
  freeform text boxes with no inherited template font styling on them (confirmed by test render).
  Usable in principle with careful `--theme-css` tuning, but skipped here to keep the pipeline simple
  and reliable — revisit if a future deck wants a "big reveal" emphasis slide.
- **`Main Content : Title + Dual Text Box`** (and the other multi-box "Dual"/"Visual Data + Text"
  variants) — confirmed by test render that MarpToPptx does **not** split a slide's markdown content
  across a layout's two body placeholders; everything still lands in a single placeholder, so these
  layouts provide no actual two-column benefit over the plain default layout. The `<div class="columns">`
  two-column markup already present in some slides (Module 02, 04, 05 comparison slides) still works
  fine — it just renders as one flowing list rather than two visual columns, with no content lost.
- **`Splash Screen`** — has zero placeholders at all; not usable for markdown-driven content.
- **`1_Main Content : Title + Text Box`** — an alternate-styled duplicate of the default content
  layout; left unused, no specific reason found to prefer it.

## After generating: manual title-slide step

MarpToPptx can only populate real PowerPoint **placeholders** (title/body) from markdown. The
template's fancy title-slide treatment (cloned via `Template[3]`) also carries a couple of plain,
non-placeholder text boxes meant for "YOUR NAME" / "TITLE, COMPANY NAME, COUNTRY" — since these
aren't placeholders, markdown can't fill them, so MarpToPptx leaves them blank rather than showing
stale boilerplate text. **After running `./build-slides.sh`, open each of the 7 generated decks once
and, on the title slide only, either fill in the presenter's name/title/company in those empty boxes
or delete them.** This is a one-time step per deck, not something the build script can automate (the
boxes only exist once the real template's slide is cloned into your output file).

## If you edit the template

The layout cheat-sheet above was derived empirically (there's no way to statically prove which
layouts render distinctly — see `docs/facilitator-guide.md`'s "Slides" section). If the template file
is replaced or the conference issues an updated version, re-verify layout names and behavior before
trusting this table — layout names must match **exactly** (case-insensitive, but spacing/punctuation
must be identical) or MarpToPptx silently falls back to the deck-wide default layout.

## Claude Slides variant

`claude-slides/` holds a single-deck version of the same content built with Claude Slides instead
of Marp — see [`claude-slides/README.md`](claude-slides/README.md). Its outputs live alongside the
Marp decks as `dist/pdf/fabric-iq-workshop.pdf` and `dist/pptx/fabric-iq-workshop.pptx`.
