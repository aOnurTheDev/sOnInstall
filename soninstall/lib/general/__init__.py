from soninstall.lib.general.general_menu import (
	select_hostname,
	select_installer_language,
	select_ntp,
	select_timezone,
)
from soninstall.lib.general.system_menu import select_driver, select_kernel, select_swap

__all__ = [
	'select_driver',
	'select_hostname',
	'select_installer_language',
	'select_kernel',
	'select_ntp',
	'select_swap',
	'select_timezone',
]
