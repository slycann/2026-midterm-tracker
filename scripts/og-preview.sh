#!/bin/zsh
# Rebuild img/og-preview.png, the 1200×630 link-preview image (WhatsApp, iMessage, Slack, X):
# a snapshot of the top of the Today tab (header and Senate map). Run from the project root
# with a local server running: python3 -m http.server 8000
set -e
CHROME="$HOME/Library/Caches/ms-playwright/chromium-1208/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing"
URL="${1:-http://localhost:8000/index.html}"
TMP=$(mktemp -d)
# Render at 2x; headless Chrome leaves the bottom of the window blank, so render tall and keep
# the top 845 CSS px (1690 px at 2x), which ends just below the map.
"$CHROME" --headless --disable-gpu --hide-scrollbars --force-prefers-reduced-motion --force-device-scale-factor=2 \
  --virtual-time-budget=8000 --window-size=1200,1000 --screenshot="$TMP/full.png" "$URL" 2>/dev/null
swiftc -O scripts/crop-top.swift -o "$TMP/crop-top"
"$TMP/crop-top" "$TMP/full.png" "$TMP/crop.png" 1690
sips --resampleHeight 630 "$TMP/crop.png" --out "$TMP/small.png" >/dev/null
sips --padToHeightWidth 630 1200 --padColor F4F5F7 "$TMP/small.png" --out img/og-preview.png >/dev/null 2>&1
rm -rf "$TMP"
sips -g pixelWidth -g pixelHeight img/og-preview.png | tail -2
