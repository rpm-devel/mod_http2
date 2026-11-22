# Apache package names and module paths differ between SUSE and RHEL/Fedora.
%if 0%{?suse_version}
%global httpd_devel_pkg apache2-devel
%global httpd_pkg apache2
%global openssl_devel_pkg libopenssl-devel
%if 0%{?suse_version} >= 1600
%global httpd_apxs %{_bindir}/apxs
%else
%global httpd_apxs %{_sbindir}/apxs2
%endif
%global httpd_moddir %{_libdir}/apache2
%global httpd_modconfdir %{_sysconfdir}/apache2/conf.d
%else
%global httpd_devel_pkg httpd-devel
%global httpd_pkg httpd
%global openssl_devel_pkg openssl-devel
%{!?_httpd_apxs: %global _httpd_apxs %{_sbindir}/apxs}
%global httpd_apxs %{_httpd_apxs}
%{!?_httpd_moddir: %global _httpd_moddir %{_libdir}/httpd/modules}
%{!?_httpd_modconfdir: %global _httpd_modconfdir %{_sysconfdir}/httpd/conf.d}
%global httpd_moddir %{_httpd_moddir}
%global httpd_modconfdir %{_httpd_modconfdir}
%{!?_httpd_mmn: %global _httpd_mmn %(cat %{_includedir}/httpd/.mmn 2>/dev/null || echo 0-0)}
%endif

Name:		mod_http2
Version:	2.0.42
Release:	5%{?dist}
Summary:	module implementing HTTP/2 for Apache 2
License:	Apache-2.0
URL:		https://icing.github.io/mod_h2/
ExclusiveArch:	x86_64 aarch64
Source0:	https://github.com/icing/mod_h2/releases/download/v%{version}/mod_http2-%{version}.tar.gz
# >= 2.4.48 is a real upstream requirement (not just this org's minimum) --
# this module's h2_c1.c/h2_c1_io.c #include <http_ssl.h>, a header Apache
# httpd only started shipping in httpd-devel at 2.4.48. RHEL/AlmaLinux 8's
# httpd-devel (2.4.37) predates that; EL7/8 are rejected explicitly instead of
# reaching a fatal compile error.
%if 0%{?rhel} && 0%{?rhel} <= 8
%{error:mod_http2 2.0.42 requires Apache httpd >= 2.4.48; EL7/8 ship older versions}
%endif
BuildRequires:	gcc, make, pkgconfig, %{httpd_devel_pkg} >= 2.4.48, libnghttp2-devel >= 1.7.0, %{openssl_devel_pkg}
Requires:       %{httpd_pkg} >= 2.4.48
%if !0%{?suse_version}
Requires:       httpd-mmn = %{_httpd_mmn}
%endif
Requires:       libnghttp2 >= 1.21.1

%description
The mod_h2 Apache httpd module implements the HTTP2 protocol (h2+h2c) on
top of libnghttp2 for httpd 2.4 servers.

%prep
%autosetup -p1

%build
%configure --with-apxs=%{httpd_apxs}
%make_build V=1

%install
%make_install
httpd_prefix=$(%{httpd_apxs} -q PREFIX)
rm -rf %{buildroot}${httpd_prefix}/share/doc/%{name}

# NOTE: upstream's own libtool install already places mod_http2.so and
# mod_proxy_http2.so directly under %{httpd_moddir} with no .N.N.N
# soname suffix (unlike a standard versioned shared library) -- an
# earlier revision of this spec assumed a rm+mv rename step here, which
# broke %%install once upstream stopped emitting the .0.0.0 suffix.

# create configuration
mkdir -p %{buildroot}%{httpd_modconfdir}
echo "LoadModule http2_module %{httpd_moddir}/mod_http2.so" > %{buildroot}%{httpd_modconfdir}/10-h2.conf
echo "LoadModule proxy_http2_module %{httpd_moddir}/mod_proxy_http2.so" > %{buildroot}%{httpd_modconfdir}/10-proxy_h2.conf

%check
make check

%files
%doc README README.md ChangeLog AUTHORS
%license LICENSE
%config(noreplace) %{httpd_modconfdir}/10-h2.conf
%config(noreplace) %{httpd_modconfdir}/10-proxy_h2.conf
%{httpd_moddir}/mod_http2.so
%{httpd_moddir}/mod_proxy_http2.so

%changelog
* Thu Oct 01 2026 CasjaysDev <rpm-devel@casjaysdev.pro> - 2.0.42-5
- Make the Apache 2.4.48 minimum explicit for unsupported EL7/8 targets

* Tue Sep 29 2026 CasjaysDev <rpm-devel@casjaysdev.pro> - 2.0.42-4
- Remove upstream documentation from the Apache prefix after install

* Tue Sep 29 2026 CasjaysDev <rpm-devel@casjaysdev.pro> - 2.0.42-3
- Use distro Apache apxs paths for Leap 16, Tumbleweed, and EL10

* Mon Sep 28 2026 CasjaysDev <rpm-devel@casjaysdev.pro> - 2.0.42-2
- Complete SUSE Apache package, apxs, module path, config path, and runtime
  dependency handling; keep the RHEL/Fedora module magic number dependency
- Configure with the distro-specific apxs and use absolute module paths

* Sun Jul 05 2026 CasjaysDev <rpm-devel@casjaysdev.pro> - 2.0.42-1
- Multi-distro pass: guard httpd-devel/apache2-devel and httpd/apache2
  (BuildRequires, Conflicts) behind 0%%{?suse_version} for openSUSE/SLES;
  RHEL/CentOS 7+, Alma/Rocky/Oracle 8+, Fedora 40+ keep httpd-devel/httpd
- ExclusiveArch already present, no noarch/BuildArch lines found; verified
  libnghttp2-devel is the correct package name on both Fedora and openSUSE
  (no divergence, left unguarded)
- NOTE: %%install/%%files still rely on %%{httpd_moddir}/%%{httpd_modconfdir}/
  %%{_httpd_mmn} macros, which only httpd-devel's macros.httpd provides;
  openSUSE's apache2-devel uses a different macro namespace (%%apache_*), so
  this package still will not fully build on SUSE without a macro rewrite
  beyond this pass's scope
- Update to 2.0.42 (Source0 verified 302→200)
- Remove stale commented-out OpenSSL path hacks from %%build

* Fri Jul 03 2026 CasjaysDev <rpm-devel@casjaysdev.pro> - 2.0.39-1
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
