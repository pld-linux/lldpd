## TODO:
# - separate package with client and daemon (possible?)
#
# Conditional build:
%bcond_without	snmp		# SNMP subagent (net-snmp)
%bcond_with	seccomp		# seccomp syscall filter (experimental upstream)
%bcond_without	static_libs	# static library
%bcond_without	tests		# unit tests

Summary:	Implementation of IEEE 802.1AB, EDP and CDP
Summary(pl.UTF-8):	Implementacja IEEE 802.1AB, EDP oraz CDP
Name:		lldpd
Version:	1.0.22
Release:	1
License:	ISC
Group:		Networking
Source0:	https://media.luffy.cx/files/lldpd/%{name}-%{version}.tar.gz
# Source0-md5:	7dc5ed313e931f4bfd0ddd1dcf504303
Source1:	%{name}.init
Source2:	%{name}.sysconfig
URL:		https://lldpd.github.io/
%{?with_tests:BuildRequires:	check-devel >= 0.9.4}
BuildRequires:	libbsd-devel
BuildRequires:	libcap-devel >= 2
BuildRequires:	libevent-devel >= 2.0.5
%{?with_seccomp:BuildRequires:	libseccomp-devel >= 1}
BuildRequires:	libxml2-devel
%{?with_snmp:BuildRequires:	net-snmp-devel}
BuildRequires:	pkgconfig
BuildRequires:	readline-devel
BuildRequires:	rpmbuild(macros) >= 1.671
Requires(post,preun):	/sbin/chkconfig
Requires(post,preun,postun):	systemd-units >= 38
Requires:	%{name}-libs = %{version}-%{release}
Requires:	rc-scripts
Requires:	systemd-units >= 38
Conflicts:	openlldp
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
LLDP (Link Layer Discovery Protocol) (also known as 802.1ab) is an
industry standard protocol designed to supplant proprietary Link-Layer
protocols such as Extreme's EDP (Extreme Discovery Protocol) and CDP
(Cisco Discovery Protocol). The goal of LLDP is to provide an
inter-vendor compatible mechanism to deliver Link-Layer notifications
to adjacent network devices.

lldpd is a lldp daemon for GNU/Linux and implements both reception and
sending. It supports both LLDP and LLDP-MED (contributed by Michael
Hanig). It also implements an SNMP subagent for net-snmp to get local
and remote LLDP information. The LLDP MIB is partially implemented but
the most useful tables are here.

lldpd supports bridge, vlan and bonding. bonding need to be done on
real physical devices, not on bridges, vlans, etc. However, vlans can
be mapped on the bonding device. You can bridge vlan but not add vlans
on bridges. More complex setups may give false results.

%package libs
Summary:	lldpctl library to interface with lldpd
Summary(pl.UTF-8):	Biblioteka lldpctl do komunikacji z lldpd
Group:		Libraries

%description libs
lldpctl library to query and configure lldpd.

%description libs -l pl.UTF-8
Biblioteka lldpctl do odpytywania i konfigurowania lldpd.

%package devel
Summary:	Header files for lldpctl library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki lldpctl
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}

%description devel
Header files for lldpctl library.

%description devel -l pl.UTF-8
Pliki nagłówkowe biblioteki lldpctl.

%package static
Summary:	Static lldpctl library
Summary(pl.UTF-8):	Statyczna biblioteka lldpctl
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
Static lldpctl library.

%description static -l pl.UTF-8
Statyczna biblioteka lldpctl.

%package -n bash-completion-%{name}
Summary:	Bash completion for lldpcli command
Summary(pl.UTF-8):	Bashowe dopełnianie parametrów polecenia lldpcli
Group:		Applications/Shells
Requires:	%{name} = %{version}-%{release}
Requires:	bash-completion >= 1:2.0
BuildArch:	noarch

%description -n bash-completion-%{name}
Bash completion for lldpcli command.

%description -n bash-completion-%{name} -l pl.UTF-8
Bashowe dopełnianie parametrów polecenia lldpcli.

%package -n zsh-completion-%{name}
Summary:	zsh completion for lldpcli command
Summary(pl.UTF-8):	Dopełnianie parametrów polecenia lldpcli dla powłoki zsh
Group:		Applications/Shells
Requires:	%{name} = %{version}-%{release}
Requires:	zsh
BuildArch:	noarch

%description -n zsh-completion-%{name}
zsh completion for lldpcli command.

%description -n zsh-completion-%{name} -l pl.UTF-8
Dopełnianie parametrów polecenia lldpcli dla powłoki zsh.

%prep
%setup -q

%build
%configure \
	--disable-silent-rules \
	%{!?with_static_libs:--disable-static} \
	--with-apparmordir=no \
	--without-embedded-libevent \
	--with-libbsd \
	--with-privsep-user=daemon \
	--with-privsep-group=daemon \
	--with-readline \
	--with%{!?with_seccomp:out}-seccomp \
	--with%{!?with_snmp:out}-snmp \
	--with-systemdsystemunitdir=%{systemdunitdir} \
	--with-sysusersdir=no \
	--with-xml

%{__make}

%if %{with tests}
%{__make} check
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/{sysconfig,rc.d/init.d}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

%{__rm} $RPM_BUILD_ROOT%{_libdir}/liblldpctl.la
%{__rm} -r $RPM_BUILD_ROOT%{_docdir}/%{name}

install -p %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/lldpd
cp -p %{SOURCE2} $RPM_BUILD_ROOT/etc/sysconfig/lldpd

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add lldpd
%service lldpd restart "LLDP Daemon"
%systemd_post lldpd.service

%preun
if [ "$1" = "0" ]; then
	%service lldpd stop
	/sbin/chkconfig --del lldpd
fi
%systemd_preun lldpd.service

%postun
%systemd_reload

%triggerpostun -- lldpd < 1.0.22
%systemd_trigger lldpd.service

%post	libs -p /sbin/ldconfig
%postun	libs -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc NEWS README.md
%attr(754,root,root) /etc/rc.d/init.d/lldpd
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/lldpd
%dir %{_sysconfdir}/lldpd.d
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/lldpd.d/README.conf
%{systemdunitdir}/lldpd.service
%attr(755,root,root) %{_sbindir}/lldpcli
%{_sbindir}/lldpctl
%attr(755,root,root) %{_sbindir}/lldpd
%{_mandir}/man8/lldpcli.8*
%{_mandir}/man8/lldpctl.8*
%{_mandir}/man8/lldpd.8*

%files libs
%defattr(644,root,root,755)
%doc LICENSE
%attr(755,root,root) %{_libdir}/liblldpctl.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/liblldpctl.so.4

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/liblldpctl.so
%{_includedir}/lldp-const.h
%{_includedir}/lldpctl.h
%{_includedir}/lldpctl.hpp
%{_pkgconfigdir}/lldpctl.pc

%if %{with static_libs}
%files static
%defattr(644,root,root,755)
%{_libdir}/liblldpctl.a
%endif

%files -n bash-completion-%{name}
%defattr(644,root,root,755)
%{bash_compdir}/lldpcli

%files -n zsh-completion-%{name}
%defattr(644,root,root,755)
%{zsh_compdir}/_lldpcli
