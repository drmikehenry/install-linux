import os
import re
import subprocess
import sys
from pathlib import Path


def build_pandoc() -> None:
    for p in sys.argv[1:]:
        markdown_source = Path(p)
        build = markdown_source.parent / "build"
        html_path = (build / markdown_source.name).with_suffix(".html")
        build.mkdir(exist_ok=True)
        subprocess.run(
            [
                "pandoc",
                "--standalone",
                str(markdown_source),
                "-o",
                str(html_path),
            ],
            check=True,
        )


def extract_packages(name: str) -> list[str]:
    packages = set()
    for root, dirs, files in os.walk("."):
        for f in files:
            if f != name:
                continue
            for line in (Path(root) / f).read_text().splitlines():
                m = re.search(r"^\s+-\s+(\S+)$", line.rstrip())
                if m:
                    packages.add(m.group(1))
    return sorted(packages)


def make_install_script(
    script_name: str, install_cmd: str, packages: list[str]
) -> None:
    with open(script_name, "w") as f:
        f.write("#!/bin/sh\n")
        if packages:
            f.write(install_cmd)
            for p in packages:
                f.write(f" \\\n    {p}")
            f.write("\n")
    os.chmod(script_name, 0o755)


def extract_ubuntu_packages() -> None:
    install_cmd = "DEBIAN_FRONTEND=noninteractive apt-get install -y"
    packages = extract_packages("packages-ubuntu.yml")
    make_install_script("install-ubuntu-packages.sh", install_cmd, packages)


def extract_fedora_packages() -> None:
    install_cmd = "dnf install -y"
    packages = extract_packages("packages-fedora.yml")
    make_install_script("install-fedora-packages.sh", install_cmd, packages)
