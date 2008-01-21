%define _enable_debug_packages %{nil}
%define debug_package          %{nil}

%if %mdkversion < 200610
%define py_platsitedir %{_libdir}/python%{pyver}/site-packages/
%endif

Summary:	Mandriva Management Console Agent
Name:		mmc-agent
Version:	2.2.0
Release:	%mkrel 3
License:	GPL
Group:		System/Servers
URL:		http://mds.mandriva.org/
Source0:	%{name}-%{version}.tar.gz
Source1:	mmc-agent.init
Patch0:		mmc-agent-Makefile_fix.diff
Patch1:		mmc-agent_mdv_conf.diff
BuildRequires:	python-devel
#Requires:	python-pyopenssl
Requires:	pycrypto
Requires:	python-mmc-base
Requires:	python-OpenSSL
Requires(post): rpm-helper
Requires(preun): rpm-helper
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
XMLRPC server of the MMC API.

%package -n	python-mmc-base
Summary:	Mandriva Management Console base plugin
Group:		System/Servers
Requires:	python-ldap
Requires:	python-mmc-plugins-tools
Requires:	python-twisted
Requires:	python-twisted-conch
Requires:	python-twisted-core
Requires:	python-twisted-lore
Requires:	python-twisted-mail
Requires:	python-twisted-names
Requires:	python-twisted-runner
Requires:	python-twisted-web
Requires:	python-twisted-words

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
Requires:	python-mmc-base
Requires:	samba-server
Requires:	samba-vscan-clamav

%description -n	python-mmc-samba
SAMBA management plugin for the MMC.

%package -n	python-mmc-mail
Summary:	Mandriva Management Console base plugin
Group:		System/Servers
Requires:	postfix
Requires:	postfix-ldap
Requires:	python-mmc-base

%description -n	python-mmc-mail
Mail account management plugin for the MMC.

%package -n	python-mmc-ox
Summary:	Mandriva Management Console Open-Xchange plugin
Group:		System/Servers
Requires:	python-mmc-base
Requires:	python-psycopg

%description -n	python-mmc-ox
Open-Xchange management plugin for the MMC.
This plugin needs a working installation of Open-Xchange to be functional.

%package -n	python-mmc-proxy
Summary:	Mandriva Management Console proxy plugin
Group:		System/Servers
Requires:	python-mmc-base
Requires:	squid
Requires:	squidGuard

%description -n	python-mmc-proxy
Squidguard/Squid management plugin for the MMC.

%package -n	python-mmc-network
Summary:	Mandriva Management Console network plugin
Group:		System/Servers
Requires:	bind
Requires:	dhcp-server
Requires:	python-mmc-base

%description -n	python-mmc-network
DNS/DHCP management plugin for the MMC.

This plugin requires a LDAP-patched version of ISC DHCPD and BIND9.

%package -n	python-mmc-plugins-tools
Summary:	Required tools for some MMC plugins
Group:		System/Servers
Requires:	mkisofs

%description -n	python-mmc-plugins-tools
Contains common tools needed by some plugins of mmc-agent package.


%prep

%setup -q -n %{name}-%{version}
for i in `find . -type d -name .svn`; do
    if [ -e "$i" ]; then rm -rf $i; fi >&/dev/null
done

%patch0 -p0
%patch1 -p1

cp %{SOURCE1} mmc-agent.init

# lib64 fixes
perl -pi -e "s|/usr/lib/|%{_libdir}/|g" mmc/plugins/samba/__init__.py conf/plugins/samba.ini conf/plugins/base.ini

# mdv default fixes
for i in `find -type f`; do
    perl -pi -e "s|ou=Groups\b|ou=Group|g;s|ou=Users\b|ou=People|g;s|ou=Computers\b|ou=Hosts|g" $i
done

%build

%install
rm -rf %{buildroot}

%makeinstall_std LIBDIR=%{_libdir}/mmc

rm -rf %{buildroot}%{_prefix}/lib*/python*
python setup.py install --root=%{buildroot} --install-purelib=%{py_platsitedir}


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
%doc contrib COPYING Changelog
%attr(0755,root,root) %{_initrddir}/mmc-agent
%attr(0755,root,root) %dir %{_sysconfdir}/mmc/agent
%attr(0755,root,root) %dir %{_sysconfdir}/mmc/agent/keys
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/agent/config.ini
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/agent/keys/cacert.pem
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/agent/keys/privkey.pem
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/logrotate.d/mmc-agent
%attr(0755,root,root) %{_sbindir}/mmc-agent
%{py_platsitedir}/mmc/agent.py*
%if %mdkversion >= 200700
%{py_platsitedir}/*.egg-info
%endif
%attr(0755,root,root) %dir /var/log/mmc
%{_datadir}/openldap/schema/mmc.schema

%files -n python-mmc-base
%defattr(-,root,root,0755)
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/base.ini
%{py_platsitedir}/mmc/support
%{py_platsitedir}/mmc/__init__.py*
%{py_platsitedir}/mmc/plugins/__init__.py*
%{py_platsitedir}/mmc/plugins/base

%files -n python-mmc-mail
%defattr(-,root,root,0755)
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/mail.ini
%{py_platsitedir}/mmc/plugins/mail

%files -n python-mmc-network
%defattr(-,root,root,0755)
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/network.ini
%{py_platsitedir}/mmc/plugins/network

%files -n python-mmc-plugins-tools
%defattr(-,root,root,0755)
%{_libdir}/mmc/backup-tools/cdlist
%{_libdir}/mmc/backup-tools/backup.sh

%files -n python-mmc-proxy
%defattr(-,root,root,0755)
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/proxy.ini
%{py_platsitedir}/mmc/plugins/proxy

%files -n python-mmc-samba
%defattr(-,root,root,0755)
%attr(0640,root,root) %config(noreplace) %{_sysconfdir}/mmc/plugins/samba.ini
%{py_platsitedir}/mmc/plugins/samba
%{_libdir}/mmc/add_machine_script
