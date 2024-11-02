import nox

nox.options.default_venv_backend = "uv"
nox.options.error_on_external_run = True
nox.options.reuse_existing_virtualenvs = False
nox.options.sessions = ["run"]


@nox.session
def run(s: nox.Session) -> None:
    s.install(".")
    s.run("extract", "install-linux-local.md")
    s.run("build_pandoc", "README.md", "install-linux-local.md")
    s.run("extract_ubuntu_packages")
    s.run("extract_fedora_packages")
