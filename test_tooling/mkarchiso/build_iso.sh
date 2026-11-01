#!/bin/bash

set -e

packages_file="/tmp/archlive/packages.x86_64"

# Packages to add to the archiso profile packages
packages=(
	gcc
	git
	pkgconfig
	python
	python-pip
	python-uv
	python-setuptools
	python-pyparted
	python-pydantic
	python-textual
)

if [ -d "/tmp/archlive" ]; then
    rm -rf "/tmp/archlive"
fi
mkdir -p /tmp/archlive/airootfs/root/soninstall-git
cp -r . /tmp/archlive/airootfs/root/soninstall-git

cat <<- _EOF_ | tee /tmp/archlive/airootfs/root/.zprofile
	cd soninstall-git
	rm -rf dist

	uv build --no-build-isolation --wheel
	uv pip install dist/*.whl --break-system-packages --system --no-build --no-deps

	echo "This is an unofficial ISO for development and testing of sOninstall. No support will be provided."
	echo "This ISO was built from Git SHA $GITHUB_SHA"
	echo "Type soninstall to launch the installer."
_EOF_

pacman --noconfirm -S archiso

cp -r /usr/share/archiso/configs/releng/* /tmp/archlive

sed -i /archinstall/d "$packages_file"

# Add packages to the archiso profile packages
for package in "${packages[@]}"; do
	echo "$package" >> "$packages_file"
done

find /tmp/archlive
cd /tmp/archlive

mkarchiso -v -w work/ -o out/ ./
