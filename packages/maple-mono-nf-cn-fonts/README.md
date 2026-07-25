# maple-mono-nf-cn-fonts

Fedora RPM packaging for the combined Nerd Fonts + CJK cuts of Maple Mono.

Current packaging target:

- upstream release `v7.9` from `subframe7536/maple-font`
- hinted static TTF builds carrying both the complete Nerd Fonts 3.4.0 icon set
  and Chinese glyph coverage (see `packages/maple-mono-cn-fonts/README.md` for
  what the "CN" label actually covers — it has no Korean hangul)
- eight weights (Thin to ExtraBold) plus italics

Subpackages built from this spec:

| Font family                    | Binary RPM                         | Source asset                    |
| ------------------------------ | ---------------------------------- | ------------------------------- |
| `Maple Mono NF CN`             | `maple-mono-nf-cn-fonts`           | `MapleMono-NF-CN.zip`           |
| `Maple Mono NL NF CN`          | `maple-mono-nl-nf-cn-fonts`        | `MapleMonoNL-NF-CN.zip`         |
| `Maple Mono Normal NF CN`      | `maple-mono-normal-nf-cn-fonts`    | `MapleMonoNormal-NF-CN.zip`     |
| `Maple Mono Normal NL NF CN`   | `maple-mono-normal-nl-nf-cn-fonts` | `MapleMonoNormalNL-NF-CN.zip`   |

This is the largest source package in the repo. Each upstream asset is ~160 MB
and each installed family is ~320 MB (1.25 GB for all four), because both the
icon set and the ideograph set are repeated across all sixteen static styles.
Budget accordingly before enabling it in COPR — see the size table in
`packages/maple-mono-fonts/README.md`.

See `packages/maple-mono-fonts/README.md` for the full 16-family matrix, what
the `NL` / `Normal` / `NF` / `CN` axes mean, and the packaging rationale shared
by all four Maple Mono source packages.
