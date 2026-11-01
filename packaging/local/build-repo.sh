#!/usr/bin/env bash
# Builds the soninstall package from this checkout (uncommitted changes included) into a local
# pacman repository, such as the one the sOnOs ISO profile installs soninstall from:
#
#   packaging/local/build-repo.sh ~/sOnOs/repo
#
# Run it as a regular user, makepkg uses sudo only to install missing build dependencies.
set -euo pipefail

if [[ $# -ne 1 ]]; then
	echo "Usage: $0 <repository directory>" >&2
	exit 1
fi

if [[ $EUID -eq 0 ]]; then
	echo 'Run this as a regular user, makepkg does not build packages as root.' >&2
	exit 1
fi

HERE=$(cd "$(dirname "$0")" && pwd)
mkdir -p "$1"
REPO_DIR=$(cd "$1" && pwd)

# Only the new build stays in the repository
rm -f "$REPO_DIR"/soninstall-*.pkg.tar.zst
(cd "$HERE" && PKGDEST=$REPO_DIR makepkg --syncdeps --force --clean --cleanbuild --noconfirm --needed)
repo-add --quiet "$REPO_DIR/sonos.db.tar.gz" "$REPO_DIR"/soninstall-*.pkg.tar.zst

echo "soninstall is in the [sonos] repository at $REPO_DIR"
