%global giturl  https://gitlab.com/tuxedocomputers/development/packages/tuxedo-drivers/
%define buildforkernels akmod
%global debug_package %{nil}

Name:           tuxedo-drivers-kmod
Version:        4.22.3
Release:        %autorelease
Summary:        Drivers for Tuxedo computers (hardware compat check disabled)

Group:          System Environment/Kernel

License:        GPLv2
URL:            https://github.com/Atul977/Fedora-Tuxedo-Repo
Source0:        %{giturl}/-/archive/v%{version}/tuxedo-drivers-v%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Recommends:     udev-hid-bpf

BuildRequires:  kmodtool
BuildRequires:  akmods
BuildRequires:  make
BuildRequires:  gcc
BuildRequires:  patch
BuildRequires:  bash
BuildRequires:  findutils
BuildRequires:  kernel-devel
BuildRequires:  elfutils-libelf-devel
BuildRequires:  openssl-devel
BuildRequires:  perl
BuildRequires:  redhat-rpm-config

%description
Collection of Linux drivers for Tuxedo computers.
Built with the hardware compatibility check disabled so that
non-TUXEDO hardware (rebadged Clevo/Uniwill laptops) can use
these drivers normally.

%{expand:%(kmodtool --target %{_target_cpu} --kmodname %{name} %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null) }

# ── Userspace config sub-package ──────────────────────────────────────────────
%package -n tuxedo-drivers
Summary:        Common files for Tuxedo drivers.
Provides:       tuxedo-drivers-kmod-common = %{version}
Requires:       tuxedo-drivers-kmod >= %{version}

%description -n tuxedo-drivers
Configuration for Tuxedo computer drivers.
(Built with hardware compatibility check disabled.)

# ── Prep ──────────────────────────────────────────────────────────────────────
%prep
%autosetup -n tuxedo-drivers-v%{version} -p 1

# error out if there was something wrong with kmodtool
%{?kmodtool_check}

# ── DISABLE HARDWARE COMPATIBILITY CHECK ──────────────────────────────────────
# Directly replace the tuxedo_is_compatible() function with a stub that always
# returns true. This uses awk for reliable multi-line function replacement —
# more robust than sed for brace-delimited C functions.
COMPAT_FILE="src/tuxedo_compatibility_check/tuxedo_compatibility_check.c"

if [ -f "$COMPAT_FILE" ]; then
    awk '
    /^bool tuxedo_is_compatible\(void\)/ {
        print "bool tuxedo_is_compatible(void) {"
        print "\treturn true; /* compat check bypassed for non-TUXEDO hw */"
        print "}"
        # skip lines until we hit the closing brace of the original function
        in_func = 1
        next
    }
    in_func && /^\}/ {
        in_func = 0
        next
    }
    in_func { next }
    { print }
    ' "$COMPAT_FILE" > "${COMPAT_FILE}.patched"
    mv "${COMPAT_FILE}.patched" "$COMPAT_FILE"

    echo "--- tuxedo_is_compatible() successfully replaced ---"
    grep -A3 "bool tuxedo_is_compatible" "$COMPAT_FILE"
else
    echo "WARNING: $COMPAT_FILE not found — searching..."
    find src/ -name "tuxedo_compatibility_check.c" 2>/dev/null || true
fi
# ─────────────────────────────────────────────────────────────────────────────

# Ensure all scripts in the source tree are executable
find . -name "*.sh" -exec chmod +x {} \;

# print kmodtool output for debugging
kmodtool --target %{_target_cpu} --kmodname %{name} \
    %{?buildforkernels:--%{buildforkernels}} \
    %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null

for kernel_version in %{?kernel_versions} ; do
  mkdir -p _kmod_build_${kernel_version%%___*}
  cp -ar src/* _kmod_build_${kernel_version%%___*}/
done

# ── Build ─────────────────────────────────────────────────────────────────────
%build
for kernel_version in %{?kernel_versions} ; do
  make V=1 %{?_smp_mflags} \
    -C ${kernel_version##*___} \
    M=${PWD}/_kmod_build_${kernel_version%%___*} \
    VERSION=v%{version} modules
done

# ── Install ───────────────────────────────────────────────────────────────────
%install
# Module list derived from dkms.conf — update when upstream adds new hardware
ARRAY=(
  "clevo_acpi"
  "clevo_wmi"
  "tuxedo_keyboard"
  "uniwill_wmi"
  "ite_8291/ite_8291"
  "ite_8291_lb/ite_8291_lb"
  "ite_8297/ite_8297"
  "ite_829x/ite_829x"
  "tuxedo_io/tuxedo_io"
  "tuxedo_compatibility_check/tuxedo_compatibility_check"
  "tuxedo_nb05/tuxedo_nb05_keyboard"
  "tuxedo_nb05/tuxedo_nb05_power_profiles"
  "tuxedo_nb05/tuxedo_nb05_ec"
  "tuxedo_nb05/tuxedo_nb05_sensors"
  "tuxedo_nb05/tuxedo_nb05_kbd_backlight"
  "tuxedo_nb05/tuxedo_nb05_fan_control"
  "tuxedo_nb04/tuxedo_nb04_keyboard"
  "tuxedo_nb04/tuxedo_nb04_wmi_ab"
  "tuxedo_nb04/tuxedo_nb04_wmi_bs"
  "tuxedo_nb04/tuxedo_nb04_sensors"
  "tuxedo_nb04/tuxedo_nb04_power_profiles"
  "tuxedo_nb04/tuxedo_nb04_kbd_backlight"
  "tuxedo_nb02_nvidia_power_ctrl/tuxedo_nb02_nvidia_power_ctrl"
  "tuxedo_tuxi/tuxi_acpi"
  "tuxedo_tuxi/tuxedo_tuxi_fan_control"
  "stk8321/stk8321"
  "gxtp7380/gxtp7380"
)

for kernel_version in %{?kernel_versions}; do
  mkdir -p %{buildroot}%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/
  for module_path in "${ARRAY[@]}"; do
    module_name=$(basename "${module_path}")
    ko_file="_kmod_build_${kernel_version%%___*}/${module_path}.ko"
    if [ -f "$ko_file" ]; then
      install -D -m 755 "$ko_file" \
        %{buildroot}%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix}/${module_name}.ko
    else
      echo "WARNING: $ko_file not found, skipping"
    fi
  done
done
%{?akmod_install}

# Install userspace config
mkdir -p %{buildroot}%{_usr}/lib
mv files/usr/lib/modprobe.d  %{buildroot}%{_usr}/lib
mv files/usr/lib/udev        %{buildroot}%{_usr}/lib

# ── Files ─────────────────────────────────────────────────────────────────────
%files -n tuxedo-drivers
%{_usr}/lib/modprobe.d/*
%{_usr}/lib/udev/*
%doc README.md
%license LICENSE

%changelog
* Wed Apr 29 2026 Atul (custom build) - 4.22.2-1
- Use awk for robust multi-line function replacement of tuxedo_is_compatible()
- Fix script permission errors with find -exec chmod +x
- Add missing BuildRequires for complete kernel module build environment
- Add bounds check on module .ko existence before install
