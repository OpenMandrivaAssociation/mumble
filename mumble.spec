Summary:	Low-latency, high-quality voice communication for gamers
Name:		mumble
Version:	1.1.3
Release:	%mkrel 1
License:	GPLv2+
Group:		Sound
Url:		http://mumble.sourceforge.net/
Source0:	http://downloads.sourceforge.net/mumble/%{name}-%{version}.tar.bz2
Source1:	%{name}.desktop
Source2:	%{name}-server.desktop
BuildRequires:	qt4-devel
BuildRequires:	boost-devel
BuildRequires:	pulseaudio-devel
BuildRequires:	libalsa-devel
BuildRequires:	openssl-devel
BuildRequires:	libxevie-devel
BuildRequires:	dbus-devel
BuildRequires:	qt4-linguist
BuildRoot:	%{_tmppath}/%{name}-%{version}-buildroot

%description
Low-latency, high-quality voice communication for gamers.

Includes game linking, so voice from other players comes 
from the direction of their characters, and has echo 
cancellation so the sound from your loudspeakers won't be 
audible to other players.

%prep
%setup -q

#rm -fr speex

%build
qmake main.pro DEFINIES+=NO_UPDATES DEFINIES+=DEFAULT_SOUNDSYSTEM=PulseAudio

%make

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

install -D -m0755 release/mumble "%{buildroot}%{_bindir}/mumble"
install -D -m0755 release/murmurd "%{buildroot}%{_sbindir}/murmurd"
ln_s ../sbin/murmurd "%{buildroot}%{_bindir}/mumble-server"
ln_s murmurd "%{buildroot}%{_sbindir}/murmur"

install -d "%{buildroot}%{_libdir}"
install release/libmumble.* "%{buildroot}%{_libdir}/"
install -D -m0644 plugins/mumble_plugin.h "%{buildroot}%{_includedir}/mumble_plugin.h"

install -D -m0644 icons/mumble.64x64.png "%{buildroot}%{_datadir}/pixmaps/mumble.png"
install -D -m0644 "%{SOURCE1}" "%{buildroot}%{_datadir}/applications/mumble.desktop"
install -D -m0644 "%{SOURCE2}" "%{buildroot}%{_datadir}/applications/mumble-server.desktop"

%find_lang %{name}

%if %mdkversion < 200900
%post
%{update_menus}
%{update_desktop_database}
%update_icon_cache hicolor
%endif

%if %mdkversion < 200900
%postun
%{clean_menus}
%{clean_desktop_database}
%clean_icon_cache hicolor
%endif

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files -f %{name}.lang
%defattr(644,root,root,755)
%doc
%attr(755,root,root)
