# Source this file.

build_pandoc() {
    build=$(dirname "$1")/build
    mkdir -p "$build"
    pandoc --standalone "$1" -o "$build/$(basename "${1%.md}.html")"
}

# $1 - `packages-ubuntu.yml` or `packages-fedora.yml`.
extract_packages_yml() {
    find . -name "$1" -print0 | xargs -0 cat |
        perl -ne 'if (/^\s+-\s+(.*)/) { print "  $1 \\\n"; }' |
        sort
}

extract_ubuntu_packages() {
    {
        echo '#!/bin/sh'
        echo "DEBIAN_FRONTEND=noninteractive apt-get install -y \\"
        extract_packages_yml packages-ubuntu.yml
        echo
    } > install-ubuntu-packages.sh
    chmod +x install-ubuntu-packages.sh
}

extract_fedora_packages() {
    {
        echo '#!/bin/sh'
        echo "dnf install -y \\"
        extract_packages_yml packages-fedora.yml
        echo
    } > install-fedora-packages.sh
    chmod +x install-fedora-packages.sh
}
