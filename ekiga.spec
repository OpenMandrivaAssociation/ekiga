%define opal_version 3.6.8

%define kde_support 0
%{?_kde_support: %{expand: %%global kde_support 1}}

Summary:	Voice and Video over IP software (H323 / SIP)
Name:		ekiga
Version:	3.2.7
Release:	%mkrel 3
License:	GPLv2+
Group:		Video
BuildRequires:	libgnomeui2-devel >= 2.0.0
BuildRequires:	opal3-devel >= %{opal_version}
Buildrequires:	ptlib-devel
BuildRequires:  avahi-glib-devel
BuildRequires:  avahi-client-devel
BuildRequires:	openldap-devel
BuildRequires:  libsigc++2.0-devel
BuildRequires:  libxv-devel
BuildRequires:  scrollkeeper
BuildRequires:  intltool
BuildRequires:  evolution-data-server-devel
BuildRequires:  dbus-glib-devel
BuildRequires:  libnotify-devel
BuildRequires:  automake
BuildRequires:  gnome-doc-utils >= 0.3.2 libxslt-proc
BuildRequires:  desktop-file-utils
%if %kde_support
BuildRequires:  kdelibs4-devel
%endif
Source0:	http://ftp.gnome.org/pub/GNOME/sources/ekiga/%{name}-%{version}.tar.bz2
Patch0: ekiga-3.1.0-format-string.patch
Patch1: ekiga-3.2.7-notify-0.7.patch
Patch2: ekiga-3.2.7-gtkflags.patch
Obsoletes:	gnomemeeting
Provides:	gnomemeeting

URL:		http://www.ekiga.org
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
Conflicts:	dynamic <= 0.3-2mdk
Requires:	soundwrapper
Requires:	opal3
Suggests:	yelp

%description
Ekiga is a tool to communicate with video and audio over the internet.
It uses both SIP and H323 protocol and is compatible with Microsoft Netmeeting.
It used to be called GnomeMeeting

%prep
%setup -q
%apply_patches

%build
%if %kde_support
  QTDIR="/usr/lib/qt4" ; export QTDIR ; 
  PATH="/usr/lib/qt4/bin:$PATH" ; export PATH ; 
%endif
%configure2_5x	\
%if %kde_support
        --enable-kde \
%endif
	--disable-schemas-install --enable-dbus
%make 

%install
rm -rf $RPM_BUILD_ROOT

%makeinstall_std


%find_lang %{name} --with-gnome 
for omf in %buildroot%_datadir/omf/*/{*-??,*-??_??}.omf;do
echo "%lang($(basename $omf|sed -e s/.*-// -e s/.omf//)) $(echo $omf|sed s!%buildroot!!)" >> %name.lang
done

sed -i -e 's,^Exec=ekiga,Exec=soundwrapper %{_bindir}/ekiga,g' $RPM_BUILD_ROOT%{_datadir}/applications/ekiga.desktop

desktop-file-install --vendor="" \
  --remove-category="Application" \
  --add-category="X-MandrivaLinux-CrossDesktop" \
  --dir $RPM_BUILD_ROOT%{_datadir}/applications $RPM_BUILD_ROOT%{_datadir}/applications/*


%define launchers %{_sysconfdir}/dynamic/launchers/webcam
# dynamic support
mkdir -p $RPM_BUILD_ROOT%launchers
cat > $RPM_BUILD_ROOT%launchers/%name.desktop << EOF
[Desktop Entry]
Name=Ekiga \$devicename
Comment=Ekiga
TryExec=%{_bindir}/ekiga
Exec=soundwrapper %{_bindir}/ekiga
Terminal=false
Icon=ekiga
Type=Application
StartupNotify=true
EOF


rm -rf %buildroot/var/lib/scrollkeeper

%define schemas ekiga

%post
%if %mdkversion < 200900
%post_install_gconf_schemas %{schemas}
%{update_menus}
%update_icon_cache hicolor
%endif

update-alternatives --install %{launchers}/kde.desktop webcam.kde.dynamic %launchers/%name.desktop 40
update-alternatives --install %{launchers}/gnome.desktop webcam.gnome.dynamic %launchers/%name.desktop 40
%if %mdkversion < 200900
%update_scrollkeeper
%endif

%preun
if [ -r %{_sysconfdir}/gconf/schemas/gnomemeeting.schemas -a -x %{_bindir}/gconftool-2 ]; then
GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source` gconftool-2 --makefile-uninstall-rule %{_sysconfdir}/gconf/schemas/gnomemeeting.schemas > /dev/null
  update-alternatives --remove webcam.kde.dynamic %launchers/gnomemeeting.desktop
  update-alternatives --remove webcam.gnome.dynamic %launchers/gnomemeeting.desktop
fi
%preun_uninstall_gconf_schemas %{schemas}

%postun
%if %mdkversion < 200900
%{clean_menus}
%{clean_scrollkeeper}
%clean_icon_cache hicolor
%endif

if [ "$1" = "0" ]; then
  update-alternatives --remove webcam.kde.dynamic %launchers/%name.desktop
  update-alternatives --remove webcam.gnome.dynamic %launchers/%name.desktop
fi

%clean
rm -rf $RPM_BUILD_ROOT

%files -f %{name}.lang
%defattr(-,root,root)
%doc README NEWS FAQ AUTHORS TODO
%{_bindir}/*
%dir %{_datadir}/omf/*
%{_datadir}/dbus-1/services/org.ekiga*
%{_datadir}/omf/*/*-C.omf
%{_datadir}/applications/*
%{_datadir}/pixmaps/*
%{_datadir}/sounds/*
%_datadir/icons/hicolor/*/apps/*
%{_mandir}/*/*
%{_sysconfdir}/gconf/schemas/*
%config(noreplace) %launchers/*.desktop
