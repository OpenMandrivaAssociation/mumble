Summary:	Low-latency, high-quality voice communication for gamers.
Name:		mumble
Version:	1.1.3
Release:	%mkrel 1
License:	GPLv2+
Group:		Sound
Url:		http://mumble.sourceforge.net/
Source0:	http://downloads.sourceforge.net/mumble/%{name}-%{version}.tar.bz2
BuildRequires:	qt4-devel
BuildRoot:	%{_tmppath}/%{name}-%{version}-buildroot

%description
Low-latency, high-quality voice communication for gamers.

Includes game linking, so voice from other players comes 
from the direction of their characters, and has echo 
cancellation so the sound from your loudspeakers won't be 
audible to other players.

%prep
%setup -q

%build
qmake main.pro

%make

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%makeinstall_std

%find_lang %{name}

%post
%{update_menus}
%if %mdkversion >= 200700
%{update_desktop_database}
%update_icon_cache hicolor
%endif

%postun
%{clean_menus}
%if %mdkversion >= 200700
%{clean_desktop_database}
%clean_icon_cache hicolor
%endif

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files -f %{name}.lang
%defattr(644,root,root,755)
%doc
%attr(755,root,root)
