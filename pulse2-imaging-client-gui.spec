%define name pulse2-imaging-client-gui
%define version 0.1
%define release %mkrel 1

Name:		%{name}
Summary:	Pulse 2 Imaging Client GUI
Group:		XXXX
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
Version:	%{version}
Release:	%{release}
License:	GPL
URL:		http://pulse2.mandriva.com
Prefix:		%{_prefix}
Source:		%{name}-%{version}.tar.bz2
requires:	python pulse2-imaging-client-standalone

%description
Pulse 2 Imaging Client GUI

%prep
rm -rf ${RPM_BUILD_ROOT}
%setup -q -n %{name}-%{version}

%build

%install
mkdir -p %{buildroot}/opt/%{name}-%{version}
mkdir -p %{buildroot}/%{_sysconfdir}/profile.d
install -m755 $RPM_BUILD_DIR/%{name}-%{version}/*.py %{buildroot}/opt/%{name}-%{version}
cp -avf $RPM_BUILD_DIR/%{name}-%{version}/i18n %{buildroot}/opt/%{name}-%{version}/
cp -avf $RPM_BUILD_DIR/%{name}-%{version}/BeaM* %{buildroot}/opt/%{name}-%{version}/
cp -avf $RPM_BUILD_DIR/%{name}-%{version}/media %{buildroot}/opt/%{name}-%{version}/

cat > %{buildroot}/%{_sysconfdir}/profile.d/beam.sh <<EOF
#!/bin/sh
export PATH=$PATH:/opt/%{name}-%{version}/
EOF

%clean
rm -rf ${RPM_BUILD_ROOT}

# /?\ pourquoi opt ?
%post 
mkdir /opt/%{name}-%{version}/lrs-bin
# /?\ wtf ?
cd /opt/%{name}-%{version}/lrs-bin
# /?\ wtf ?
for lrsbin in `ls -1 /usr/bin/image_*`
# /?\ wtf ?
	do ln -sf $lrsbin `basename $lrsbin`
done

# /?\ wtf ?
ln -sf /usr/bin/autorestore autorestore
ln -sf /usr/bin/autosave autosave

%postun 
rm -rf /opt/%{name}-%{version}/lrs-bin

%files
%defattr(-,root,root)
%attr(755,root,root) /opt/%{name}-%{version}/*.py
/opt/%{name}-%{version}/media/*
# à intégrer ?
/opt/%{name}-%{version}/i18n
%attr(755,root,root) %{_sysconfdir}/profile.d/%name.sh

%changelog
