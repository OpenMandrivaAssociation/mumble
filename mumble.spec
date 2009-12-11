# configuration options for the server (murmur)
%define build_server	1
%define build_ice	0
# configuration options for the client
%define build_speechd	1
%define build_g15	1

%{?_without_server: %{expand: %%global build_server 0}}
%{?_with_server: %{expand: %%global build_server 1}}

%{?_without_ice: %{expand: %%global build_ice 0}}
%{?_with_ice: %{expand: %%global build_ice 1}}

%{?_without_speechd: %{expand: %%global build_speechd 0}}
%{?_with_speechd: %{expand: %%global build_speechd 1}}

%{?_without_g15: %{expand: %%global build_g15 0}}
%{?_with_g15: %{expand: %%global build_g15 1}}

Summary:	Low-latency, high-quality voice communication for gamers
Name:		mumble
Version:	1.2.0
Release:	%mkrel 1
License:	BSD-like
Group:		Sound
Url:		http://mumble.sourceforge.net/
Source0:	http://downloads.sourceforge.net/mumble/%{name}-%{version}.tar.gz
# conf files courtesy of debian package
Source1:	%{name}-server.ini
Source2:	%{name}-server-web.conf
Source3:	MurmurPHP.ini
Source4:	README.install.urpmi.mumble-server-web
Source5:	%{name}-server-init.mdv
Patch0:		%{name}-fix-string-error.patch
%if %mdkversion < 200910
Buildrequires:	kde3-macros
%endif 
Buildrequires:	kde4-macros
BuildRequires:	libspeex-devel
BuildRequires:	celt-devel
BuildRequires:	qt4-devel >= 4.4.1
BuildRequires:	boost-devel
BuildRequires:	pulseaudio-devel
BuildRequires:	libalsa-devel
BuildRequires:	libogg-devel
BuildRequires:	openssl-devel
BuildRequires:	libxevie-devel
BuildRequires:	qt4-linguist >= 4.4.1
BuildRequires:	protobuf-devel
BuildRequires:	protobuf-compiler
BuildRequires:	avahi-compat-libdns_sd-devel
%if %build_speechd
BuildRequires:	speech-dispatcher-devel
%endif
%if %build_g15
BuildRequires:	g15daemon_client-devel
%endif
Requires:	qt4-database-plugin-sqlite >= 4.3.0
Requires:	%{name}-plugins = %{version}-%{release}
Suggests:	%{name}.protocol
%if %build_speechd
Suggests:	speech-dispatcher
%endif
%if %build_g15
Suggests:	g15daemon
%endif
BuildRoot:	%{_tmppath}/%{name}-%{version}-buildroot

%description
Low-latency, high-quality voice communication for gamers.

Includes game linking, so voice from other players comes 
from the direction of their characters, and has echo 
cancellation so the sound from your loudspeakers won't be 
audible to other players.

%package 11x
Summary:	The 1.1.x compatible client for mumble
Group:		Sound
Requires:	%{name} = %{version}-%{release}

%description 11x
This package provides the 1.1.x compatible client for Mumble, used
to connect to older servers.

%if %mdkversion < 200910
%package protocol-kde3
Summary:	The mumble protocol for KDE3
Group:		Graphical desktop/KDE
Requires:	%{name} = %{version}-%{release}

%description protocol-kde3
The mumble protocol for KDE3.
%endif

%package protocol-kde4
Summary:	The mumble protocol for KDE4
Group:		Graphical desktop/KDE
Requires:	%{name} = %{version}-%{release}

%description protocol-kde4
The mumble protocol for KDE4.

%package plugins
Summary:	Mumble plugins
Group:		Sound
Requires:       %{name} = %{version}-%{release}
# 24 may 2009 : necessary for upgrading
Provides:       %mklibname %{name} 1 
Provides:       %mklibname %{name} -d
Obsoletes:	%mklibname %{name} 1
Obsoletes:	%mklibname %{name} -d
# ugly fix for a requires on libc.so.6(GLIBC_PRIVATE) from
# the plugin that makes the package uninstallable without
# --nodeps
AutoReqProv:	0

%description plugins
This packages provides the Mumble plugins.

%if %build_server
%package server
Summary:	Murmur, the VOIP server for Mumble
Group:		Sound
Requires(post):	rpm-helper
Requires(preun):	rpm-helper
%if %build_ice
BuildRequires:	slice2cpp
%endif
Requires:	%{name} = %{version}-%{release}
Requires:	dbus

%description server
This package provides Murmur, the VOIP server for Mumble.

%package server-web
Summary:	Web scripts for mumble-server
Group:		Sound
Requires:	apache
Requires:	perl-CGI
Requires:	mail-server
%if %build_ice
Requires:	zeroc-ice-php
%endif
Requires:	%{name}-server = %{version}-%{release}

%description server-web
This package contains the web scripts for mumble-server.

%endif

%prep
%setup -q
%patch0 -p1 -b .strfmt
cp -p %{SOURCE4} README.install.urpmi

%build
%qmake_qt4 main.pro \
%if %build_server == 0
	CONFIG+=no-server \
%endif
%if %build_ice == 0
	CONFIG+=no-ice \
%endif
%if %build_speechd == 0
	CONFIG+=no-speechd \
%endif
%if %build_g15 == 0
	CONFIG+=no-g15 \
%endif
	CONFIG+=no-bundled-speex \
	CONFIG+=no-bundled-celt \
	CONFIG+=no-embed-qt-translations \
	CONFIG+=no-update \
	DEFINES+=PLUGIN_PATH=%{_libdir}/%{name} \
	DEFINES+=DEFAULT_SOUNDSYSTEM=PulseAudio

%make

%install
rm -rf %{buildroot}

# --- Mumble install ---

install -D -m 0755 release/%{name} %{buildroot}%{_bindir}/%{name}
install -m 0755 scripts/%{name}-overlay %{buildroot}%{_bindir}/%{name}-overlay
install -D -m 0755 scripts/%{name}.protocol %{buildroot}%{_kde_datadir}/kde4/services/%{name}.protocol
%if %mdkversion < 200910
install -D -m 0755 scripts/%{name}.protocol %{buildroot}%{_kde3_datadir}/kde3/services/%{name}.protocol
%endif
install -d -m 0755 %{buildroot}%{_libdir}/%{name}/plugins
cp -Pp release/libmumble* %{buildroot}%{_libdir}/%{name}/
cp -p release/plugins/liblink.so %{buildroot}%{_libdir}/%{name}/

# ---Mumble 11X ---
install -D -m 0755 release/%{name}11x %{buildroot}%{_bindir}/%{name}11x

# Mumble icons
install -D -m 0644 icons/%{name}.svg %{buildroot}%{_iconsdir}/hicolor/scalable/apps/%{name}.svg

# Mumble desktop file
install -d -m 0755 %{buildroot}%{_datadir}/applications
install -m 0644 scripts/%{name}.desktop %{buildroot}%{_datadir}/applications/%{name}.desktop
desktop-file-install \
		     --remove-category="Qt" \
		     --dir %{buildroot}%{_datadir}/applications %{buildroot}%{_datadir}/applications/*

# Create a Mumble11x desktop file from the Mumble one
sed -e "s/Name\=Mumble/Name\=Mumble-11x/g" \
	-e "s/Exec\=mumble/Exec\=mumble11x/g" \
	%{buildroot}%{_datadir}/applications/%{name}.desktop \
	> %{buildroot}%{_datadir}/applications/%{name}11x.desktop

%if %build_server
# --- Mumble-server/Murmur install ---

install -D -m0755 release/murmurd "%{buildroot}%{_sbindir}/murmurd"
install -m0755 scripts/murmur-user-wrapper %{buildroot}%{_bindir}/
mkdir -p %{buildroot}%{_sysconfdir}/{dbus-1/system.d,logrotate.d}
install -m0644 scripts/murmur.conf %{buildroot}%{_sysconfdir}/dbus-1/system.d/%{name}-server.conf
install -m0644 scripts/murmur.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/%{name}-server
install -m0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/%{name}-server.ini

%if %build_ice
# install Mumur.ice  in /usr/share/slice
install -D -m0755 src/murmur/Murmur.ice %{buildroot}%{_datadir}/slice/Murmur.ice
%endif

# install initscript
mkdir -p %{buildroot}%{_initrddir}
install -m0744 %{SOURCE5} %{buildroot}%{_initrddir}/%{name}-server

# create /etc/default/mumble-server
mkdir %{buildroot}%{_sysconfdir}/default
cat << EOF > %{buildroot}%{_sysconfdir}/default/%{name}-server
#0 = don't start, 1 = start
MURMUR_DAEMON_START=0
EOF

# create database directory
install -d -m0755 %{buildroot}%{_var}/lib/%{name}-server

# create log directory
install -d -m0755 %{buildroot}%{_var}/log/%{name}-server

# install example
mkdir -p %{buildroot}%{_var}/%{name}-server/examples

# --- Mumble-server-web files ---
install -D -m0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/httpd/conf.d/%{name}-server-web.conf
install -D -m0644 %{SOURCE3} %{buildroot}%{_sysconfdir}/php.d/MurmurPHP.ini
install -D -m0644 scripts/weblist.php %{buildroot}%{_datadir}/%{name}-server-web/www/weblist.php
install -D -m0755 scripts/weblist.pl %{buildroot}%{_datadir}/%{name}-server-web/www/weblist.cgi
install -D -m0755 scripts/murmur.pl %{buildroot}%{_datadir}/%{name}-server-web/www/register.cgi
pushd %{buildroot}%{_datadir}/%{name}-server-web/www
ln -s weblist.php index.php
popd
%endif

# --- Manpages ---
install -d -m 0755 %{buildroot}%{_mandir}/man1
%if %build_server == 0
install -m 0644 man/mumble* %{buildroot}%{_mandir}/man1
%else
install -m 0644 man/* %{buildroot}%{_mandir}/man1
%endif

%clean
rm -rf %{buildroot}

%if %mdkversion < 200900
%post
%{update_menus}
%update_desktop_database
%update_icon_cache hicolor
%endif

%if %mdkversion < 200900
%postun
%{clean_menus}
%clean_desktop_database
%clean_icon_cache hicolor
%endif


%if %build_server
%pre server
%_pre_useradd %{name}-server %{_var}/lib/%{name}-server /bin/sh

%post server
%_post_service %{name}-server
%__service messagebus reload

%preun server
if [ $1 = 0 ]; then
	%_preun_service %{name}-server
fi

%postun server
%_postun_userdel %{name}-server
%endif


%files
%defattr(-,root,root)
%doc README README.Linux CHANGES LICENSE
%{_bindir}/%{name}
%{_bindir}/%{name}-overlay
%{_datadir}/applications/%{name}.desktop
%{_iconsdir}/hicolor/*/apps/%{name}.svg
%{_mandir}/man1/%{name}.*
%{_mandir}/man1/%{name}-overlay.*

%files 11x
%defattr(-,root,root,-)
%{_bindir}/%{name}11x
%{_datadir}/applications/%{name}11x.desktop
%{_mandir}/man1/%{name}11x.*

%if %mdkversion < 200910
%files protocol-kde3
%defattr(-,root,root)
%{_kde3_datadir}/kde3/services/%{name}.protocol
%endif

%files protocol-kde4
%defattr(-,root,root)
%{_kde_datadir}/kde4/services/%{name}.protocol

%files plugins
%defattr(-,root,root,-)
%{_libdir}/%{name}

%if %build_server
%files server
%defattr(-,root,root)
%doc scripts/murmur.ini
%{_bindir}/murmur-user-wrapper
%{_sbindir}/murmurd
%{_initrddir}/%{name}-server
%config(noreplace) %{_sysconfdir}/%{name}-server.ini
%{_sysconfdir}/logrotate.d/%{name}-server
%{_sysconfdir}/dbus-1/system.d/%{name}-server.conf
%config(noreplace) %{_sysconfdir}/default/%{name}-server
%attr(-,mumble-server,mumble-server) %dir %{_var}/lib/%{name}-server
%attr(-,mumble-server,root) %dir %{_var}/log/%{name}-server
%if %build_ice
%{_datadir}/slice/Murmur.ice
%endif
%{_mandir}/man1/murmur-user-wrapper.*
%{_mandir}/man1/murmurd.*

%files server-web
%doc README.install.urpmi
%defattr(-,root,root)
%config(noreplace) %{_sysconfdir}/httpd/conf.d/%{name}-server-web.conf
%config(noreplace) %{_sysconfdir}/php.d/MurmurPHP.ini
%{_datadir}/%{name}-server-web
%endif
