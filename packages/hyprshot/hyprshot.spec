Name:           hyprshot
Version:        1.3.0
Release:        %autorelease
Summary:        Utility to easily take screenshots in Hyprland using your mouse
BuildArch:      noarch

License:        GPL-3.0-only
URL:            https://github.com/Gustash/Hyprshot
Source0:        %{url}/archive/%{version}/Hyprshot-%{version}.tar.gz

Requires:       /usr/bin/notify-send
Requires:       grim
Requires:       jq
Requires:       slurp
Requires:       wl-clipboard
Recommends:     hyprpicker

%description
Hyprshot is a utility to easily take screenshots in Hyprland using your mouse.
It supports window, region and output capture, and can save to disk and copy to
the clipboard.

%prep
%autosetup -n Hyprshot-%{version}

%build
# shell script package: nothing to build

%install
install -Dpm0755 hyprshot %{buildroot}%{_bindir}/hyprshot

%check
bash -n hyprshot

%files
%license LICENSE
%doc README.md
%{_bindir}/hyprshot

%changelog
%autochangelog
