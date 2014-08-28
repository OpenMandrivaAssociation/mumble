# configuration options for the server (murmur)
%bcond_without server
%bcond_with ice
# configuration options for the client
%bcond_without client
%bcond_without speechd
%bcond_with g15

Summary:	Low-latency, high-quality voice communication for gamers
Name:		mumble
Version:	1.2.8
Release:	2
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
Source6:	%{name}-server.logrotate
Source7:        %{name}-tmpfiles.conf
Source100:	mumble.rpmlintrc
Patch0:		mumble-1.2.4-celt-0.11.1.patch
Patch1:		0001-use-std-max-instead-of-MAX.patch
Patch2:		mumble-1.2.5-fdr-compile-fix.patch
BuildRequires:	kde4-macros
BuildRequires:	protobuf-compiler
BuildRequires:	qt4-linguist
BuildRequires:	boost-devel
BuildRequires:	cap-devel
%if %{with g15}
BuildRequires:	g15daemon_client-devel
%endif
BuildRequires:	qt4-devel
%if %{with speechd}
BuildRequires:	speech-dispatcher-devel
%endif
BuildRequires:	pkgconfig(alsa)
BuildRequires:	pkgconfig(avahi-compat-libdns_sd)
BuildRequires:	pkgconfig(celt) >= 0.11.1
BuildRequires:	pkgconfig(libcap-ng)
BuildRequires:	pkgconfig(libpulse)
BuildRequires:	pkgconfig(libssl)
BuildRequires:	pkgconfig(ogg)
BuildRequires:	pkgconfig(protobuf)
BuildRequires:	pkgconfig(speex) >= 1.2
BuildRequires:	pkgconfig(sndfile)
BuildRequires:	pkgconfig(xevie)
BuildRequires:	pkgconfig(xi)
Requires:	qt4-database-plugin-sqlite
Requires:	%{name}-plugins = %{EVRD}
Suggests:	%{name}-protocol
%if %{with speechd}
Suggests:	speech-dispatcher
%endif
%if %{with g15}
Suggests:	g15daemon
%endif
# Strange, but true: We actually do require several different
# versions of the same library (celt) installed at the same time.
# The reason is that they're API/ABI compatible, but bitstream
# incompatible, releases - mumble dlopens any celt library it can
# find to support their bitstream versions.
# Since a lot of Mumble users are on legacy celt (0.7.x) [that's
# what Ubuntu ships], it is necessary to have that version
# installed to talk to those users.
Requires:	%mklibname celt0_ 0
Requires:	%mklibname celt0_ 2

%description
Low-latency, high-quality voice communication for gamers.

Includes game linking, so voice from other players comes from the direction
of their characters, and has echo cancellation so the sound from your
loudspeakers won't be audible to other players.

%if %{with client}
%files
%doc README README.Linux CHANGES LICENSE
%{_bindir}/%{name}
%{_bindir}/%{name}-overlay
%{_datadir}/applications/%{name}.desktop
%{_iconsdir}/hicolor/*/apps/%{name}.svg
%{_mandir}/man1/%{name}.*
%{_mandir}/man1/%{name}-overlay.*
%endif

#----------------------------------------------------------------------------

%if %{with client}
%package protocol-kde4
Summary:	The mumble protocol for KDE4
Group:		Graphical desktop/KDE
Requires:	%{name} = %{EVRD}
Provides:	%{name}-protocol

%description protocol-kde4
The mumble protocol for KDE4.

%files protocol-kde4
%{_kde_datadir}/kde4/services/%{name}.protocol
%endif

#----------------------------------------------------------------------------

%if %{with client}
%package plugins
Summary:	Mumble plugins
Group:		Sound
Requires:	%{name} = %{EVRD}

%description plugins
This packages provides the Mumble plugins.

%files plugins
%{_libdir}/%{name}
%endif

#----------------------------------------------------------------------------

%if %{with server}
%package server
Summary:	Murmur, the VOIP server for Mumble
Group:		Sound
%if %{with ice}
BuildRequires:	slice2cpp
%endif
Requires:	dbus
Requires:	qt4-database-plugin-sqlite
Requires(post,preun):	rpm-helper

%description server
This package provides Murmur, the VOIP server for Mumble.

%files server
%if %{without client}
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
%attr(-,mumble-server,mumble-server) %dir %{_var}/lib/%{name}-server
%attr(-,mumble-server,root) %dir %{_var}/log/%{name}-server
%attr(-,mumble-server,mumble-server) %dir %{_var}/run/%{name}-server
%if %{with ice}
%{_datadir}/slice/Murmur.ice
%endif
%{_mandir}/man1/murmur-user-wrapper.*
%{_mandir}/man1/murmurd.*

%pre server
%_pre_useradd %{name}-server %{_var}/lib/%{name}-server /bin/sh

%post server
%_post_service %{name}-server
%tmpfiles_create %{_tmpfilesdir}/%{name}-server
%__service messagebus reload

%preun server
if [ $1 = 0 ]; then
	%_preun_service %{name}-server
fi

%postun server
%_postun_userdel %{name}-server

%endif

#----------------------------------------------------------------------------

%if %{with server}
%package server-web
Summary:	Web scripts for mumble-server
Group:		Sound
Requires:	%{name}-server = %{EVRD}
Requires:	apache
Requires:	mail-server
Requires:	perl-CGI
%if %{with ice}
Requires:	zeroc-ice-php
%endif

%description server-web
This package contains the web scripts for mumble-server.

%files server-web
%doc README.install.urpmi
%config(noreplace) %{_sysconfdir}/httpd/conf.d/%{name}-server-web.conf
%config(noreplace) %{_sysconfdir}/php.d/MurmurPHP.ini
%{_datadir}/%{name}-server-web
%endif

#----------------------------------------------------------------------------

%prep
%setup -q
%patch0 -p1 -b .celt11~
%patch1 -p1 -b .max~
%patch2 -p1 -b .compile~
cp -p %{SOURCE4} README.install.urpmi

%build
%qmake_qt4 main.pro \
%if %{without server}
	CONFIG+=no-server \
%endif
%if %{without ice}
	CONFIG+=no-ice \
%endif
%if %{without client}
	CONFIG+=no-client \
%endif
%if %{without speechd}
	CONFIG+=no-speechd \
%endif
%if %{without g15}
	CONFIG+=no-g15 \
%endif
	CONFIG+=no-bundled-speex \
	CONFIG+=no-bundled-celt \
	CONFIG+=no-embed-qt-translations \
	CONFIG+=no-update \
	DEFINES+=PLUGIN_PATH=%{_libdir}/%{name} \
	DEFINES+=DEFAULT_SOUNDSYSTEM=PulseAudio

%make -j2

%install
%if %{with client}
# --- Mumble install ---

install -D -m 0755 release/%{name} %{buildroot}%{_bindir}/%{name}
install -m 0755 scripts/%{name}-overlay %{buildroot}%{_bindir}/%{name}-overlay
install -D -m 0755 scripts/%{name}.protocol %{buildroot}%{_kde_datadir}/kde4/services/%{name}.protocol
install -d -m 0755 %{buildroot}%{_libdir}/%{name}/plugins
cp -Pp release/libmumble* %{buildroot}%{_libdir}/%{name}/
cp -p release/plugins/liblink.so %{buildroot}%{_libdir}/%{name}/

# Mumble icons
install -D -m 0644 icons/%{name}.svg %{buildroot}%{_iconsdir}/hicolor/scalable/apps/%{name}.svg

# Mumble desktop file
install -d -m 0755 %{buildroot}%{_datadir}/applications
install -m 0644 scripts/%{name}.desktop %{buildroot}%{_datadir}/applications/%{name}.desktop
desktop-file-install \
	--remove-category="Qt" \
	--dir %{buildroot}%{_datadir}/applications %{buildroot}%{_datadir}/applications/*
%endif

%if %{with server}
# --- Mumble-server/Murmur install ---

install -D -m0755 release/murmurd "%{buildroot}%{_sbindir}/murmurd"
install -D -m0755 scripts/murmur-user-wrapper %{buildroot}%{_bindir}/murmur-user-wrapper
mkdir -p %{buildroot}%{_sysconfdir}/{dbus-1/system.d,logrotate.d}
install -m0644 scripts/murmur.conf %{buildroot}%{_sysconfdir}/dbus-1/system.d/%{name}-server.conf
install -m0644 %{SOURCE6} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}-server
install -m0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/%{name}-server.ini

%if %{with ice}
# install Mumur.ice  in /usr/share/slice
install -D -m0755 src/murmur/Murmur.ice %{buildroot}%{_datadir}/slice/Murmur.ice
%endif

# install initscript
mkdir -p %{buildroot}%{_initrddir}
install -m0744 %{SOURCE5} %{buildroot}%{_initrddir}/%{name}-server

# create database directory
install -d -m0755 %{buildroot}%{_var}/lib/%{name}-server

# create log directory
install -d -m0755 %{buildroot}%{_var}/log/%{name}-server

# create tmpfiles directory
install -D -p -m 0644 %{SOURCE7} %{buildroot}%{_tmpfilesdir}/%{name}-server.conf

# create pidfile directory
install -d -m0755 %{buildroot}%{_var}/run/%{name}-server

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
%if %{with server}
install -m 0644 man/murmur* %{buildroot}%{_mandir}/man1
%endif
%if %{with client}
install -m 0644 man/mumble* %{buildroot}%{_mandir}/man1
%endif

