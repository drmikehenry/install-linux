---
title: casey Installation
---

# casey (i7, 4xSSD)

- Gigabyte Z97X-UD5H-BK motherboard:
  http://www.gigabyte.com/products/product-page.aspx?pid=4978#ov

- Use Intel Ethernet adapter if given a choice (seems like the default now).

## casey partitioning

- Press F12 to get boot menu.

- Boot EFI Ubuntu ISO and "Try Ubuntu".

- OPTIONAL: Erase SSDs:

      echo -n mem > /sys/power/state
      # Press power button to awaken.
      for i in a b c d; do
        echo "Drive /dev/sd$i"
        hdparm --user-master u --security-set-pass password /dev/sd$i
        hdparm --user-master u --security-erase password /dev/sd$i
      done

  Reboot into "Try Ubuntu".

- Launch installer.
- Minimal installation.
- Do not download updates during installation.
- Installation type: Advanced features | Erase disk and use ZFS
- Choose `sda`.
- Choose New York time zone.
- Your name: Power User
- Your computer's name: casey
- Pick a username: poweruser

- OPTIONAL: Reboot into new Ubuntu to test; then boot back into "Try Ubuntu".

### Prepare to use bolt notes

    # Install Vim, NFS:
    apt update
    apt install -y vim nfs-common

    # Mount bolt:/m:
    mkdir /m
    mount bolt:/m/ /m/

### Reconfigure ZFS pools

    bind 'set enable-bracketed-paste off'

    # Create temporary mount points:
    mkdir /mnt/backup
    mkdir /mnt/target
    mkdir /mnt/esp

    # Insert Flash drive, detect device node (/dev/sdg in this case):
    dmesg -T

    # Unmount anthing under `/media`:
    umount /media<TabComplete>

    # (one-time) Create a backup filesystem:
    mke2fs -j -F /dev/sdg

    # Mount backup filesystem:
    mount /dev/sdg /mnt/backup

    zpool import -R /mnt/target rpool
    zpool import -R /mnt/target bpool

    zpool status

    zfs snapshot -r bpool@1
    zfs send -R bpool@1 > /mnt/backup/bpool.zfs
    zfs snapshot -r rpool@1
    zfs send -R rpool@1 > /mnt/backup/rpool.zfs

    # bpool.zfs size: 253M
    # rpool.zfs size: 6.5G

    # OPTIONAL: examine partitions:
    sgdisk -p /dev/sda

    mount /dev/sda1 /mnt/esp
    tar -cf /mnt/backup/esp.tar -C /mnt/esp .
    umount /mnt/esp

    zpool destroy bpool
    zpool destroy rpool

    for i in /dev/sd[abcd]; do sgdisk --zap-all $i; done
    partprobe

    # Get this message:
    #   Error: Partition(s) 2 on /dev/sda have been written, but we have been
    #   unable to inform the kernel of the change, probably because it/they are in
    #   use.  As a result, the old partition(s) will remain in use.  You should
    #   reboot now before making further changes.
    # Therefore, reboot and return to this point (skipping the installation and
    # destroy/create of zpools and such):
    reboot

    # Allocate ESP:
    sgdisk /dev/sda     -n 1:0:+1GiB -t 1:EF00

    # Allocate swap:
    sgdisk /dev/sda     -n 2:0:+4GiB -t 2:8200

    # Allocate ZFS boot volume:
    sgdisk /dev/sda     -n 3:0:+2GiB -t 3:BE00

    # Allocate remainder of disk for ZFS root volume:
    sgdisk /dev/sda     -n 4:0:0 -t 4:BF00

- Display final partitioning:

      sgdisk /dev/sda -p

  With output:

      Disk /dev/sda: 500118192 sectors, 238.5 GiB
      Model: Crucial_CT256M55
      Sector size (logical/physical): 512/4096 bytes
      Disk identifier (GUID): 0FE8658D-E0ED-4F02-BF5C-17A8848A9F11
      Partition table holds up to 128 entries
      Main partition table begins at sector 2 and ends at sector 33
      First usable sector is 34, last usable sector is 500118158
      Partitions will be aligned on 2048-sector boundaries
      Total free space is 2014 sectors (1007.0 KiB)

      Number  Start (sector)    End (sector)  Size       Code  Name
         1            2048         2099199   1024.0 MiB  EF00
         2         2099200        10487807   4.0 GiB     8200
         3        10487808        14682111   2.0 GiB     BE00
         4        14682112       500118158   231.5 GiB   BF00

- Clone partition information onto other drives:

      for i in b c d; do
        sgdisk -R /dev/sd$i /dev/sda
        sgdisk -G /dev/sd$i
      done

- Create filesystems on all EFI System Partitions (ESP):

      # TODO: Just sda for now:
      # for i in /dev/sd[abcd]1; do mkfs.vfat -F32 $i; done
      mkfs.vfat -F32 /dev/sda1

- Make swap partitions:

      for i in /dev/sd[abcd]2; do mkswap $i; done

- Partitioning is now complete.

      zpool create -f \
        -o ashift=12 \
        -o autotrim=on \
        -o cachefile=/etc/zfs/zpool.cache \
        -o compatibility=grub2 \
        -o feature@livelist=enabled \
        -o feature@zpool_checkpoint=enabled \
        -O devices=off \
        -O acltype=posixacl \
        -O xattr=sa \
        -O compression=lz4 \
        -O normalization=formD \
        -O relatime=on \
        -O canmount=off \
        -O mountpoint=/boot \
        -R /mnt/target \
        bpool \
        mirror /dev/sd[abcd]3

      zpool create -f \
          -o ashift=12 \
          -o autotrim=on \
          -O acltype=posixacl \
          -O xattr=sa \
          -O dnodesize=auto \
          -O compression=lz4 \
          -O normalization=formD \
          -O relatime=on \
          -O canmount=off \
          -O mountpoint=/ \
          -R /mnt/target \
          rpool \
          /dev/sd[abcd]4

      mount /dev/sda1 /mnt/esp
      tar -xf /mnt/backup/esp.tar -C /mnt/esp
      umount /mnt/esp

      zfs receive bpool -F < /mnt/backup/bpool.zfs
      zfs receive rpool -F < /mnt/backup/rpool.zfs

      # Launder to use PARTUUID:
      zpool export bpool
      zpool export rpool
      zpool import -d /dev/disk/by-partuuid -N -R /mnt/target rpool
      zpool import -d /dev/disk/by-partuuid -N -R /mnt/target bpool

      zfs mount -a

      # Force re-creation of cache file for all pools:
      zpool set cachefile=/etc/zfs/zpool.cache bpool
      zpool set cachefile=/etc/zfs/zpool.cache rpool

      # Copy over current valid cache file:
      cp /etc/zfs/zpool.cache /mnt/target/etc/zfs/

      mount --rbind /dev  /mnt/target/dev
      mount --rbind /proc /mnt/target/proc
      mount --rbind /sys  /mnt/target/sys
      chroot /mnt/target /bin/bash --login

      # Repeat for new `chroot` prompt:
      bind 'set enable-bracketed-paste off'

      # Update /etc/fstab for new `PARTUUID` values for `/boot/efi`
      # and `swap`:
      ll /dev/disk/by-partuuid | grep sda1
      ll /dev/disk/by-partuuid | grep 'sd[abcd]2'

      vi /etc/fstab

      # Mount ESP:
      mount /dev/sda1 /boot/efi

      update-initramfs -c -k all
      update-grub
      grub-install --target=x86_64-efi --efi-directory=/boot/efi \
        --bootloader-id=ubuntu --recheck --no-floppy

      # Exit the `chroot`.
      exit

      # Restart into installed system:
      reboot

==============================================================================

- The large spinning hard drive has one GPT partition holding an LVM physical
  volume:

  - Launch ``gdisk``.

  - Create one partition, type ``8e00`` (Linux LVM).

  - Create volume group:

        vgcreate casey_spinner /dev/sde1

  - Volumes created later.

        lvcreate casey_spinner -L 500G -n lv_snapshot
        mke2fs -t ext4 /dev/casey_spinner/lv_snapshot
        mount /dev/casey_spinner/lv_snapshot /snapshot

        vim /etc/fstab

        /dev/mapper/casey_spinner-lv_snapshot /snapshot ext4  defaults  0 2
