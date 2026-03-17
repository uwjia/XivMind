# Electron Resources Directory

This directory contains resources for building the Electron application.

## Required Files

### icon.ico
Windows application icon (multi-size ICO format).

**Required sizes:**
- 16x16
- 32x32
- 48x48
- 64x64
- 128x128
- 256x256

**How to create:**
1. Design a 256x256 PNG icon
2. Use online tools like https://icoconvert.com/ or https://convertio.co/png-ico/
3. Or use ImageMagick: `convert icon.png -define icon:auto-resize=256,128,64,48,32,16 icon.ico`

### icon.png
PNG version of the icon for Linux and macOS (optional for Windows-only build).

## Notes

- Place your icon files in this directory before running `npm run build:electron`
- If no icon is provided, Electron will use a default icon
- The icon should represent the XivMind brand identity
