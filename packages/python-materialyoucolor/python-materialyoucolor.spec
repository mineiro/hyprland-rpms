%global srcname materialyoucolor
%global python3_sitearch %(%{__python3} -c "import sysconfig; print(sysconfig.get_path('platlib', vars={'base': '/usr', 'platbase': '/usr'}))")

Name:           python-materialyoucolor
Version:        3.0.2
Release:        %autorelease
Summary:        Material You color generation algorithms for Python

License:        MIT
URL:            https://github.com/T-Dynamos/materialyoucolor-python
Source0:        https://files.pythonhosted.org/packages/source/m/%{srcname}/%{srcname}-%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  python3-devel
BuildRequires:  python3-pybind11
BuildRequires:  python3-setuptools

%description
Material You color generation algorithms for Python. The package tracks the
upstream project and builds the bundled pybind11 quantization extension so the
native backend remains available on Fedora.

%package -n python3-materialyoucolor
Summary:        %{summary}
Requires:       python3-pillow

%description -n python3-materialyoucolor
Material You color generation algorithms for Python. This package provides the
`materialyoucolor` module and its optional native quantization backend.

%prep
%autosetup -n %{srcname}-%{version}

%build
%{__python3} setup.py build

%install
PYTHONDONTWRITEBYTECODE=1 %{__python3} setup.py install \
    --skip-build \
    --root %{buildroot} \
    --prefix %{_prefix} \
    --install-lib %{python3_sitearch}

%check
cd /tmp
PYTHONPATH="%{buildroot}%{python3_sitearch}" %{__python3} - <<'PY'
from materialyoucolor.quantize import ImageQuantizeCelebi, QuantizeCelebi
from materialyoucolor.scheme import Scheme

assert callable(QuantizeCelebi)
assert callable(ImageQuantizeCelebi)

scheme = Scheme.light(0xFF4285F4)
assert "primary" in scheme.props
PY

%files -n python3-materialyoucolor
%license LICENSE
%doc README.md
%{python3_sitearch}/materialyoucolor/
%{python3_sitearch}/materialyoucolor-*.egg-info

%changelog
%autochangelog
