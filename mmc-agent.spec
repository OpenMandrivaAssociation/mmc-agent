%define _enable_debug_packages %{nil}
%define debug_package          %{nil}

%if %mdkversion < 200610
%define py_puresitedir %{_prefix}/lib/python%{pyver}/site-packages/
%endif

Summary:	Mandriva Management Console Agent
Name:		mmc-agent
Version:	2.3.2
Release:	%mkrel 10
License:	GPL
Group:		System/Servers
URL:		http://mds.mandriva.org/
Source0:	%{name}-%{version}.tar.gz
Source1:	%{name}.init
Patch0:		%{name}-Makefile_fix.diff
Patch1:		%{name}_mdv_conf.diff
Patch2:		%{name}-plugins-base.diff
BuildRequires:	python-devel
#Requires:	python-pyopenssl
Requires:	pycrypto
Requires:	python-mmc-base >= 2.3.2
Requires:	python-OpenSSL
Requires(post): rpm-helper
Requires(preun): rpm-helper
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildArch: 	noarch

%description
XMLRPC server of the MMC API.

%package -n	python-mmc-base
Summary:	Mandriva Management Console base plugin
Group:		System/Servers
Requires:	python-ldap
Requires:	python-twisted
Requires:	python-twisted-conch
Requires:	python-twisted-core
Requires:	python-twisted-lore
Requires:	python-twisted-mail
Requires:	python-twisted-names
Requires:	python-twisted-runner
Requires:	python-twisted-web
Requires:	python-twisted-words
Provides:	python-mmc-plugins-tools = %{version}-%{release}
Obsoletes:	python-mmc-plugins-tools

%description -n	python-mmc-base
Contains the base infrastructure for all MMC plugins:
 * support classes
 * base LDAP management classes

%package -n	python-mmc-samba
Summary:	Mandriva Management Console SAMBA plugin
Group:		System/Servers
#Requires:	python-pylibacl
Requires:	acl
Requires:	pylibacl
Requires:	python-mmc-base >= 2.3.2
Requires:	samba-server

%description -n	python-mmc-samba
SAMBA management plugin for the MMC.

%package -n	python-mmc-mail
Summary:	Mandriva Management Console base plugin
Group:		System/Servers
Requires:	postfix
Requires:	postfix-ldap
Requires:	python-mmc-base >= 2.3.2

%description -n	python-mmc-mail
Mail account management plugin for the MMC.

%package -n	python-mmc-proxy
Summary:	Mandriva Management Console proxy plugin
Group:		System/Servers
Requires:	python-mmc-base >= 2.3.2
Requires:	squid
Requires:	squidGuard

%description -n	python-mmc-proxy
Squidguard/Squid management plugin for the MMC.

%package -n	python-mmc-network
Summary:	Mandriva Management Console network plugin
Group:		System/Servers
Requires:	python-mmc-base >= 2.3.2

%description -n	python-mmc-network
DNS/DHCP management plugin for the MMC.

This plugin requires a LDAP-patched version of ISC DHCPD and BIND9.

%prep

%setup -q -n %{name}-%{version}

for i in `find . -type d -name .svn`; do
    if [ -e "$i" ]; then rm -rf $i; fi >&/dev/null
done

%patch0 -p0
%patch1 -p1
%patch2 -p0

cp %{SOURCE1} mmc-agent.init

# mdv default fixes
for i in `find -type f`; do
    perl -pi -e "s|ou=Groups\b|ou=Group|g;s|ou=Users\b|ou=People|g;s|ou=Computers\b|ou=Hosts|g" $i
done

%build

%install
rm -rf %{buildroot}

%makeinstall_std LIBDIR=%{_prefix}/lib/mmc

rm -rf %{buildroot}%{_prefix}/lib*/python*
python setup.py install --root=%{buildroot} --install-purelib=%{py_puresitedir}

install -d %{buildroot}%{_initrddir}
install -d %{buildroot}%{_sysconfdir}/logrotate.d
install -d %{buildroot}/var/log/mmc

install -m0755 mmc-agent.init %{buildroot}%{_initrddir}/mmc-agent

# install log rotation stuff
cat > %{buildroot}%{_sysconfdir}/logrotate.d/mmc-agent << EOF
/var/log/mmc/mmc-agent.log /var/log/dhcp-ldap-startup.log /var/log/mmc/mmc-fileprefix.log {
    create 644 root root
    monthly
    compress
    missingok
    postrotate
	%{_initrddir}/mmc-agent condrestart >/dev/null 2>&1 || :
    endscript
}
EOF

# put the openldap schemas in place
install -d %{buildroot}%{_datadir}/openldap/schema
install -m0644 contrib/ldap/mmc.schema %{buildroot}%{_datadir}/openldap/schema/

%post
%_post_service mmc-agent

%preun
%_preun_service mmc-agent

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,0755)
%doc COPYING Changelog
%attr(0755,root,root) %{_initrddir}/mmc-agent
%dir %{_sysconfdir}/mmc
%dir %{_sysconfdir}/mmc/agent
%dir %{_sysconfdir}/mmc/agent/keys
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/agent/config.ini
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/agent/keys/cacert.pem
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/agent/keys/privkey.pem
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/logrotate.d/mmc-agent
%attr(0755,root,root) %{_sbindir}/mmc-agent
%{py_puresitedir}/mmc/agent.py*
%if %mdkversion >= 200700
%{py_puresitedir}/*.egg-info
%endif
%dir /var/log/mmc

%files -n python-mmc-base
%defattr(-,root,root,0755)
%doc contrib
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/base.ini
%{_sbindir}/mds-report
%{_prefix}/lib/mmc/backup-tools/cdlist
%{_prefix}/lib/mmc/backup-tools/backup.sh
%{py_puresitedir}/mmc/support
%{py_puresitedir}/mmc/__init__.py*
%{py_puresitedir}/mmc/plugins/__init__.py*
%{py_puresitedir}/mmc/plugins/base
%{py_puresitedir}/mmc/client.py*
%{_datadir}/openldap/schema/mmc.schema

%files -n python-mmc-mail
%defattr(-,root,root,0755)
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/mail.ini
%{py_puresitedir}/mmc/plugins/mail

%files -n python-mmc-network
%defattr(-,root,root,0755)
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/network.ini
%{py_puresitedir}/mmc/plugins/network

%files -n python-mmc-proxy
%defattr(-,root,root,0755)
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/proxy.ini
%{py_puresitedir}/mmc/plugins/proxy

%files -n python-mmc-samba
%defattr(-,root,root,0755)
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/samba.ini
%{py_puresitedir}/mmc/plugins/samba
%{_prefix}/lib/mmc/add_machine_script
%{_prefix}/lib/mmc/add_change_share_script
%{_prefix}/lib/mmc/add_printer_script
%{_prefix}/lib/mmc/delete_printer_script
%{_prefix}/lib/mmc/delete_share_script
