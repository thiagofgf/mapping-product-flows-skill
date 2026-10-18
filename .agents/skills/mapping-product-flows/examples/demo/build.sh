#!/usr/bin/env bash
# Regenerate the demo: screenshots, boards, PNGs, overview and catalog.
# Needs FLOWMAP_PKG (a package.json whose project has playwright) and npx access to mcp-excalidraw-server.
set -euo pipefail
cd "$(dirname "$0")"
T=../../tools
node capture.mjs
for b in 01-access 02-tasks; do python3 $T/build_board.py "specs/$b.json" "output/$b.excalidraw"; done
python3 $T/build_index.py specs/index.json output/00-overview.excalidraw
python3 $T/gen_md.py specs/index.json specs/catalog-header.md output/use-case-catalog.md
for f in output/*.excalidraw; do npx -y mcp-excalidraw-server@2.1.2 render "$f" --out "${f%.excalidraw}.png"; done
