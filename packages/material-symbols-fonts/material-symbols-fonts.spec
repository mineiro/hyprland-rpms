# Build from the actively updated upstream "master" branch. The upstream
# "main" branch and the old 4.0.0 tag track the deprecated Material Icons set,
# while Material Symbols is the current Google-maintained icon font family.
%global commit0        f2749daed485839fb131415339546549d302bebc
%global snapshot_date  20260327

Version:        0^git%{snapshot_date}
Release:        %autorelease
URL:            https://github.com/google/material-design-icons

%global fontlicense     Apache-2.0
%global fontlicenses    LICENSE
%global fontdocs        README.md variablefont/*.codepoints
%global fontfamily      Material Symbols
%global fontsummary     Google Material Symbols variable icon fonts
%global fonts           variablefont/*.ttf
%global fontorg         com.google

%global fontdescription %{expand:
Material Symbols is the current official Google Material icon set. This
package ships the self-hostable variable TTF fonts for the Outlined, Rounded,
and Sharp families.}

# prepare-sources.sh repacks the active Material Symbols assets into a small
# source tarball so builds do not need the full upstream web asset tree.
Source0:        %{name}-%{snapshot_date}.tar.xz

%fontpkg

%prep
%autosetup -n %{name}-%{snapshot_date}

%build
%fontbuild

%install
%fontinstall
metainfo=%{buildroot}%{_metainfodir}/%{fontorg}.%{name}.metainfo.xml

# The Fedora font macros generate invalid metainfo; see bz 1943727.
sed -e 's,updatecontact,update_contact,g' \
    -e 's,<!\[CDATA\[\(.*\)\]\]>,\1,' \
    -e 's,<font></font>,<font>Material Symbols Outlined</font>\n    <font>Material Symbols Rounded</font>\n    <font>Material Symbols Sharp</font>,' \
    -i "${metainfo}"

%check
%fontcheck

%fontfiles

%changelog
%autochangelog
