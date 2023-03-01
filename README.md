---
title: Install Linux README
---

# Reference

## Vim shortcut for pasting

For convenient pasting from Vim, use `~/bin/pastewin` against a
convenient KDE Konsole (e.g., `konsole-3`):

    nmap <f8> VY:silent !pastewin konsole-3<CR>
    xmap <f8>  Y:silent !pastewin konsole-3<CR>

Then press `<F8>` on a line to paste it, or visually select to paste the
entire selection.

Test on this line:

    echo Hello

Or this multi-line:

    echo Hello \
      there

To remove maps:

    nunmap <f8>|xunmap <f8>

Note: the `pastewin` script requires `xdotool`.

## Fixing "bracketed paste"

- Connecting via ssh to an unconfigured box might enable "bracketed
  paste" mode, wherein a paste into the terminal requires a manual
  press of "Enter" to complete the paste operation.

  To manually disable "bracketed paste" mode, run the following at the prompt:

      bind 'set enable-bracketed-paste off'

  To manually query "bracketed paste" mode:

      bind -v | grep bracketed

## Ansible terminology

The *Ansible control node* runs `ansible` to perform installations
on a *managed node*.

## Using ansible

- In general, playbooks are run by using `ssh` to connect to the
  managed node. The user on the managed node will be either `root` or
  an unprivileged user. For many installation tasks, the playbook will
  use `become` to execute with root privileges on the managed node;
  such playbooks should be invoked with the `root` user or with an
  unprivileged user with "sudo" privileges. Other times, the user on
  the managed node should be a particular unprivileged user, allowing
  setup of that user's own files; such playbooks generally have the
  word `user` in them.
- Example playbook invocations:
  - Connect via SSH as unprivileged `poweruser` user, then `sudo` to
    become root; prompt for the `poweruser` user's SSH password and
    `sudo` password (the latter defaults to the former):

        ansible-playbook \
          -u poweruser \
          --ask-pass \
          --ask-become-pass \
          -l HOST \
          playbook-requiring-root.yml

  - Connect via SSH as unprivileged `USER` user to perform per-user
    setup; assume SSH `authorized_key` has already been setup:

        ansible-playbook \
          -u USER \
          -l HOST \
          user-playbook.yml

  - Connect via SSH as unprivileged `USER` user, then `sudo` to become root,
    prompting for `sudo` password; assumes SSH `authorized_key` has already been
    setup for `USER`:

        ansible-playbook \
          --ask-become-pass \
          -u USER \
          -l HOST \
          playbook-requiring-root.yml

  - Connect via SSH as unprivileged `USER` user, then `sudo` to become root
    without prompting for `sudo` password; assumes SSH `authorized_key` and
    passwordless `sudo` have already been setup for `USER`:

        ansible-playbook \
          -u USER \
          -l HOST \
          playbook-requiring-root.yml

  - Connect as `root` via SSH `authorized_key`:

        ansible-playbook \
          -u root \
          -l HOST \
          some-playbook.yml

# Installation

## Prepare Ansible control node

- The Ansible control node can be the same machine as the managed node, but more
  commonly it will be a separate machine.

- Install ansible on the control node (unneeded on the managed node):

      apt update
      apt install -y software-properties-common
      apt-add-repository --yes --update ppa:ansible/ansible
      apt install -y ansible

- Install `sshpass` (necessary for Ansible to use the 'ssh' connection type with
  passwords):

      apt install -y sshpass

- Acquire `ansible/` directory to `~/projects/ansible`.

- Run ansible.

## Pre-installation of managed node

This step installs a minimal working system that can boot on its own.

### Prepare managed node for standard pre-installation

This is the simplest option.  It uses the distro's standard installation process
to setup a minimal system.

- Run distro's installer.

- Choose minimal installation, setting up hostname, network, etc.

- Boot into newly installed system.

### Prepare managed node for custom pre-installation

- Boot distro's live environment.

- Login to managed node; become root:

      sudo -i

- UBUNTU: Give `ubuntu` user a password:

      passwd ubuntu

- UBUNTU: Update APT cache:

      apt update

- UBUNTU: Install openssh server:

      apt install -y openssh-server

- (fedora) Setup openssh server:

  - Install if necessary (installed by default on Live media):

        dnf install -y openssh-server

  - Restart and enable the server:

        systemctl restart sshd
        systemctl enable sshd

- Determine managed node's IP address:

      ip -br -c a

- Perform any node-specific pre-installation.

- Boot into newly installed system.

## Prepare managed node for installation

- Login to managed node; become root:

      sudo -i

- UBUNTU: Update APT cache:

      apt update

- UBUNTU: Install openssh server:

      apt install -y openssh-server

- (fedora) Setup openssh server:

  - Install if necessary (installed by default on Live media):

        dnf install -y openssh-server

  - Restart and enable the server:

        systemctl restart sshd
        systemctl enable sshd

- Determine managed node's IP address:

      ip -br -c a

## Prepare ansible configuration on control node

- Login to Ansible control node.

### Verify managed node IP address

- Verify proper IP address is present for managed node:

      cd ~/projects/ansible
      cat ansible-hosts.yml

  For example, with a host name `ubuntu-dev`:

      ---
      all:
        hosts:
          ubuntu-dev:
            ansible_host: 1.2.3.4
            ansible_port: 22
            ansible_python_interpreter: /usr/bin/python3

### Setup `ANSIBLE_HOST`, `ANSIBLE_USER` variables

- For convenience of pasting below, the environment variable
  `ANSIBLE_HOST` must be setup to be the host name in
  `ansible-hosts.yml` above, e.g.:

      export ANSIBLE_HOST=ubuntu-dev

- And the environment variable `ANSIBLE_USER` must be setup to be the
  main username that will operate the system; e.g., `mike`:

      export ANSIBLE_USER=mike

### Add HOST IP to `known_hosts`

- Add host's IP address (**NOT** host name) to `known_hosts`:

      # Use IP address for ANSIBLE_HOST, e.g.:
      ssh poweruser@1.2.3.4

  Answer "yes" to "Are you sure you want to continue connecting
  (yes/no)?", then press Ctrl-C after host is added to `known_hosts`.

## Install Linux via Ansible

See `install-linux-local/README.md` for local steps.
