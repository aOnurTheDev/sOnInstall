<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="docs/logo/sonos.svg">
    <img src="docs/logo/sonos-light.svg" alt="sOnOs" width="320">
  </picture>
</p>

<h1 align="center">sOninstall</h1>

<p align="center">
  The installer of <a href="https://github.com/aOnurTheDev/sOnOs">sOnOs</a>, an Arch-based Linux distribution for developers and gamers.<br>
  Nine questions, then a ready desktop.
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-GPL--3.0-blue" alt="License: GPL-3.0"></a>
  <img src="https://img.shields.io/badge/python-3.14-blue" alt="Python 3.14">
  <a href="https://github.com/aOnurTheDev/sOnInstall/issues"><img src="https://img.shields.io/github/issues/aOnurTheDev/sOnInstall" alt="Issues"></a>
</p>

---

## Contents

- [Installing sOnOs](#installing-sonos)
- [What you get](#what-you-get)
- [Languages](#languages)
- [The full menu and other scripts](#the-full-menu-and-other-scripts)
- [Configuration files](#configuration-files)
- [Getting sOninstall](#getting-soninstall)
- [Putting sOninstall on the sOnOs ISO](#putting-soninstall-on-the-sonos-iso)
- [Development](#development)
- [FAQ](#faq)
- [Credits and license](#credits-and-license)

## Installing sOnOs

Boot the [sOnOs ISO](https://github.com/aOnurTheDev/sOnOs/releases). The installer starts on its own and asks:

| Step | Question | Notes |
|:---:|---|---|
| 1 | Language | English by default. The installer continues in it, and it becomes the language of the installed system. |
| 2 | Keyboard layout | The layout of the chosen language is preselected, e.g. `trq` for Turkish. |
| 3 | Username | |
| 4 | Password | Also used for root. |
| 5 | Timezone | |
| 6 | Desktop environment | KDE Plasma, GNOME, COSMIC, Hyprland and more. |
| 7 | NVIDIA driver | `nvidia-open`, for GeForce GTX 16xx, RTX 20xx and newer. Preselected when an NVIDIA card is found. |
| 8 | Development tools | Compilers, Visual Studio Code, Docker and every programming language, about 10 GB. Off by default. |
| 9 | Disk | The default layout, or your own partitions. |

A summary is shown before anything is written to the disk. Everything not asked uses sensible defaults: NetworkManager, PipeWire, Bluetooth, zram swap, systemd-boot and the hostname `sOnOs`.

If you quit the installer, start it again with:

```shell
soninstall
```

> [!TIP]
> No network cable? The installer offers to connect to Wi-Fi before it starts.

## What you get

| | |
|---|---|
| **Desktop** | The environment you picked, with its everyday apps. KDE Plasma comes with Konsole, Dolphin, Kate, Ark, Gwenview, Okular, Spectacle and KCalc. |
| **Apps** | Firefox (in your language), VLC, Steam, gamemode, fastfetch, btop |
| **Graphics** | Vulkan drivers for the GPUs in the machine, 32-bit ones included for Steam. NVIDIA's driver when you ask for it. |
| **Tools** | Disk, file system, network, VPN and virtualization tools, the editors micro, nano, neovim and vim, and zsh |
| **Development** *(optional)* | GCC, Clang, CMake, GDB, Visual Studio Code, Docker, Arduino and AVR tools, and Rust, Go, Python, Java, JavaScript/TypeScript, C#, Haskell, Zig and over 20 more languages |
| **sOnOs** | The sOnOs name and logo in the boot menu, the console, "About this system" pages and fastfetch |

An installation takes about **7 GB** without the development tools and about **17 GB** with them. The full package list is in [the sOnOs profile](soninstall/default_profiles/sonos.py).

## Languages

sOninstall is translated by the community into over 40 languages, some of them partly; Turkish is complete. The chosen language is also used for the installed system: `LANG`, the keyboard layout and the Firefox language pack.

The Linux console has no font for some scripts, such as Japanese, Chinese or Arabic. When one of those is chosen on the console, the installer stays in English, and the installed system still gets the language.

Translations are welcome, see [the translation guide](soninstall/locales/README.md).

## The full menu and other scripts

The menu where every setting can be changed, including disk encryption, the bootloader, kernels, mirrors and choosing development tools one by one:

```shell
soninstall --script guided
```

Other scripts run with `--script <name>`. Options most people do not need are behind `--advanced`, and every option is listed by `soninstall --help`.

## Configuration files

An installation can be described in two JSON files and run without questions:

- `user_configuration.json`: everything except secrets ([example](examples/config-sample.json))
- `user_credentials.json`: passwords ([example](examples/creds-sample.json))

The easiest way to get them is to set everything up in the menu and choose **Save configuration**. Then:

```shell
soninstall --config user_configuration.json --creds user_credentials.json
```

Both options also accept URLs. Configuration files saved by archinstall work too.

<details>
<summary>Encrypted credentials</summary>

User passwords are stored as `yescrypt` hashes. The disk encryption password has to be stored as it is, so when saving, sOninstall offers to encrypt `user_credentials.json`. To use an encrypted file, give the key in one of these ways:

- `--creds-decryption-key <password>`
- the `SONINSTALL_CREDS_DECRYPTION_KEY` environment variable
- or type it when asked

</details>

## Getting sOninstall

It comes installed on the sOnOs ISO. On other Arch Linux based systems, install it from the AUR:

```shell
git clone https://aur.archlinux.org/soninstall-git.git
cd soninstall-git && makepkg -si
```

Or run it from the source code, once the dependencies listed in [pyproject.toml](pyproject.toml) are installed:

```shell
git clone https://github.com/aOnurTheDev/sOnInstall
cd sOnInstall && sudo python -m soninstall
```

sOninstall can be installed next to archinstall.

## Putting sOninstall on the sOnOs ISO

The [sOnOs ISO profile](https://github.com/aOnurTheDev/sOnOs) installs `soninstall` from a local package repository. To build the package from this checkout, uncommitted changes included, into that repository:

```shell
packaging/local/build-repo.sh ~/sOnOs/repo
```

Then build the ISO from the profile as usual:

```shell
sudo mkarchiso -v -r -w ~/sonos-work -o ~/sonos-out .
```

## Development

```shell
python -m venv .venv
.venv/bin/pip install -e '.[dev,doc]'

.venv/bin/pytest
.venv/bin/ruff check . && .venv/bin/mypy && .venv/bin/flake8 && .venv/bin/pylint soninstall tests
```

The same checks run as [pre-commit](https://pre-commit.com/) hooks, see [CONTRIBUTING.md](CONTRIBUTING.md).

<details>
<summary>Trying it in a virtual machine</summary>

```shell
qemu-img create -f qcow2 disk.qcow2 40G
cp /usr/share/edk2/x64/OVMF_VARS.4m.fd vars.fd

qemu-system-x86_64 -enable-kvm -machine q35 -cpu host -smp 4 -m 4096 \
  -drive if=pflash,format=raw,readonly=on,file=/usr/share/edk2/x64/OVMF_CODE.4m.fd \
  -drive if=pflash,format=raw,file=vars.fd \
  -drive file=disk.qcow2,if=virtio \
  -cdrom sOnOs-x86_64.iso
```

The live system keeps its changes in memory and has little room for them by default. To install a test build there, make room first:

```shell
mount -o remount,size=1G /run/archiso/cowspace
```

</details>

## FAQ

<details>
<summary>How do I install sOnOs next to Windows?</summary>

1. Leave some unallocated space on the disk, e.g. by shrinking the Windows partition in Windows' Disk Management.
2. Boot the sOnOs ISO and go through the questions up to the disk.
3. Choose manual partitioning and the disk Windows is on.
4. Create a partition in the free space and give it the mountpoint `/`.
5. Give the existing EFI partition (`Boot/ESP`) the mountpoint `/boot`, without formatting it.
6. Confirm and continue with the installation.

</details>

<details>
<summary>Package installation fails with keyring or signature errors</summary>

Update the keyring first:

```shell
pacman -Sy archlinux-keyring
```

</details>

<details>
<summary>Something went wrong, how do I report it?</summary>

Open an [issue](https://github.com/aOnurTheDev/sOnInstall/issues) and include the log. From the ISO, this command uploads it and prints a link to share:

```shell
soninstall share-log
```

The log is at `/var/log/soninstall/install.log`.

</details>

## Credits and license

sOninstall is a fork of [archinstall](https://github.com/archlinux/archinstall) by Anton Hvornum and the archinstall contributors. Like archinstall, it is licensed under the [GPL-3.0](LICENSE).

Contributions are welcome, see [CONTRIBUTING.md](CONTRIBUTING.md) and the [AI usage policy](AI_POLICY.md).
