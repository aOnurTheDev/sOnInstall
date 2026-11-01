from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Any, NotRequired, Self, TypedDict, override

from soninstall.lib.models.config import SubConfig, SummaryLevel
from soninstall.lib.translationhandler import tr


class PowerManagement(StrEnum):
	POWER_PROFILES_DAEMON = 'power-profiles-daemon'
	TUNED = auto()


class PowerManagementConfigSerialization(TypedDict):
	power_management: str


class BluetoothConfigSerialization(TypedDict):
	enabled: bool


class Audio(StrEnum):
	NO_AUDIO = 'No audio server'
	PIPEWIRE = auto()
	PULSEAUDIO = auto()


class AudioConfigSerialization(TypedDict):
	audio: str


class PrintServiceConfigSerialization(TypedDict):
	enabled: bool


class Firewall(StrEnum):
	UFW = auto()
	FWD = 'firewalld'


class FirewallConfigSerialization(TypedDict):
	firewall: str


class FontPackage(StrEnum):
	NOTO = 'noto-fonts'
	EMOJI = 'noto-fonts-emoji'
	CJK = 'noto-fonts-cjk'
	LIBERATION = 'ttf-liberation'
	DEJAVU = 'ttf-dejavu'

	def description(self) -> str:
		match self:
			case FontPackage.NOTO:
				return tr('Unicode font coverage for most languages')
			case FontPackage.EMOJI:
				return tr('color emoji for browsers and apps')
			case FontPackage.CJK:
				return tr('Chinese, Japanese, Korean characters')
			case FontPackage.LIBERATION:
				return tr('Arial/Times/Courier replacement, Cyrillic support for Steam/games')
			case FontPackage.DEJAVU:
				return tr('wide Unicode coverage, good fallback font')


class DevelopmentTool(StrEnum):
	BUILD_TOOLS = 'C / C++ and build tools'
	VSCODE = 'Visual Studio Code'
	DOCKER = 'Docker'
	EMBEDDED = 'Embedded (Arduino, AVR, STM32)'
	RUST = 'Rust'
	GO = 'Go'
	PYTHON = 'Python'
	JAVA = 'Java'
	JAVASCRIPT = 'JavaScript / TypeScript'
	RUBY = 'Ruby'
	PHP = 'PHP'
	LUA = 'Lua'
	PERL = 'Perl'
	HASKELL = 'Haskell'
	R = 'R'
	ELIXIR = 'Elixir'
	OCAML = 'OCaml'
	FORTRAN = 'Fortran'
	ZIG = 'Zig'
	D = 'D'
	CSHARP_FSHARP = 'C# / F# (.NET)'
	KOTLIN = 'Kotlin'
	DART = 'Dart'
	JULIA = 'Julia'
	ERLANG = 'Erlang'
	CLOJURE = 'Clojure'
	COMMON_LISP = 'Common Lisp'
	SCHEME = 'Scheme'
	PROLOG = 'Prolog'
	NIM = 'Nim'
	CRYSTAL = 'Crystal'
	VALA = 'Vala'
	GROOVY = 'Groovy'
	ASSEMBLY = 'Assembly'

	def packages(self) -> list[str]:
		match self:
			case DevelopmentTool.BUILD_TOOLS:
				return [
					'base-devel',
					'gcc',
					'clang',
					'lld',
					'lldb',
					'gdb',
					'make',
					'cmake',
					'ninja',
					'autoconf',
					'automake',
					'bison',
					'flex',
					'pkgconf',
					'valgrind',
					'doxygen',
				]
			case DevelopmentTool.VSCODE:
				return ['code']
			case DevelopmentTool.DOCKER:
				return ['docker', 'docker-compose']
			case DevelopmentTool.EMBEDDED:
				return ['arduino-cli', 'avr-libc', 'avrdude', 'dfu-util', 'minicom', 'openocd', 'picocom', 'stlink']
			case DevelopmentTool.RUST:
				return ['rust']
			case DevelopmentTool.GO:
				return ['go']
			case DevelopmentTool.PYTHON:
				return ['python', 'python-pip', 'python-poetry']
			case DevelopmentTool.JAVA:
				return ['jdk-openjdk', 'maven', 'gradle']
			case DevelopmentTool.JAVASCRIPT:
				return ['nodejs', 'npm', 'pnpm', 'typescript', 'deno']
			case DevelopmentTool.RUBY:
				return ['ruby', 'rubygems']
			case DevelopmentTool.PHP:
				return ['php', 'composer']
			case DevelopmentTool.LUA:
				return ['lua', 'luajit', 'luarocks']
			case DevelopmentTool.PERL:
				return ['perl']
			case DevelopmentTool.HASKELL:
				return ['ghc', 'cabal-install']
			case DevelopmentTool.R:
				return ['r']
			case DevelopmentTool.ELIXIR:
				return ['elixir']
			case DevelopmentTool.OCAML:
				return ['ocaml', 'opam']
			case DevelopmentTool.FORTRAN:
				return ['gcc-fortran']
			case DevelopmentTool.ZIG:
				return ['zig']
			case DevelopmentTool.D:
				return ['ldc']
			case DevelopmentTool.CSHARP_FSHARP:
				return ['dotnet-sdk']
			case DevelopmentTool.KOTLIN:
				return ['kotlin']
			case DevelopmentTool.DART:
				return ['dart']
			case DevelopmentTool.JULIA:
				return ['julia']
			case DevelopmentTool.ERLANG:
				return ['erlang']
			case DevelopmentTool.CLOJURE:
				return ['clojure']
			case DevelopmentTool.COMMON_LISP:
				return ['sbcl']
			case DevelopmentTool.SCHEME:
				return ['guile']
			case DevelopmentTool.PROLOG:
				return ['swi-prolog']
			case DevelopmentTool.NIM:
				return ['nim']
			case DevelopmentTool.CRYSTAL:
				return ['crystal']
			case DevelopmentTool.VALA:
				return ['vala']
			case DevelopmentTool.GROOVY:
				return ['groovy']
			case DevelopmentTool.ASSEMBLY:
				return ['nasm', 'yasm']

	def packages_text(self) -> str:
		text = tr('Installed packages') + ':\n'

		for package in self.packages():
			text += f'    - {package}\n'

		return text


class DevelopmentConfigSerialization(TypedDict):
	tools: list[str]


class FontsConfigSerialization(TypedDict):
	fonts: list[str]


class ZramAlgorithm(StrEnum):
	ZSTD = auto()
	LZO_RLE = 'lzo-rle'
	LZO = auto()
	LZ4 = auto()
	LZ4HC = auto()


class ApplicationSerialization(TypedDict):
	bluetooth_config: NotRequired[BluetoothConfigSerialization]
	audio_config: NotRequired[AudioConfigSerialization]
	power_management_config: NotRequired[PowerManagementConfigSerialization]
	print_service_config: NotRequired[PrintServiceConfigSerialization]
	firewall_config: NotRequired[FirewallConfigSerialization]
	fonts_config: NotRequired[FontsConfigSerialization]
	development_config: NotRequired[DevelopmentConfigSerialization]


@dataclass
class AudioConfiguration(SubConfig):
	audio: Audio

	NAME: str = tr('Audio')

	@override
	def json(self) -> AudioConfigSerialization:
		return {
			'audio': self.audio.value,
		}

	@override
	def summary(self, _level: SummaryLevel = SummaryLevel.BASIC) -> list[str]:
		return [self.audio.value]

	@classmethod
	def parse_arg(cls, arg: dict[str, Any]) -> Self:
		return cls(
			Audio(arg['audio']),
		)


@dataclass
class BluetoothConfiguration(SubConfig):
	enabled: bool

	NAME: str = tr('Bluetooth')

	@override
	def json(self) -> BluetoothConfigSerialization:
		return {'enabled': self.enabled}

	@override
	def summary(self, _level: SummaryLevel = SummaryLevel.BASIC) -> list[str]:
		if self.enabled:
			return [tr('enabled')]
		return []

	@classmethod
	def parse_arg(cls, arg: BluetoothConfigSerialization) -> Self:
		return cls(arg['enabled'])


@dataclass
class PowerManagementConfiguration(SubConfig):
	power_management: PowerManagement

	NAME: str = tr('Power management')

	@override
	def json(self) -> PowerManagementConfigSerialization:
		return {
			'power_management': self.power_management.value,
		}

	@override
	def summary(self, _level: SummaryLevel = SummaryLevel.BASIC) -> list[str]:
		return [self.power_management.value]

	@classmethod
	def parse_arg(cls, arg: PowerManagementConfigSerialization) -> Self:
		return cls(
			PowerManagement(arg['power_management']),
		)


@dataclass
class PrintServiceConfiguration(SubConfig):
	enabled: bool

	NAME: str = tr('Print service')

	@override
	def json(self) -> PrintServiceConfigSerialization:
		return {'enabled': self.enabled}

	@override
	def summary(self, _level: SummaryLevel = SummaryLevel.BASIC) -> list[str]:
		if self.enabled:
			return [tr('enabled')]
		return []

	@classmethod
	def parse_arg(cls, arg: PrintServiceConfigSerialization) -> Self:
		return cls(arg['enabled'])


@dataclass
class FirewallConfiguration(SubConfig):
	firewall: Firewall

	NAME: str = tr('Firewall')

	@override
	def json(self) -> FirewallConfigSerialization:
		return {
			'firewall': self.firewall.value,
		}

	@override
	def summary(self, _level: SummaryLevel = SummaryLevel.BASIC) -> list[str]:
		return [self.firewall.value]

	@classmethod
	def parse_arg(cls, arg: dict[str, Any]) -> Self:
		return cls(
			Firewall(arg['firewall']),
		)


@dataclass
class FontsConfiguration(SubConfig):
	fonts: list[FontPackage]

	NAME: str = tr('Fonts')

	@override
	def json(self) -> FontsConfigSerialization:
		return {'fonts': [f.value for f in self.fonts]}

	@override
	def summary(self, _level: SummaryLevel = SummaryLevel.BASIC) -> list[str]:
		if self.fonts:
			return [', '.join(f.value for f in self.fonts)]
		return []

	@classmethod
	def parse_arg(cls, arg: FontsConfigSerialization) -> Self:
		return cls(fonts=[FontPackage(f) for f in arg['fonts']])


@dataclass
class DevelopmentConfiguration(SubConfig):
	tools: list[DevelopmentTool]

	NAME: str = tr('Development tools')

	def packages(self) -> list[str]:
		return list(dict.fromkeys(package for tool in self.tools for package in tool.packages()))

	@override
	def json(self) -> DevelopmentConfigSerialization:
		return {'tools': [t.value for t in self.tools]}

	@override
	def summary(self, _level: SummaryLevel = SummaryLevel.BASIC) -> list[str]:
		if self.tools:
			return [', '.join(t.value for t in self.tools)]
		return []

	@classmethod
	def parse_arg(cls, arg: DevelopmentConfigSerialization) -> Self:
		return cls(tools=[DevelopmentTool(t) for t in arg['tools']])


@dataclass(frozen=True)
class ZramConfiguration(SubConfig):
	enabled: bool
	algorithm: ZramAlgorithm = ZramAlgorithm.ZSTD

	NAME: str = tr('Zram')

	@classmethod
	def parse_arg(cls, arg: bool | dict[str, Any]) -> Self:
		if isinstance(arg, bool):
			return cls(enabled=arg)

		enabled = arg.get('enabled', True)
		algo = arg.get('algorithm', arg.get('algo', ZramAlgorithm.ZSTD.value))
		return cls(enabled=enabled, algorithm=ZramAlgorithm(algo))

	@override
	def json(self) -> dict[str, bool | str]:
		return {
			'enabled': self.enabled,
			'algorithm': self.algorithm.value,
		}

	@override
	def summary(self, _level: SummaryLevel = SummaryLevel.BASIC) -> list[str]:
		if self.enabled:
			return [
				tr('enabled'),
				tr('Algorithm "{}"').format(self.algorithm),
			]

		return [tr('Zram disabled')]


@dataclass
class ApplicationConfiguration(SubConfig):
	bluetooth_config: BluetoothConfiguration | None = None
	audio_config: AudioConfiguration | None = None
	power_management_config: PowerManagementConfiguration | None = None
	print_service_config: PrintServiceConfiguration | None = None
	firewall_config: FirewallConfiguration | None = None
	fonts_config: FontsConfiguration | None = None
	development_config: DevelopmentConfiguration | None = None

	NAME: str = tr('Application')

	@classmethod
	def parse_arg(
		cls,
		args: dict[str, Any] | None = None,
		old_audio_config: dict[str, Any] | None = None,
	) -> Self:
		app_config = cls()

		if args and (bluetooth_config := args.get('bluetooth_config')) is not None:
			app_config.bluetooth_config = BluetoothConfiguration.parse_arg(bluetooth_config)

		# deprecated: backwards compatibility
		if old_audio_config is not None:
			app_config.audio_config = AudioConfiguration.parse_arg(old_audio_config)

		if args and (audio_config := args.get('audio_config')) is not None:
			app_config.audio_config = AudioConfiguration.parse_arg(audio_config)

		if args and (power_management_config := args.get('power_management_config')) is not None:
			app_config.power_management_config = PowerManagementConfiguration.parse_arg(power_management_config)

		if args and (print_service_config := args.get('print_service_config')) is not None:
			app_config.print_service_config = PrintServiceConfiguration.parse_arg(print_service_config)

		if args and (firewall_config := args.get('firewall_config')) is not None:
			app_config.firewall_config = FirewallConfiguration.parse_arg(firewall_config)

		if args and (fonts_config := args.get('fonts_config')) is not None:
			app_config.fonts_config = FontsConfiguration.parse_arg(fonts_config)

		if args and (development_config := args.get('development_config')) is not None:
			app_config.development_config = DevelopmentConfiguration.parse_arg(development_config)

		return app_config

	@override
	def json(self) -> ApplicationSerialization:
		config: ApplicationSerialization = {}

		if self.bluetooth_config:
			config['bluetooth_config'] = self.bluetooth_config.json()

		if self.audio_config:
			config['audio_config'] = self.audio_config.json()

		if self.power_management_config:
			config['power_management_config'] = self.power_management_config.json()

		if self.print_service_config:
			config['print_service_config'] = self.print_service_config.json()

		if self.firewall_config:
			config['firewall_config'] = self.firewall_config.json()

		if self.fonts_config:
			config['fonts_config'] = self.fonts_config.json()

		if self.development_config:
			config['development_config'] = self.development_config.json()

		return config

	@override
	def summary(self, level: SummaryLevel = SummaryLevel.BASIC) -> list[str]:
		configs = [
			self.bluetooth_config,
			self.audio_config,
			self.power_management_config,
			self.print_service_config,
			self.firewall_config,
			self.fonts_config,
			self.development_config,
		]

		out: list[str] = []

		for config in configs:
			if config:
				summary = config.summary(level)
				if len(summary) == 1:
					out.append(f'{config.NAME} "{summary[0]}"')
				else:
					out.append('?????')

		return out
