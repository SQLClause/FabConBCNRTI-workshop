# Claude Slides deck

A single-deck version of all seven module decks, built with **Claude Slides** (the Slides
artifact type in Claude) as a test of that toolchain against the Marp/MarpToPptx pipeline in the
parent folder. Content is the same theory material as `../module-0X-slides.md`; the screenshots
are the repo's own `assets/screenshots/` files.

| File | What it is |
|---|---|
| `fabric-iq-workshop.html` | **Source of truth.** Exported from the Claude Slides artifact (https://claude.ai/artifact/4AszjVVdYqRRLLoHiVgnXd). One `<section>` per 1920×1080 slide in the Claude Slides format, `<aside>` = speaker notes, `data-section` = outline sections. Opens in any browser (← / → to page). |
| `build.py` | Regenerates the two files below from the HTML. |
| `../dist/pdf/fabric-iq-workshop.pdf` | Printed from the HTML with headless Chrome. |
| `../dist/pptx/fabric-iq-workshop.pptx` | One full-bleed image per slide + speaker notes. **Not editable** — for an editable PowerPoint, use *Download → PowerPoint* on the artifact page. |

## Rebuild

```bash
pip install python-pptx pymupdf
python3 build.py
```

Requires Google Chrome (set `CHROME=/path/to/chrome` if it isn't in the default macOS location).
