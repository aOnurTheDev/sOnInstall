from importlib.metadata import PackageNotFoundError, version

# Name of the distribution in pyproject.toml
DISTRIBUTION_NAME = 'soninstall'


def get_version() -> str:
	try:
		return version(DISTRIBUTION_NAME)
	except PackageNotFoundError:
		return 'sOninstall version not found'
