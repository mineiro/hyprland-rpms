# Combined Nerd Fonts + CJK cuts of Maple Mono. See maple-mono-fonts.spec for
# the packaging rationale shared by all four Maple Mono source packages:
# upstream publishes one release asset per feature-cut/glyph-set/format
# combination, the four feature cuts are separate font families, and the
# glyph-set axis is split across source packages so these CJK assets do not
# weigh down the small cuts.
#
# Each source asset here is roughly 160 MB and each installed family is roughly
# 340 MB, because both the Nerd Fonts icon set and the CJK coverage are repeated
# across all sixteen static styles.
#
# The four feature cuts packaged here are:
#
#   NF CN            ligatures, cursive italic
#   NL NF CN         no ligatures
#   Normal NF CN     "JetBrains Mono-like" preset; freezes cv01, cv02,
#                    cv33-cv36, cv61, cv62 and ss05-ss08 on for conventional
#                    letterforms
#   Normal NL NF CN  the Normal preset without ligatures
#
# The zip filenames carry no version, so every source uses a "#/" fragment to
# store a versioned local copy; without it a stale download would survive a
# version bump.

Version:        7.9
Release:        %autorelease
URL:            https://github.com/subframe7536/maple-font

Source0:        %{url}/releases/download/v%{version}/MapleMono-NF-CN.zip#/MapleMono-NF-CN-%{version}.zip
Source1:        %{url}/releases/download/v%{version}/MapleMonoNL-NF-CN.zip#/MapleMonoNL-NF-CN-%{version}.zip
Source2:        %{url}/releases/download/v%{version}/MapleMonoNormal-NF-CN.zip#/MapleMonoNormal-NF-CN-%{version}.zip
Source3:        %{url}/releases/download/v%{version}/MapleMonoNormalNL-NF-CN.zip#/MapleMonoNormalNL-NF-CN-%{version}.zip

%global fontorg         io.github.subframe7536
%global fontlicense     OFL-1.1

%global fontfamily0     Maple Mono NF CN
%global fontsummary0    Maple Mono with the complete Nerd Fonts icon set and Chinese glyph coverage
%global fonts0          base/*.ttf
%global fontlicenses0   base/LICENSE.txt
%global fontdocs0       base/config.json
%global fontdescription0 %{expand:
Maple Mono NF CN is the fully loaded build of Maple Mono. It carries both the
complete Nerd Fonts 3.4.0 glyph set (Powerline, Font Awesome, Devicons,
Material Design Icons, Weather Icons and others) and the common Chinese
ideograph set, kana, bopomofo, fullwidth forms and CJK punctuation, with those
glyphs at exactly twice the advance width of the Latin ones. Korean hangul is
not covered.

This is the default cut, with ligatures enabled.}

%global fontfamily1     Maple Mono NL NF CN
%global fontsummary1    Maple Mono NF CN without programming ligatures
%global fonts1          nl/*.ttf
%global fontlicenses1   nl/LICENSE.txt
%global fontdocs1       nl/config.json
%global fontdescription1 %{expand:
Maple Mono NL NF CN is the no-ligature cut of Maple Mono with both the complete
Nerd Fonts 3.4.0 glyph set and Chinese glyph coverage. It keeps the rounded
letterforms and cursive italics of the base family, but drops the programming
ligatures, so sequences such as "=>", "!=" and "->" render as individual
characters.}

%global fontfamily2     Maple Mono Normal NF CN
%global fontsummary2    Maple Mono NF CN with conventional letterforms
%global fonts2          normal/*.ttf
%global fontlicenses2   normal/LICENSE.txt
%global fontdocs2       normal/config.json
%global fontdescription2 %{expand:
Maple Mono Normal NF CN is the conventional-letterform cut of Maple Mono, close
to the look of JetBrains Mono, with both the complete Nerd Fonts 3.4.0 glyph set
and Chinese glyph coverage. Upstream builds it by freezing the character variants
cv01, cv02, cv33-cv36, cv61 and cv62 plus the stylistic sets ss05-ss08 on, which
replaces the distinctive curved and single-storey glyphs of the base family.

Ligatures are enabled in this cut.}

%global fontfamily3     Maple Mono Normal NL NF CN
%global fontsummary3    Maple Mono NF CN with conventional letterforms and without ligatures
%global fonts3          normal-nl/*.ttf
%global fontlicenses3   normal-nl/LICENSE.txt
%global fontdocs3       normal-nl/config.json
%global fontdescription3 %{expand:
Maple Mono Normal NL NF CN combines the two reduced cuts of Maple Mono with both
the complete Nerd Fonts 3.4.0 glyph set and Chinese glyph coverage: the
conventional JetBrains Mono-like letterforms of Maple Mono Normal, and the
dropped programming ligatures of Maple Mono NL.}

BuildRequires:  unzip

%fontpkg -a

%prep
# Every asset is a flat archive carrying its own LICENSE.txt and config.json, so
# each one has to be unpacked into a separate directory.
%setup -q -c -T
unzip -q -d base %{SOURCE0}
unzip -q -d nl %{SOURCE1}
unzip -q -d normal %{SOURCE2}
unzip -q -d normal-nl %{SOURCE3}

%build
%fontbuild -a

%install
%fontinstall -a

%check
%fontcheck -a

%fontfiles -a

%changelog
%autochangelog
