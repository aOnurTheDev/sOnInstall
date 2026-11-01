from functools import lru_cache

from soninstall.lib.log import debug
from soninstall.lib.packages.packages import check_package_upgrade


@lru_cache(maxsize=128)
def check_version_upgrade() -> str | None:
	debug('Checking version')
	upgrade = None

	upgrade = check_package_upgrade('soninstall')

	if upgrade is None:
		debug('No sOninstall upgrades found')
		return None

	debug(f'sOninstall latest: {upgrade}')

	return upgrade
