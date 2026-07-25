# maple-mono-cn-fonts

Fedora RPM packaging for the CJK cuts of Maple Mono.

Current packaging target:

- upstream release `v7.9` from `subframe7536/maple-font`
- hinted static TTF builds with Chinese glyph coverage at a 2:1 advance width
  relative to the Latin glyphs
- eight weights (Thin to ExtraBold) plus italics

Subpackages built from this spec:

| Font family               | Binary RPM                      | Source asset                 |
| ------------------------- | ------------------------------- | ---------------------------- |
| `Maple Mono CN`           | `maple-mono-cn-fonts`           | `MapleMono-CN.zip`           |
| `Maple Mono NL CN`        | `maple-mono-nl-cn-fonts`        | `MapleMonoNL-CN.zip`         |
| `Maple Mono Normal CN`    | `maple-mono-normal-cn-fonts`    | `MapleMonoNormal-CN.zip`     |
| `Maple Mono Normal NL CN` | `maple-mono-normal-nl-cn-fonts` | `MapleMonoNormalNL-CN.zip`   |

Measured coverage of `MapleMono-CN-Regular.ttf` (v7.9), which is what the "CN"
label actually means: 22,731 mapped codepoints, of which 20,976 are CJK unified
ideographs (U+4E00-U+9FFF), plus 93 hiragana, 96 katakana, 43 bopomofo, 46 CJK
punctuation and 18 fullwidth forms. There is **no** hangul — neither syllables
nor jamo — and no CJK extension A. Latin advance width is 600 against 1200 for
ideographs, so the 2:1 claim holds. Describe it as a Chinese font, not a CJK
font.

This is one of the two heavy Maple Mono source packages, second only to
`maple-mono-nf-cn-fonts`. Each upstream asset is ~140 MB and each installed
family is ~288 MB (1.13 GB for all four), because the ideograph set is repeated
across all sixteen static styles. Budget accordingly before enabling it in
COPR — see the size table in `packages/maple-mono-fonts/README.md`.

See `packages/maple-mono-fonts/README.md` for the full 16-family matrix, what
the `NL` / `Normal` / `NF` / `CN` axes mean, and the packaging rationale shared
by all four Maple Mono source packages.
