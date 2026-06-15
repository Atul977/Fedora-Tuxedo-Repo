# 🦎 Tuxedo Hardware Control for Non-TUXEDO Laptops (Fedora)

> [!CAUTION]
> **FEDORA ONLY:** Packages in this repo are built for Fedora Linux and will not work on Ubuntu, openSUSE, Debian, or Arch.

> [!NOTE]
> The hardware compatibility check in the official tuxedo-drivers is **disabled** here, so the drivers work on rebadged Clevo/Uniwill hardware not sold under the TUXEDO brand.

Enables native hardware control on supported laptops:

* 🎨 **RGB Keyboard Backlighting**
* 🌬️ **Fan Speed Curves**
* ⚡ **Power & Performance Profiles**

---

### 💻 Supported Devices

* **Acer Aspire A715-79G Series**
* **Acer ALG Series**
* Any laptop built on **Clevo / Uniwill hardware** that requires tuxedo-drivers

**🧪 Tested on:**

* **CPU:** Intel Core i5-13420H
* **GPU:** NVIDIA GeForce RTX 3050 (6 GB)
* **OS:** Fedora Linux (latest)

---

### 📦 Included Packages

| Package | Description |
| :--- | :--- |
| `akmod-tuxedo-drivers` | 🔧 Kernel drivers. Compiles automatically for your running kernel on first boot. |
| `tuxedo-rs` | ⚙️ `tailord` hardware daemon + GTK4 `tailor_gui`. Patched with the Niri color picker fix. |

---

### 🚀 Installation

```bash
# 1. Add the repo
sudo curl -Lo /etc/yum.repos.d/tuxedo-fedora.repo \
  https://atul977.github.io/Fedora-Tuxedo-Repo/tuxedo-fedora.repo

# 2. Install
sudo dnf install akmod-tuxedo-drivers tuxedo-rs

# 3. Reboot — akmod compiles the kernel modules automatically on first boot
reboot
```

After rebooting, start the hardware daemon:

```bash
sudo systemctl enable --now tailord.service
```

---

### 🔄 Updates

Upstream releases are tracked daily and rebuilt automatically. To update:

```bash
sudo dnf update
```

---

### ❓ Troubleshooting

**Modules not loading and you don't want to reboot:**
```bash
sudo akmods --force && sudo dracut --force && reboot
```

**Verify modules loaded correctly:**
```bash
lsmod | grep tuxedo
```

**tailord not starting:**
```bash
sudo journalctl -u tailord.service -e
```
