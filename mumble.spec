Summary:	Low-latency, high-quality voice communication for gamers
Name:		mumble
Version:	1.4.230
Release:	1
License:	BSD
Group:		Communications/Telephony
Url:		http://mumble.sourceforge.net/
Source0:	https://github.com/mumble-voip/mumble/releases/download/%{version}%{?prel:-%prel}/%{name}-%{version}%{?prel:-%prel}.tar.gz
# conf files courtesy of debian package
Source1:	%{name}-server.ini
Source2:	%{name}-server-web.conf
Source3:	MurmurPHP.ini
Source5:	%{name}-server-init.mdv
Source6:	%{name}-server.logrotate
Source7:	%{name}-tmpfiles.conf
#Patch0:		mumble-1.3.0-mga-celt071_include_dir.patch
# Fix broken logrotate script (start-stop-daemon not available anymore), BZ 730129
#Patch1:		mumble-1.2.3-fdr-logrotate.patch
# Fix broken celt-0.11.3 (uncompatible with mumble) mga#12853
#Patch2:		mumble-1.3.0-mga-only-use-celt071-libnames.patch
#Patch3:		mumble-1.3.0-celt071-AudioInput.patch
Patch4:		mumble-1.4.0-fix-linking-failure-in-overlay_gl.patch
Patch5:		https://patch-diff.githubusercontent.com/raw/mumble-voip/mumble/pull/5354.patch

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
BuildRequires:	pkgconfig(alsa)
BuildRequires:	pkgconfig(libpulse)
BuildRequires:	pkgconfig(libpipewire-0.3)
BuildRequires:	pkgconfig(rnnoise)
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

BuildRequires:	pkgconfig(speech-dispatcher)

#BuildRequires:	g15daemon_client-devel

# For sanity, add as dep celt
Celt is currently bundled until we fix system version. Anyway it neec compact version 0.7 (angry.p)
#Requires:	celt

Requires:	qt5-database-plugin-sqlite
Requires:	%{name}-plugins = %{version}-%{release}
Recommends:	%{name}-protocol-plasma5

Recommends:	speech-dispatcher
Recommends:	g15daemon

%description
Low-latency, high-quality voice communication for gamers.

Includes game linking, so voice from other players comes
from the direction of their characters, and has echo
cancellation so the sound from your loudspeakers won't be
audible to other players.

%package	plugins
Summary:	Mumble plugins
Group:		Communications/Telephony
Requires:	%{name} = %{version}-%{release}

%description	plugins
This packages provides the Mumble plugins.

%package	server
Summary:	Murmur, the VOIP server for Mumble
Group:		Communications/Telephony
Requires(post):	systemd >= %{systemd_required_version}
Requires(pre):	rpm-helper
Requires(post):	rpm-helper
Requires(preun): rpm-helper

# Currently ice source is dropped in Cooker. Let's enable it when package brack to repo (angry.p)
# keep ice-devel, pkgconfig(ice) is not the same ice devel pkg
#BuildRequires:	ice-devel
# (cg) ice-devel should require this itself, but it doesn't...
#BuildRequires:	ice

Requires:	qt5-database-plugin-sqlite
Requires:	dbus

%description	server
This package provides Murmur, the VOIP server for Mumble.

%prep
%autosetup -n %{name}-%{version}.src -p1

%build
%cmake \
	-Dice=off \
	-Doverlay-xcompile=off \
	-Dwarnings-as-errors=off \
	-Dbundled-opus=off \
	-Dbundled-rnnoise=off \
	-Dalsa=on \
	-Dpulseaudio=on \
	-Dpipewire=on

%make_build

%install
%make_install -C build


%files
%doc CHANGES LICENSE
%{_bindir}/%{name}
%{_bindir}/%{name}-overlay
%{_datadir}/applications/org.mumble_voip.mumble.desktop
%{_datadir}/metainfo/org.mumble_voip.mumble.appdata.xml
%{_iconsdir}/hicolor/*x*/apps/mumble.png
%{_iconsdir}/hicolor/scalable/apps/mumble.svg
%{_mandir}/man1/mumble-overlay.1.*
%{_mandir}/man1/mumble.1.*

%files plugins
%{_libdir}/%{name}

%files server
%doc CHANGES LICENSE
#doc scripts/murmur.ini
%{_bindir}/mumble-server
%{_mandir}/man1/murmur-user-wrapper.1.*
%{_mandir}/man1/murmurd.1.*
