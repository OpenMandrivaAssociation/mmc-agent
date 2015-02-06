%if %mdkversion < 200610
%define py_puresitedir %{_prefix}/lib/python%{pyver}/site-packages/
%endif

Summary:	Mandriva Management Console Agent
Name:		mmc-agent
Version:	2.3.2
Release:	13
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


%changelog
* Mon Dec 06 2010 Oden Eriksson <oeriksson@mandriva.com> 2.3.2-12mdv2011.0
+ Revision: 612873
- the mass rebuild of 2010.1 packages

* Tue Jun 08 2010 Anne Nicolas <ennael@mandriva.org> 2.3.2-11mdv2010.1
+ Revision: 547263
- fix typo in LSB headers of initscript

  + Per Øyvind Karlsen <peroyvind@mandriva.org>
    - don't explicitly disable debug packages, it's already implied by being noarch
    - drop redundant attributes for directories, it's already specified with %%defattr
    - take ownership of %%{_sysconfdir}/mmc

* Thu Jan 28 2010 Oden Eriksson <oeriksson@mandriva.com> 2.3.2-10mdv2010.1
+ Revision: 497582
- merge certain changes from mes5 updates (#55912):
 - use %%py_puresitedir instead of %%py_platsitedir (misc)
 - remove arch dependant references

* Sun Nov 08 2009 Glen Ogilvie <nelg@mandriva.org> 2.3.2-9mdv2010.1
+ Revision: 462798
- apply patch added in release 8. This fixes bug #48596

* Thu Sep 03 2009 Christophe Fergeau <cfergeau@mandriva.com> 2.3.2-8mdv2010.0
+ Revision: 426156
- rebuild

* Thu Apr 23 2009 Anne Nicolas <ennael@mandriva.org> 2.3.2-7mdv2009.1
+ Revision: 368788
- clean spec file
- fix #48596

  + Oden Eriksson <oeriksson@mandriva.com>
    - rebuild

* Sat Dec 27 2008 Funda Wang <fwang@mandriva.org> 2.3.2-5mdv2009.1
+ Revision: 319856
- rebuild for new python

  + Oden Eriksson <oeriksson@mandriva.com>
    - another try...

* Fri Dec 19 2008 Oden Eriksson <oeriksson@mandriva.com> 2.3.2-3mdv2009.1
+ Revision: 316268
- bump release due to stupid build system

* Fri Dec 19 2008 Oden Eriksson <oeriksson@mandriva.com> 2.3.2-2mdv2009.1
+ Revision: 316267
- bump release

* Thu Dec 18 2008 Oden Eriksson <oeriksson@mandriva.com> 2.3.2-1mdv2009.1
+ Revision: 315687
- fix deps
- 2.3.2
- rediffed P1
- dropped the pulse2_1.2.0rc6 patch (P2), it's implemented upstream

* Mon Nov 24 2008 Oden Eriksson <oeriksson@mandriva.com> 2.3.1-6mdv2009.1
+ Revision: 306341
- added pulse2 1.2.0rc6 fixes (P2)

* Wed Sep 24 2008 Vincent Guardiola <vguardiola@mandriva.com> 2.3.1-5mdv2009.0
+ Revision: 287855
- Remove requires
- Remove requires

* Fri Sep 19 2008 Oden Eriksson <oeriksson@mandriva.com> 2.3.1-4mdv2009.0
+ Revision: 285883
- whoops! pulse2-1.1.0_fixes was meant for cs4 only
- bump release
- added fixes for pulse2-1.1.0

* Wed Aug 06 2008 Thierry Vignaud <tv@mandriva.org> 2.3.1-2mdv2009.0
+ Revision: 265140
- rebuild early 2009.0 package (before pixel changes)

* Mon May 05 2008 Oden Eriksson <oeriksson@mandriva.com> 2.3.1-1mdv2009.0
+ Revision: 201305
- 2.3.1

* Wed Mar 12 2008 Oden Eriksson <oeriksson@mandriva.com> 2.3.0-1mdv2008.1
+ Revision: 187170
- 2.3.0

* Mon Feb 18 2008 Oden Eriksson <oeriksson@mandriva.com> 2.2.0-4mdv2008.1
+ Revision: 170117
- fix http://mds.mandriva.org/ticket/159 (Obsolete python-mmc-plugins-tools package)

* Mon Jan 21 2008 Oden Eriksson <oeriksson@mandriva.com> 2.2.0-3mdv2008.1
+ Revision: 155688
- rebuild
- fix deps, attributes and the logrotate script
- tiny fixes in the initscript

* Fri Jan 11 2008 Oden Eriksson <oeriksson@mandriva.com> 2.2.0-2mdv2008.1
+ Revision: 148717
- add pinit support (lsb tags)

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Tue Dec 04 2007 Oden Eriksson <oeriksson@mandriva.com> 2.2.0-1mdv2008.1
+ Revision: 115149
- 2.2.0
- rediffed P1

* Fri Sep 28 2007 Oden Eriksson <oeriksson@mandriva.com> 2.1.0-1mdv2008.0
+ Revision: 93675
- 2.1.0

* Wed Sep 12 2007 Oden Eriksson <oeriksson@mandriva.com> 2.0.1-0.r201.6mdv2008.0
+ Revision: 84694
- bump release (dacapo)
- bump release (again)
- bump release
- rebuild
- rebuild
- rebranded
- rebranding

* Fri Aug 31 2007 Crispin Boylan <crisb@mandriva.org> 2.0.0-6mdv2008.0
+ Revision: 76792
- Remove unused python-twisted modules from requires

* Thu Jul 19 2007 Oden Eriksson <oeriksson@mandriva.com> 2.0.0-5mdv2008.0
+ Revision: 53551
- move the php deps into the lmc-web-base package

* Mon Jul 09 2007 Oden Eriksson <oeriksson@mandriva.com> 2.0.0-4mdv2008.0
+ Revision: 50691
- catch the mdv defaults (Andreas Hasenack)

* Fri Jul 06 2007 Oden Eriksson <oeriksson@mandriva.com> 2.0.0-3mdv2008.0
+ Revision: 49188
- fix deps

* Tue Jul 03 2007 Oden Eriksson <oeriksson@mandriva.com> 2.0.0-2mdv2008.0
+ Revision: 47501
- really make it backportable to CS4

* Tue Jul 03 2007 Oden Eriksson <oeriksson@mandriva.com> 2.0.0-1mdv2008.0
+ Revision: 47466
- 2.0.0 (final)
- rediffed P0
- make it backportable to CS4

* Fri Jun 29 2007 Oden Eriksson <oeriksson@mandriva.com> 2.0.0-0.r158.1mdv2008.0
+ Revision: 45750
- Import lmc-agent



* Fri Jun 29 2007 Oden Eriksson <oeriksson@mandriva.com> 2.0.0-0.r158.1mdv2008.0
- initial Mandriva package
