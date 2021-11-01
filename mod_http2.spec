# Module Magic Number
%{!?_httpd_mmn: %global _httpd_mmn %(cat %{_includedir}/httpd/.mmn 2>/dev/null || echo 0-0)}

Name:		mod_http2
Version:	1.10.12
Release:	1%{dist}
Summary:	module implementing HTTP/2 for Apache 2
Group:		System Environment/Daemons
License:	ASL 2.0
URL:		https://icing.github.io/mod_h2/
Source0:	https://github.com/icing/mod_h2/releases/download/v%{version}/mod_http2-%{version}.tar.gz
BuildRequires:	pkgconfig, httpd-devel >= 2.4.20, libnghttp2-devel >= 1.7.0
Requires:	httpd-mmn = %{_httpd_mmn}, libnghttp2 >= 1.21.1
Conflicts:      httpd < 2.4.25-8

%description
The mod_h2 Apache httpd module implements the HTTP2 protocol (h2+h2c) on
top of libnghttp2 for httpd 2.4 servers.

%prep
%setup -q

%build
#CFLAGS="$CFLAGS -I/root/openssl-1.1.0g/include" LDFLAGS=-L/root/openssl-1.1.0g \
#CXXFLAGS="$CXXFLAGS -I/root/openssl-1.1.0g/include" LDFLAGS=-L/root/openssl-1.1.0g \
#CPPFLAGS="$CPPFLAGS -I/root/openssl-1.1.0g/include" LDFLAGS=-L/root/openssl-1.1.0g %configure
make %{?_smp_mflags} V=1

%install
make DESTDIR=%{buildroot} install
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
