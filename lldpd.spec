## TODO:
# - separate package with client and daemon (possible?)

Summary:	Implementation of IEEE 802.1AB, EDP and CDP
Summary(pl.UTF-8):	Implementacja IEEE 802.1AB, EDP oraz CDP
Name:		lldpd
Version:	0.5.7
Release:	0.1
License:	GPL
Group:		Networking
Source0:	http://media.luffy.cx/files/lldpd/%{name}-%{version}.tar.gz
# Source0-md5:	3db3a80fa6a384cd59e9d6a42ce7b630
#Source2:	%{name}-lldpd.init
#Source3:	%{name}-lldpd.sysconfig
#Source4:	%{name}-lldpd.service
URL:		https://github.com/vincentbernat/lldpd/wiki
BuildRequires:	autoconf >= 1.5
BuildRequires:	automake
BuildRequires:	libconfuse-devel
Requires(post,preun,postun):	systemd-units >= 38
Requires:	systemd-units >= 38
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

%prep
%setup -q

%build
%configure
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
#install -d $RPM_BUILD_ROOT{/etc/{sysconfig,rc.d/init.d},%{systemdunitdir}}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

#install %{SOURCE2} $RPM_BUILD_ROOT/etc/rc.d/init.d/lldpd
#install %{SOURCE3} $RPM_BUILD_ROOT/etc/sysconfig/lldpd
#install %{SOURCE4} $RPM_BUILD_ROOT%{systemdunitdir}/lldpd.service

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

%triggerpostun -- openlldp < 0.4
%systemd_trigger lldpd.service

%files
%defattr(644,root,root,755)
%doc CHANGELOG README.md
#%attr(754,root,root) /etc/rc.d/init.d/lldpd
#%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/lldpd
#%{systemdunitdir}/lldpd.service
%attr(755,root,root) %{_sbindir}/lldpd
%attr(755,root,root) %{_sbindir}/lldpctl
%{_mandir}/man8/lldpd.8*
%{_mandir}/man8/lldpctl.8*

