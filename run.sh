#!/bin/bash

build_pandoc()
{
    build=$(dirname "$1")/build
    mkdir -p "$build"
    pandoc --standalone "$1" -o "$build/$(basename "${1%.md}.html")"
}

./extract.py

build_pandoc README.md
build_pandoc use-linux.md
build_pandoc install-linux.md
build_pandoc ../install-linux-local/install-linux-local.md
build_pandoc ../install-linux-local/README.md

# For VM testing:
{
    echo "DEBIAN_FRONTEND=noninteractive apt-get install -y \\"
    find . -name packages-ubuntu.yml -print0 | xargs -0 cat |
        perl -ne 'if (/^\s+-\s+(.*)/) { print "  $1 \\\n"; }'
    echo
} > install-ubuntu-packages.sh
{
    echo "dnf install -y \\"
    find . -name packages-fedora.yml -print0 | xargs -0 cat |
        perl -ne 'if (/^\s+-\s+(.*)/) { print "  $1 \\\n"; }'
    echo
} > install-fedora-packages.sh
