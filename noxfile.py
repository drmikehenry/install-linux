import os
import re
import subprocess
import typing as T
from pathlib import Path

import nox
import tomli

nox.options.default_venv_backend = "uv"
nox.options.error_on_external_run = True
nox.options.reuse_existing_virtualenvs = False
nox.options.sessions = ["run"]


# Hack to extend `PATH` to include `uv`-installed interpreters inspired by:
# <https://github.com/astral-sh/uv/issues/6579>.
def gen_python_bin_paths() -> T.Generator[Path, None, None]:
    uv_python_dir = Path(
        subprocess.check_output(["uv", "python", "dir"], text=True).strip()
    )
    for p in uv_python_dir.glob("*"):
        p_bin = p / "bin"
        p_python_exe = p / "python.exe"
        if p_bin.is_dir():
            yield p_bin
        elif p_python_exe.is_file():
            yield p


def add_uv_pythons_to_path() -> None:
    paths_new = ":".join(str(p) for p in gen_python_bin_paths())
    if paths_new:
        paths_old = os.environ["PATH"]
        os.environ["PATH"] = f"{paths_new}:{paths_old}"


add_uv_pythons_to_path()


def normalize(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def dep_groups(name: str) -> T.Generator[str, None, None]:
    name = normalize(name)
    for dep in _dependency_groups[name]:
        if isinstance(dep, dict):
            yield from dep_groups(dep["include-group"])
        else:
            yield dep


def read_dependency_groups() -> T.Dict[str, T.Union[str, T.Dict[str, str]]]:
    with open("pyproject.toml", "rb") as f:
        groups = {
            normalize(k): v
            for k, v in tomli.load(f)["dependency-groups"].items()
        }
        return groups


_dependency_groups = read_dependency_groups()


# @nox.session(python=["3.9", "3.10", "3.11", "3.12"])
@nox.session
def test(s: nox.Session) -> None:
    s.install(".", *dep_groups("test"))
    s.run(
        "python",
        "-m",
        "pytest",
    )


# For some sessions, set `venv_backend="none"` to simply execute scripts within
# the existing `uv` environment. This requires that `nox` is run with that
# environment active (e.g., via `uv run nox`).
@nox.session(venv_backend="none")
def fmt(s: nox.Session) -> None:
    s.run("ruff", "check", ".", "--select", "I", "--fix")
    s.run("ruff", "format", ".")


@nox.session(venv_backend="none")
@nox.parametrize(
    "command",
    [
        ["ruff", "check", "."],
        ["ruff", "format", "--check", "."],
    ],
)
def lint(s: nox.Session, command: T.List[str]) -> None:
    s.run(*command)


@nox.session(venv_backend="none")
def lint_fix(s: nox.Session) -> None:
    s.run("ruff", "check", ".", "--fix")


@nox.session()
def type_check(s: nox.Session) -> None:
    s.install(".", *dep_groups("type_check"))
    s.run("mypy", "src", "tests", "noxfile.py")


@nox.session
def check(s: nox.Session) -> None:
    s.install(*dep_groups("nox"))
    s.run("nox", "-s", "lint")
    s.run("nox", "-s", "type_check")
    s.run("nox", "-s", "test")


@nox.session
def run(s: nox.Session) -> None:
    s.install(".")
    s.run("extract", "install-linux.md")
    s.run("build_pandoc", "README.md", "use-linux.md", "install-linux.md")
    s.run("extract_ubuntu_packages")
    s.run("extract_fedora_packages")
