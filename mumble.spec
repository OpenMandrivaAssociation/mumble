%define _disable_ld_no_undefined 1
%global optflags %(echo %{optflags} |sed -e 's,-m64,,') -O3 -DPROTOBUF_USE_DLLS

%define build_number %(echo %{version} |cut -d. -f3)
# The 1.6.x tarball is versioned by build number. The git tag is not.
%global upstream_tag v1.6.0-alpha2

Summary:	Low-latency, high-quality voice communication for gamers
Name:		mumble
Version:	1.6.1001
Release:	1
License:	BSD
Group:		Communications/Telephony
Url:		https://www.mumble.info
# Default SQLite database lives in /var/lib/mumble-server.
Patch0:		mumble-server_config_database_path.patch
Source0:	https://github.com/mumble-voip/mumble/releases/download/%{upstream_tag}/mumble-%{version}.tar.gz

BuildRequires:	cmake
BuildRequires:	ninja
BuildRequires:	python
# 1.6 is Qt 6 only.
BuildRequires:	qmake-qt6
BuildRequires:	cmake(Qt6LinguistTools)
BuildRequires:	pkgconfig(Qt6Concurrent)
BuildRequires:	pkgconfig(Qt6Core)
BuildRequires:	pkgconfig(Qt6DBus)
BuildRequires:	pkgconfig(Qt6Gui)
BuildRequires:	pkgconfig(Qt6Network)
BuildRequires:	pkgconfig(Qt6Sql)
BuildRequires:	pkgconfig(Qt6Svg)
BuildRequires:	pkgconfig(Qt6Widgets)
BuildRequires:	pkgconfig(Qt6Xml)
BuildRequires:	cmake(Boost)
BuildRequires:	cmake(CLI11)
BuildRequires:	cmake(Poco)
BuildRequires:	cmake(absl)
BuildRequires:	cmake(nlohmann_json)
BuildRequires:	cmake(spdlog)
BuildRequires:	cmake(utf8cpp)
BuildRequires:	protobuf-compiler
BuildRequires:	pkgconfig(alsa)
BuildRequires:	pkgconfig(avahi-compat-libdns_sd)
BuildRequires:	pkgconfig(gl)
BuildRequires:	pkgconfig(libcap)
BuildRequires:	pkgconfig(libmariadb)
BuildRequires:	pkgconfig(libpq)
BuildRequires:	pkgconfig(openssl)
BuildRequires:	pkgconfig(opus)
BuildRequires:	pkgconfig(protobuf)
BuildRequires:	pkgconfig(rnnoise)
BuildRequires:	pkgconfig(sndfile)
BuildRequires:	pkgconfig(speech-dispatcher)
BuildRequires:	pkgconfig(speexdsp)
BuildRequires:	pkgconfig(sqlite3)
BuildRequires:	pkgconfig(xext)
BuildRequires:	pkgconfig(xi) >= 1.6.0
# overlay-xcompile builds libmumbleoverlay.x86 with clang -m32. That
# links against the i686 sysroot, which is not in the default chroot.
%ifarch %{x86_64}
BuildRequires:	cross-i686-openmandriva-linux-gnu-clang
BuildRequires:	cross-i686-openmandriva-linux-gnu-libc
BuildRequires:	cross-i686-openmandriva-linux-gnu-gcc
BuildRequires:	cross-i686-openmandriva-linux-gnu-binutils
BuildRequires:	cross-i686-openmandriva-linux-gnu-kernel-headers
%endif

Requires:	qt6-qtbase-sql-sqlite
Requires:	%{name}-plugins = %{EVRD}
Recommends:	%{name}-protocol-plasma5
Recommends:	qt6-qttranslations
Recommends:	speech-dispatcher

%description
Low-latency, high-quality voice communication for gamers.

Includes game linking, so voice from other players comes
from the direction of their characters, and has echo
cancellation so the sound from your loudspeakers won't be
audible to other players.

%package	plugins
Summary:	Mumble plugins
Group:		Communications/Telephony
Requires:	%{name} = %{EVRD}

%description	plugins
This packages provides the Mumble plugins.

%package	server
Summary:	Murmur, the VOIP server for Mumble
Group:		Communications/Telephony

%description	server
This package provides Murmur, the VOIP server for Mumble.

%prep
%autosetup -p1 -n %{name}-%{version}

# System SOCI is 4.0.3. Mumble needs the bundled SOCI >= 4.1 for its BLOB API.

%cmake \
	-DCMAKE_BUILD_TYPE=Release \
	-DCMAKE_INSTALL_SYSCONFDIR:PATH=%{_sysconfdir} \
	-DMUMBLE_INSTALL_SERVICEFILEDIR:PATH=%{_unitdir} \
	-DMUMBLE_INSTALL_SYSUSERSDIR:PATH=%{_sysusersdir} \
	-DMUMBLE_INSTALL_TMPFILESDIR:PATH=%{_tmpfilesdir} \
	-DBUILD_NUMBER=%{build_number} \
	-Dice=OFF \
%ifnarch %{x86_64}
	-Doverlay-xcompile=OFF \
%endif
	-Dwarnings-as-errors=OFF \
	-Dbundled-utfcpp=OFF \
	-Dbundled-json=OFF \
	-Dbundled-spdlog=OFF \
	-Dbundled-cli11=OFF \
	-Dbundled-speex=OFF \
	-Dbundled-rnnoise=OFF \
	-Drnnoise=ON \
	-Dbundled-soci=ON \
	-Denable-sqlite=ON \
	-Denable-mysql=ON \
	-Denable-postgresql=ON \
	-Dalsa=ON \
	-Dpulseaudio=ON \
	-Dpipewire=ON \
	-Dspeechd=ON \
	-G Ninja

%build
%ninja_build -C build

%install
%ninja_install -C build

mkdir -p %{buildroot}%{_localstatedir}/lib/mumble-server

%files
%license LICENSE
%{_bindir}/%{name}
# The overlay is not built on ARM.
%ifnarch %{arm} aarch64
%{_bindir}/%{name}-overlay
%{_mandir}/man1/mumble-overlay.1.*
%endif
%{_datadir}/applications/info.mumble.Mumble.desktop
%{_datadir}/metainfo/info.mumble.Mumble.appdata.xml
%{_iconsdir}/hicolor/*x*/apps/mumble.png
%{_iconsdir}/hicolor/scalable/apps/mumble.svg
%{_mandir}/man1/mumble.1.*

%files plugins
%{_libdir}/%{name}

%files server
%license LICENSE
%{_bindir}/%{name}-server
%{_bindir}/%{name}-server-user-wrapper
%dir %attr(0750,_mumble-server,_mumble-server) %{_localstatedir}/lib/%{name}-server
%{_mandir}/man1/%{name}-server.1.*
%{_mandir}/man1/%{name}-server-user-wrapper.1.*
%{_sysusersdir}/%{name}-server.conf
%{_unitdir}/%{name}-server.service
%{_tmpfilesdir}/%{name}-server.conf
%dir %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/%{name}-server.ini
