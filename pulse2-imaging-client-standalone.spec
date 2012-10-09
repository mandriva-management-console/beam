%define name pulse2-imaging-client-standalone
%define version 0.1
%define release %mkrel 2

Name:		%{name}
Summary: 	Pulse 2 Imaging Client Standalone
Group:		XXXX
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
Version:	%{version}
Release:	%{release}
License:	GPL
URL:		http://pulse2.mandriva.com
Prefix:		%{_prefix}
Source:		%{name}-%{version}.tar.bz2
buildrequires:	glibc-static-devel gcc3.3-cpp gcc3.3

%description
Pulse 2 Imaging Client Standalone

%prep
rm -rf ${RPM_BUILD_ROOT}
%setup -q -n %{name}-%{version}

%build
%make

%install
# /!\ mettre dans un répertoire dédié : /usr/share/pulse2/lib, /usr/share/pulse2/bin
mkdir -p %{buildroot}%{_bindir}
mkdir -p %{buildroot}%{_libdir}
install -m755 $RPM_BUILD_DIR/%{name}-%{version}/autosave/autosave %{buildroot}%{_bindir}/autosave
install -m755 $RPM_BUILD_DIR/%{name}-%{version}/autorestore/autorestore %{buildroot}%{_bindir}/autorestore
install -m755 $RPM_BUILD_DIR/%{name}-%{version}/revosave/image_e2fs %{buildroot}%{_bindir}/
install -m755 $RPM_BUILD_DIR/%{name}-%{version}/revosave/image_fat %{buildroot}%{_bindir}/
install -m755 $RPM_BUILD_DIR/%{name}-%{version}/revosave/image_jfs %{buildroot}%{_bindir}/
install -m755 $RPM_BUILD_DIR/%{name}-%{version}/revosave/image_lvm %{buildroot}%{_bindir}/
install -m755 $RPM_BUILD_DIR/%{name}-%{version}/revosave/image_ntfs %{buildroot}%{_bindir}/
install -m755 $RPM_BUILD_DIR/%{name}-%{version}/revosave/image_raw %{buildroot}%{_bindir}/
install -m755 $RPM_BUILD_DIR/%{name}-%{version}/revosave/image_swap %{buildroot}%{_bindir}/
install -m755 $RPM_BUILD_DIR/%{name}-%{version}/revosave/image_ufs %{buildroot}%{_bindir}/
install -m755 $RPM_BUILD_DIR/%{name}-%{version}/revosave/image_xfs %{buildroot}%{_bindir}/
install -m755 $RPM_BUILD_DIR/%{name}-%{version}/revosave/liblrs.so %{buildroot}%{_libdir}/liblrs.so
install -m755 $RPM_BUILD_DIR/%{name}-%{version}/revosave/liblrs.so.1 %{buildroot}%{_libdir}/liblrs.so.1

%clean
rm -rf ${RPM_BUILD_ROOT}

# /!\ à faire depuis la GUI ?
%post -p /sbin/ldconfig

%postun -p /sbin/ldconfig

%files
%defattr(-,root,root)
%attr(755,root,root) %{_bindir}/*
%{_libdir}/liblrs*

%changelog
