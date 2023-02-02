---
title: Install Linux Local README
---

# Installation

See `install-linux/README.md` for overview.

## Install Linux via Ansible

### Bootstrap

- Setup ssh key for root (enter `poweruser` password at `SSH password` prompt,
  then press Enter to reuse for `BECOME password`):

      ansible-playbook \
        --ask-pass \
        --ask-become-pass \
        -u poweruser \
        -l $ANSIBLE_HOST \
        root-ssh-authorized_key.yml

- Bootstrap bare minimum:

      ansible-playbook \
        -u root \
        -l $ANSIBLE_HOST \
        bootstrap-local.yml

- OPTIONAL Setup `/localhome`-based home directories:

      ansible-playbook \
        -u root \
        -l $ANSIBLE_HOST \
        localhome.yml

  `/root/localhome-migrate.log` will be fetched and displayed.  Inspect the
  output to verify the migration was successful.

- base:

      ansible-playbook \
        -u root \
        -l $ANSIBLE_HOST \
        base.yml

- WORKSTATION: workstation-mounts:

      ansible-playbook \
        -u root \
        -l $ANSIBLE_HOST \
        workstation-mounts.yml

- OPTIONAL UBUNTU Remove snaps:

      ansible-playbook \
        -u root \
        -l $ANSIBLE_HOST \
        remove-snaps.yml

- OPTIONAL UBUNTU Use Mozilla PPA for Firefox, Thunderbird:

      ansible-playbook \
        -u root \
        -l $ANSIBLE_HOST \
        mozilla-ppa.yml

  Note: this also reinstalls Firefox from the PPA because the snap version was
  likely purged (and Firefox is installed by default).

- accounts:

      ansible-playbook \
        -u root \
        -l $ANSIBLE_HOST \
        accounts.yml

- local-passwords:

      ansible-playbook \
        -u root \
        -l $ANSIBLE_HOST \
        local-passwords.yml

**TODO** Insert ZFS instructions for setting up per-user datasets.

- Setup Git repos in home directory (requires password for `$ANSIBLE_USER`):

      ansible-playbook \
        --ask-become-pass \
        -u $ANSIBLE_USER \
        -l $ANSIBLE_HOST \
        user-root-git-repos.yml

- Setup `$ANSIBLE_USER` for Rust:

      ansible-playbook \
        -u $ANSIBLE_USER \
        -l $ANSIBLE_HOST \
        user-rust.yml

- WORKSTATION: workstation:

      ansible-playbook \
        -u root \
        -l $ANSIBLE_HOST \
        workstation.yml

  FEDORA Might want to do this as root (now that Plasma is here), or
  just reboot:

      systemctl isolate graphical.target

- UBUNTU Restart `gdm` so that Plasma becomes a valid option:

      systemctl restart gdm

- HOME: home:

      ansible-playbook \
        -u root \
        -l $ANSIBLE_HOST \
        home.yml

- user-plasma:

      ansible-playbook \
        -u $ANSIBLE_USER \
        -l $ANSIBLE_HOST \
        user-plasma.yml
