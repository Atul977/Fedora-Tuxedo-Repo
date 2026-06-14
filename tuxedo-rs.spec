Name:           tuxedo-rs
Version:        0.2.5
Release:        1%{?dist}
Summary:        Rust daemon and GTK4 GUI for TUXEDO hardware
License:        GPL-2.0-or-later
URL:            https://github.com/AaronErhardt/tuxedo-rs
Source0:        tuxedo-rs-%{version}.tar.gz
Source1:        fixed_color_button.rs

BuildRequires:  cargo rust meson ninja-build desktop-file-utils pkgconfig(gtk4) pkgconfig(libadwaita-1) gettext systemd-rpm-macros

%description
Unified package containing the tailord Rust daemon and the tailor_gui GTK4 application (Patched 
for Niri)[cite: 7].

%prep
%autosetup -n tuxedo-rs-tailord-v%{version}

# Overwrite the source code with your Niri fix before building
cp %{SOURCE1} tailor_gui/src/components/color_button.rs

%build
# 1. Build the daemon using Cargo (just like Arch)
cd tailord
cargo build --release
cd ..

# 2. Build the GUI using Meson
cd tailor_gui
%meson
%meson_build
cd ..

%install
# 1. Install the GUI components
cd tailor_gui
%meson_install
cd ..

# 2. Install the daemon binary (Cargo outputs to the root target/ directory)
install -Dm0755 target/release/tailord -t %{buildroot}%{_bindir}/
install -Dm0644 tailord/com.tux.Tailor.conf -t %{buildroot}%{_datadir}/dbus-1/system.d/

# 3. Generate and install the systemd service directly
mkdir -p %{buildroot}%{_unitdir}
printf "[Unit]\nDescription=Tuxedo Tailor\n[Service]\nExecStart=/usr/bin/tailord\n[Install]\nWantedBy=multi-user.target\n" > %{buildroot}%{_unitdir}/tailord.service

%post
%systemd_post tailord.service

%preun
%systemd_preun tailord.service

%postun
%systemd_postun_with_restart tailord.service

%files
%license LICENSE
%{_bindir}/tailord
%{_bindir}/tailor_gui
%{_datadir}/applications/*.desktop
%{_datadir}/glib-2.0/schemas/*.xml
%{_datadir}/icons/hicolor/*/apps/*
%{_unitdir}/tailord.service
%{_datadir}/dbus-1/system.d/com.tux.Tailor.conf
%{_datadir}/metainfo/*.xml
%{_datadir}/tailor_gui/
