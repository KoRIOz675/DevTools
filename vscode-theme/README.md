# Neon Drive

> A cyberpunk synthwave VS Code theme. Dark neon city nights and 1980s retro-futurism.

Available in two variants: **Neon Drive Dark** and **Neon Drive Light**.

---

## Preview

### Neon Drive Dark

<picture><img src="../docs/neon-drive-dark.png" alt="neon-drive-dark" height="350"></picture>

Built on a deep `#0A0B1F` base with electric pinks, neon cyans, and gold accents.

### Neon Drive Light

<picture><img src="../docs/neon-drive-light.png" alt="neon-drive-dark" height="350"></picture>

Built on a soft `#FAF7FF` lavender-white base — same synthwave identity, optimized for bright environments.

---

## Semantic Color System

Both themes share the same semantic roles. Only luminance and surfaces differ.

| Role                 | Dark      | Light     |
| -------------------- | --------- | --------- |
| Background           | `#0A0B1F` | `#FAF7FF` |
| Surface              | `#111331` | `#F2ECFF` |
| Foreground           | `#F6F7FF` | `#25213A` |
| Keywords / Tags      | `#FF4FD8` | `#D900A7` |
| Functions / Storage  | `#43C7FF` | `#007FFF` |
| Classes / Types      | `#B347FF` | `#8C35FF` |
| Strings              | `#00F7FF` | `#00B8D9` |
| Numbers / Attributes | `#FFE14A` | `#DDAA00` |
| Comments             | `#7A8BC7` | `#7A7294` |
| Errors               | `#FF2E97` | `#FF2E97` |
| Warnings             | `#FFB347` | `#FF8C42` |

---

## Language Support

Language-specific overrides are included for:

- TypeScript / TSX
- JavaScript / JSX
- Vue
- PHP (including PHPDoc, namespaces, `use` statements)
- Python (including `self` parameter)
- Markdown (headings, links, bold, italic, code blocks)
- JSON (keys vs values distinctly colored)
- CoffeeScript

---

## Installation

### Manual (no marketplace required)

1. Copy the theme folder into your VS Code extensions directory:

```bash
mkdir -p ~/.vscode/extensions/local.neon-drive-theme/themes
cp neon-drive-dark.json ~/.vscode/extensions/local.neon-drive-theme/themes/
cp neon-drive-light.json ~/.vscode/extensions/local.neon-drive-theme/themes/
```

2. Create `~/.vscode/extensions/local.neon-drive-theme/package.json`:

```json
{
  "publisher": "local",
  "name": "neon-drive-theme",
  "displayName": "Neon Drive",
  "description": "Cyberpunk Synthwave theme — dark and light",
  "version": "1.0.0",
  "engines": { "vscode": "^1.70.0" },
  "categories": ["Themes"],
  "contributes": {
    "themes": [
      {
        "label": "Neon Drive Dark",
        "uiTheme": "vs-dark",
        "path": "./themes/neon-drive-dark.json"
      },
      {
        "label": "Neon Drive Light",
        "uiTheme": "vs",
        "path": "./themes/neon-drive-light.json"
      }
    ]
  }
}
```

3. Clear the extensions cache and fully restart VS Code:

```bash
rm -rf ~/.config/Code/CachedExtensions
rm -rf ~/.config/Code/Cache
pkill -f code
code .
```

> **Note:** The extension folder name must match `publisher.name` — `local.neon-drive-theme` in this case. VS Code silently ignores folders that don't follow this convention.

4. Apply the theme via `Ctrl+Shift+P` → **Preferences: Color Theme** → select **Neon Drive Dark** or **Neon Drive Light**.

---

## Design Principles

- **Consistent semantic roles** — each color has exactly one job. No five shades of pink for keywords.
- **High contrast** — all syntax colors meet comfortable contrast ratios for long coding sessions.
- **Reduced noise** — the original 2077 theme had 10+ near-identical pinks. Neon Drive normalizes these into two distinct roles: Primary Pink and Hot Pink.
- **Shared structure** — dark and light variants are generated from the same semantic palette. Switching between them never breaks visual logic.

---

## Base Theme

Derived from and inspired by [2077 theme](https://github.com/endormi/vscode-2077-theme) by endormi.
