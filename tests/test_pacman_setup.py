from pathlib import Path
from unittest.mock import Mock, patch

from soninstall.lib.installer import Installer
from soninstall.lib.models.pacman import PacmanConfiguration
from soninstall.lib.pacman.config import PacmanConfig


def test_clean_package_cache_removes_downloaded_packages(tmp_path: Path) -> None:
	cache = tmp_path / 'var/cache/pacman/pkg'
	cache.mkdir(parents=True)
	(cache / 'steam-1.0.0.87-3-x86_64.pkg.tar.zst').write_bytes(b'x' * 10)
	(cache / 'steam-1.0.0.87-3-x86_64.pkg.tar.zst.sig').write_bytes(b'x')
	# Directories (e.g. pacman's download-* leftovers) are not touched
	(cache / 'download-abc').mkdir()

	Installer.clean_package_cache(Mock(spec=Installer, target=tmp_path))

	assert [p.name for p in cache.iterdir()] == ['download-abc']


def test_clean_package_cache_without_cache_dir(tmp_path: Path) -> None:
	Installer.clean_package_cache(Mock(spec=Installer, target=tmp_path))


def test_parallel_downloads_applied_to_host(tmp_path: Path) -> None:
	host_conf = tmp_path / 'pacman.conf'
	host_conf.write_text('[options]\n#Color\nParallelDownloads = 5\n')

	with patch('soninstall.lib.pacman.config.PACMAN_CONF', host_conf):
		PacmanConfig(None).configure(PacmanConfiguration(parallel_downloads=10, color=True), on_host=True)

	assert host_conf.read_text().splitlines() == ['[options]', 'Color', 'ParallelDownloads = 10']


def test_initramfs_is_built_once_at_the_end(tmp_path: Path) -> None:
	mask = tmp_path / 'hooks/90-mkinitcpio-install.hook'
	installer = Mock(spec=Installer, _initramfs_hook_masked=False)
	installer.mkinitcpio.return_value = True
	installer._unmask_initramfs_hook = lambda: Installer._unmask_initramfs_hook(installer)

	with (
		patch('soninstall.lib.installer._INITRAMFS_HOOK_MASK', mask),
		patch('soninstall.lib.installer.running_from_iso', return_value=True),
	):
		Installer.defer_initramfs_builds(installer)
		assert mask.is_symlink()
		assert str(mask.readlink()) == '/dev/null'

		Installer.build_deferred_initramfs(installer)

	assert not mask.is_symlink()
	installer.mkinitcpio.assert_called_once_with(['-P'])


def test_initramfs_hook_left_alone_outside_the_iso(tmp_path: Path) -> None:
	mask = tmp_path / 'hooks/90-mkinitcpio-install.hook'
	installer = Mock(spec=Installer, _initramfs_hook_masked=False)

	with (
		patch('soninstall.lib.installer._INITRAMFS_HOOK_MASK', mask),
		patch('soninstall.lib.installer.running_from_iso', return_value=False),
	):
		Installer.defer_initramfs_builds(installer)

	assert not mask.is_symlink()
