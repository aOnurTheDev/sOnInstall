import json
from pathlib import Path
from typing import TYPE_CHECKING, override

from soninstall.default_profiles.desktop import DesktopProfile
from soninstall.lib.hardware import SysInfo
from soninstall.lib.pacman.pacman import Pacman

if TYPE_CHECKING:
	from soninstall.lib.installer import Installer


SONOS_PROFILE_NAME = 'sOnOs'

FASTFETCH_LOGO = Path(__file__).parent / 'sonos_assets/fastfetch-logo.txt'
FASTFETCH_LOGO_TARGET = 'usr/share/sonos/fastfetch-logo.txt'

# The icon os-release names with LOGO=sonos. Without it, "About this system" pages and
# login screens fall back to the Arch Linux logo.
LOGO_ICON = Path(__file__).parent / 'sonos_assets/sonos.svg'
LOGO_ICON_TARGETS = ['usr/share/icons/hicolor/scalable/apps/sonos.svg', 'usr/share/pixmaps/sonos.svg']

# The text above the console login prompt, the name comes from os-release (Arch Linux otherwise)
ISSUE = '\\S{PRETTY_NAME} \\r (\\l)\n\n'

# fastfetch falls back to /etc/xdg/fastfetch when a user has no config of their own,
# so this one file covers root, existing accounts and accounts created later
FASTFETCH_CONFIG_TARGET = 'etc/xdg/fastfetch/config.jsonc'
FASTFETCH_CONFIG = {
	'logo': {
		'source': f'/{FASTFETCH_LOGO_TARGET}',
		# $1 in the logo is the red "On", $2 the rest
		'color': {'1': 'red', '2': 'white'},
	},
	'display': {'color': {'keys': 'red', 'title': 'red'}},
	# A config without a module list shows only the logo, so this is fastfetch's default list
	'modules': [
		'title',
		'separator',
		'os',
		'host',
		'kernel',
		'uptime',
		'packages',
		'shell',
		'display',
		'de',
		'wm',
		'wmtheme',
		'theme',
		'icons',
		'font',
		'cursor',
		'terminal',
		'terminalfont',
		'cpu',
		'gpu',
		'memory',
		'swap',
		'disk',
		'localip',
		'battery',
		'poweradapter',
		'locale',
		'break',
		'colors',
	],
}

OS_RELEASE = (
	'NAME="sOnOs"\n'
	'PRETTY_NAME="sOnOs"\n'
	'ID=sonos\n'
	'ID_LIKE=arch\n'
	'BUILD_ID=rolling\n'
	'ANSI_COLOR="38;2;23;147;209"\n'
	'HOME_URL="https://github.com/aOnurTheDev/sOnOs"\n'
	'DOCUMENTATION_URL="https://github.com/aOnurTheDev/sOnOs"\n'
	'SUPPORT_URL="https://github.com/aOnurTheDev/sOnOs"\n'
	'BUG_REPORT_URL="https://github.com/aOnurTheDev/sOnOs"\n'
	'PRIVACY_POLICY_URL="https://github.com/aOnurTheDev/sOnOs"\n'
	'LOGO="sonos"\n'
)

LSB_RELEASE = 'DISTRIB_ID="sOnOs"\nDISTRIB_RELEASE="rolling"\nDISTRIB_DESCRIPTION="sOnOs"\n'

# 64-bit Vulkan drivers; the 32-bit build of each is called lib32-<name>
VULKAN_DRIVERS = ['vulkan-radeon', 'vulkan-intel', 'vulkan-nouveau', 'nvidia-utils', 'vulkan-swrast']

# Tools installed with every sOnOs system, by category. Development tools are picked in the installer.
EXTRA_PACKAGES = [
	# Hardware and firmware tools
	'linux-firmware-marvell',
	'sof-firmware',
	'arch-install-scripts',
	'efibootmgr',
	'xdg-utils',
	'bolt',
	'alsa-utils',
	'dmidecode',
	'lsscsi',
	'mmc-utils',
	'sdparm',
	'sg3_utils',
	'usbutils',
	'usb_modeswitch',
	'usbmuxd',
	'libfido2',
	'libusb-compat',
	'pcsclite',
	'tpm2-tools',
	'openpgp-card-tools',
	# Disks, filesystems and recovery
	'bcachefs-tools',
	'btrfs-progs',
	'dosfstools',
	'e2fsprogs',
	'exfatprogs',
	'f2fs-tools',
	'fatresize',
	'fsarchiver',
	'gpart',
	'gptfdisk',
	'jfsutils',
	'lvm2',
	'mdadm',
	'dmraid',
	'smartmontools',
	'mtools',
	'nilfs-utils',
	'ntfsprogs',
	'nvme-cli',
	'partclone',
	'parted',
	'partimage',
	'squashfs-tools',
	'testdisk',
	'udftools',
	'xfsprogs',
	'ddrescue',
	'pv',
	# Networking and wireless
	'bind',
	'dhcpcd',
	'dnsmasq',
	'ethtool',
	'iw',
	'iwd',
	'linux-atm',
	'ldns',
	'modemmanager',
	'ndisc6',
	'nbd',
	'networkmanager',
	'nfs-utils',
	'nmap',
	'openconnect',
	'openssh',
	'openvpn',
	'ppp',
	'pptpclient',
	'reflector',
	'systemd-resolvconf',
	'tcpdump',
	'vpnc',
	'wireguard-tools',
	'wireless-regdb',
	'wireless_tools',
	'wpa_supplicant',
	'wvdial',
	'xl2tpd',
	'open-iscsi',
	# Virtualization
	'qemu-base',
	'qemu-guest-agent',
	'open-vm-tools',
	'virtualbox-guest-utils',
	'hyperv',
	# Command line tools, editors and terminals
	'b43-fwcutter',
	'curl',
	'darkhttpd',
	'diffutils',
	'fastfetch',
	'fd',
	'foot-terminfo',
	'ghostty-terminfo',
	'gpm',
	'hdparm',
	'htop',
	'btop',
	'irssi',
	'jq',
	'kitty-terminfo',
	'kmscon-terminfo',
	'less',
	'lftp',
	'lynx',
	'man-db',
	'man-pages',
	'mc',
	'nano',
	'neovim',
	'7zip',
	'ripgrep',
	'rsync',
	'rxvt-unicode-terminfo',
	'screen',
	'sequoia-sq',
	'terminus-font',
	'tmux',
	'tree',
	'unzip',
	'wget',
	'zip',
	'zsh',
	'git',
]


def logo_banner(columns: int) -> str:
	"""The fastfetch logo in colour, centered in a terminal that is `columns` wide"""
	white, red, reset = '\x1b[1;37m', '\x1b[1;31m', '\x1b[0m'
	lines = FASTFETCH_LOGO.read_text().splitlines()
	width = max(len(line.replace('$1', '').replace('$2', '')) for line in lines)
	indent = ' ' * max((columns - width) // 2, 0)

	return '\n'.join(f'{indent}{white}{line.replace("$1", red).replace("$2", white)}{reset}' for line in lines)


class SonosProfile(DesktopProfile):
	def __init__(self) -> None:
		super().__init__()
		self.name = SONOS_PROFILE_NAME

	@property
	@override
	def packages(self) -> list[str]:
		return list(
			dict.fromkeys(
				[
					*super().packages,
					'gamemode',
					'git',
					'micro',
					'neovim',
					'vim',
					'steam',
					'blueman',
					'fastfetch',
					'btop',
					'zsh',
					'7zip',
					'ntfs-3g',
					'brightnessctl',
					'pavucontrol',
					# No desktop profile brings a browser or a media player
					'firefox',
					'vlc',
					'vlc-plugins-all',
					'noto-fonts-emoji',
					*EXTRA_PACKAGES,
				]
			)
		)

	@override
	def install(self, install_session: Installer) -> None:
		# Steam depends on vulkan-driver and lib32-vulkan-driver. If nothing installed provides
		# them, pacman --noconfirm picks the NVIDIA packages whatever the GPU is, so the drivers
		# for this machine have to be in place before Steam is installed.
		headers = [f'{kernel}-headers' for kernel in install_session.kernels]
		install_session.add_additional_packages([*self._vulkan_packages(install_session), *headers])

		super().install(install_session)

		if language_pack := self._firefox_language_pack(install_session.target):
			install_session.add_additional_packages([language_pack])

	@staticmethod
	def _firefox_language_pack(target: Path) -> str | None:
		"""Firefox is English only, its translations are separate packages (firefox-i18n-tr, firefox-i18n-pt-br, ...)"""
		locale_conf = target / 'etc/locale.conf'
		if not locale_conf.exists():
			return None

		values = dict(line.split('=', 1) for line in locale_conf.read_text().splitlines() if '=' in line)
		# tr_TR.UTF-8, sr_RS@latin
		locale = values.get('LANG', '').strip('"').split('.')[0].split('@')[0]
		language, _, country = locale.lower().partition('_')

		if not language or language in ('c', 'en'):
			return None

		available = {line.decode().strip() for line in Pacman.run('-Ssq ^firefox-i18n-')}
		candidates = [f'firefox-i18n-{language}-{country}', f'firefox-i18n-{language}']

		return next((package for package in candidates if package in available), None)

	def _vulkan_packages(self, install_session: Installer) -> list[str]:
		installed = {line.decode().strip() for line in Pacman.run(f'-Qq --root {install_session.target}')}

		# Use the drivers that came with the selected graphics driver, otherwise detect the GPU
		drivers = [driver for driver in VULKAN_DRIVERS if driver in installed] or self._detect_vulkan_drivers()

		return [*drivers, *(f'lib32-{driver}' for driver in drivers), 'lib32-mesa']

	@staticmethod
	def _detect_vulkan_drivers() -> list[str]:
		drivers = []

		if SysInfo.has_amd_graphics():
			drivers.append('vulkan-radeon')
		if SysInfo.has_intel_graphics():
			drivers.append('vulkan-intel')
		if SysInfo.has_nvidia_graphics():
			# Works with the in-kernel nouveau driver, unlike nvidia-utils
			drivers.append('vulkan-nouveau')

		# No supported GPU (e.g. a virtual machine): fall back to the CPU-based driver
		return drivers or ['vulkan-swrast']

	@override
	def post_install(self, install_session: Installer) -> None:
		super().post_install(install_session)

		target = install_session.target

		# /etc/os-release is a symlink to /usr/lib/os-release, which the filesystem package
		# overwrites on every update. A regular /etc/os-release takes precedence, belongs to no
		# package and is left alone by systemd-tmpfiles, so the branding survives updates.
		os_release = target / 'etc/os-release'
		os_release.unlink(missing_ok=True)
		os_release.write_text(OS_RELEASE)

		# Unified kernel images embed os-release and systemd-boot takes the menu title from it.
		# The guided installer builds them once more at the end, after this branding.

		# lsb-release does not mark this file as a backup file, so keep pacman from overwriting it
		lsb_release = target / 'etc/lsb-release'
		if lsb_release.exists():
			lsb_release.write_text(LSB_RELEASE)
			self._add_no_upgrade(target / 'etc/pacman.conf', 'etc/lsb-release')

		# A backup file of the filesystem package, so updates leave it alone
		(target / 'etc/issue').write_text(ISSUE)

		for icon_target in LOGO_ICON_TARGETS:
			icon = target / icon_target
			icon.parent.mkdir(parents=True, exist_ok=True)
			LOGO_ICON.copy(icon)

		# GTK and COSMIC only find icons that are in the cache of the theme
		if (target / 'usr/bin/gtk-update-icon-cache').exists():
			install_session.arch_chroot('gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor')

		logo = target / FASTFETCH_LOGO_TARGET
		logo.parent.mkdir(parents=True, exist_ok=True)
		FASTFETCH_LOGO.copy(logo)

		fastfetch_config = target / FASTFETCH_CONFIG_TARGET
		fastfetch_config.parent.mkdir(parents=True, exist_ok=True)
		fastfetch_config.write_text(json.dumps(FASTFETCH_CONFIG, indent=2) + '\n')

	@staticmethod
	def _add_no_upgrade(pacman_conf: Path, file: str) -> None:
		lines = pacman_conf.read_text().splitlines()
		entry = f'NoUpgrade = {file}'

		if entry in lines or '[options]' not in lines:
			return

		# pacman collects every NoUpgrade line, so a new line right below [options] is enough
		lines.insert(lines.index('[options]') + 1, entry)
		pacman_conf.write_text('\n'.join(lines) + '\n')
