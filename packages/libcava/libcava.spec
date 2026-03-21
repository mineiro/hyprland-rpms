%global upstream_commit f4b69943ea7fecbbeec97fac8e73af03b39be499
%global upstream_shortcommit %(c=%{upstream_commit}; echo ${c:0:7})

Name:           libcava
Version:        0.10.7
Release:        %autorelease
Summary:        Shared audio visualization library from CAVA

License:        MIT
URL:            https://github.com/LukashonakV/cava
Source0:        %{url}/archive/%{upstream_commit}/cava-%{upstream_shortcommit}.tar.gz

BuildRequires:  gcc
BuildRequires:  meson
BuildRequires:  iniparser-devel
BuildRequires:  pkgconfig(fftw3)

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description
Shared library from the CAVA audio visualizer project.

%description devel
Development files for %{name}.

%prep
%autosetup -n cava-%{upstream_commit} -p1

%build
%meson \
  -Dbuild_target=lib \
  -Dcava_font=false \
  -Dinput_alsa=disabled \
  -Dinput_portaudio=disabled \
  -Dinput_pulse=disabled \
  -Dinput_sndio=disabled \
  -Dinput_pipewire=disabled \
  -Dinput_oss=disabled \
  -Dinput_jack=disabled \
  -Doutput_sdl=disabled \
  -Doutput_sdl_glsl=disabled \
  -Doutput_ncurses=disabled
# Upstream embeds these assets with relative .incbin paths from config.c.
# Meson compiles from the out-of-tree build dir, so stage matching paths there.
ln -sfn ../example_files %{_vpath_builddir}/example_files
ln -sfn ../output %{_vpath_builddir}/output
%meson_build

%install
%meson_install

%check
:

%files
%license LICENSE
%{_libdir}/libcava.so.0{,.*}

%files devel
%{_includedir}/cava/
%{_libdir}/libcava.so
%{_libdir}/pkgconfig/libcava.pc

%changelog
%autochangelog
