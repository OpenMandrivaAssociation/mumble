%define _disable_ld_no_undefined 1
%global optflags %(echo %{optflags} |sed -e 's,-m64,,') -O3 -DPROTOBUF_USE_DLLS

%define build_number %(echo %{version} |cut -d. -f3)

Summary:	Low-latency, high-quality voice communication for gamers
Name:		mumble
Version:	1.5.735
Release:	2
License:	BSD
Group:		Communications/Telephony
Url:		https://www.mumble.info
Patch0:		mumble-server_config_database_path.patch
#Patch1:		auxiliary_files_fallback_path_fix.patch
Patch2:		mumble-fix-build.patch
Source0:	https://github.com/mumble-voip/mumble/releases/download/v%{version}/mumble-%{version}.tar.gz
# conf files courtesy of debian package
Source1:	%{name}-server-web.conf
Source2:	FindPythonInterpreter.cmake
Source3:	%{name}-server-init.mdv
Source4:	%{name}-server.logrotate
Source5:	%{name}-tmpfiles.conf
Source6:	mumble-server.sysusers

BuildConflicts:	celt-devel >= 0.7.0
BuildRequires:	desktop-file-utils
BuildRequires:	cmake
BuildRequires:	ninja
BuildRequires:	cmake(ECM)
BuildRequires:	cmake(Qt5LinguistTools)
BuildRequires:	cmake(Poco)
BuildRequires:	cmake(Utf8Proc)
BuildRequires:	poco
BuildRequires:	qt6-qttranslations
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
BuildRequires:	pkgconfig(libutf8proc)
BuildRequires:  pkgconfig(expat)
BuildRequires:	pkgconfig(python)
BuildRequires:	pkgconfig(alsa)
BuildRequires:	pkgconfig(libpulse)
BuildRequires:	pkgconfig(libpipewire-0.3)
BuildRequires:	pkgconfig(rnnoise)
BuildRequires:	boost-devel
BuildRequires:	protobuf-compiler
# For protobuf
BuildRequires:	cmake(absl)
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
#Celt is currently bundled until we fix system version. Anyway it neec compact version 0.7 (angry.p)
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
Requires(post):	systemd
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
%autosetup -p1
cp %{S:2} 3rdparty/FindPythonInterpreter/
%cmake \
	-DCMAKE_BUILD_TYPE=Release \
	-DCMAKE_INSTALL_SYSCONFDIR:PATH=%{_sysconfdir} \
	-DBUILD_NUMBER=%{build_number} \
	-Dice=off \
%ifnarch %{x86_64}
	-Doverlay-xcompile=off \
%endif
	-Dbundled-renamenoise=on \
	-Drenamenoise=on \
	-Dwarnings-as-errors=off \
	-Dbundled-opus=off \
	-Dbundled-speex=off \
	-Dalsa=on \
	-Dpulseaudio=on \
	-Dpipewire=on \
	-Dprotobuf_PROTOC_EXE=$(which protoc) \
	-G Ninja
 
 #-Dbundled-rnnoise=off \

%build
%ninja_build -C build

%install
%ninja_install -C build

mkdir -p %{buildroot}%{_localstatedir}/lib/mumble-server

mkdir -p %{buildroot}%{_sysusersdir}
cp -f %{S:6} %{buildroot}%{_sysusersdir}/mumble-server.conf

%files
%license LICENSE
%{_bindir}/%{name}
%{_bindir}/%{name}-overlay
%{_datadir}/applications/info.mumble.Mumble.desktop
%{_datadir}/metainfo/info.mumble.Mumble.appdata.xml
%{_iconsdir}/hicolor/*x*/apps/mumble.png
%{_iconsdir}/hicolor/scalable/apps/mumble.svg
%{_mandir}/man1/mumble-overlay.1.*
%{_mandir}/man1/mumble.1.*

%files plugins
%{_libdir}/%{name}

%pre server
%sysusers_create_package mumble-server %{S:6}

%files server
%license LICENSE
%{_bindir}/%{name}-server
%{_bindir}/%{name}-server-user-wrapper
#{_datadir}/dbus-1/system.d/%{name}-server.conf
%dir %attr(-,_%{name}-server,_%{name}-server) %{_localstatedir}/lib/%{name}-server
%{_mandir}/man1/%{name}-server.1.*
%{_mandir}/man1/%{name}-server-user-wrapper.1.*
%{_sysusersdir}/%{name}-server.conf
%{_sysconfdir}/systemd/system/mumble-server.service
%{_sysconfdir}/sysusers.d/mumble-server.conf
%{_sysconfdir}/tmpfiles.d/mumble-server.conf
%dir %{_sysconfdir}/%{name}
#config(noreplace) %{_sysconfdir}/%{name}/MumbleServer.ice
%config(noreplace) %{_sysconfdir}/%{name}/%{name}-server.ini
