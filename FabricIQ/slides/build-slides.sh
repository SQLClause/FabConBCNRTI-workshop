#!/usr/bin/env bash
#
# build-slides.sh
#
# Renders every slides/module-*.md (Marp-flavored markdown) into a native,
# editable PowerPoint deck under slides/dist/pptx/, using the conference's
# own branded template (slides/template/*.pptx) for masters, layouts, and
# theming via MarpToPptx (https://github.com/jongalloway/MarpToPptx).
#
# PRESENTER NOTE: this script requires .NET 10 SDK and the MarpToPptx global
# tool:
#   dotnet tool install --global MarpToPptx
# This is a *build-time* dependency for whoever is generating/updating the
# .pptx decks before the event — attendees do not need .NET for anything in
# this workshop.
#
# Usage:
#   ./build-slides.sh
#
# Output:
#   slides/dist/pptx/module-00.pptx ... module-06.pptx
#
# See slides/README.md for the layout cheat-sheet and the required manual
# post-generation step (filling in the presenter's name/title/company on
# each deck's title slide).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SLIDES_DIR="$SCRIPT_DIR"
THEME_FILE="$SLIDES_DIR/marp-theme.css"
OUT_DIR="$SLIDES_DIR/dist/pptx"
TEMPLATE_FILE="$SLIDES_DIR/template/EMFCC26_SpeakerPPT_TemplateA_Styled_Accessibility Review_Updated_11Aug.pptx"

# --- Preflight: marp2pptx available? --------------------------------------

if command -v marp2pptx >/dev/null 2>&1; then
  MARP2PPTX=(marp2pptx)
elif command -v dotnet >/dev/null 2>&1; then
  echo "NOTE: 'marp2pptx' not found on PATH; falling back to 'dnx MarpToPptx'" >&2
  echo "      (no permanent install, resolved fresh from NuGet each run)." >&2
  MARP2PPTX=(dnx MarpToPptx)
else
  echo "ERROR: neither 'marp2pptx' nor 'dotnet' was found on PATH." >&2
  echo "" >&2
  echo "This script generates PowerPoint decks from the Marp markdown sources" >&2
  echo "using MarpToPptx, a .NET tool that renders real, editable PowerPoint" >&2
  echo "shapes onto this conference's branded template." >&2
  echo "" >&2
  echo "Install .NET 10 SDK from https://dotnet.microsoft.com/download, then run:" >&2
  echo "  dotnet tool install --global MarpToPptx" >&2
  echo "and re-run this script. This is a build-time-only dependency for the" >&2
  echo "presenter — workshop attendees do not need .NET for anything else here." >&2
  exit 1
fi

if [ ! -f "$TEMPLATE_FILE" ]; then
  echo "ERROR: template file not found at:" >&2
  echo "  $TEMPLATE_FILE" >&2
  echo "Expected the conference PowerPoint template under slides/template/." >&2
  exit 1
fi

if [ ! -f "$THEME_FILE" ]; then
  echo "ERROR: theme file not found at $THEME_FILE" >&2
  exit 1
fi

mkdir -p "$OUT_DIR"

# --- Build ------------------------------------------------------------

shopt -s nullglob
DECKS=("$SLIDES_DIR"/module-*.md)
shopt -u nullglob

if [ ${#DECKS[@]} -eq 0 ]; then
  echo "ERROR: no slides/module-*.md files found in $SLIDES_DIR" >&2
  exit 1
fi

echo "Found ${#DECKS[@]} deck(s) to build."
echo "Template: $TEMPLATE_FILE"
echo "Output directory: $OUT_DIR"
echo ""

FAILED=0

for deck in "${DECKS[@]}"; do
  base="$(basename "$deck" .md)"          # e.g. module-00-slides
  name="${base%-slides}"                  # e.g. module-00
  out_file="$OUT_DIR/${name}.pptx"

  echo "==> Building ${name}.pptx from $(basename "$deck")"

  if "${MARP2PPTX[@]}" "$deck" \
      --template "$TEMPLATE_FILE" \
      --theme-css "$THEME_FILE" \
      -o "$out_file"; then
    echo "    OK -> $out_file"
  else
    echo "    FAILED: $(basename "$deck")" >&2
    FAILED=1
  fi
  echo ""
done

if [ "$FAILED" -ne 0 ]; then
  echo "One or more decks failed to build. See errors above." >&2
  exit 1
fi

echo "All decks built successfully in $OUT_DIR"
echo ""
echo "REMINDER: each deck's title slide needs a one-time manual fill-in of the"
echo "presenter's name/title/company in PowerPoint -- MarpToPptx clears those"
echo "template text boxes but can't populate them from markdown. See"
echo "slides/README.md, 'After generating: manual title-slide step'."
