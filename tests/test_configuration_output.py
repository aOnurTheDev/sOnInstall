import json
from pathlib import Path

from pytest import MonkeyPatch

from soninstall.lib.args import USER_CONFIG_FILE, USER_CREDS_FILE, ArchConfigHandler
from soninstall.lib.models.application import ApplicationConfiguration, DevelopmentConfiguration, DevelopmentTool


def test_development_tools() -> None:
	packages = [package for tool in DevelopmentTool for package in tool.packages()]
	assert 'gcc' in packages
	assert 'rust' in packages
	assert 'code' in packages
	assert 'gamemode' not in packages
	# Not in the Arch repos; including them would make pacstrap fail
	assert 'scala' not in packages
	assert 'swift' not in packages

	config = DevelopmentConfiguration(tools=[DevelopmentTool.BUILD_TOOLS, DevelopmentTool.RUST])
	# gcc is in both groups, but installed once
	assert config.packages().count('gcc') == 1

	app_config = ApplicationConfiguration(development_config=config)
	assert app_config.json() == {'development_config': {'tools': ['C / C++ and build tools', 'Rust']}}
	assert ApplicationConfiguration.parse_arg(json.loads(json.dumps(app_config.json()))) == app_config

	# Keys of an older version are ignored
	assert (
		ApplicationConfiguration.parse_arg(
			{
				'developer_tools': True,
				'game_mode': True,
				'programming_languages': ['Rust'],
			}
		).json()
		== {}
	)


def test_user_config_roundtrip(
	monkeypatch: MonkeyPatch,
	config_fixture: Path,
) -> None:
	monkeypatch.setattr('sys.argv', ['soninstall', '--config', str(config_fixture)])

	handler = ArchConfigHandler()
	arch_config = handler.config

	# the version is retrieved dynamically from an installed soninstall package
	# as there is no version present in the test environment we'll set it manually
	arch_config.version = '3.0.2'

	test_out_dir = Path('/tmp/')
	test_out_file = test_out_dir / USER_CONFIG_FILE

	arch_config.save(test_out_dir)

	result = json.loads(test_out_file.read_text())
	expected = json.loads(config_fixture.read_text())

	# the parsed config will check if the given device exists otherwise
	# it will ignore the modification; as this test will run on various local systems
	# and the CI pipeline there's no good way specify a real device so we'll simply
	# copy the expected result to the actual result
	result['disk_config']['config_type'] = expected['disk_config']['config_type']
	result['disk_config']['device_modifications'] = expected['disk_config']['device_modifications']

	assert json.dumps(result, sort_keys=True) == json.dumps(expected, sort_keys=True)


def test_creds_roundtrip(
	monkeypatch: MonkeyPatch,
	creds_fixture: Path,
) -> None:
	monkeypatch.setattr('sys.argv', ['soninstall', '--creds', str(creds_fixture)])

	handler = ArchConfigHandler()
	arch_config = handler.config

	test_out_dir = Path('/tmp/')
	test_out_file = test_out_dir / USER_CREDS_FILE

	arch_config.save(test_out_dir, creds=True)

	result = json.loads(test_out_file.read_text())
	expected = json.loads(creds_fixture.read_text())

	assert sorted(result.items()) == sorted(expected.items())
