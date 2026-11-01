import os
import shutil
import sys
import time
from collections.abc import Callable

from soninstall.default_profiles.sonos import SONOS_PROFILE_NAME, logo_banner
from soninstall.lib.applications.application_handler import ApplicationHandler
from soninstall.lib.args import ArchConfig, ArchConfigHandler
from soninstall.lib.authentication.authentication_handler import AuthenticationHandler
from soninstall.lib.bootloader.utils import validate_bootloader_layout
from soninstall.lib.configuration import confirm_config
from soninstall.lib.disk.filesystem import FilesystemHandler
from soninstall.lib.disk.utils import disk_layouts
from soninstall.lib.general.general_menu import PostInstallationAction, select_post_installation
from soninstall.lib.global_menu import GlobalMenu
from soninstall.lib.installer import Installer, accessibility_tools_in_use, run_custom_user_commands
from soninstall.lib.log import debug, error, info
from soninstall.lib.menu.util import delayed_warning
from soninstall.lib.mirror.mirror_handler import MirrorListHandler
from soninstall.lib.models import Bootloader
from soninstall.lib.models.device import DiskLayoutType, EncryptionType
from soninstall.lib.models.packages import Repository
from soninstall.lib.models.users import User
from soninstall.lib.network.network_handler import install_network_config
from soninstall.lib.packages.util import check_version_upgrade
from soninstall.lib.profile.profiles_handler import profile_handler
from soninstall.lib.translationhandler import tr
from soninstall.tui.components import tui


def show_menu(
	arch_config_handler: ArchConfigHandler,
	mirror_list_handler: MirrorListHandler,
) -> None:
	upgrade = check_version_upgrade()
	title_text = 'sOninstall'

	if upgrade:
		text = tr('New version available') + f': {upgrade}'
		title_text += f' ({text})'

	global_menu = GlobalMenu(
		arch_config_handler.config,
		mirror_list_handler,
		arch_config_handler.args.skip_boot,
		advanced=arch_config_handler.args.advanced,
		title=title_text,
	)

	result: ArchConfig | None = tui.run(global_menu)
	if result is None:
		sys.exit(0)


def perform_installation(
	arch_config_handler: ArchConfigHandler,
	mirror_list_handler: MirrorListHandler,
	auth_handler: AuthenticationHandler,
	application_handler: ApplicationHandler,
) -> None:
	"""
	Performs the installation steps on a block device.
	Only requirement is that the block devices are
	formatted and setup prior to entering this function.
	"""
	start_time = time.monotonic()
	info('Starting installation...')

	mountpoint = arch_config_handler.args.mountpoint
	config = arch_config_handler.config

	if not config.disk_config:
		error('No disk configuration provided')
		return

	disk_config = config.disk_config
	run_mkinitcpio = not config.bootloader_config or not config.bootloader_config.uki
	locale_config = config.locale_config
	optional_repositories = list(config.mirror_config.optional_repositories) if config.mirror_config else []
	# Compare by name: the profile handler loads its own copy of the profile class,
	# so isinstance() does not match profiles picked in the menu.
	is_sonos = bool(config.profile_config and config.profile_config.profile and config.profile_config.profile.name == SONOS_PROFILE_NAME)
	# Steam needs multilib
	if is_sonos and Repository.Multilib not in optional_repositories:
		optional_repositories.append(Repository.Multilib)
	mountpoint = disk_config.mountpoint if disk_config.mountpoint else mountpoint

	if is_sonos:
		print(f'\n{logo_banner(shutil.get_terminal_size().columns)}\n')

	with Installer(
		mountpoint,
		disk_config,
		kernels=config.kernels,
		firmware=config.firmware_optdeps,
		silent=arch_config_handler.args.silent,
		os_name=SONOS_PROFILE_NAME if is_sonos else 'Arch Linux',
	) as installation:
		# Mount all the drives to the desired mountpoint
		if disk_config.config_type != DiskLayoutType.Pre_mount:
			installation.mount_ordered_layout()

		installation.sanity_check(
			arch_config_handler.args.skip_ntp,
			arch_config_handler.args.skip_wkd,
		)

		if disk_config.config_type != DiskLayoutType.Pre_mount:
			if disk_config.disk_encryption and disk_config.disk_encryption.encryption_type != EncryptionType.NO_ENCRYPTION:
				# generate encryption key files for the mounted luks devices
				installation.generate_key_files()

		if mirror_config := config.mirror_config:
			installation.set_mirrors(mirror_list_handler, mirror_config, on_target=False)

		installation.minimal_installation(
			optional_repositories=optional_repositories,
			mkinitcpio=run_mkinitcpio,
			hostname=arch_config_handler.config.hostname,
			locale_config=locale_config,
			pacman_config=config.pacman_config,
		)

		# Only after the base system: the mkinitcpio hook also sets up the kernel (presets,
		# /boot/vmlinuz-*) when it is installed, the later runs only rebuild the images
		installation.defer_initramfs_builds()

		if mirror_config := config.mirror_config:
			installation.set_mirrors(mirror_list_handler, mirror_config, on_target=True)

		if config.swap and config.swap.enabled:
			installation.setup_swap(algo=config.swap.algorithm)

		if config.bootloader_config and config.bootloader_config.bootloader != Bootloader.NO_BOOTLOADER:
			installation.add_bootloader(
				config.bootloader_config.bootloader,
				config.bootloader_config.uki,
				config.bootloader_config.removable,
				config.bootloader_config.plymouth,
			)

		if config.network_config:
			install_network_config(
				config.network_config,
				installation,
				config.profile_config,
			)

		users = None
		if config.auth_config:
			if config.auth_config.users:
				users = config.auth_config.users
				installation.create_users(config.auth_config.users)
				auth_handler.setup_auth(installation, config.auth_config, config.hostname)

		if app_config := config.app_config:
			application_handler.install_applications(installation, app_config)

		if profile_config := config.profile_config:
			profile_handler.install_profile_config(installation, profile_config)

		if config.packages and config.packages[0] != '':
			installation.add_additional_packages(config.packages)

		if timezone := config.timezone:
			installation.set_timezone(timezone)

		if config.ntp:
			installation.activate_time_synchronization()

		if accessibility_tools_in_use():
			installation.enable_espeakup()

		if config.auth_config and config.auth_config.root_enc_password:
			root_user = User('root', config.auth_config.root_enc_password, False)
			installation.set_user_password(root_user)

		if (profile_config := config.profile_config) and profile_config.profile:
			profile_config.profile.post_install(installation)

			if users:
				profile_config.profile.provision(installation, users)

		# If the user provided a list of services to be enabled, pass the list to the enable_service function.
		# Note that while it's called enable_service, it can actually take a list of services and iterate it.
		if services := config.services:
			installation.enable_service(services)

		if disk_config.has_default_btrfs_vols():
			btrfs_options = disk_config.btrfs_options
			snapshot_config = btrfs_options.snapshot_config if btrfs_options else None
			snapshot_type = snapshot_config.snapshot_type if snapshot_config else None
			if snapshot_type:
				bootloader = config.bootloader_config.bootloader if config.bootloader_config else None
				installation.setup_btrfs_snapshot(snapshot_type, bootloader)

		# If the user provided custom commands to be run post-installation, execute them now.
		if cc := config.custom_commands:
			run_custom_user_commands(cc, installation)

		# Also picks up the sOnOs branding, which unified kernel images embed
		installation.build_deferred_initramfs()
		installation.clean_package_cache()

		installation.genfstab()

		debug(f'Disk states after installing:\n{disk_layouts()}')

		if not arch_config_handler.args.silent:
			elapsed_time = time.monotonic() - start_time
			action: PostInstallationAction = tui.run(lambda: select_post_installation(elapsed_time))

			match action:
				case PostInstallationAction.EXIT:
					pass
				case PostInstallationAction.REBOOT:
					os.system('reboot')
				case PostInstallationAction.CHROOT:
					try:
						installation.drop_to_shell()
					except Exception:
						pass


def main(
	arch_config_handler: ArchConfigHandler | None = None,
	menu: Callable[[ArchConfigHandler, MirrorListHandler], None] = show_menu,
) -> None:
	"""`menu` collects the configuration interactively, the rest of the flow is shared."""
	if arch_config_handler is None:
		arch_config_handler = ArchConfigHandler()

	mirror_list_handler = MirrorListHandler(
		offline=arch_config_handler.args.offline,
		verbose=arch_config_handler.args.verbose,
	)

	if not arch_config_handler.args.silent:
		menu(arch_config_handler, mirror_list_handler)

	arch_config_handler.config.write_debug()
	arch_config_handler.config.save()

	# Safety net for silent/config-file flow. The TUI menu blocks Install via
	# GlobalMenu._validate_bootloader() before reaching this point.
	if failure := validate_bootloader_layout(
		arch_config_handler.config.bootloader_config,
		arch_config_handler.config.disk_config,
	):
		error(failure.description)
		return None

	if arch_config_handler.args.dry_run:
		return None

	if not arch_config_handler.args.silent:
		aborted = False
		res: bool = tui.run(lambda: confirm_config(arch_config_handler.config))

		if not res:
			debug('Installation aborted')
			aborted = True

		if aborted:
			return main(arch_config_handler, menu)

	if arch_config_handler.config.disk_config:
		fs_handler = FilesystemHandler(arch_config_handler.config.disk_config)

		if not delayed_warning(tr('Starting device modifications in ')):
			return main(menu=menu)

		fs_handler.perform_filesystem_operations()

	perform_installation(
		arch_config_handler,
		mirror_list_handler,
		AuthenticationHandler(),
		ApplicationHandler(),
	)

	return None


if __name__ == '__main__':
	main()
