#!/bin/bash

. helpers.sh

./extract.py install-linux.md

build_pandoc README.md
build_pandoc use-linux.md
build_pandoc install-linux.md

extract_ubuntu_packages
extract_fedora_packages
