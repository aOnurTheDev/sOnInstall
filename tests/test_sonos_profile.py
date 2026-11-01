import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from soninstall.default_profiles.desktops.plasma import PlasmaFlavor, PlasmaProfile
from soninstall.default_profiles.profile import CustomSetting
from soninstall.default_profiles.sonos import FASTFETCH_LOGO, FASTFETCH_LOGO_TARGET, LOGO_ICON, LOGO_ICON_TARGETS, SONOS_PROFILE_NAME, SonosProfile, logo_banner
from soninstall.lib.hardware import SysInfo
from soninstall.lib.installer import Installer
from soninstall.lib.pacman.pacman import Pacman
from soninstall.lib.profile.profiles_handler import profile_handler

ARCH_OS_RELEASE = 'NAME="Arch Linux"\nID=arch\n'


def _session(target: Path) -> Mock:
	return Mock(spec=Installer, target=target, kernels=['linux'])


def test_profile_is_a_desktop_profile_that_round_trips() -> None:
	# The handler loads its own copy of the class, which is what the menu and saved configs use
	profile = profile_handler.get_profile_by_name(SONOS_PROFILE_NAME)
	kde = profile_handler.get_profile_by_name('KDE Plasma')
	assert profile is not None
	assert kde is not None
	assert profile.is_top_level_profile()
	assert profile.is_desktop_profile()

	profile.current_selection = [kde]
	try:
		reloaded = profile_handler.parse_profile_config(profile_handler.to_json(profile))
		assert reloaded is not None
		assert reloaded.name == SONOS_PROFILE_NAME
		assert reloaded.current_selection_names() == ['KDE Plasma']
	finally:
		profile.reset()


def test_packages_leave_audio_and_network_to_the_menus() -> None:
	packages = SonosProfile().packages

	assert 'steam' in packages
	assert 'firefox' in packages
	assert 'xdg-utils' in packages  # from the desktop profile
	assert len(packages) == len(set(packages))

	# Installed through the Applications menu, so a different choice there
	# (e.g. PulseAudio) does not conflict with the profile
	for package in ('pipewire-pulse', 'bluez'):
		assert package not in packages

	# Development tools are picked in the installer
	for package in ('base-devel', 'code', 'rust', 'jdk-openjdk', 'docker', 'arduino-cli'):
		assert package not in packages

	# Packages from the requested tool list that only make sense on the live ISO
	for package in ('archinstall', 'mkinitcpio-archiso', 'nvidia-open', 'broadcom-wl-dkms', 'cloud-init'):
		assert package not in packages


def test_profile_enables_no_services(tmp_path: Path) -> None:
	# Services come from the menus (network, audio, bluetooth), so another choice there
	# never ends up with two network managers or sound servers running
	session = _session(tmp_path)

	with patch.object(Pacman, 'run', return_value=[]):
		SonosProfile().install(session)

	session.enable_service.assert_not_called()


@pytest.mark.parametrize(
	('installed', 'gpus', 'drivers'),
	[
		# Drivers that came with the selected graphics driver
		(b'mesa\nvulkan-radeon\n', (False, False, False), ['vulkan-radeon', 'lib32-vulkan-radeon']),
		(b'nvidia-utils\n', (False, False, True), ['nvidia-utils', 'lib32-nvidia-utils']),
		# No graphics driver selected: detect the GPU
		(b'', (False, False, True), ['vulkan-nouveau', 'lib32-vulkan-nouveau']),
		(b'', (True, True, False), ['vulkan-radeon', 'vulkan-intel', 'lib32-vulkan-radeon', 'lib32-vulkan-intel']),
		(b'', (False, False, False), ['vulkan-swrast', 'lib32-vulkan-swrast']),
	],
)
def test_vulkan_drivers_are_installed_before_steam(
	tmp_path: Path,
	installed: bytes,
	gpus: tuple[bool, bool, bool],
	drivers: list[str],
) -> None:
	amd, intel, nvidia = gpus
	session = _session(tmp_path)

	with (
		patch.object(Pacman, 'run', return_value=installed.splitlines(keepends=True)),
		patch.object(SysInfo, 'has_amd_graphics', return_value=amd),
		patch.object(SysInfo, 'has_intel_graphics', return_value=intel),
		patch.object(SysInfo, 'has_nvidia_graphics', return_value=nvidia),
	):
		SonosProfile().install(session)

	first, *rest = (c.args[0] for c in session.add_additional_packages.call_args_list)
	assert first == [*drivers, 'lib32-mesa', 'linux-headers']
	assert any('steam' in packages for packages in rest)


def test_post_install_branding_survives_updates(tmp_path: Path) -> None:
	(tmp_path / 'usr/lib').mkdir(parents=True)
	(tmp_path / 'usr/lib/os-release').write_text(ARCH_OS_RELEASE)
	(tmp_path / 'etc').mkdir()
	(tmp_path / 'etc/os-release').symlink_to('../usr/lib/os-release')
	(tmp_path / 'etc/lsb-release').write_text('DISTRIB_ID="Arch"\n')
	(tmp_path / 'etc/pacman.conf').write_text('[options]\nHoldPkg = pacman glibc\n\n[core]\nInclude = /etc/pacman.d/mirrorlist\n')

	profile = SonosProfile()
	# Running it twice must not add anything twice
	profile.post_install(_session(tmp_path))
	profile.post_install(_session(tmp_path))

	os_release = tmp_path / 'etc/os-release'
	assert not os_release.is_symlink()
	assert 'ID=sonos\n' in os_release.read_text()
	# The file the filesystem package owns is left alone
	assert (tmp_path / 'usr/lib/os-release').read_text() == ARCH_OS_RELEASE

	assert 'DISTRIB_ID="sOnOs"' in (tmp_path / 'etc/lsb-release').read_text()
	pacman_conf = (tmp_path / 'etc/pacman.conf').read_text().splitlines()
	assert pacman_conf.count('NoUpgrade = etc/lsb-release') == 1
	assert pacman_conf.index('NoUpgrade = etc/lsb-release') == pacman_conf.index('[options]') + 1

	assert (tmp_path / FASTFETCH_LOGO_TARGET).read_text() == FASTFETCH_LOGO.read_text()
	config = json.loads((tmp_path / 'etc/xdg/fastfetch/config.jsonc').read_text())

	# os-release says LOGO=sonos, the icon has to exist or the Arch Linux logo is shown
	assert 'LOGO="sonos"' in os_release.read_text()
	for icon in LOGO_ICON_TARGETS:
		assert (tmp_path / icon).read_bytes() == LOGO_ICON.read_bytes()
	assert (tmp_path / 'etc/issue').read_text().startswith('\\S{PRETTY_NAME}')
	assert config['logo']['source'] == f'/{FASTFETCH_LOGO_TARGET}'
	# Without a module list fastfetch shows only the logo
	assert {'title', 'os', 'kernel', 'cpu', 'memory'} <= set(config['modules'])


def test_fastfetch_logo_colours_on_red() -> None:
	for line in FASTFETCH_LOGO.read_text().splitlines():
		# $1 (red) starts the "On", $2 (white) ends it
		assert line.count('$1') == 1
		assert line.count('$2') == 1
		assert line.index('$1') < line.index('$2')


def test_logo_banner_is_centered() -> None:
	lines = logo_banner(100).splitlines()
	assert len(lines) == len(FASTFETCH_LOGO.read_text().splitlines())

	for line in lines:
		assert '$' not in line
		assert '\x1b[1;31m' in line  # the red "On"
		# 58 columns wide, so 21 spaces on each side
		assert line.startswith(' ' * 21 + '\x1b')

	# A narrow terminal gets no indentation
	assert logo_banner(20).startswith('\x1b')


@pytest.mark.parametrize(
	('lang', 'package'),
	[
		('tr_TR.UTF-8', 'firefox-i18n-tr'),
		('pt_BR.UTF-8', 'firefox-i18n-pt-br'),
		('sr_RS@latin', 'firefox-i18n-sr'),
		('xx_XX.UTF-8', None),
	],
)
def test_firefox_language_pack(tmp_path: Path, lang: str, package: str | None) -> None:
	(tmp_path / 'etc').mkdir()
	(tmp_path / 'etc/locale.conf').write_text(f'LANG={lang}\n')
	available = [b'firefox-i18n-tr\n', b'firefox-i18n-pt-br\n', b'firefox-i18n-pt-pt\n', b'firefox-i18n-sr\n']

	with patch.object(Pacman, 'run', return_value=available):
		assert SonosProfile._firefox_language_pack(tmp_path) == package


def test_no_firefox_language_pack_for_english(tmp_path: Path) -> None:
	(tmp_path / 'etc').mkdir()
	(tmp_path / 'etc/locale.conf').write_text('LANG=en_US.UTF-8\n')

	with patch.object(Pacman, 'run') as run:
		assert SonosProfile._firefox_language_pack(tmp_path) is None
		# No locale.conf at all
		assert SonosProfile._firefox_language_pack(tmp_path / 'missing') is None

	run.assert_not_called()


@pytest.mark.parametrize('flavor', [None, *PlasmaFlavor])
def test_plasma_comes_with_its_applications(flavor: PlasmaFlavor | None) -> None:
	plasma = PlasmaProfile()
	if flavor is not None:
		plasma.custom_settings[CustomSetting.PlasmaFlavor] = flavor.value

	packages = plasma.packages
	assert (flavor or PlasmaFlavor.Meta).value in packages
	for application in ('konsole', 'dolphin', 'kate'):
		assert application in packages


def test_logo_icon_needs_no_fonts() -> None:
	# Qt draws icons without CSS fonts, so the letters are paths
	icon = LOGO_ICON.read_text()
	assert '<path' in icon
	assert '<text' not in icon
	assert '@font-face' not in icon
