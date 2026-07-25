# maple-mono-fonts

Fedora RPM packaging for Maple Mono. This directory is the reference package of
the four-part Maple Mono set; the other three carry the heavier glyph sets.

Current packaging target:

- upstream release `v7.9` from `subframe7536/maple-font`
- hinted static TTF builds, eight weights (Thin to ExtraBold) plus italics

## Full package matrix

Upstream has two independent axes. The **feature cut** axis changes the
letterforms and is a distinct font family upstream, so each cut is its own RPM.
The **glyph set** axis changes coverage and drives download size, so it is split
across four source packages instead:

Installed sizes below are measured from the Fedora 44 x86_64 build of `v7.9`.

| Source package           | Feature cut | Font family                  | Binary RPM                         | Installed |
| ------------------------ | ----------- | ---------------------------- | ---------------------------------- | --------: |
| `maple-mono-fonts`       | base        | `Maple Mono`                 | `maple-mono-fonts`                 |    4.3 MB |
| `maple-mono-fonts`       | NL          | `Maple Mono NL`              | `maple-mono-nl-fonts`              |    3.9 MB |
| `maple-mono-fonts`       | Normal      | `Maple Mono Normal`          | `maple-mono-normal-fonts`          |    4.2 MB |
| `maple-mono-fonts`       | Normal NL   | `Maple Mono Normal NL`       | `maple-mono-normal-nl-fonts`       |    3.8 MB |
| `maple-mono-nf-fonts`    | base        | `Maple Mono NF`              | `maple-mono-nf-fonts`              |   36.6 MB |
| `maple-mono-nf-fonts`    | NL          | `Maple Mono NL NF`           | `maple-mono-nl-nf-fonts`           |   36.2 MB |
| `maple-mono-nf-fonts`    | Normal      | `Maple Mono Normal NF`       | `maple-mono-normal-nf-fonts`       |   36.5 MB |
| `maple-mono-nf-fonts`    | Normal NL   | `Maple Mono Normal NL NF`    | `maple-mono-normal-nl-nf-fonts`    |   36.1 MB |
| `maple-mono-cn-fonts`    | base        | `Maple Mono CN`              | `maple-mono-cn-fonts`              |  288.4 MB |
| `maple-mono-cn-fonts`    | NL          | `Maple Mono NL CN`           | `maple-mono-nl-cn-fonts`           |  288.0 MB |
| `maple-mono-cn-fonts`    | Normal      | `Maple Mono Normal CN`       | `maple-mono-normal-cn-fonts`       |  288.3 MB |
| `maple-mono-cn-fonts`    | Normal NL   | `Maple Mono Normal NL CN`    | `maple-mono-normal-nl-cn-fonts`    |  287.9 MB |
| `maple-mono-nf-cn-fonts` | base        | `Maple Mono NF CN`           | `maple-mono-nf-cn-fonts`           |  319.8 MB |
| `maple-mono-nf-cn-fonts` | NL          | `Maple Mono NL NF CN`        | `maple-mono-nl-nf-cn-fonts`        |  319.4 MB |
| `maple-mono-nf-cn-fonts` | Normal      | `Maple Mono Normal NF CN`    | `maple-mono-normal-nf-cn-fonts`    |  319.7 MB |
| `maple-mono-nf-cn-fonts` | Normal NL   | `Maple Mono Normal NL NF CN` | `maple-mono-normal-nl-nf-cn-fonts` |  319.3 MB |

Installing everything comes to ~2.6 GB, of which ~2.4 GB is the two CJK
packages.

What the axes mean:

- **NL** drops the programming ligatures.
- **Normal** is upstream's "JetBrains Mono-like" preset. It freezes the
  character variants `cv01`, `cv02`, `cv33`-`cv36`, `cv61`, `cv62` and the
  stylistic sets `ss05`-`ss08` on, replacing the distinctive curved and
  single-storey glyphs with conventional ones.
- **NF** patches in the complete Nerd Fonts 3.4.0 icon set.
- **CN** adds Chinese coverage — ~21k CJK unified ideographs plus kana,
  bopomofo, fullwidth forms and CJK punctuation — at twice the Latin advance
  width. Despite the "CJK" shorthand, it carries no Korean hangul; see
  `packages/maple-mono-cn-fonts/README.md` for the measured coverage.

This matches the coverage of ArchLinuxCN and is a superset of what Homebrew
(8 casks), Scoop (5) and the AUR (3) ship.

## Packaging notes

- upstream publishes one zip asset per feature-cut/glyph-set/format combination
  (44 assets per release) rather than a source tarball, so each spec points
  `Source0`-`Source3` straight at release assets and `%prep` unpacks each into
  its own directory; every asset is a flat archive with a top-level
  `LICENSE.txt` and `config.json` that would otherwise collide
- the assets have no version in their filenames, so every source uses the `#/`
  fragment to store a versioned local copy; without it a stale download would
  survive a version bump
- static TTF is packaged rather than the variable, OTF or woff2 builds. Those
  are alternate encodings of the *same* font families, so shipping more than one
  would put duplicate families in fontconfig. The Nerd Fonts cuts are
  static-only upstream anyway.
- the glyph-set axis is split across four source packages rather than becoming
  16 subpackages of one spec, because the CJK assets are 140-160 MB each; a
  single spec would drag ~1.3 GB of sources into every rebuild of the 4 MB cuts
- `%fontpkgname2` is set explicitly in this spec. The fonts macros derive RPM
  names using the "WPF font selection model" simplifications, which strip a
  trailing `normal` — without the override, `Maple Mono Normal` would collapse
  onto `maple-mono-fonts` and collide with the base family. The other `Normal`
  cuts are safe because `normal` is not the trailing token there.
- `config.json` is shipped as documentation because it records the exact
  upstream build configuration, including the Nerd Fonts version, the CJK
  scaling factors and the feature-freeze state of every stylistic variant
