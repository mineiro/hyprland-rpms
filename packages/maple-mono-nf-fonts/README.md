# maple-mono-nf-fonts

Fedora RPM packaging for the Nerd Fonts patched cuts of Maple Mono.

Current packaging target:

- upstream release `v7.9` from `subframe7536/maple-font`
- hinted static TTF builds with the complete Nerd Fonts 3.4.0 icon set
- eight weights (Thin to ExtraBold) plus italics

Subpackages built from this spec:

| Font family               | Binary RPM                      | Source asset                  |
| ------------------------- | ------------------------------- | ----------------------------- |
| `Maple Mono NF`           | `maple-mono-nf-fonts`           | `MapleMono-NF.zip`            |
| `Maple Mono NL NF`        | `maple-mono-nl-nf-fonts`        | `MapleMonoNL-NF.zip`          |
| `Maple Mono Normal NF`    | `maple-mono-normal-nf-fonts`    | `MapleMonoNormal-NF.zip`      |
| `Maple Mono Normal NL NF` | `maple-mono-normal-nl-nf-fonts` | `MapleMonoNormalNL-NF.zip`    |

Each family is about 36.5 MB installed, so the four together are 145 MB.

See `packages/maple-mono-fonts/README.md` for the full 16-family matrix, what
the `NL` / `Normal` / `NF` / `CN` axes mean, and the packaging rationale shared
by all four Maple Mono source packages.
