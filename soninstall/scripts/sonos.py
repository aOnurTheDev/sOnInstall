import os

from soninstall.default_profiles.sonos import SONOS_PROFILE_NAME
from soninstall.lib.args import ArchConfig, ArchConfigHandler
from soninstall.lib.disk.disk_menu import select_disk_config
from soninstall.lib.general.general_menu import select_timezone
from soninstall.lib.global_menu import GlobalMenu
from soninstall.lib.hardware import GfxDriver, SysInfo
from soninstall.lib.locale.locale_menu import select_kb_layout
from soninstall.lib.locale.utils import set_kb_layout
from soninstall.lib.menu.helpers import Confirmation, Input, Selection
from soninstall.lib.menu.util import get_password
from soninstall.lib.mirror.mirror_handler import MirrorListHandler
from soninstall.lib.models.application import ApplicationConfiguration, DevelopmentConfiguration, DevelopmentTool
from soninstall.lib.models.authentication import AuthenticationConfiguration
from soninstall.lib.models.profile import ProfileConfiguration
from soninstall.lib.models.users import User
from soninstall.lib.profile.profiles_handler import profile_handler
from soninstall.lib.translationhandler import Language, tr, translation_handler
from soninstall.lib.user.user_menu import validate_username
from soninstall.scripts import guided
from soninstall.tui.components import tui
from soninstall.tui.menu_item import MenuItem, MenuItemGroup
from soninstall.tui.result import ResultType

STEPS = 9

# The system locale for each language of the installer
LANGUAGE_LOCALES = {
	'ar': 'ar_EG.UTF-8',
	'ca': 'ca_ES.UTF-8',
	'cs': 'cs_CZ.UTF-8',
	'da': 'da_DK.UTF-8',
	'de': 'de_DE.UTF-8',
	'el': 'el_GR.UTF-8',
	'en': 'en_US.UTF-8',
	'es': 'es_ES.UTF-8',
	'et': 'et_EE.UTF-8',
	'fi': 'fi_FI.UTF-8',
	'fr': 'fr_FR.UTF-8',
	'ga': 'ga_IE.UTF-8',
	'gl': 'gl_ES.UTF-8',
	'he': 'he_IL.UTF-8',
	'hi': 'hi_IN',
	'hu': 'hu_HU.UTF-8',
	'id': 'id_ID.UTF-8',
	'it': 'it_IT.UTF-8',
	'ja': 'ja_JP.UTF-8',
	'ka': 'ka_GE.UTF-8',
	'ko': 'ko_KR.UTF-8',
	'ku': 'ku_TR.UTF-8',
	'lt': 'lt_LT.UTF-8',
	'nb': 'nb_NO.UTF-8',
	'ne': 'ne_NP',
	'nl': 'nl_NL.UTF-8',
	'pl': 'pl_PL.UTF-8',
	'pt': 'pt_PT.UTF-8',
	'pt_BR': 'pt_BR.UTF-8',
	'ro': 'ro_RO.UTF-8',
	'ru': 'ru_RU.UTF-8',
	# The translation is written in the Latin alphabet
	'sr': 'sr_RS@latin',
	'sv': 'sv_SE.UTF-8',
	'ta': 'ta_IN',
	'tr': 'tr_TR.UTF-8',
	'uk': 'uk_UA.UTF-8',
	'ur': 'ur_PK',
	'uz': 'uz_UZ.UTF-8',
	'vi': 'vi_VN',
	'zh-CN': 'zh_CN.UTF-8',
	'zh-TW': 'zh_TW.UTF-8',
}

# Preselected console keymaps. Only for languages written in the Latin alphabet,
# as the username has to be typed in it right after.
LANGUAGE_KEYMAPS = {
	'cs': 'cz',
	'da': 'dk',
	'de': 'de-latin1',
	'es': 'es',
	'et': 'et',
	'fi': 'fi',
	'fr': 'fr-latin1',
	'hu': 'hu',
	'it': 'it',
	'lt': 'lt',
	'nb': 'no',
	'nl': 'nl',
	'pl': 'pl',
	'pt': 'pt-latin1',
	'pt_BR': 'br-abnt2',
	'ro': 'ro',
	'sv': 'sv-latin1',
	'tr': 'trq',
}

# No Linux console font has these scripts, so on the console the installer stays in English.
# The installed system still gets the language.
CONSOLE_UNSUPPORTED = frozenset({'ar', 'he', 'hi', 'ja', 'ka', 'ko', 'ne', 'ta', 'ur', 'vi', 'zh-CN', 'zh-TW'})

# Latin, Greek and Cyrillic, including the Turkish letters that default8x16 lacks
CONSOLE_FONT = 'LatGrkCyr-8x16'


def _step(number: int) -> None:
	tui.step = tr('Step {} of {}').format(number, STEPS)


def _languages() -> list[Language]:
	"""English first, then the rest alphabetically"""
	return sorted(translation_handler.translated_languages, key=lambda lang: (lang.abbr != 'en', lang.name_en))


def _language_label(language: Language) -> str:
	native = language.translated_lang

	if native and native != language.name_en and language.abbr not in CONSOLE_UNSUPPORTED:
		return f'{language.name_en} - {native}'

	return language.name_en


async def _ask_language(preset: Language) -> Language:
	group = MenuItemGroup([MenuItem(_language_label(lang), value=lang) for lang in _languages()])
	group.set_focus_by_value(preset)

	result = await Selection[Language](
		group,
		header=tr('Select your language'),
		allow_skip=False,
		enable_filter=True,
	).show()

	return result.get_value()


def _set_language(config: ArchConfig, language: Language) -> None:
	installer_language = language

	if language.abbr in CONSOLE_UNSUPPORTED and os.environ.get('TERM') == 'linux':
		installer_language = translation_handler.get_language_by_abbr('en')

	config.installer_language = installer_language
	translation_handler.activate(installer_language)
	tui.translate_bindings()

	if locale_config := config.locale_config:
		locale_config.sys_lang = LANGUAGE_LOCALES.get(language.abbr, locale_config.sys_lang)
		locale_config.sys_enc = 'UTF-8'
		locale_config.console_font = CONSOLE_FONT
		locale_config.kb_layout = LANGUAGE_KEYMAPS.get(language.abbr, locale_config.kb_layout)


async def _ask_username(preset: str | None) -> str:
	while True:
		result = await Input(
			tr('Enter a username'),
			default_value=preset,
			allow_skip=False,
			validator_callback=validate_username,
		).show()

		if result.type_ == ResultType.Selection and (username := result.get_value()):
			return username


async def _ask(config: ArchConfig) -> ArchConfig:
	"""Ask only what has no sensible default; everything else keeps the defaults of the full menu."""
	# Everything after this is shown in the chosen language
	_step(1)
	_set_language(config, await _ask_language(config.installer_language))

	# Before the username and password, so they are typed with the right layout
	_step(2)
	if locale_config := config.locale_config:
		if kb_layout := await select_kb_layout(locale_config.kb_layout):
			locale_config.kb_layout = kb_layout
			set_kb_layout(kb_layout)

	_step(3)
	users = config.auth_config.users if config.auth_config else []
	username = await _ask_username(users[0].username if users else None)

	_step(4)
	password = None
	while password is None:
		password = await get_password(tr('Enter a password for "{}", it is also used for root').format(username))

	config.auth_config = AuthenticationConfiguration(
		root_enc_password=password,
		users=[User(username, password, sudo=True)],
	)

	_step(5)
	config.timezone = await select_timezone(config.timezone) or config.timezone

	_step(6)
	profile = profile_handler.get_profile_by_name(SONOS_PROFILE_NAME)
	if profile:
		await profile.do_on_select()

	_step(7)
	nvidia = await Confirmation(
		header=tr('Install the NVIDIA driver? It supports GeForce GTX 16xx, RTX 20xx and newer cards.') + '\n',
		allow_skip=False,
		preset=SysInfo.has_nvidia_graphics(),
	).show()

	config.profile_config = ProfileConfiguration(
		profile=profile,
		gfx_driver=GfxDriver.NvidiaOpenKernel if nvidia.get_value() else GfxDriver.AllOpenSource,
		greeter=profile.default_greeter_type if profile else None,
	)

	_step(8)
	development = await Confirmation(
		header=tr('Install the development tools? Compilers, Visual Studio Code, Docker and all programming languages, about 10 GB.') + '\n',
		allow_skip=False,
		preset=False,
	).show()

	app_config = config.app_config or ApplicationConfiguration()
	app_config.development_config = DevelopmentConfiguration(tools=list(DevelopmentTool)) if development.get_value() else None
	config.app_config = app_config

	_step(9)
	disk_config = None
	while disk_config is None:
		disk_config = await select_disk_config(config.disk_config)
	config.disk_config = disk_config
	tui.step = None

	# tui.run() treats a None result as the user quitting
	return config


def show_wizard(arch_config_handler: ArchConfigHandler, mirror_list_handler: MirrorListHandler) -> None:
	config = arch_config_handler.config

	# Fill in the defaults of the full menu (bootloader, network, audio, swap, ...)
	GlobalMenu(config, mirror_list_handler, arch_config_handler.args.skip_boot).sync_all_to_config()

	tui.run(lambda: _ask(config))


def main(arch_config_handler: ArchConfigHandler | None = None) -> None:
	guided.main(arch_config_handler, menu=show_wizard)
