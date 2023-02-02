#!/bin/bash

. ../install-linux/helpers.sh

../install-linux/extract.py install-linux-local.md

build_pandoc README.md
build_pandoc install-linux-local.md

extract_ubuntu_packages
extract_fedora_packages
