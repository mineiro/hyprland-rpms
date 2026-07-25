# Maple Mono is published as one release asset per feature-cut/glyph-set/format
# combination rather than as a source tarball. Upstream's four feature cuts are
# separate font families, so each one becomes its own subpackage:
#
#   (base)      ligatures, cursive italic
#   NL          no ligatures
#   Normal      "JetBrains Mono-like" preset; freezes cv01, cv02, cv33-cv36,
#               cv61, cv62 and ss05-ss08 on for conventional letterforms
#   Normal NL   the Normal preset without ligatures
#
# The glyph-set axis is split across separate source packages instead of more
# subpackages here, because the CJK assets are 140 MB or more each and would
# otherwise make every rebuild of the small cuts drag a gigabyte of sources:
#
#   maple-mono-fonts        this package, base glyph set
#   maple-mono-nf-fonts     Nerd Fonts icon glyphs
#   maple-mono-cn-fonts     CJK glyph coverage
#   maple-mono-nf-cn-fonts  Nerd Fonts icon glyphs and CJK glyph coverage
#
# The hinted static TTF assets are packaged rather than the variable, OTF or
# woff2 ones: those are alternate encodings of the same font families and would
# collide in fontconfig, and the Nerd Fonts cuts are static-only upstream.
#
# The zip filenames carry no version, so every source uses a "#/" fragment to
# store a versioned local copy; without it a stale download would survive a
# version bump.

Version:        7.9
Release:        %autorelease
URL:            https://github.com/subframe7536/maple-font

Source0:        %{url}/releases/download/v%{version}/MapleMono-TTF.zip#/MapleMono-TTF-%{version}.zip
Source1:        %{url}/releases/download/v%{version}/MapleMonoNL-TTF.zip#/MapleMonoNL-TTF-%{version}.zip
Source2:        %{url}/releases/download/v%{version}/MapleMonoNormal-TTF.zip#/MapleMonoNormal-TTF-%{version}.zip
Source3:        %{url}/releases/download/v%{version}/MapleMonoNormalNL-TTF.zip#/MapleMonoNormalNL-TTF-%{version}.zip

%global fontorg         io.github.subframe7536
%global fontlicense     OFL-1.1

%global fontfamily0     Maple Mono
%global fontsummary0    Open source monospace font with ligatures and rounded letterforms
%global fonts0          base/*.ttf
%global fontlicenses0   base/LICENSE.txt
%global fontdocs0       base/config.json
%global fontdescription0 %{expand:
Maple Mono is an open source monospace font aimed at code readability. It
combines rounded letterforms, a cursive italic cut, programming ligatures, and a
large set of opt-in stylistic and character variants (ss01-ss11, cv01-cv99) that
let you reshape individual glyphs.

This is the default cut, with ligatures enabled.}

%global fontfamily1     Maple Mono NL
%global fontsummary1    Maple Mono without programming ligatures
%global fonts1          nl/*.ttf
%global fontlicenses1   nl/LICENSE.txt
%global fontdocs1       nl/config.json
%global fontdescription1 %{expand:
Maple Mono NL is the no-ligature cut of Maple Mono. It keeps the rounded
letterforms, cursive italics and stylistic variants of the base family, but
drops the programming ligatures, so sequences such as "=>", "!=" and "->" render
as individual characters.}

# The fonts macros derive package names with the "WPF font selection model"
# simplifications, which strip a trailing "normal" - that would map this family
# onto maple-mono-fonts and collide with the base family above.
%global fontpkgname2    maple-mono-normal-fonts
%global fontfamily2     Maple Mono Normal
%global fontsummary2    Maple Mono with conventional letterforms
%global fonts2          normal/*.ttf
%global fontlicenses2   normal/LICENSE.txt
%global fontdocs2       normal/config.json
%global fontdescription2 %{expand:
Maple Mono Normal is the conventional-letterform cut of Maple Mono, close to the
look of JetBrains Mono. Upstream builds it by freezing the character variants
cv01, cv02, cv33-cv36, cv61 and cv62 plus the stylistic sets ss05-ss08 on, which
replaces the distinctive curved and single-storey glyphs of the base family.

Ligatures are enabled in this cut.}

%global fontfamily3     Maple Mono Normal NL
%global fontsummary3    Maple Mono with conventional letterforms and without ligatures
%global fonts3          normal-nl/*.ttf
%global fontlicenses3   normal-nl/LICENSE.txt
%global fontdocs3       normal-nl/config.json
%global fontdescription3 %{expand:
Maple Mono Normal NL combines the two reduced cuts of Maple Mono: the
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
