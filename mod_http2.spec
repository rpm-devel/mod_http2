# SUSE/openSUSE ship the Apache HTTP Server dev package as apache2-devel
# (providing httpd) instead of RHEL/Fedora's httpd-devel (providing httpd).
# NOTE: apache2-devel does not provide the %%{_httpd_moddir}/%%{_httpd_modconfdir}/
# %%{_httpd_mmn} RPM macros used below (those come only from httpd-devel's
# macros.httpd) -- this spec's %%install/%%files still require RHEL/Fedora's
# httpd-devel macro namespace to build; the guard below only fixes package
# naming for BuildRequires/Requires/Conflicts.
%if 0%{?suse_version}
%global httpd_devel_pkg apache2-devel
%global httpd_pkg apache2
%else
%global httpd_devel_pkg httpd-devel
%global httpd_pkg httpd
%endif

# Module Magic Number
%{!?_httpd_mmn: %global _httpd_mmn %(cat %{_includedir}/httpd/.mmn 2>/dev/null || echo 0-0)}

Name:		mod_http2
Version:	2.0.42
Release:	1%{?dist}
Summary:	module implementing HTTP/2 for Apache 2
License:	Apache-2.0
URL:		https://icing.github.io/mod_h2/
ExclusiveArch:	x86_64 aarch64
Source0:	https://github.com/icing/mod_h2/releases/download/v%{version}/mod_http2-%{version}.tar.gz
BuildRequires:	pkgconfig, %{httpd_devel_pkg} >= 2.4.20, libnghttp2-devel >= 1.7.0
Requires:	httpd-mmn = %{_httpd_mmn}, libnghttp2 >= 1.21.1
Conflicts:      %{httpd_pkg} < 2.4.25-8

%description
The mod_h2 Apache httpd module implements the HTTP2 protocol (h2+h2c) on
top of libnghttp2 for httpd 2.4 servers.

%prep
%autosetup -p1

%build
%make_build V=1

%install
%make_install
rm -rf %{buildroot}/etc/httpd/share/doc/

# remove links and rename SO files
rm -r %{buildroot}%{_httpd_moddir}/mod_http2.so
rm -r %{buildroot}%{_httpd_moddir}/mod_proxy_http2.so
mv %{buildroot}%{_httpd_moddir}/mod_http2.so.0.0.0 %{buildroot}%{_httpd_moddir}/mod_http2.so
mv %{buildroot}%{_httpd_moddir}/mod_proxy_http2.so.0.0.0 %{buildroot}%{_httpd_moddir}/mod_proxy_http2.so

# create configuration
mkdir -p %{buildroot}%{_httpd_modconfdir}
echo "LoadModule http2_module modules/mod_http2.so" > %{buildroot}%{_httpd_modconfdir}/10-h2.conf
echo "LoadModule proxy_http2_module modules/mod_proxy_http2.so" > %{buildroot}%{_httpd_modconfdir}/10-proxy_h2.conf

%check
make check

%files
%doc README README.md ChangeLog AUTHORS
%license LICENSE
%config(noreplace) %{_httpd_modconfdir}/10-h2.conf
%config(noreplace) %{_httpd_modconfdir}/10-proxy_h2.conf
%{_httpd_moddir}/mod_http2.so
%{_httpd_moddir}/mod_proxy_http2.so

%changelog
* Sat Jul 05 2026 CasjaysDev <rpm-devel@casjaysdev.pro> - 2.0.42-1
- Multi-distro pass: guard httpd-devel/apache2-devel and httpd/apache2
  (BuildRequires, Conflicts) behind 0%%{?suse_version} for openSUSE/SLES;
  RHEL/CentOS 7+, Alma/Rocky/Oracle 8+, Fedora 40+ keep httpd-devel/httpd
- ExclusiveArch already present, no noarch/BuildArch lines found; verified
  libnghttp2-devel is the correct package name on both Fedora and openSUSE
  (no divergence, left unguarded)
- NOTE: %%install/%%files still rely on %%{_httpd_moddir}/%%{_httpd_modconfdir}/
  %%{_httpd_mmn} macros, which only httpd-devel's macros.httpd provides;
  openSUSE's apache2-devel uses a different macro namespace (%%apache_*), so
  this package still will not fully build on SUSE without a macro rewrite
  beyond this pass's scope
- Update to 2.0.42 (Source0 verified 302→200)
- Remove stale commented-out OpenSSL path hacks from %%build

* Thu Jul 03 2026 CasjaysDev <rpm-devel@casjaysdev.pro> - 2.0.39-1
- SPDX: ASL 2.0 → Apache-2.0; add ExclusiveArch: x86_64 aarch64
- %%autosetup -p1, %%make_build V=1, %%make_install

* Fri Apr 24 2026 CasjaysDev <rpm-devel@casjaysdev.pro> - 2.0.39-1
- Update to 2.0.39
- Modernize spec for EL10

* Fri Oct 20 2017 Joe Orton <jorton@redhat.com> - 1.10.12-1
- update to 1.10.12

* Thu Aug 03 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.10.10-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Mon Jul 31 2017 Joe Orton <jorton@redhat.com> - 1.10.10-1
- update to 1.10.10

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 1.10.7-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Thu Jul  6 2017 Joe Orton <jorton@redhat.com> - 1.10.7-1
- update to 1.10.7

* Mon Jun 12 2017 Joe Orton <jorton@redhat.com> - 1.10.6-1
- update to 1.10.6

* Tue May 16 2017 Joe Orton <jorton@redhat.com> - 1.10.5-1
- update to 1.10.5

* Mon Apr 10 2017 Luboš Uhliarik <luhliari@redhat.com> - 1.10.1-1
- Initial import (#1440780).
