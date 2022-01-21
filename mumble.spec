#define _disable_lto 1

%global optflags %{optflags} -lGLX

# configuration options for the server (murmur)
%define build_server	1
%define build_web	1
%define build_ice	0
# configuration options for the client
%define build_client	1
%define build_speechd	1
%define build_g15	1

%{?_without_server:	%{expand: %%global build_server 0}}
%{?_without_server:	%{expand: %%global build_ice 0}}
%{?_with_server:	%{expand: %%global build_server 1}}

%{?_without_ice:	%{expand: %%global build_ice 0}}
%{?_with_ice:		%{expand: %%global build_ice 1}}

%{?_without_client:	%{expand: %%global build_client 0}}
%{?_without_client:	%{expand: %%global build_speechd 0}}
%{?_without_client:	%{expand: %%global build_g15 0}}
%{?_with_client:	%{expand: %%global build_client 1}}

%{?_without_speechd:	%{expand: %%global build_speechd 0}}
%{?_with_speechd:	%{expand: %%global build_speechd 1}}

%{?_without_g15:	%{expand: %%global build_g15 0}}
%{?_with_g15:		%{expand: %%global build_g15 1}}

Summary:	Low-latency, high-quality voice communication for gamers
Name:		mumble
Version:	1.4.230
Release:	1
License:	BSD
Group:		Communications/Telephony
Url:		http://mumble.sourceforge.net/
Source0:	https://github.com/mumble-voip/mumble/releases/download/%{version}%{?prel:-%prel}/%{name}-%{version}%{?prel:-%prel}.tar.gz
#Patch0:		mumble-1.3.1-openssl3.patch
# conf files courtesy of debian package
Source1:	%{name}-server.ini
Source2:	%{name}-server-web.conf
Source3:	MurmurPHP.ini
#Source4:	README.install.urpmi.mumble-server-web
Source5:	%{name}-server-init.mdv
Source6:	%{name}-server.logrotate
Source7:	%{name}-tmpfiles.conf
#Patch0:		mumble-1.3.0-mga-celt071_include_dir.patch
# Fix broken logrotate script (start-stop-daemon not available anymore), BZ 730129
#Patch1:		mumble-1.2.3-fdr-logrotate.patch
# Fix broken celt-0.11.3 (uncompatible with mumble) mga#12853
#Patch2:		mumble-1.3.0-mga-only-use-celt071-libnames.patch
#Patch3:		mumble-1.3.0-celt071-AudioInput.patch
#Patch4:		mumble-1.3.0-fix-linking-failure-in-overlay_gl.patch

BuildConflicts:	celt-devel >= 0.7.0
BuildRequires:	desktop-file-utils
BuildRequires:	cmake
BuildRequires:	cmake(ECM)
BuildRequires:	cmake(Qt5LinguistTools)
BuildRequires:	cmake(Poco)
BuildRequires:	qt5-qttranslations
BuildRequires:	pkgconfig(Qt5Core)
BuildRequires:	pkgconfig(Qt5Concurrent)
BuildRequires:	pkgconfig(Qt5DBus)
BuildRequires:	pkgconfig(Qt5Gui)
BuildRequires:	pkgconfig(Qt5Help)
BuildRequires:	pkgconfig(Qt5Network)
BuildRequires:	pkgconfig(Qt5Sql)
BuildRequires:	pkgconfig(Qt5Svg)
BuildRequires:	pkgconfig(Qt5Widgets)
BuildRequires:	pkgconfig(Qt5Xml)
BuildRequires:  pkgconfig(expat)
BuildRequires:	pkgconfig(python)
BuildRequires:	boost-devel
BuildRequires:	protobuf-compiler
BuildRequires:	pkgconfig(avahi-compat-libdns_sd)
# NOT YET IN OMV
#BuildRequires:	pkgconfig(grpc)
BuildRequires:	pkgconfig(libcap)
BuildRequires:	pkgconfig(protobuf)
BuildRequires:	pkgconfig(speex) >= 1.2
BuildRequires:	pkgconfig(speexdsp)
# NOT YET IN OMV
#BuildRequires:	pkgconfig(celt071)
#BuildRequires:	pkgconfig(celt)
BuildRequires:  pkgconfig(ice)
BuildRequires:	pkgconfig(libpulse)
BuildRequires:	pkgconfig(alsa)
BuildRequires:	pkgconfig(ogg)
BuildRequires:	pkgconfig(openssl)
BuildRequires:	pkgconfig(xevie)
BuildRequires:	pkgconfig(sndfile)
BuildRequires:	pkgconfig(opus)
BuildRequires:	pkgconfig(xi) >= 1.6.0
BuildRequires:	pkgconfig(gl)
BuildRequires:	pkgconfig(dri)
BuildRequires:	pkgconfig(glu)
BuildRequires:	pkgconfig(glut)
BuildRequires:	egl-devel

%if %build_speechd
BuildRequires:	pkgconfig(speech-dispatcher)
%endif

%if %build_g15
BuildRequires:	g15daemon_client-devel
%endif

# (cg) The celt libraries are loaded dynamically but we need at least 0.7.1 to
# be compatible with the Windows and OSX clients
# The 0.11 version can work if the clients (and presumably the server) all
# support it.
# Using mklibname is not ideal but it's the easiest option for now
#Requires:	%{mklibname celt 071 0}

#We try to use bundled Celt 0.7 and 0.11

# For sanity, add as dep celt
Requires:	celt

Requires:	qt5-database-plugin-sqlite
Requires:	%{name}-plugins = %{version}-%{release}
Recommends:	%{name}-protocol-plasma5

%if %build_speechd
Recommends:	speech-dispatcher
%endif

%if %build_g15
Recommends:	g15daemon
%endif

%description
Low-latency, high-quality voice communication for gamers.

Includes game linking, so voice from other players comes
from the direction of their characters, and has echo
cancellation so the sound from your loudspeakers won't be
audible to other players.

%package	protocol-plasma5
Summary:	The mumble protocol for Plasma5
Group:		Graphical desktop/KDE
Requires:	%{name} = %{version}-%{release}
# keep just protocol for plasma5 (kde4 is dead)
Obsoletes:	mumble-protocol-kde4

%description	protocol-plasma5
The mumble protocol for Plasma5.

%package	plugins
Summary:	Mumble plugins
Group:		Communications/Telephony
Requires:	%{name} = %{version}-%{release}

%description	plugins
This packages provides the Mumble plugins.

%if %build_server
%package	server
Summary:	Murmur, the VOIP server for Mumble
Group:		Communications/Telephony
Requires(post):	systemd >= %{systemd_required_version}
Requires(pre):	rpm-helper
Requires(post):	rpm-helper
Requires(preun):	rpm-helper
%if %build_ice
# keep ice-devel, pkgconfig(ice) is not the same ice devel pkg
BuildRequires:	ice-devel
# (cg) ice-devel should require this itself, but it doesn't...
BuildRequires:	ice
%endif
Requires:	qt5-database-plugin-sqlite
Requires:	dbus
%if !%build_web
Conflicts:	%{name}-server-web
%endif

%description	server
This package provides Murmur, the VOIP server for Mumble.

%if %build_web
%package	server-web
Summary:	Web scripts for mumble-server
Group:		Communications/Telephony
Requires:	apache
Requires:	perl-CGI
Requires:	mail-server
%if %build_ice
Requires:	ice
%endif
Requires:	%{name}-server = %{version}-%{release}

%description	server-web
This package contains the web scripts for mumble-server.

%endif
%endif

%prep
%autosetup -n %{name}-%{version}.src -p1

#cp -p %{SOURCE4} README.install.urpmi

%build
%cmake \
	-Dice=off \
	-Doverlay-xcompile=off

%make_build
#%qmake_qt5 main.pro \
#	CONFIG+=no-ice \
#	LIBS+="-lpng16 -lfreetype -lXrender -lfontconfig -lGL"
#%if %build_server == 0
#	CONFIG+=no-server \
#%endif
#%if %build_client == 0
#	CONFIG+=no-client \
#%endif
#%if %build_speechd == 0
#	CONFIG+=no-speechd \
#%endif
#%if %build_g15 == 0
#	CONFIG+=no-g15 \
#%endif
#	CONFIG+=grpc \
#	CONFIG+=no-bundled-speex \
#	#CONFIG+=no-bundled-celt \
#	CONFIG+=no-bundled-opus \
#	CONFIG+=no-embed-qt-translations \
#	CONFIG+=no-update \
#	DEFINES+=PLUGIN_PATH=%{_libdir}/%{name} \
#	DEFINES+=DEFAULT_SOUNDSYSTEM=PulseAudio
#
#%{_qt5_bindir}/lrelease src/mumble/*.ts
#%make_build
#
%install
%if %build_client
# --- Mumble install ---

install -D -m 0755 release/%{name} %{buildroot}%{_bindir}/%{name}
install -m 0755 scripts/%{name}-overlay %{buildroot}%{_bindir}/%{name}-overlay
install -D -m 0644 scripts/%{name}.protocol %{buildroot}%{_kf5_services}/%{name}.protocol
install -d -m 0755 %{buildroot}%{_libdir}/%{name}/plugins
cp -pr release/libmumble* %{buildroot}%{_libdir}/%{name}/
cp -pr release/plugins/liblink.so %{buildroot}%{_libdir}/%{name}/

# Mumble icons
install -D -m 0644 icons/%{name}.svg %{buildroot}%{_iconsdir}/hicolor/scalable/apps/%{name}.svg

# Mumble desktop file
install -d -m 0755 %{buildroot}%{_datadir}/applications
install -m 0644 scripts/%{name}.desktop %{buildroot}%{_datadir}/applications/%{name}.desktop
desktop-file-install \
		     --remove-category="Qt" \
		     --dir %{buildroot}%{_datadir}/applications %{buildroot}%{_datadir}/applications/*

# translations
mkdir -p %{buildroot}%{_datadir}/%{name}/translations
install -m 0644 src/%{name}/*.qm %{buildroot}%{_datadir}/%{name}/translations/
%endif

%if %build_server
# --- Mumble-server/Murmur install ---

install -D -m 0755 release/murmurd "%{buildroot}%{_sbindir}/murmurd"
install -D -m 0755 scripts/murmur-user-wrapper %{buildroot}%{_bindir}/murmur-user-wrapper
mkdir -p %{buildroot}%{_sysconfdir}/{dbus-1/system.d,logrotate.d}
install -m 0644 scripts/murmur.conf %{buildroot}%{_sysconfdir}/dbus-1/system.d/%{name}-server.conf
install -m 0644 %{SOURCE6} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}-server
install -m 0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/%{name}-server.ini

%if %build_ice
# install Mumur.ice  in /usr/share/slice
#install -D -m 0755 src/murmur/Murmur.ice %{buildroot}%{_datadir}/slice/Murmur.ice
%endif

# install initscript
mkdir -p %{buildroot}%{_initrddir}
install -m 0744 %{SOURCE5} %{buildroot}%{_initrddir}/%{name}-server

# create database directory
install -d -m 0755 %{buildroot}%{_localstatedir}/lib/%{name}-server

# create log directory
install -d -m 0755 %{buildroot}%{_localstatedir}/log/%{name}-server

# create tmpfiles directory
install -D -p -m 0644 %{SOURCE7} %{buildroot}%{_tmpfilesdir}/%{name}-server.conf

# install example
mkdir -p %{buildroot}%{_localstatedir}/%{name}-server/examples

# create pidfile directory
install -d -m 0755 %{buildroot}%{_rundir}/%{name}-server

%if %build_web
# --- Mumble-server-web files ---
install -D -m 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/httpd/conf.d/%{name}-server-web.conf
%if %build_ice
install -D -m 0644 %{SOURCE3} %{buildroot}%{_sysconfdir}/php.d/MurmurPHP.ini
install -D -m 0644 scripts/server/ice/weblist.php %{buildroot}%{_datadir}/%{name}-server-web/www/weblist.php
%endif
install -D -m 0755 scripts/server/dbus/weblist.pl %{buildroot}%{_datadir}/%{name}-server-web/www/weblist.cgi
install -D -m 0755 scripts/server/dbus/murmur.pl %{buildroot}%{_datadir}/%{name}-server-web/www/register.cgi
pushd %{buildroot}%{_datadir}/%{name}-server-web/www
ln -s weblist.php index.php
popd
%endif
%endif

# --- Manpages ---
install -d -m 0755 %{buildroot}%{_mandir}/man1
%if %build_server
install -m 0644 man/murmur* %{buildroot}%{_mandir}/man1
%endif
%if %build_client
install -m 0644 man/mumble* %{buildroot}%{_mandir}/man1
%endif

%if %build_server
%pre server
%_pre_useradd %{name}-server %{_var}/lib/%{name}-server /bin/sh

%post server
%_tmpfilescreate %{_tmpfilesdir}/%{name}-server
%_post_service %{name}-server

%preun server
%_preun_service %{name}-server

%postun server
%_postun_userdel %{name}-server
%endif


%if %build_client
%files
%doc README README.Linux CHANGES LICENSE
%{_bindir}/%{name}
%{_bindir}/%{name}-overlay
%{_datadir}/%{name}/
%{_datadir}/applications/%{name}.desktop
%{_iconsdir}/hicolor/*/apps/%{name}.svg
%{_mandir}/man1/%{name}.*
%{_mandir}/man1/%{name}-overlay.*

%files protocol-plasma5
#{_kf5_services}/%{name}.protocol

%files plugins
%{_libdir}/%{name}
%endif

%if %build_server
%files server
%if %build_client == 0
%doc README README.Linux CHANGES LICENSE
%endif
%doc scripts/murmur.ini
%{_bindir}/murmur-user-wrapper
%{_sbindir}/murmurd
%{_initrddir}/%{name}-server
%{_tmpfilesdir}/%{name}-server.conf
%config(noreplace) %{_sysconfdir}/%{name}-server.ini
%{_sysconfdir}/logrotate.d/%{name}-server
%{_sysconfdir}/dbus-1/system.d/%{name}-server.conf
%attr(-,mumble-server,mumble-server) %dir %{_localstatedir}/lib/%{name}-server
%attr(-,mumble-server,root) %dir %{_localstatedir}/log/%{name}-server
%attr(-,mumble-server,mumble-server) %ghost %dir %{_rundir}/%{name}-server
%if %build_ice
%{_datadir}/slice/Murmur.ice
%endif
%{_mandir}/man1/murmur-user-wrapper.*
%{_mandir}/man1/murmurd.*

%if %build_web
%files server-web
#doc README.install.urpmi
%config(noreplace) %{_sysconfdir}/httpd/conf.d/%{name}-server-web.conf
%if %build_ice
%config(noreplace) %{_sysconfdir}/php.d/MurmurPHP.ini
%endif
%{_datadir}/%{name}-server-web
%endif
%endif
