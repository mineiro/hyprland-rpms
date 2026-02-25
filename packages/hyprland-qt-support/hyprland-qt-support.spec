Name:           hyprland-qt-support
Version:        0.1.0
Release:        %autorelease
Summary:        Qt6 QML style provider for hypr* apps

License:        BSD-3-Clause
URL:            https://github.com/hyprwm/hyprland-qt-support
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
Patch0:         patches/0001-fix-cmake-project-version-order.patch

ExcludeArch:    %{ix86}

BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  qt6-rpm-macros
BuildRequires:  cmake(Qt6Quick)
BuildRequires:  cmake(Qt6QuickControls2)
BuildRequires:  cmake(Qt6Qml)
BuildRequires:  pkgconfig(hyprlang) >= 0.6.8

%description
%{summary}.

%prep
%autosetup -p1

%build
%cmake \
  -DCMAKE_BUILD_TYPE=Release \
  -DINSTALL_QMLDIR=%{_qt6_qmldir}
%cmake_build

%install
%cmake_install

%check
# Add/enable upstream tests after confirming they are stable in mock/COPR.
:

%files
%license LICENSE
%doc README.md
%{_libdir}/libhyprland-quick-style-impl.so
%{_libdir}/libhyprland-quick-style.so
%{_qt6_qmldir}/org/hyprland/

%changelog
%autochangelog
