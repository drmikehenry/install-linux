---
title: Using ZFS-on-root with Ubuntu
---

Note: not yet ready.

# Pre-install Ubuntu with ZFS-on-root

- Setup ssh key for root (uses `ubuntu` user):

      ansible-playbook \
        --ask-pass \
        --ask-become-pass \
        -u ubuntu \
        -l $ANSIBLE_HOST \
        root-ssh-authorized_key.yml

- Prepare for ZFS installation:

      ansible-playbook \
        -u root \
        -l $ANSIBLE_HOST \
        ubuntu-zfs-prepare.yml

- Enumerate disks to use:

      ansible \
        $ANSIBLE_HOST \
        -u root \
        -a 'ls -l /dev/disk/by-id'

  Incorporate output into `disks` variable in `ubuntu-zfs-format-HOST.yml`,
  e.g.:

      ... ata-VBOX_CD-ROM_VB2-01700376 -> ../../sr0
      ... ata-VBOX_HARDDISK_VB5bde8c14-de8c4709 -> ../../sda
      ... ata-VBOX_HARDDISK_VB81562bc4-019c8c1c -> ../../sdc
      ... ata-VBOX_HARDDISK_VBb2e9004f-5f781231 -> ../../sdd
      ... ata-VBOX_HARDDISK_VBe57f2aef-17cda556 -> ../../sdb

      ==>

      disks:
        - '/dev/disk/by-id/ata-VBOX_HARDDISK_VB5bde8c14-de8c4709'
        - '/dev/disk/by-id/ata-VBOX_HARDDISK_VB81562bc4-019c8c1c'
        - '/dev/disk/by-id/ata-VBOX_HARDDISK_VBb2e9004f-5f781231'
        - '/dev/disk/by-id/ata-VBOX_HARDDISK_VBe57f2aef-17cda556'

- Format drives:

      ansible-playbook \
        -u root \
        -l $ANSIBLE_HOST \
        ubuntu-zfs-format-HOST.yml

- Perform system installation:

      ansible-playbook \
        -u root \
        -l $ANSIBLE_HOST \
        ubuntu-zfs-system-installation.yml
