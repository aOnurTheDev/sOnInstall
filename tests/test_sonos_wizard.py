import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest

from soninstall.default_profiles.sonos import SONOS_PROFILE_NAME
from soninstall.lib.args import ArchConfig, ArchConfigHandler
from soninstall.lib.global_menu import GlobalMenu
from soninstall.lib.hardware import GfxDriver
from soninstall.lib.menu.helpers import Confirmation
from soninstall.lib.models.application import Audio, DevelopmentConfiguration, DevelopmentTool
from soninstall.lib.models.network import NicType
from soninstall.lib.models.users import Password
from soninstall.lib.profile.profiles_handler import profile_handler
from soninstall.lib.translationhandler import tr, translation_handler
from soninstall.lib.user.user_menu import validate_username
from soninstall.scripts import sonos
from soninstall.tui.result import Result


def _run_wizard(config: ArchConfig, nvidia: bool = False, development: bool = False, language: str = 'en') -> AsyncMock:
	profile = profile_handler.get_profile_by_name(SONOS_PROFILE_NAME)
	kde = profile_handler.get_profile_by_name('KDE Plasma')
	assert profile is not None
	assert kde is not None

	async def pick_kde() -> None:
		profile.current_selection = [kde]

	disk = Mock()
	set_kb_layout = Mock()
	select_kb_layout = AsyncMock(return_value='trq')

	with (
		patch.object(sonos, '_ask_language', AsyncMock(return_value=translation_handler.get_language_by_abbr(language))),
		patch.object(sonos, 'select_kb_layout', select_kb_layout),
		patch.object(sonos, 'set_kb_layout', set_kb_layout),
		patch.object(sonos, '_ask_username', AsyncMock(return_value='onur')),
		# An empty password is asked again
		patch.object(sonos, 'get_password', AsyncMock(side_effect=[None, Password(plaintext='secret')])),
		patch.object(sonos, 'select_timezone', AsyncMock(return_value='Europe/Istanbul')),
		patch.object(profile, 'do_on_select', pick_kde),
		# The NVIDIA question, then the development tools question
		patch.object(Confirmation, 'show', AsyncMock(side_effect=[Result.true() if answer else Result.false() for answer in (nvidia, development)])),
		# The disk is required, skipping asks again
		patch.object(sonos, 'select_disk_config', AsyncMock(side_effect=[None, disk])),
	):
		try:
			asyncio.run(sonos._ask(config))
		finally:
			profile.reset()
			translation_handler.activate(translation_handler.get_language_by_abbr('en'))

	assert config.disk_config is disk
	set_kb_layout.assert_called_once_with('trq')
	return select_kb_layout


@pytest.mark.parametrize(('nvidia', 'driver'), [(True, GfxDriver.NvidiaOpenKernel), (False, GfxDriver.AllOpenSource)])
@pytest.mark.parametrize('development', [True, False])
def test_wizard_asks_only_the_essentials(nvidia: bool, driver: GfxDriver, development: bool) -> None:
	config = ArchConfig()
	# What show_wizard() does before asking
	GlobalMenu(config).sync_all_to_config()

	_run_wizard(config, nvidia, development)

	assert config.locale_config is not None
	assert config.locale_config.kb_layout == 'trq'
	assert config.timezone == 'Europe/Istanbul'

	assert config.auth_config is not None
	(user,) = config.auth_config.users
	assert user.username == 'onur'
	assert user.sudo
	# root gets the same password as the user
	assert config.auth_config.root_enc_password is user.password

	assert config.profile_config is not None
	assert config.profile_config.profile is not None
	assert config.profile_config.profile.name == SONOS_PROFILE_NAME
	assert config.profile_config.gfx_driver == driver
	# The greeter of the chosen desktop
	kde = profile_handler.get_profile_by_name('KDE Plasma')
	assert kde is not None
	assert config.profile_config.greeter == kde.default_greeter_type

	# Everything else comes from the defaults of the full menu
	assert config.hostname == 'sOnOs'
	assert config.bootloader_config is not None
	assert config.network_config is not None
	assert config.network_config.type == NicType.NM
	assert config.app_config is not None
	assert config.app_config.audio_config is not None
	assert config.app_config.audio_config.audio == Audio.PIPEWIRE
	# One question for all development tools, without dropping the other application defaults
	if development:
		assert config.app_config.development_config == DevelopmentConfiguration(tools=list(DevelopmentTool))
	else:
		assert config.app_config.development_config is None
	assert config.app_config.bluetooth_config is not None


def test_sonos_wizard_is_the_default_script() -> None:
	handler = Mock(args=Mock(script=None), config=Mock(script=None))
	assert ArchConfigHandler.get_script(handler) == 'sonos'


@pytest.mark.parametrize(('username', 'valid'), [('onur', True), ('Onur', False), ('1onur', False), ('a' * 33, False)])
def test_validate_username(username: str, valid: bool) -> None:
	assert (validate_username(username) is None) == valid


def test_language_is_asked_first_and_used_for_the_system() -> None:
	config = ArchConfig()
	GlobalMenu(config).sync_all_to_config()

	select_kb_layout = _run_wizard(config, language='tr')

	# The installer continued in Turkish
	assert config.installer_language.abbr == 'tr'
	assert config.locale_config is not None
	assert config.locale_config.sys_lang == 'tr_TR.UTF-8'
	assert config.locale_config.sys_enc == 'UTF-8'
	# Has the Turkish letters
	assert config.locale_config.console_font == 'LatGrkCyr-8x16'
	# The Turkish layout is offered first
	select_kb_layout.assert_awaited_once_with('trq')


def test_installer_text_follows_the_language() -> None:
	try:
		sonos._set_language(ArchConfig(), translation_handler.get_language_by_abbr('tr'))
		# "Step" in Turkish, which has a dotless i
		assert tr('Step {} of {}').format(1, 9) == 'Ad\u0131m 1/9'
	finally:
		translation_handler.activate(translation_handler.get_language_by_abbr('en'))


@pytest.mark.parametrize(('term', 'installer'), [('linux', 'en'), ('xterm-256color', 'ja')])
def test_console_keeps_english_for_scripts_it_cannot_show(monkeypatch: pytest.MonkeyPatch, term: str, installer: str) -> None:
	monkeypatch.setenv('TERM', term)
	config = ArchConfig()
	GlobalMenu(config).sync_all_to_config()
	assert config.locale_config is not None
	# The keymap of the running system
	kb_layout = config.locale_config.kb_layout

	try:
		sonos._set_language(config, translation_handler.get_language_by_abbr('ja'))
	finally:
		translation_handler.activate(translation_handler.get_language_by_abbr('en'))

	assert config.installer_language.abbr == installer
	# The installed system is Japanese either way
	assert config.locale_config is not None
	assert config.locale_config.sys_lang == 'ja_JP.UTF-8'
	# No Latin keymap for it, the default stays
	assert config.locale_config.kb_layout == kb_layout


def test_every_language_has_a_system_locale() -> None:
	languages = sonos._languages()
	assert languages[0].abbr == 'en'
	assert {language.abbr for language in languages} == set(sonos.LANGUAGE_LOCALES)

	supported = Path('/usr/share/i18n/SUPPORTED')
	if supported.exists():
		locales = {line.split()[0] for line in supported.read_text().splitlines() if line.strip()}
		assert set(sonos.LANGUAGE_LOCALES.values()) <= locales


def test_language_labels() -> None:
	assert sonos._language_label(translation_handler.get_language_by_abbr('tr')) == 'Turkish - Türkçe'
	assert sonos._language_label(translation_handler.get_language_by_abbr('en')) == 'English'
	# Its own name cannot be shown on the console
	assert sonos._language_label(translation_handler.get_language_by_abbr('ja')) == 'Japanese'
