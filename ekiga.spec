%define opal_version 3.10.10

%define kde_support 0
%{?_kde_support: %{expand: %%global kde_support 1}}

#define _disable_rebuild_configure 1

Summary:	Voice and Video over IP software (H323 / SIP)
Name:		ekiga
Version:	4.0.1
Release:	17
License:	GPLv2+
Group:		Video
Url:		http://www.ekiga.org
Source0:	http://ftp.gnome.org/pub/GNOME/sources/ekiga/4.0/%{name}-%{version}.tar.xz
Patch1:		ekiga-4.0.1-libresolv.patch
BuildRequires:	desktop-file-utils
BuildRequires:	gnome-common
BuildRequires:	intltool
BuildRequires:	scrollkeeper
BuildRequires:	xsltproc
BuildRequires:	boost-devel
BuildRequires:	gettext-devel
BuildRequires:	openldap-devel
BuildRequires:	pkgconfig(avahi-client)
BuildRequires:	pkgconfig(avahi-glib)
BuildRequires:	pkgconfig(dbus-1)
BuildRequires:	pkgconfig(dbus-glib-1)
BuildRequires:	pkgconfig(gconf-2.0)
BuildRequires:	pkgconfig(gnome-doc-utils)
BuildRequires:	pkgconfig(gnome-icon-theme)
BuildRequires:	pkgconfig(glib-2.0)
BuildRequires:	pkgconfig(gtk+-2.0)
BuildRequires:	pkgconfig(libebook-1.2)
BuildRequires:	pkgconfig(libnotify)
BuildRequires:	pkgconfig(opal) >= %{opal_version}
Buildrequires:	pkgconfig(ptlib) >= 2.10.9
BuildRequires:	pkgconfig(sigc++-2.0)
BuildRequires:	pkgconfig(xv)
%if %kde_support
BuildRequires:	kdelibs4-devel
%endif
%rename		gnomemeeting

Requires(post,postun):	scrollkeeper >= 0.3
Requires:	gnome-icon-theme
Requires:	opal3 >= %{opal_version}
Suggests:	yelp

%description
Ekiga is a tool to communicate with video and audio over the internet.
It uses both SIP and H323 protocol and is compatible with Microsoft Netmeeting.
It used to be called GnomeMeeting

%prep
%setup -q
%autopatch -p1

%build
%if %kde_support
QTDIR="/usr/lib/qt4" ; export QTDIR ; 
PATH="/usr/lib/qt4/bin:$PATH" ; export PATH ; 
%endif
export CXX="%__cxx -std=gnu++11"
%configure	\
%if %kde_support
	--enable-kde \
%endif
	--disable-schemas-install \
	--enable-dbus \
	--disable-gdu \
	--disable-gconf

make

%install
%makeinstall_std

%find_lang %{name} --with-gnome

desktop-file-install --vendor="" \
	--remove-category="Application" \
	--add-category="X-MandrivaLinux-CrossDesktop" \
	--dir %{buildroot}%{_datadir}/applications \
	%{buildroot}%{_datadir}/applications/*

%define launchers %{_sysconfdir}/dynamic/launchers/webcam
# dynamic support
mkdir -p %{buildroot}%{launchers}
cat > %{buildroot}%{launchers}/%{name}.desktop << EOF
[Desktop Entry]
Name=Ekiga \$devicename
Comment=Ekiga
TryExec=%{_bindir}/ekiga
Exec=%{_bindir}/ekiga
Terminal=false
Icon=ekiga
Type=Application
StartupNotify=true
EOF

rm -rf %{buildroot}/var/lib/scrollkeeper


%preun
if [ -r %{_sysconfdir}/gconf/schemas/gnomemeeting.schemas -a -x %{_bindir}/gconftool-2 ]; then
GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source` gconftool-2 --makefile-uninstall-rule %{_sysconfdir}/gconf/schemas/gnomemeeting.schemas > /dev/null
  update-alternatives --remove webcam.kde.dynamic %{launchers}/gnomemeeting.desktop
  update-alternatives --remove webcam.gnome.dynamic %{launchers}/gnomemeeting.desktop
fi
%preun_uninstall_gconf_schemas %{schemas}

%postun
if [ "$1" = "0" ]; then
  update-alternatives --remove webcam.kde.dynamic %{launchers}/%{name}.desktop
  update-alternatives --remove webcam.gnome.dynamic %{launchers}/%{name}.desktop
fi

%files -f %{name}.lang
%doc README NEWS FAQ AUTHORS TODO
%config(noreplace) %{launchers}/*.desktop
%{_bindir}/*
%{_libdir}/%{name}
%{_sysconfdir}/ekiga/*
%{_datadir}/dbus-1/services/org.ekiga*
%{_datadir}/applications/*
%{_datadir}/pixmaps/*
%{_datadir}/sounds/*
%{_iconsdir}/hicolor/*/apps/*
%{_mandir}/*/*

