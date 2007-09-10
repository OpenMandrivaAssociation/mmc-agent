%define _enable_debug_packages %{nil}
%define debug_package          %{nil}

%if %mdkversion < 200610
%define py_platsitedir %{_libdir}/python%{pyver}/site-packages/
%endif

Summary:	Linbox Management Console Agent
Name:		lmc-agent
Version:	2.0.0
Release:	%mkrel 6
License:	GPL
Group:		System/Servers
URL:		http://lds.linbox.org/
Source0:	%{name}-%{version}.tar.gz
Source1:	lmc-agent.init
Patch0:		lmc-agent-Makefile_fix.diff
Patch1:		lmc-agent_mdv_conf.diff
BuildRequires:	python-devel
#Requires:	python-pyopenssl
Requires:	pycrypto
Requires:	python-lmc-base
Requires:	python-OpenSSL
Requires(post): rpm-helper
Requires(preun): rpm-helper
Buildroot:	%{_tmppath}/%{name}-buildroot

%description
XMLRPC server of the LMC API.

%package -n	python-lmc-base
Summary:	Linbox Management Console base plugin
Group:		System/Servers
Requires:	python-ldap
Requires:	python-lmc-plugins-tools
Requires:	python-twisted
Requires:	python-twisted-conch
Requires:	python-twisted-core
Requires:	python-twisted-lore
Requires:	python-twisted-mail
Requires:	python-twisted-names
Requires:	python-twisted-runner
Requires:	python-twisted-web
Requires:	python-twisted-words
Requires:	python-zope-interface

%description -n	python-lmc-base
Contains the base infrastructure for all LMC plugins:
 * support classes
 * base LDAP management classes

%package -n	python-lmc-samba
Summary:	Linbox Management Console SAMBA plugin
Group:		System/Servers
#Requires:	python-pylibacl
Requires:	acl
Requires:	pylibacl
Requires:	python-lmc-base
Requires:	samba-server
Requires:	samba-vscan-clamav

%description -n	python-lmc-samba
SAMBA management plugin for the LMC.

%package -n	python-lmc-mail
Summary:	Linbox Management Console base plugin
Group:		System/Servers
Requires:	postfix
Requires:	postfix-ldap
Requires:	python-lmc-base

%description -n	python-lmc-mail
Mail account management plugin for the LMC.

%package -n	python-lmc-ox
Summary:	Linbox Management Console Open-Xchange plugin
Group:		System/Servers
Requires:	python-lmc-base
Requires:	python-psycopg

%description -n	python-lmc-ox
Open-Xchange management plugin for the LMC.
This plugin needs a working installation of Open-Xchange to be functional.

%package -n	python-lmc-proxy
Summary:	Linbox Management Console proxy plugin
Group:		System/Servers
Requires:	python-lmc-base
Requires:	squid
Requires:	squidGuard

%description -n	python-lmc-proxy
Squidguard/Squid management plugin for the LMC.

%package -n	python-lmc-network
Summary:	Linbox Management Console network plugin
Group:		System/Servers
Requires:	bind
Requires:	dhcp-server
Requires:	python-lmc-base

%description -n	python-lmc-network
DNS/DHCP management plugin for the LMC.

This plugin requires a LDAP-patched version of ISC DHCPD and BIND9.

%package -n	python-lmc-plugins-tools
Summary:	Required tools for some LMC plugins
Group:		System/Servers
Requires:	mkisofs

%description -n	python-lmc-plugins-tools
Contains common tools needed by some plugins of lmc-agent package.

%prep

%setup -q -n %{name}-%{version}
for i in `find . -type d -name .svn`; do
    if [ -e "$i" ]; then rm -rf $i; fi >&/dev/null
done

%patch0 -p0
%patch1 -p1

cp %{SOURCE1} lmc-agent.init

# lib64 fixes
perl -pi -e "s|/usr/lib/|%{_libdir}/|g" lmc/plugins/samba/__init__.py conf/plugins/samba.ini conf/plugins/base.ini

# mdv default fixes
for i in `find -type f`; do
    perl -pi -e "s|ou=Groups\b|ou=Group|g;s|ou=Users\b|ou=People|g;s|ou=Computers\b|ou=Hosts|g" $i
done

%build

%install
rm -rf %{buildroot}

%makeinstall_std LIBDIR=%{_libdir}/lmc

rm -rf %{buildroot}%{_prefix}/lib*/python*
python setup.py install --root=%{buildroot} --install-purelib=%{py_platsitedir}


install -d %{buildroot}/var/log/lmc
install -d %{buildroot}%{_initrddir}
install -d %{buildroot}%{_sysconfdir}/logrotate.d

install -m0755 lmc-agent.init %{buildroot}%{_initrddir}/lmc-agent

# install log rotation stuff
cat > %{buildroot}%{_sysconfdir}/logrotate.d/lmc-agent << EOF
/var/log/lmc/lmc-agent.log /var/log/dhcp-ldap-startup.log /var/log/lmc/lmc-fileprefix.log {
    create 644 root root
    monthly
    compress
    missingok
    postrotate
        /bin/kill -HUP `cat /var/run/lmc-agent.pid 2> /dev/null` 2> /dev/null || true
    endscript
}
EOF

# put the openldap schemas in place
install -d %{buildroot}%{_datadir}/openldap/schema
install -m0644 contrib/ldap/lmc.schema %{buildroot}%{_datadir}/openldap/schema/

%post
%_post_service lmc-agent

%preun
%_preun_service lmc-agent

%clean
rm -rf %{buildroot}

%files
%defattr(-,root,root,0755)
%doc contrib COPYING Changelog
%attr(0755,root,root) %{_initrddir}/lmc-agent
%attr(0755,root,root) %dir %{_sysconfdir}/lmc/agent
%attr(0755,root,root) %dir %{_sysconfdir}/lmc/agent/keys
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/lmc/agent/config.ini
%attr(0600,root,root) %config(noreplace) %{_sysconfdir}/lmc/agent/keys/cacert.pem
%attr(0600,root,root) %config(noreplace) %{_sysconfdir}/lmc/agent/keys/privkey.pem
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/logrotate.d/lmc-agent
%attr(0755,root,root) %{_sbindir}/lmc-agent
%{py_platsitedir}/lmc/agent.py*
%if %mdkversion >= 200700
%{py_platsitedir}/*.egg-info
%endif
%attr(0755,root,root) %dir /var/log/lmc
%{_datadir}/openldap/schema/lmc.schema

%files -n python-lmc-base
%defattr(-,root,root,0755)
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/lmc/plugins/base.ini
%{py_platsitedir}/lmc/support
%{py_platsitedir}/lmc/__init__.py*
%{py_platsitedir}/lmc/plugins/__init__.py*
%{py_platsitedir}/lmc/plugins/base

%files -n python-lmc-mail
%defattr(-,root,root,0755)
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/lmc/plugins/mail.ini
%{py_platsitedir}/lmc/plugins/mail

%files -n python-lmc-network
%defattr(-,root,root,0755)
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/lmc/plugins/network.ini
%{py_platsitedir}/lmc/plugins/network

%files -n python-lmc-plugins-tools
%defattr(-,root,root,0755)
%{_libdir}/lmc/backup-tools/cdlist
%{_libdir}/lmc/backup-tools/backup.sh

%files -n python-lmc-proxy
%defattr(-,root,root,0755)
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/lmc/plugins/proxy.ini
%{py_platsitedir}/lmc/plugins/proxy
%{py_platsitedir}/lmc/proxy.py*

%files -n python-lmc-samba
%defattr(-,root,root,0755)
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/lmc/plugins/samba.ini
%{py_platsitedir}/lmc/plugins/samba
%{_libdir}/lmc/add_machine_script
