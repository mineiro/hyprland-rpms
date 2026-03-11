%global debug_package %{nil}

Name:           dart-sass
Version:        1.98.0
Release:        %autorelease
Summary:        Sass compiler implemented in Dart

License:        MIT
URL:            https://github.com/sass/dart-sass
Source0:        %{url}/releases/download/%{version}/%{name}-%{version}-linux-x64.tar.gz
Source1:        %{url}/releases/download/%{version}/%{name}-%{version}-linux-arm64.tar.gz

ExclusiveArch:  x86_64 aarch64

Conflicts:      rubygem-sass

%description
The reference Sass compiler implemented in Dart. This package installs the
official standalone Linux distribution and provides the `sass` command.

%prep
rm -rf sass src
%ifarch x86_64
tar -xzf %{SOURCE0} --strip-components=1
%endif
%ifarch aarch64
tar -xzf %{SOURCE1} --strip-components=1
%endif

%build
# Standalone upstream release; nothing to build.

%install
install -d %{buildroot}%{_libexecdir}/%{name}
cp -a sass src %{buildroot}%{_libexecdir}/%{name}/
install -d %{buildroot}%{_bindir}
ln -s ../libexec/%{name}/sass %{buildroot}%{_bindir}/sass

%check
printf '%s\n' '$color: #f00;' '.demo { color: $color; }' > test.scss
version="$("%{buildroot}%{_libexecdir}/%{name}/sass" --version)"
printf '%s\n' "$version" | grep -qx '%{version}'
output="$("%{buildroot}%{_libexecdir}/%{name}/sass" test.scss)"
printf '%s\n' "$output" | grep -q 'color: #f00;'

%files
%license %{_libexecdir}/%{name}/src/LICENSE
%{_bindir}/sass
%{_libexecdir}/%{name}/sass
%exclude %{_libexecdir}/%{name}/src/LICENSE
%{_libexecdir}/%{name}/src/

%changelog
%autochangelog
