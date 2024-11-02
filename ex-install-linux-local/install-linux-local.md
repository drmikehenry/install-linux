---
title: Linux Installation Local
---

# Machine-specific setup

See `machines/` directory for per-machine instructions.

# Network-specific setup

## Setup automount for `/m/`

AUTOMATED in role `workstation-mounts`.

- NON_BOLT: Create symlink for `/m`:

      ln -s /net/bolt.drmikehenry.com/m /m

  **NOTE** bolt.drmikehenry.com might resolve to public IP.

## Setup automount for `/nfshome/`

AUTOMATED in role `workstation-mounts`.

- NON_BOLT: Create symlink for `/nfshome`:

      ln -s /net/bolt.drmikehenry.com/home /nfshome

## SSH client setup

See `SSH client setup` in `install-linux.md` for overall instructions.

- MANUAL Setup `bolt` server configuration:

    echod -o /etc/ssh/ssh_config.d/10-bolt.conf '
      Host bolt bolt.drmikehenry.com
          Port 12345
    '
    chmod go-w /etc/ssh/ssh_config.d/10-bolt.conf

  **NOTE** Adjust port number above to server-specific value.

- Disable X11 forwarding for dewalt
  `:extract-echod:roles/local-base/files/ssh_config.d-10-dewalt.conf`:

      echod -o /etc/ssh/ssh_config.d/10-dewalt.conf '
        Host dewalt dewalt.drmikehenry.com
            ForwardX11 no
      '

  Adjust permissions:

      chmod go-w /etc/ssh/ssh_config.d/10-github.conf

  Ansible `:role:local-base`:

  ```yaml
  - name: Disable X11 forwarding for dewalt
    copy:
      dest: /etc/ssh/ssh_config.d/10-dewalt.conf
      src: ssh_config.d-10-dewalt.conf
      mode: "u=rw,go=r"
  ```

- Disable X11 forwarding for dewaltguest
  `:extract-echod:roles/local-base/files/ssh_config.d-10-dewaltguest.conf`:

      echod -o /etc/ssh/ssh_config.d/10-dewaltguest.conf '
        Host dewaltguest dewaltguest.drmikehenry.com
            ForwardX11 no
      '

  Adjust permissions:

      chmod go-w /etc/ssh/ssh_config.d/10-github.conf

  Ansible `:role:local-base`:

  ```yaml
  - name: Disable X11 forwarding for dewaltguest
    copy:
      dest: /etc/ssh/ssh_config.d/10-dewaltguest.conf
      src: ssh_config.d-10-dewaltguest.conf
      mode: "u=rw,go=r"
  ```

# Other

## Docker

- Follow instructions from `install-linux.md` for basic Docker setup,
  with variables:

      DOCKER_USER=mike

  AUTOMATED via `install-linux-local` `home.yml`.

## PyPI uploads

- Install twine `:role:local-base`:

      uvtoolg install twine

- MANUAL Create a configuration file for PyPI and TestPyPI:

      echod -o ~/.pypirc '
        [distutils]
        index-servers =
          pypi
          testpypi

        [pypi]
        username = __token__
        password = <Replace with PyPI token>
        # Alternatively, use a real user name and password combination:
        # username = drmikehenry
        # password = <password>

        [testpypi]
        repository: https://test.pypi.org/legacy/
        username = __token__
        password = <Replace with PyPI token>
        # Alternatively, use a real user name and password combination:
        # username = drmikehenry
        # password = <password>
      '

  **NOTE** Adjust the above to use the real token as generated from the PyPI web
  site.  Alternatively, setup user name and password.

- Upload to testpypi::

    twine upload -r testpypi dist/ptee-0.3.0.tar.gz

- Upload to the real PyPI::

    twine upload dist/ptee-0.3.0.tar.gz

- Check validity of an egg before upload::

    twine check dist/*

