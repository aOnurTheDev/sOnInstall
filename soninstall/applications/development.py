from typing import TYPE_CHECKING

from soninstall.lib.log import debug
from soninstall.lib.models.application import DevelopmentConfiguration

if TYPE_CHECKING:
	from soninstall.lib.installer import Installer


class DevelopmentApp:
	def install(self, install_session: Installer, development_config: DevelopmentConfiguration) -> None:
		packages = development_config.packages()
		debug(f'Installing development tools: {packages}')
		install_session.add_additional_packages(packages)
