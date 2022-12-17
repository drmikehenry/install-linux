---
title: Linux Installation
---

# System-Specific Setup

See `install-linux-local.md` for any machine-specific setup.

# Pre-Installation

## Machine Hardware Configuration

- Setup to boot as UEFI (typical):
  - (physical) setup in firmware settings.
  - (VM) System | Motherboard | check "Enable EFI"
- (VM) Configure 3000+ MB in System | Motherboard | Base Memory.
- (VM) Set Processors to 2 in System | Processor | Processors.
- (VM) Setup screen scaling for 4K monitors:
  - Settings | Display | Screen | Scale Factor: 200%
- Ensure SATA for hard drive is configured as AHCI:
  - (physical) setup in firmware settings.
  - (VM) System | Storage | Controller: SATA | Type: AHCI (already default)
- Setup boot order to boot from USB first (if desired).
- (VM) Configure for bridged networking (if desired):
  - Settings | Network | Attached to: Bridged Adapter

## Boot Media Creation

- Can `dd` a .iso file directly to a USB flash drive and boot from that.
- (ubuntu) Download *both* desktop and server iso files.
  - Need desktop iso for "Try Ubuntu" mode, installing supporting utilities,
    etc.
  - Need server iso for installing onto RAID volumes.
  - Ubuntu 22.04:
    - Desktop: `ubuntu-22.04-desktop-amd64.iso`
    - Server: `ubuntu-22.04-live-server-amd64.iso`
- (fedora) Download the live DVD iso file from:
  <http://fedoraproject.org/en/get-fedora-all>
  - Fedora 36: `Fedora-Workstation-Live-x86_64-36-1.2.iso`
  - Torrent from: <https://torrent.fedoraproject.org/>
    - <https://torrent.fedoraproject.org/torrents/Fedora-Workstation-Live-x86_64-36.torrent>
- (centos) Download the DVD iso file from a mirror at:
  <http://isoredirect.centos.org/centos/7/isos/x86_64/>
  - CentOS 7.4: `CentOS-7-x86_64-DVD-1708.iso`

## Disk Configuration

### GPT Partition Setup

- Use Ubuntu desktop "Try Ubuntu".

  (Note: Do not use the server installer, since it lacks `sgdisk` and the
  ability to install via `apt`.)

- Configure disks in a machine-specific way.

- Generic instructions follow.

#### Standard Disk Partitioning

- Example system has two drives `sda` and `sdb`.

- If any volumes, pool, RAID devices, etc., have been automatically mounted,
  unmount them before proceeding.

- Wipe out/zeroize anything on the disks:

      for i in /dev/sd[ab]; do sgdisk --zap-all $i; done

- Setup each drive as this table shows, using commands that follow:

      ====  ====== ====   ============================================
      Part  Size   Type   Purpose
      ====  ====== ====   ============================================
       1    1GiB   EF00   EFI System Partition (ESP)
       2    4GiB   8200   swap
       3    2GiB   --->   8300(ext4 /boot); BE00(ZFS boot)
       4    (big)  --->   FD00(RAID); 8E00(LVM); BF00(ZFS)
      ====  ====== ====   ============================================

- Starting values of `0` means the start of the biggest unused area.

- Allocate ESP:

      sgdisk /dev/sda     -n 1:0:+1GiB -t 1:EF00

- Allocate swap:

      sgdisk /dev/sda     -n 2:0:+4GiB -t 2:8200

- Allocate ZFS boot volume:

      sgdisk /dev/sda     -n 3:0:+2GiB -t 3:BE00

- Allocate remainder of disk for ZFS root volume:

      sgdisk /dev/sda     -n 4:0:0 -t 4:BF00

- Display final partitioning:

      sgdisk /dev/sda -p

  With output:

      Disk /dev/sda: 500118192 sectors, 238.5 GiB
      Logical sector size: 512 bytes
      Disk identifier (GUID): 4AC7E8B4-5F8E-4EF0-B354-8C348494E621
      Partition table holds up to 128 entries
      First usable sector is 34, last usable sector is 500118158
      Partitions will be aligned on 2-sector boundaries
      Total free space is 0 sectors (0 bytes)

      Number  Start (sector)    End (sector)  Size       Code  Name
         1         4196352       441397901   208.5 GiB   FD00
         2              34            2047   1007.0 KiB  EF02
         3            2048         2099199   1024.0 MiB  EF00
         4         2099200         4196351   1024.0 MiB  8300
         9       441397902       500118158   28.0 GiB    BF07

- Clone partition information onto other disk:

      sgdisk -R /dev/sdb /dev/sda
      sgdisk -G /dev/sdb

- Create filesystem on EFI System Partition (ESP):

      mkfs.vfat -F32 /dev/sda1

- Partitioning is now complete.

### RAID Setup

- Use Ubuntu desktop "Try Ubuntu".

  (Note: Do not use the server installer, since it lacks the ability to install
  via `apt`. Though it has `mdadm` on the media, you have to manually install
  it.)

- Install `mdadm`:

      apt-get install -y mdadm

- To create a RAID device:

  - RAID10 far layout (recommended for RAID10):

        mdadm --create /dev/md/0 --level raid10 --layout f2 -n 4 /dev/sd[abcd]1

  - RAID10 near layout:

        mdadm --create /dev/md/1 --level raid10 -n 4 /dev/sd[abcd]1

  - RAID0 (striped volume):

        # Two drives:
        mdadm --create /dev/md/0 --level raid0 -n 2 /dev/sd[ab]1

        # Four drives:
        mdadm --create /dev/md/0 --level raid0 -n 4 /dev/sd[abcd]1

  - RAID1 (mirrored volume):

        # Two drives:
        mdadm --create /dev/md/0 --level raid1 -n 2 /dev/sd[ab]1

    Do not worry about this warning:

        mdadm: Note: this array has metadata at the start and
            may not be suitable as a boot device.  If you plan to
            store '/boot' on this device please ensure that
            your boot-loader understands md/v1.x metadata, or use
            --metadata=0.90

### LVM Setup

- Use Ubuntu desktop installer, "Try Ubuntu".

**NOTE** Look at per-machine instructions for specifics.

- Create an LVM physical volume:

      # For a RAID system:
      pvcreate /dev/md/0

- Create a volume group named after the machine:

      # For host "HOSTNAME":
      vgcreate HOSTNAME /dev/md/0

- Create logical volumes. Name the root volume after the distro (e.g.,
  `ubuntu22_04`). **Choose machine-specific sizes**:

      lvcreate HOSTNAME -L 50G -n ubuntu22_04
      lvcreate HOSTNAME -L 366G -n home

# Initial Installation

## (ubuntu) Initial Installation

- Create partitions and volumes using desktop iso as shown above.
- Boot from Ubuntu Desktop Install DVD (use `UEFI` boot).
- Choose "Try or Install Ubuntu" at Grub prompt.
- In "Install" app, choose "Install Ubuntu".
- Keyboard layout: English (US)
- What apps: "Minimal installation"
- Uncheck "Download updates while installing Ubuntu".
- Check "Install third-party software...".
- Installation type:
  - Choose "Erase disk and install Ubuntu":
    - Advanced Features: Erase disk and use ZFS
    Alternatively, choose "Something else" for custom partitioning.
- Choose "Install now".
- Where are you?: `New_York`
- Who are you?:
  - Your name: `Power User`
  - Your computer's name: `ubuntu22-04` (for example; use single word, not a
    FQDN, no underscore).
  - Username: `poweruser`
  - Password: `the_actual_password`
  - (Note: this user will have UID=1000.)
- Wait for installation to complete.
- Reboot into new system.

## (fedora) Initial Installation

- Boot from Live CD image (live) or Network Install image (net).

- If any kernel options are required:

  - (live) At "Start Fedora Workstation Live" option, press Tab key to edit
    kernel options.
  - (net) At "Install or upgrade Fedora" option, press Tab key to edit
    kernel options.
  - Append any required kernel options for boot (e.g., `nox2apic`).

- Custom partitioning:

  - (live) Just run a terminal in the GUI.
  - (net) Press Alt-F2 and login as root to get a shell.

  Then follow custom partitioning instructions using `mdadm` et al.

- (live) When prompted, choose "Install to Hard Drive".

- Choose English (United States).

- Choose "System | Installation Destination" to choose which devices will
  participate in the installation. This allows exclusion of drives from even
  being mounted or used as swap, so that the fstab will not even mention them.

- Under "Local Standard Disks" tab, choose drives to use in any capacity (for
  installation or mounting).

- Choose "Done".

- Choose Begin Installation.

- Wait; choose "Finish Installation".

- (VM) Power off; snapshot "Base Install".

- After reboot:

  - Choose "Start Setup" button.

  - Disable "Location Services".

  - Disable "Automatic Problem Reporting".

  - Choose "Enable Third-Party Repositories".

  - Skip "Connect Your Online Accounts".

  - At "About You":
    - Full Name: Power User
    - Username: poweruser

  - "Set a Password".

  - Choose "Start Using Fedora Linux".

  - (VM) Power off; snapshot "Create Power User".

## (centos) Initial Installation

- Boot from DVD image.
- If need custom kernel options, press `e` on `Install CentOS 7` and append them
  (e.g., `nox2apic`).
- Select "Install CentOS 7".
- (first-time) Press Ctrl-Alt-F1 for text console; perform custom partitioning;
  reboot.
- Choose language as "English" and "English (United States)".
- Choose SYSTEM | INSTALLATION DESTINATION:
  - Choose all physical disks for installation.
  - Choose "I will configure partitioning".
  - Choose "Done"; brings up MANUAL PARTITIONING screen.
  - Setup RAID, LVM, mount points, etc., as desired; press Done.
- NETWORK & HOST NAME:
  - Wired Ethernet:
    - Choose "ON".
    - Configure:
      - Check "Automatically connect to this network when it is available".
  - Wireless Ethernet: Choose "ON", Configure:
    - Choose "ON":
      - Network name: toyland
    - Configure:
      - Check "Automatically connect to this network when it is available".
  - Host name:
    - Choose FQDN (e.g., `host1.domain.com`).
- Begin installation.
- ROOT PASSWORD:
  - Set root password.
- Defer USER CREATION until after login.
- Reboot into CentOS.

# Base Setup

See also `README.md` with Ansible instructions.

## First-Time Login

- Login to text console (as `root` if possible, else `poweruser`).

- (if using `poweruser`): become root:

      sudo -i

- (ubuntu) Grant root a password to allow logging in as root directly from the
  console:

      passwd

- (ubuntu) Update APT cache:

      apt update

- (ubuntu) Install openssh server:

      apt install -y openssh-server

## Remote Login for Setup

For convenience, may remotely login to continue setup.

Note that until `authorized_keys` has been setup for root on the host, can't
login as root.

### (ubuntu)

- Remotely login as poweruser, then become root:

      ssh poweruser@ubuntuhost
      sudo -i

- At first, must use `vi` instead of `vim` (until full support is installed).

### (fedora)

- Start the ssh service:

      systemctl start sshd
      systemctl enable sshd

- Remotely login as `poweruser`, then become `root`:

      ssh poweruser@fedorahost
      sudo -i

## echod

(automated)

- Create simple `echod` utility:

      vi /usr/local/bin/echod

  With contents:

```python
#!/usr/bin/env python3

import textwrap, sys
args = sys.argv[1:]
out = sys.stdout
while args:
    arg = args.pop(0)
    if arg == "-o":
        out = open(args.pop(0), "w")
    elif arg == "-a":
        out = open(args.pop(0), "a")
    else:
        out.write(textwrap.dedent(arg).strip() + "\n")
```

- Make script executable:

      chmod +x /usr/local/bin/echod

## Base Aliases

- (homegit) Setup root aliases used during installation:

      vi ~/.bashrc

  Append contents:

      # Ubuntu aliases
      alias agi='apt-get install -y'

      # CentOS/Fedora aliases
      alias yi='yum -y install'
      alias ygi='yum -y groupinstall'

  Now, source these new definitions:

      . ~/.bashrc

## Base Network Customization

- (optional) Use static IP address:

  - Disable NetworkManager:

        vim /etc/NetworkManager/NetworkManager.conf

    Comment out `dns=dnsmasq`, change `managed` to `true`:

        [main]
        plugins=ifupdown,keyfile
        #dns=dnsmasq

        [ifupdown]
        managed=true

  - Setup static IP:

        vim /etc/network/interfaces

    Change from `dhcp` to full settings:

        auto eno1
        # iface eno1 inet dhcp
        iface eno1 inet static
        # TODO: Use actual address here:
        address 192.168.254.252
        gateway 192.168.254.250
        netmask 255.255.255.0
        dns-search drmikehenry.com
        dns-nameservers 192.168.254.250

- (desktop) (mobile) Configure wired and wireless settings via NetworkManager.

- (mobile) Setup wired Ethernet for "hotplug" to avoid delay at boot:

  - Still a problem in Ubuntu 18.04.
  - Seems like preventing the wait is the right idea.
  - References:

    - <http://jrs-s.net/2018/06/17/wait-for-network-to-be-configured-no-limit/>
    - <https://askubuntu.com/questions/972215/a-start-job-is-running-for-wait-for-network-to-be-configured-ubuntu-server-17-1>

  - Disable "Wait for network to be configured (no limit)":

        systemctl mask systemd-networkd-wait-online.service

  - Below didn't seem to fix things with the laptop:
    - References:

      - <https://ubuntuforums.org/showthread.php?t=2323253&page=2>
      - <https://askubuntu.com/questions/773973/ubuntu-16-04-system-boot-waits-saying-raise-network-interfaces>

    - When installing via the server ISO, the primary network interface will be
      configured for `auto`; if that interface is not available at boot, the
      system will wait up to 5 minutes for it to become available.

    - Change `auto` to `allow-hotplug` as shown for example below:

          vim /etc/network/interfaces

          # The primary network interface
          # auto enp0s25
          allow-hotplug enp0s25
          iface enp0s25 inet dhcp

- Shrink the 300-second timeout for `auto` interfaces to something saner:

      vim /etc/dhcp/dhclient.conf

      # timeout 300;
      timeout 5;

- (mobile) Setup search domain for DHCP on "public" networks:

  - Enumerate interfaces via `ip link`.

  - For each non-loopback interface (e.g., `enp0s25`, `wlp3s0`, etc.), create a
    per-interface configuration file for dhclient with name
    `/etc/dhcp/dhclient-enp0s25.conf` (for example):

        echod -o /etc/dhcp/dhclient-enp0s25.conf '
          supersede domain-name "drmikehenry.com";
        '

        echod -o /etc/dhcp/dhclient-wlp3s0.conf '
          supersede domain-name "drmikehenry.com";
        '

## (ubuntu) Disable `apt-daily`

- (automated) Uninstall unattended-upgrades:

      apt-get remove unattended-upgrades

- (automated) Disable apt-daily-related services:

      systemctl disable apt-daily{,-upgrade}.{service,timer}
      systemctl stop apt-daily{,-upgrade}.{service,timer}

## Base Firewall Setup

### Ubuntu

(automated)

- Uncomplicated Firewall (`ufw`) is installed by default, but disabled.

- Setup to allow ssh, "deny" by default, then enable firewall:

      ufw allow ssh
      ufw default deny
      ufw enable

      # Press 'y' to allow firewall to enable.

## Static Hosts

(automated)

- Setup `/etc/hosts` as necessary for static hosts, e.g.:

      192.168.1.2 host1.domain.com host1

## (VM) Guest Additions

(manual)

- (ubuntu) Install prerequisites:

      agi build-essential linux-headers-generic dkms

- (fedora) (centos) Install prerequisites:

      ygi 'Development Tools'
      yi install dkms kernel-devel

- Reboot if needed to ensure running kernel matches latest kernel.

- Install Guest Additions using menu Devices | Insert Guest Additions CD image.

- Insert Guest Additions CD, mount, install:

      mount /dev/sr0 /mnt
      /mnt/VBoxLinuxAdditions.run
      umount /mnt

  Generally, errors indicate that the kernel source is not installed, or that
  the source version doesn't match the running kernel.

- (optional) Setup shared clipboard:

  NOTE: This can cause some issues with clipboard fighting.

  - Devices | Shared Clipboard | Bidirectional

- Reboot:

      reboot

## (optional) Local Home Directories

NOTE: Currently, snap-based Firefox fails when home directories aren't located
in `/home`.

- (automated) Install support for `luseradd`:

      agi libuser

- (automated) Install support for `cron` and `semanage`:

      yi cronie cronie-anacron policycoreutils-python-utils

- (automated) (fedora) Setup SELinux context for `/localhome`:

      semanage fcontext -a -e /home /localhome

- (automated) Create `/localhome`:

      mkdir /localhome

- (automated) (ubuntu) Use `/localhome` for new users' home directory for
  `adduser` command.  In `/etc/adduser.conf`, change `DHOME=` line to:

      DHOME=/localhome

- (automated) Use `/localhome` for new users' home directory for `useradd`
  command.  In `/etc/default/useradd`, set `HOME=` to:

      HOME=/localhome

- (automated) (ubuntu) Configure Apparmor for `/localhome`:

      echod -o /etc/apparmor.d/tunables/home.d/my_local.net '
        @{HOMEDIRS}+=/localhome/
      '

- Create `/etc/cron.d/localhome-migrate` script
  `:extract-echod:roles/localhome/files/etc-cron.d-localhome-migrate`:

      echod -o /etc/cron.d/localhome-migrate '
        SHELL=/bin/bash
        PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
        @reboot root /root/localhome-migrate.sh > /root/localhome-migrate.log 2>&1
      '

- Create `/root/localhome-migrate.sh` script

  (automated) `:extract:roles/localhome/files/localhome-migrate.sh`:

  ```bash
  #!/bin/bash

  zfs_data_set_for()
  {
      dir="$1"
      [ -d "$dir" ] || return
      [ "$(command -v zfs)" ] || return
      zfs list | grep " $dir\$" | grep -Eo '^[^ ]+'
  }

  echo "$(date) localhome-migrate.sh starting"

  home_lines=$(cut -d: -f1,6 /etc/passwd | grep ':/home/')

  if [ "$home_lines" ]; then
      printf '%s\n' "$home_lines" | while IFS=: read -r user home_dir; do
          localhome_dir="/localhome/${home_dir#/home/}"
          echo "Migrate user $user: $home_dir -> $localhome_dir"
          data_set="$(zfs_data_set_for "$home_dir")"
          if [ "$data_set" ]; then
              zfs umount "$data_set"
              zfs set mountpoint="$localhome_dir" "$data_set"
          fi
          if ! usermod -d "$localhome_dir" -m "$user"; then
              # Probably was in use; update manually.
              echo "usermod failed ($?); updating manually"
              sed -E -i -e \
                  "s|^($user:([^:]*:){4})$home_dir:|\1$localhome_dir:|" \
                  /etc/passwd
          fi
          if [ "$data_set" ]; then
              zfs mount "$data_set"
          fi
      done
  fi

  rm -f /etc/cron.d/localhome-migrate
  rm -f /root/localhome-migrate.sh
  echo "$(date) localhome-migrate.sh ending"
  ```

- (automated) Make the script executable:

      chmod +x /root/localhome-migrate.sh

- (automated) Reboot to perform `/localhome` migration:

      reboot

- (automated) Examine log of migration results:

      cat /root/localhome-migrate.log

## Base Utilities

### wget

- Install `:role:base`:

      agi wget

      yi wget

### curl

- Install `:role:base`:

      agi curl

      yi curl

### Initial Vim

- Install `:role:base`:

      agi vim

      yi vim

### Default Editor

- (ubuntu) Set default editor to vim (probably already the default once
  `vim.gtk3` is installed):

      sudo update-alternatives --config editor

  Default priorities are:

      * 0            /usr/bin/vim.gtk3    50        auto mode
        1            /bin/ed             -100       manual mode
        2            /bin/nano            40        manual mode
        3            /usr/bin/vim.basic   30        manual mode
        4            /usr/bin/vim.gtk3    50        manual mode
        5            /usr/bin/vim.tiny    15        manual mode

  So once we have `vim.gtk3`, it will become the default alternative.

  (In general, note that `/etc/alternatives/` are symlinks to the alternatives.)

- (centos) Already defaults to vim.

### sudo

- (manual) (centos) Adjust `secure_path` to include important directories like
  `/usr/local/sbin` and `/usr/local/bin`:

      visudo

  Adjust:

      #Defaults    secure_path = /sbin:/bin:/usr/sbin:/usr/bin
      Defaults    secure_path = /usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

- (manual) Create passwordless sudo access for a single user like `mike`:

      echod -o /etc/sudoers.d/mike '
        mike ALL=(ALL)  NOPASSWD: ALL
      '

## Repository Tools

### (ubuntu) Additional Apt Tools

- Install apt-related tools `:role:workstation`:

      agi apt-doc apt-show-source apt-show-versions apt-utils

- Setup apt-file:

  (automated)

  - Install and update:

        agi apt-file

        sudo apt-file update

  Example usage:

      apt-file search maelstrom

- `wajig` is a wrapper around a pile of tools:

      agi wajig

- `aptitude` is a unified tool to replace a pile of tools (pre-installed):

      agi aptitude aptitude-doc-en

  - May not have equivalent to `apt-get source`.

### (fedora) (centos) RPM Building Tools

- Install `:role:workstation`:

      yi rpm-build rpmdevtools

## Additional Repositories

### (ubuntu) Source Repositories

TODO: Ansible

- (manual) Edit `/etc/apt/sources.list` and uncomment all desired `deb-src`
  lines, e.g.:

      deb-src http://us.archive.ubuntu.com/ubuntu/ jammy main restricted

- Update apt cache:

      apt-get update

### (fedora) rpmfusion Repositories

- Configuration information from: <http://rpmfusion.org/Configuration/>

- Configure repositories for rpmfusion:

      yi --nogpgcheck http://download1.rpmfusion.org/free/fedora/rpmfusion-free-release-$(rpm -E %fedora).noarch.rpm http://download1.rpmfusion.org/nonfree/fedora/rpmfusion-nonfree-release-$(rpm -E %fedora).noarch.rpm

### (fedora) ATrpms Repositories

- Instructions from: <http://www.mjmwired.net/resources/mjm-fedora-f17.html>

- This has just a couple of packages that aren't in rpmfusion, but it can
  conflict with rpmfusion. Configure this repository, but don't keep it enabled.

- Create configuration file for ATrpms repo:

      echod -o /etc/yum.repos.d/atrpms.repo '
        [atrpms]
        name=Fedora Core $releasever - $basearch - ATrpms
        baseurl=http://dl.atrpms.net/f$releasever-$basearch/atrpms/stable
        gpgkey=http://ATrpms.net/RPM-GPG-KEY.atrpms
        enabled=0
        gpgcheck=1
      '

- Import the GPG key:

      rpm --import http://packages.atrpms.net/RPM-GPG-KEY.atrpms

### (centos) Additional Repositories

Non-http mirrors of repositories:

- CentOS itself:
  - <https://www.centos.org/download/mirrors/>

  - <ftp://ftp.gtlib.gatech.edu/pub/centos/>

  - Comment out `mirrorlist`; edit `baseurl`. E.g.:

        #mirrorlist=http://mirrorlist.centos.org/?release=$releasever&arch=$basearch&repo=os&infra=$infra

        baseurl=ftp://ftp.gtlib.gatech.edu/pub/centos/$releasever/os/$basearch/

- EPEL:
  - <https://mirrors.fedoraproject.org/mirrorlist?repo=epel-7&arch=x86_64>

  - Choose: <ftp://ftp.utexas.edu/pub/epel/7/>

  - Comment out `metalink`; edit `baseurl`. E.g.:

        #metalink=https://mirrors.fedoraproject.org/metalink?repo=epel-7&arch=$basearch

        baseurl=ftp://ftp.utexas.edu/pub/epel/7/$basearch

- Nux Dextop:
  - Available via rsync for mirroring:

        rsync -avH li.nux.ro::li.nux.ro/nux/dextop/ /path/to/destination/

  - No apparent source of ftp-based mirroring.

  - Disabling for now.

Normal repositories:

- List of additional repositories along with recommendations:
  <https://wiki.centos.org/AdditionalResources/Repositories>
- EPEL (Extra Packages for Enterprise Linux):
  <https://fedoraproject.org/wiki/EPEL>
  - Setup EPEL:

        rpm -Uvh http://download.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-10.noarch.rpm

  - **Subscribe to EPEL announce list** (see wiki page for details).
- Nux Dextop:
  - Setup Nux Dextop (**Note** Requires EPEL to be installed first):

        rpm --import http://li.nux.ro/download/nux/RPM-GPG-KEY-nux.ro
        rpm -Uvh http://li.nux.ro/download/nux/dextop/el7/x86_64/nux-dextop-release-0-5.el7.nux.noarch.rpm
- Psychotic Ninja (enabled only temporarily):
  - <http://wiki.psychotic.ninja/index.php?title=Main_Page>

  - <http://wiki.psychotic.ninja/index.php?title=Usage>

  - Setup repo key:

        rpm --import http://wiki.psychotic.ninja/RPM-GPG-KEY-psychotic

  - Setup repo (**note** even though this is `i386` and `el6`, it's a a unified
    package that works across all releases and architectures, so the below is
    correct):

        rpm -ivh http://packages.psychotic.ninja/6/base/i386/RPMS/psychotic-release-1.0.0-1.el6.psychotic.noarch.rpm

## (fedora) (centos) SELinux

- (optional) Set SELinux to be permissive:

      vim /etc/selinux/config

      SELINUX=permissive

  This prevents SELinux from denying or breaking anything, and gives a chance to
  see what's going wrong and fix it.

  - A reboot is required for this to take effect.

- (Skip; trying to keep SELinux enabled) Disable SELinux:

      vim /etc/selinux/config

      SELINUX=disabled

  - Alternatively, disable SELinux using GUI:

        system-config-selinux

  - A reboot is required for this to take effect.

- Install policy tools:

      yi checkpolicy policycoreutils-devel

## Filesystem Support

### Local Filesystems

#### gdisk Partitioning Tool

- Install `:role:base`:

      agi gdisk

#### gparted Partitioning Tool

- Install `:role:base`:

      agi gparted

### Remote Filesystems

#### Setup NFS Client Support

- Install NFS utilities `:role:base`:

      agi nfs-common

      yi nfs-utils

#### Setup SMB (CIFS) Client Support

Needed for Windows network shares.

- Install smbfs `:role:base`:

      agi cifs-utils

      yi cifs-utils

#### Setup autofs

(automated)

- Install `:role:base`:

      agi autofs

      yi autofs

- (ubuntu) Enable /net:

      mkdir /net

  Uncomment this line in `/etc/auto.master`:

      vim /etc/auto.master

      /net -hosts

- Enable autofs service (restarting because Ubuntu starts the daemon running
  before `/etc/auto.master` can be edited):

      systemctl enable autofs
      systemctl restart autofs

## Create Users

(automated)

- See `install-linux-local/local-accounts.yml`.

- If there are pre-existing home directories, generally it's best to rename them
  out of the way before creating the new users. That way, the old configuration
  files are left intact and won't cause problems with newer versions of the
  software. When ready, the old data files can be moved into place.

  For manual creation, the `-m` (create home directory) and `-s /bin/bash`
  (setup shell) switches are needed only on Ubuntu, but they work properly on
  other distros as well.  For example:

      useradd -u 1001 -m -s /bin/bash -c 'Some user' someuser

- Set password for login accounts (**one at a time**), e.g.:

      passwd someuser

- Modify groups to make `someuser` an `administrator`:

  - (ubuntu) (Note: This entails more groups than `poweruser` has):

        for i in adm cdrom sudo plugdev lxd lpadmin sambashare video; do
            usermod -aG $i someuser
        done

  - (fedora) (centos):

        usermod -aG wheel someuser

- Create `somegroup`:

      groupadd -g 1001 somegroup

- Add users to `somegroup`:

      for i in someuser; do usermod -aG data $i; done

### Post-create users (ZFS datasets)

- (ubuntu) (manual) Migrate to user-specific ZFS datasets:

  - Done by hand at present separately for each desired user.

  - By convention, Ubuntu installer appends a `${uuid}` to datasets to avoid
    collision with datasets for other installations:

        rpool/USERDATA/root_${uuid}               -> /root
        rpool/USERDATA/${user}_${uuid}            -> /home/$user
        rpool/USERDATA/${user}_${uuid}/dataset1   -> /home/$user/dataset1
        rpool/USERDATA/${user}_${uuid}/dataset2   -> /home/$user/dataset2

  - Set `user` variable:

        user=mike

  - Detect `$uuid` from pre-existing `root` dataset:

        uuid=$(zfs list -rd 1 rpool/USERDATA |
          perl -ne 'if (m@^rpool/USERDATA/root_(\S+)@) { print "$1\n"; }')

        echo "$uuid"

  - Derive variables:

        user_uuid="${user}_$uuid"
        user_home="/home/$user"
        user_home_orig="/home/$user-orig"

  - Move home directory out of the way:

        mv "$user_home" "$user_home_orig"

  - Create outer dataset for the user (used for `$HOME` as well):

        zfs create \
          "rpool/USERDATA/$user_uuid" \
          -o canmount=on \
          -o mountpoint="$user_home"

  - (optional) Create any additional ZFS datasets living below `$HOME`:

        zfs create \
          "rpool/USERDATA/$user_uuid/vms" \
          -o canmount=on \
          -o mountpoint="/home/$user/vms"

        zfs create \
          "rpool/USERDATA/$user_uuid/projects" \
          -o canmount=on \
          -o mountpoint="/home/$user/projects"

  - Change ownership of all mounts to user, then restore data back into place:

        chown -R "$user": "$user_home"
        rsync -a "$user_home_orig/" "$user_home/"

  -  If successful, remove the old directory:

        # !! Only if successful above.
        rm -rf "$user_home_orig/"

## SSH Setup

### SSH Client Setup

- Bring over old `~/.ssh/` contents as desired.

- To create `~/.ssh/` on the new machine with proper permissions, initiate a
  login then abandon it via Ctrl-C:

      ssh localhost     # Then CTRL-C without typing password

- May also copy an id to `newmachine` via:

      ssh-copy-id -i ~/.ssh/id_rsa newmachine

- Configure SSH clients. Note that host-specific settings should come first,
  since the first-found setting that matches wins:

      vim /etc/ssh/ssh_config

  (manual) TODO: Ansible

  Contents:

      # Add these lines at the top of the file:
      Host host1 host1.domain.com
              Port 12345

      # General settings:
      Host *
              ForwardX11 yes
              ServerAliveInterval 300
              SendEnv COLORFGBG

- (manual) Create `~/.ssh/config.d` directory concept:

      mkdir ~/.ssh/config.d
      echod -o ~/.ssh/config '
        Include config.d/*.conf
      '

  Example usage:

      echod -o ~/.ssh/config.d/example '
        # Example file.
        Host somehost.com
          ForwardX11 no
      '

  Note: the `config` file is not in homegit (yet) because of the need for proper
  permissions on `~/.ssh`.

### SSH Server Setup

(manual) TODO Ansible

- References:
  - SSH PasswordAuthentication vs ChallengeResponseAuthentication:
    <https://blog.tankywoo.com/linux/2013/09/14/ssh-passwordauthentication-vs-challengeresponseauthentication.html>
  - OpenSSH: requiring keys, but allow passwords from some locations:
    <https://mwl.io/archives/818>

- Perform system-specific and/or network-specific configuration:

    vim /etc/ssh/sshd_config

- (ubuntu) Configure ssh firewall:

      # ssh already allowed by default on port 22, so this is redundant:
      ufw allow ssh

- (fedora) (centos) Configure firewall:

      # On CentOS, ``ssh`` is already added.
      firewall-cmd --add-service ssh
      firewall-cmd --permanent --add-service ssh

- Enable and (re)start the ssh service:

      # Ubuntu:
      systemctl enable ssh.service
      systemctl restart ssh.service

      # Non-Ubuntu:
      systemctl enable sshd.service
      systemctl restart sshd.service

## Base Version Control

### Base Git

- For latest version, add the Git PPA before installation:

      - Reference: https://launchpad.net/~git-core/+archive/ubuntu/ppa

  - Add PPA:

        add-apt-repository -y --update ppa:git-core/ppa

- Install `:role:base`:

      agi git

      yi git

### Base Mr/MyRepos

- Now known as "myrepos" tool: <https://myrepos.branchable.com/>

- Install `:role:base`:

      agi myrepos

      yi myrepos

- Will acquire `~/.mrconfig` from clone of `home2.git` (this comes later).

### Base Subversion

- Install `:role:base`:

      agi subversion

      yi subversion

## Python Base Setup

### Python Base Plan

Goals:

- Do not conflict with the system package manager, which implies keeping "sudo
  pip install" to a bare minimum (ideally, zero such packages should be
  installed using pip into the system's Python directories).
- Allow global installation of utilities (e.g., `findx`) that work for all
  users.
- Allow installation of arbitrary versions of Python, with simultaneous
  activation of multiple major.minor versions.
- Allow creation of virtual environments for arbitrary Python versions. Changing
  global defaults for Python interpreters should not impact the envs.
- In support of scripts living in `~/bin`, install any dependencies in per-user
  `~/.local/lib/pythonx.y` via `pipxy. install --user`.
- Assume python2.7 and python3.5+ are both installed for scripts.

Supported use cases:

- Installing a Python 3 tool globally: `pipxg install`
- Installing a Python 2 tool globally: `pipsig2 install`
- Developing: `mkvirtualenv -p python X.Y`:
  - Gets latest pip, setuptools, wheel automatically.
- Installing per-user tooling:
  - pipx or pipsi; should put into a virtual environment, should get latest pip
    and such that way.
  - Python 3-only venv (no virtualenvwrapper support):
    - Create:

          python3 -m venv envname

    - Activate, upgrade pip/setuptools, install wheel:

          cd envname
          . bin/activate
          pip install -U pip setuptools wheel

### Python Base Support

(automated)

- Install venv + pip `:role:workstation`:

      agi python3-venv python3-pip

- Make symlinks to prefer Python 3-based tooling without version suffix:

      ln -s /usr/bin/python3 /usr/local/bin/python
      ln -s /usr/bin/pip3 /usr/local/bin/pip

- The pipx home directory will be `/usr/local/lib/pipx`, and binaries will live
  in `/usr/local/bin`.

- Create `pipxg` wrapper for global use
  `:extract-echod:roles/pipxg/files/pipxg`:

      echod -o /usr/local/bin/pipxg '
        #!/bin/sh

        PIPX_HOME=/usr/local/lib/pipx
        PIPX_BIN_DIR=/usr/local/bin
        export PIPX_HOME PIPX_BIN_DIR

        umask 002
        exec pipx "$@"
      '

  Make `pipxg` executable:

      chmod +x /usr/local/bin/pipxg

- Use a temporary "user" area to install pipx:

      PYTHONUSERBASE=$PWD/pipxtmp pip install --user pipx

- Bootstrap `pipx` into the global pipx area:

      PYTHONUSERBASE=$PWD/pipxtmp \
        PATH=$PYTHONUSERBASE/bin:$PATH pipxg install pipx

- Remove the temporary user area:

      rm -rf pipxtmp

- Verify global installation of `pipx` using `pipxg`:

      pipxg list

  Expected output should be similar to:

      venvs are in /usr/local/lib/pipx/venvs
      binaries are exposed on your $PATH at /usr/local/bin
         package pipx 0.13.1.1, Python 3.6.7
          - pipx

- Install virtualenvwrapper:

      pipxg install virtualenvwrapper

  For some reason, two of the binaries must be manually symlinked:

      ln -s /usr/local/lib/pipx/venvs/virtualenvwrapper/bin/virtualenv \
        /usr/local/bin

      ln -s /usr/local/lib/pipx/venvs/virtualenvwrapper/bin/virtualenv-clone \
        /usr/local/bin

- Configure per-user python3-based virtualenvwrapper based on
  <https://virtualenvwrapper.readthedocs.org/en/latest/> (all users):

      echod -a ~/.profile '
        export WORKON_HOME=$HOME/envs
        export PROJECT_HOME=$HOME/projects
        VIRTUALENVWRAPPER_PYTHON=/usr/local/lib/pipx/venvs/virtualenvwrapper/bin/python
        if [ -x "$VIRTUALENVWRAPPER_PYTHON" ]; then
            export VIRTUALENVWRAPPER_PYTHON
        else
            unset VIRTUALENVWRAPPER_PYTHON
        fi
      '

      echod -a ~/.bashrc '
        if [ -n "$(command -v virtualenvwrapper.sh)" ]; then
            . virtualenvwrapper.sh
        fi
      '

- Create area for envs and tell Git to ignore it:

      mkdir -p ~/envs
      echo envs >> ~/.gitignore

- Logout, login again to activate virtualenvwrapper.

- Make and deactivate a test virtualenv:

      mktmpenv

      pip install cowsay
      cowsay it works
      deactivate

### Python 2 Base Support

(manual)

- Install Python 2 interpreter and pip:

      agi python python-pip

- Create Python 2 pipsi area:

      mkdir -p /usr/local/lib/pipsi2/bin

- Setup paths for pipsi2:

      echod -o /etc/profile.d/pipsi2.sh '
        new="/usr/local/lib/pipsi2/bin"
        after="/usr/local/bin"
        colonized_path=":$PATH:"

        if [ -n "${colonized_path##*:${new}:*}" ]; then
            pre="${colonized_path%%:$after:*}"
            if [ "$pre" = "$colonized_path" ]; then
                # $after was not present, so just prepend the new path.
                PATH="$new:$PATH"
            else
                post="${colonized_path#*:$after:}"
                path="$pre:$after:$new:$post"
                path="${path%:}"
                PATH="${path#:}"
            fi
        fi
      '

  **Logout/login** or use other method to ensure the PATH includes these areas.

- Configure sudo to use these paths by prepending them to the
  `Defaults secure_path` line, e.g.:

      visudo

      # Create this path line:
      Defaults        secure_path="/usr/local/sbin:/usr/local/bin:/usr/local/lib/pipsi2/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin"

- Create and activate the pipsi2 environment:

      cd /usr/local/lib/pipsi2
      virtualenv -p python2 pipsi
      . pipsi/bin/activate

- Install pipsi:

      pip install pipsi

- Deactivate the `pipsi2` venv:

      deactivate

- Symlink `pipsi` into the path:

      ln -s /usr/local/lib/pipsi2/pipsi/bin/pipsi /usr/local/lib/pipsi2/bin

- Setup `pipsig2` script:

      echod -o /usr/local/lib/pipsi2/bin/pipsig2 '
        #!/bin/sh

        umask 002
        export PIPSI_HOME=/usr/local/lib/pipsi2
        export PIPSI_BIN_DIR=/usr/local/lib/pipsi2/bin
        exec "$PIPSI_BIN_DIR/pipsi" "$@"
      '
      chmod +x /usr/local/lib/pipsi2/bin/pipsig2

- Verify global installation of `pipsi` and `pipsig2`:

      pipsig2 list

  Expected output should be similar to:

      Packages and scripts installed through pipsi:
        Package "pipsi":
          pipsi

# (optional) (ubuntu) Remove Snaps

References:

- "Firefox on Ubuntu 22.04 from .deb (not from snap)":
  <https://news.ycombinator.com/item?id=31138413>
- <https://askubuntu.com/questions/1369159/how-to-remove-snap-completely-without-losing-firefox>
- <https://ubuntuhandbook.org/index.php/2022/04/install-firefox-deb-ubuntu-22-04/>
- <https://haydenjames.io/remove-snap-ubuntu-22-04-lts/>
- <https://www.debugpoint.com/2021/09/remove-firefox-snap-ubuntu/>
- <https://askubuntu.com/questions/1399383/how-to-install-firefox-as-a-traditional-deb-package-without-snap-in-ubuntu-22>
- <https://www.omgubuntu.co.uk/2022/04/how-to-install-firefox-deb-apt-ubuntu-22-04>
- <https://balintreczey.hu/blog/firefox-on-ubuntu-22-04-from-deb-not-from-snap/>
- <https://www.freecodecamp.org/news/managing-ubuntu-snaps/>

Rationale:

- Snap-based Firefox won't work with `/localhome`.

- Snaps require separate access to snap store for installation/updates.

- Snap-based apps integrate poorly with other parts of the system (plugin
  issues).

- Snaps are slow to launch.

## (ubuntu) Purge Snaps

- Purge `snapd`:

      apt-get purge snapd

- Prevent `snapd` reinstallation:

      echod -o /etc/apt/preferences.d/nosnap.pref '
        Package: snapd
        Pin: release a=*
        Pin-Priority: -10
      '

- Remove leftover `snap/` directories:

      rm -rf /home/*/snap/ /root/snap/

- Remove `/var/snap` mount point.  This is found under a randomly created name:

      zfs list | grep /var/snap

  With sample output:

    rpool/ROOT/ubuntu_itujb4/var/snap  <...> /var/snap

  Remove the volume via:

    zfs destroy rpool/ROOT/ubuntu_itujb4/var/snap

  NOTE: if receive error:

      cannot destroy 'rpool/ROOT/ubuntu_itujb4/var/snap': dataset is busy

  then there may be snap-related processes running.  Check and kill as
  necessary:

    pgrep -a snap

## (ubuntu) Add Mozilla PPA

(automated)

TODO: automated method uses Ansible `apt_repository` which still uses the old
method via`apt-key`.  Consider alternate method that does the below work.

- Use `ppa:mozillateam` for `.deb`-based Firefox.  This provides packages for
  Thunderbird as well.

- `ppa:mozillateam` points to:
  <https://launchpad.net/~mozillateam/+archive/ubuntu/ppa>

- Visiting the above URL leads to these sources lines:

      deb https://ppa.launchpadcontent.net/mozillateam/ppa/ubuntu jammy main
      deb-src https://ppa.launchpadcontent.net/mozillateam/ppa/ubuntu jammy main

  and this signing key fingerprint:

      0AB215679C571D1C8325275B9BDB3D89CE49EC21

- Download the key based on the fingerprint and store in `/etc/apt/keyrings`
  (adjusting the `--keyring` and fingerprint at the end of the command):

      gpg \
        --homedir /tmp \
        --no-default-keyring \
        --keyserver keyserver.ubuntu.com \
        --recv-keys \
        --keyring /etc/apt/keyrings/mozillateam.gpg \
        0AB215679C571D1C8325275B9BDB3D89CE49EC21

- Create a `.sources` file for `mozillateam`:

      echod -o /etc/apt/sources.list.d/mozillateam.sources "
        Types: deb
        URIs: https://ppa.launchpadcontent.net/mozillateam/ppa/ubuntu/
        Suites: $(lsb_release -cs)
        Components: main
        Signed-By: /etc/apt/keyrings/mozillateam.gpg
      "

- Update APT cache:

      apt update

- Install Firefox as `.deb`:

      agi firefox

  This restores Firefox (because the snap version was likely purged).

  For other Firefox installation methods, see Firefox section.

# Ansible Control Node

## Ansible via pipxg

This is the preferred installation method.

- Install `:role:workstation`:

      pipxg install --include-deps ansible

  Note: the `--include-deps` switch is necessary for `pipx` to install
  `ansible` because it's built from a number of dependent packages that expose
  the various commands.

## Ansible via Package Manager

Alternatively, Ansible may be installed from the package manager using a PPA to
get the latest version:

    apt update
    apt install -y software-properties-common
    apt-add-repository --yes --update ppa:ansible/ansible
    apt install -y ansible

# Clone Standard Repositories

## Clone home.git, home2.git

(automated)

- Bring over `.home.git` and `.home2.git`:

      cd ~
      git clone --bare ssh://server/srv/git/home.git ~/.home.git
      git clone --bare ssh://server/srv/git/home2.git ~/.home2.git

- Setup temporary aliases:

      alias homegit='GIT_DIR=~/.home.git GIT_WORK_TREE=~  git'
      alias home2git='GIT_DIR=~/.home2.git GIT_WORK_TREE=~  git'

- Diff if desired to see what will be overwritten:

      homegit diff --cached
      home2git diff --cached

- Perform hard reset:

      homegit reset --hard
      home2git reset --hard

- Update to setup ignores:

      homegitupdate

- Restart shell to acquire Bash aliases, PATH (including `~/bin`), etc.

- As root:

      cd ~
      git clone --bare ~mike/.home.git
      git clone --bare ~mike/.home2.git

      # Continue steps from above.

## Clone vimfiles, vimfiles-local

- Clone vimfiles, vimfiles-local:

  (automated)

      git clone ssh://server/srv/git/vimfiles.git ~/.vim
      git clone ssh://server/srv/git/vimfiles-local.git ~/.vimlocal

- Perform additional Vim setup:

  (manual)

      cd ~/.vim/bundle/cpsm
      ./install.sh

- (optional) After upgrade, restore these from old installation:

      ~/.viminfo
      ~/.cache/vim

- Clone vimfiles, vimfiles-local for root:

  (automated)

      git clone ~mike/.vim ~/.vim
      git clone ~mike/.vimlocal ~/.vimlocal

- Perform additional Vim setup for root:

  (manual)

      cd /root/.vim/bundle/cpsm
      ./install.sh

## Bash

(manual)

- **Retain original `.bash_history`**:

  - For `root` and `mike`, prepend `~/.bash_history` from previous installation
    to current history file using text editor.

- (homegit) Use `~/.bashrc` settings from source control in general.

- The version of readline used in Bash 5.1 enables "bracketed paste" by default,
  which causes text pasted into the Bash prompt to stay highlighted and not
  execute (even if the text contains a final newline).

  (homegit) To restore the old behavior, create `~/.inputrc` with contents:

      set enable-bracketed-paste off

  To manually disable bracketed past, entered this command directly at the Bash
  prompt:

      bind 'set enable-bracketed-paste off'

  To manually query "bracketed paste" mode:

      bind -v | grep bracketed

- References:

  - <https://utcc.utoronto.ca/~cks/space/blog/unix/BashBracketedPasteChange?showcomments>
  - <https://news.ycombinator.com/item?id=24801490>
  - <https://thejh.net/misc/website-terminal-copy-paste> (risk of untrusted
    pasting)

## Update grub

(manual) TODO Ansible

- Update grub configuration to display boot-time messages and append any
  hardware-specific options.

- (ubuntu): Change grub configuration lines:

      vim /etc/default/grub

      #GRUB_TIMEOUT_STYLE=hidden
      GRUB_TIMEOUT=2

  Then update grub to regenerate `/boot/grub/grub.cfg` and the initramfs:

      update-grub

- (fedora) (centos): Update grub kernel command line options:

      vim /etc/default/grub

  Remove `rhgb` and `quiet` and append any hardware-specific options.

  Then update the grub configuration file and regenerate the initramfs:

      # (BIOS systems)
      grub2-mkconfig -o /boot/grub2/grub.cfg
      # (EFI systems)
      grub2-mkconfig -o /boot/efi/EFI/centos/grub.cfg

      dracut --force

  **NOTE** Do not point at `/etc/grub2.cfg`, as that symlink will be
  clobbered because of backup behavior in `grub2-mkconfig`.

# Graphical Environment

## Plasma Installation

- Optional for systems that will run X11.

- Install `:role:workstation`:

      agi kubuntu-desktop

      yi @'KDE Plasma Workspaces'

**NOTE** Do not login to Plasma yet; wait until home directory has been setup.

- Verify will boot graphically:

      systemctl get-default

  If `multi-user.target`, switch to graphical:

      systemctl set-default graphical.target

- Launch display manager now:

      systemctl isolate graphical.target

- Restart `gdm` so that Plasma becomes a valid option:

      systemctl restart gdm

## (ubuntu) Kubuntu Extras

- Install extras `:role:workstation`:

      agi kubuntu-restricted-extras

  Provides codecs, flash player, Microsoft fonts, ...

# System update and reboot

- (ubuntu) From a root prompt, install updates:

      apt-get -y dist-upgrade

- (fedora) (centos) From a root prompt, install updates:

      yum -y upgrade

- **Note**: a restart may be needed after updates:

      reboot

# Mission-Critical Apps

## Login as `mike`

- May now login as `mike` user (into Plasma if installed).

- (manual) Change default locations:

      xdg-user-dirs-update --set DOCUMENTS  ~/x
      xdg-user-dirs-update --set DOWNLOAD   ~/download
      xdg-user-dirs-update --set MUSIC      ~/music
      xdg-user-dirs-update --set PICTURES   ~/pictures
      xdg-user-dirs-update --set VIDEOS     ~/videos

  Note: Leave the following directories at their original names with leading
  capital letters, since they are potentially still useful but will stay out of
  the way of tab-completion for more common directories:

  - `Desktop`
  - `Public`
  - `Templates`

- (manual) Remove default directories, setup symlinks:

      cd ~
      rmdir Documents Downloads Music Pictures Videos

      ln -s /m/shared/pictures ~/pictures
      ln -s /m/shared/videos ~/videos

      # (non-bolt)
      ln -s /home/m/mike/x ~/x
      ln -s /home/m/shared/download ~/download
      ln -s /home/m/shared/music/Music ~/music

      # (bolt)
      ln -s /m/mike/x ~/x
      ln -s /m/shared/download ~/download
      ln -s /m/shared/music/Music ~/music

## KeePassx/KeePassxc

- KeePassXC is the newer community fork of KeePassX. It uses database format 2.

- Ensure using version 2.x. Note: CentOS needs `keepassx2` (v2.0.3) to get
  version 2.x; `keepassx` is older 1.x. Sadly, command name is `keepassx2` in
  this case. The `kee` script deals with the inconsistent naming.

- Install `:role:home`:

      agi keepassxc

      yi keepassxc

- Create mount points:

      sudo mkdir -p /mnt/{keepass,keemirror,keebackup}

  Ansible `:role:home`:

  ```yaml
  - name: Create Keepass mount points
    file:
      path: "/mnt/{{ item }}"
      state: directory
      mode: 0755
    loop:
      - keepass
      - keemirror
      - keebackup
  ```

- Setup mount points in `/etc/fstab`:

      echod -a /etc/fstab '
      LABEL=KEEPASS   /mnt/keepass    vfat shortname=lower,user,noauto 0 0
      LABEL=KEEMIRROR /mnt/keemirror  vfat shortname=lower,user,noauto 0 0
      LABEL=KEEBACKUP /mnt/keebackup  vfat shortname=lower,user,noauto 0 0
      '

  Ansible `:role:home`:

  ```yaml
  - name: Setup Keepass fstab entries
    mount:
      path: "/mnt/{{ item }}"
      src: "LABEL={{ item | upper }}"
      fstype: vfat
      boot: false
      opts: "shortname=lower,user"
      state: present
    loop:
      - keepass
      - keemirror
      - keebackup
  ```

- (manual) Run KeePassXC, then setup via Tools | Settings:

  - General | uncheck "Load previous databases on startup".

- Use `~/bin2/kee` script to maintain mirror/backup.

## KDE Wallet/kwallet

- <http://homepages.inf.ed.ac.uk/da/id/gpg-howto.shtml>
- <https://wiki.archlinux.org/index.php/KDE_Wallet>

Use Blowfish encryption with KDE wallet instead of GPG.

- (ubuntu) kdewallet is already setup.

- (centos) Wallet isn't setup properly out-of-the-box:
  - Start `kdewalletmanager`; runs in the task bar.
  - Open the wallet manager.
  - Create the default wallet; must be named `kdewallet`.
  - Choose blowfish encryption instead of GPG (too hard to figure out GPG).

## Keychain

(automated)

Gentoo keychain is a small script that sets up ssh-agent at first login. The
agent thereafter will maintain the keys in memory for passwordless usage of ssh.

- Install `:role:workstation`:

      agi keychain

      yi keychain

- (homegit) Create `ssh-identities` script to list valid ssh identities:

      echod -o ~/bin/ssh-identities '
        #!/bin/sh

        find ~/.ssh -maxdepth 1 -name 'id_*' -not -name '*.pub' -print
      '
      chmod +x ~/bin/ssh-identities

- (homegit) Append the following configuration lines:

      echod -a ~/.profile '
        # Require interactive shell, keychain present, and stdin/stdout are ttys.
        if [ "$PS1" ] && [ "$(command -v keychain)" ] && tty -s && tty -s 0<&1; then
            eval "$(keychain --eval --nogui --quiet "$(~/bin/ssh-identities)")"
        fi
      '

- For ssh-add during Plasma startup:

  - First, setup KDE wallet with a key (run `kwalletmanager`).

  - (homegit) Create script to source at Plasma startup to launch `ssh-agent` if
    necessary:

        mkdir -p ~/.config/plasma-workspace/env
        echod -o ~/.config/plasma-workspace/env/ssh-agent-startup.sh '
          [ -n "$SSH_AGENT_PID" ] || eval "$(ssh-agent -s)"
        '

  - (homegit) Create script to enumerate SSH identities:

        echod -o ~/bin/ssh-identities '
          #!/bin/sh

          find ~/.ssh -maxdepth 1 -name 'id_*' -not -name '*.pub' -print
        '

        chmod +x ~/bin/ssh-identities '

  - (homegit) Create `.desktop` to invoke `ssh-identities`
    at Plasma startup:

        mkdir -p ~/.config/autostart
        echod -o ~/.config/autostart/ssh-identities-add.desktop '
          [Desktop Entry]
          Type=Application
          Name=ssh-identities-add
          Exec=ssh-identities-add
        '

## cron

- Adjust root's crontab as follows:

      vim /etc/crontab

  Add these lines:

      SHELL=/bin/bash
      MAILTO=root

## anacron

(manual) TODO Ansible

- anacron controls the launch of daily and weekly jobs in `/etc/cron.daily` and
  `/etc/cron.weekly`.

- Adjust time of daily launch of anacron:

      vim /etc/cron.d/anacron

      30 2    * * *   root    test -x /etc/init.d/anacron && ...

## Unison

- As of Unison v2.52, there is replica format support across Unison versions
  back to v2.48:

  - <https://github.com/bcpierce00/unison/wiki/2.52-Migration-Guide>

  In addition, the OCaml version no longer matters.

- The easiest solution for now is to download binaries from Github, as distros
  haven't yet gotten v2.52:

  - <https://github.com/bcpierce00/unison/releases/download/v2.52.1/unison-v2.52.1+ocaml-4.14.0+x86_64.linux.tar.gz>

  - <https://github.com/bcpierce00/unison/releases/download/v2.52.1/unison-v2.52.1+ocaml-4.14.0+x86_64.windows.zip>

  On the server, extract as `unison-<major>.<minor>`:

      mkdir unison-v2.52.1
      cd unison-v2.52.1
      tar -zxf ../unison-v2.52.1+ocaml-4.14.0+x86_64.linux.tar.gz
      cp bin/unison /usr/local/bin/unison-2.52

  On clients, extract as above, and symlink to `unison`:

      # Perform extraction to /usr/local/bin as above, then:
      ln -s /usr/local/bin/unison-2.52 /usr/local/bin/unison

- For now, `~/bin/unison.sh` uses `unison -addversionno` to invoke
  `unison-<major>.<minor>` on the server; eventually when all clients have
  upgraded to v2.52+, the server can have the `/usr/local/bin/unison` symlink
  and clients can stop using `-addversionno`.

### Configure unison

- (non-server) As root, create `/home/m` directory:

      sudo mkdir /home/m
      sudo chown -h mike:data /home/m
      sudo chmod 775 /home/m

#### After Distro Upgrade

- After distro upgrade, can restore unison files from original directories,
  e.g.:

      rsync -ax /path/to/old/home_m/ /home/m/
      rm -rf /root/.unison

      # For casey:
      ln -s /home/m/sys/unison/casey-root ~/.unison

      # For mobi:
      ln -s /home/m/sys/unison/mobi-root ~/.unison

### Unison From Scratch

- Create location for configuration:

      mkdir -p /home/m/sys/unison/mobi-root

- Symlink `/root/.unison` to `/home/m/sys/unison/mobi-root`:

      rm -rf /root/.unison
      ln -s /home/m/sys/unison/mobi-root /root/.unison

- Steal and modify `default.prf` from `/m/sys/unison/xxx`, placing into
  `/root/.unison/default.prf`, e.g.:

      cp /m/sys/unison/mobi-root/default.prf /root/.unison/default.prf
      vim /root/.unison/default.prf

- Have to pre-create sub-paths from `default.prf` above.

  **Verify the paths before doing this**. Check for `path = xxx` in
  `default.prf` and pre-create these paths:

      cd /home/m
      mkdir -p mike shared/{download,music} sys/{bin,unison}

- **Examine and remove any old Unison archive files** for previous
  synchronization attempts (**on both sides**, if using saved `/home/m`).
  Archive files start with `ar`, and they have an associated fingerprint file
  starting with `fp`. Delete both after finding out which file matches:

      ssh root@bolt
      cd /root/.unison
      less ar8e1f839be1ad42103cbd6c4f18e0d12d
      rm ar8e1f839be1ad42103cbd6c4f18e0d12d
      rm fp8e1f839be1ad42103cbd6c4f18e0d12d

### Running Unison

- Synchronize with server (as root):

      unison -addversionno -ui text

  **Note** The above `-addversionno` switch ensures that the proper version of
  unison is run on the server side. It may be left off when the version is known
  to be the same.

  The `~/bin/unison.sh` script forces `-addversionno` to ensure the right
  version is always used.

- Setup nightly unison sync:

  - Add the following to `/etc/crontab`:

        # min hour dom  mon dow  user  what
        # Main machine (casey):
          30  2     *    *   *   root  /root/bin/unison.sh -batch -terse
        # Laptop (mobi):
          30  4     *    *   *   root  /root/bin/unison.sh -batch -terse

## Firefox

### Firefox Installation

#### (ubuntu) Firefox Installation from `.deb`

- Firefox is generally installed by default on Ubuntu; if manual installation of
  the `.deb` is required:

      agi firefox

  **NOTE**, however, that the stock Ubuntu repository's `firefox` package is
  transitional; it merely installs Firefox as a snap.  To truly get a
  `.deb`-based installation requires use of the Mozilla PPA (see previous
  instructions).

#### Firefox Installation from Tarball

- Download official tarball (e.g., version `101.0.1`):

      cd /tmp
      wget -c https://ftp.mozilla.org/pub/firefox/releases/101.0.1/linux-x86_64/en-US/firefox-101.0.1.tar.bz2

- Expand tarball into `/opt/firefox`, then rename and symlink executable:

      cd /opt
      tar -xf /tmp/firefox-101.0.1.tar.bz2
      mv firefox firefox-101.0.1
      ln -sf $PWD/firefox-101.0.1/firefox /usr/local/bin/firefox

### Firefox Notes

#### Firefox Determine Profile Directory

Use "Help | More Troubleshooting Information" to determine the profile
  directory:

- Reference: <https://support.mozilla.org/en-US/kb/profiles-where-firefox-stores-user-data#w_how-do-i-find-my-profile>

- For typical Firefox, this will be:

      ~/.mozilla/firefox/<random>.default/

- For snap-based Firefox, the tree lives instead at:

      ~/snap/firefox/common/.cache/mozilla/firefox/<random>.default/

#### Firefox Profile Important Files

These may be copied individually from an old profile in lieu of copying the
entire profile.

- History:

      places.sqlite
      places.sqlite-wal

- Saved passwords:

      key4.db
      logins.json

- Autocomplete history:

      formhistory.sqlite

- Cookies:

      cookies.sqlite

- Open tabs and windows:

      sessionstore.jsonlz4

#### Firefox Set as Default Browser

- To have Firefox make itself the default browser, exit Firefox and run:

      firefox -silent -setDefaultBrowser

  See <https://kb.mozillazine.org/Default_browser> for details.

- (ubuntu) Setup `x-www-browser` alternative to be Firefox:

      sudo update-alternatives --config x-www-browser

#### Firefox re-enabling copy/paste, right-click

- References:
  - "Ask HN: How to disable right-click blocking in the browser"
    <https://news.ycombinator.com/item?id=32285459>

### Firefox Configuration

#### Firefox Profiles

Firefox profile names are awkward.  Previous to Firefox 67, profiles were named:

    <random>.default

In Firefox 67, profiles are now separated by Firefox release (Nightly, Beta,
Developer Edition, and Extended Support Release (ESR) variants):
<https://support.mozilla.org/en-US/kb/dedicated-profiles-firefox-installation>

Now normal release versions of Firefox create profiles named as:

    <random>.default-release

Firefox 100 on Ubuntu even seems to create *both* variants at the same time,
setting the `.default-release` version as the "default" profile to use:

    <random1>.default
    <random2>.default-release

An example profile setup (after running Firefox):

```ini
[Install4F96D1932A9F858E]
Default=g1pr8a68.default-release
Locked=1

[Profile1]
Name=default
IsRelative=1
Path=sl0b92ny.default
Default=1

[Profile0]
Name=default-release
IsRelative=1
Path=g1pr8a68.default-release

[General]
StartWithLastProfile=1
Version=2
```

Because of the `Default=1` setting, `Profile1` is the default profile (with the
path `sl0b92ny.default`).

#### (recommended) Symlinking the Profile

The easiest way to get a predictable name is to create a symlink to the profile
directory, e.g.:

    cd ~/.mozilla/firefox
    ln -s sl0b92ny.default mike

#### (alternative) Create a New Firefox Profile

Alternatively, a new profile can be created with a predictable name.

- Launch the profile manager:

      firefox -ProfileManager

  - Create a new profile `mike`.

  - Choose "Choose Folder".

  - Add a directory named `mike`.

  - Choose "Open" to use that folder for the profile.

  - Choose "Finish" to complete profile creation.

  - Keep "Use the selected profile without asking at startup" checked.

  - Select `default-release`; choose "Delete Profile".

  - Select `default`; choose "Delete Profile".

  - Choose "Start Firefox"; do not just "Exit".

Note that if you choose "Exit" instead of "Start Firefox" after creating the
profile, the new profile won't be correctly marked as the default in
`~/.mozilla/firefox/profiles.ini`; that file will contain something like this:

```ini
[Install4F96D1932A9F858E]
Default=
Locked=1

[Profile0]
Name=mike
IsRelative=1
Path=mike

[General]
StartWithLastProfile=1
Version=2
```

Starting Firefox will lead to the Profile Manager dialog once again until "Start
Firefox" is chosen.  Afterward, `profiles.ini` will instead contain:

```ini
[Install4F96D1932A9F858E]
Default=mike
Locked=1

[Profile0]
Name=mike
IsRelative=1
Path=mike
Default=1

[General]
StartWithLastProfile=1
Version=2
```

Allowing Firefox to start sets the `Default=<profile_name>` key in
`[InstallXXXXXX]` and the `Default=1` key in `[Profile0]`.

#### (optional) Create Extra Firefox Profiles

To create an additional profile (e.g., `ExtraProfileName`), ensure Firefox is
not running and repeat the previous steps for profile creation, but:

- Before choosing "Start Firefox", select your preferred default profile and
  check "Use the selected profile without asking at startup" (otherwise, the
  newly created profile will be the default).

- As before, use "Start Firefox" instead of "Exit" to ensure that `profiles.ini`
  is updated correctly.

- To launch with new profile when no other Firefox is running:

      firefox -P ExtraProfileName

- To launch a profile while another profile is running:

      /usr/lib/firefox/firefox -P ExtraProfileName -no-remote

#### Firefox Certificate Authority

- Add drmikehenry-ca.crt certificate authority:

  - Browse to: <http://bolt.drmikehenry.com/certs/>
  - Save `drmikehenry-ca.crt` in temporary location.
  - Edit Settings | Privacy & Security | Certificates | View Certificates |
    Authorities | Import, choose `drmikehenry-ca.crt` from temporary location.
  - Check to trust for all purposes:
    - To identify websites.
    - To identify email users.
  - Verify can access: <https://bolt.drmikehenry.com/>

#### Firefox Settings

(manual):

- Enable menu bar (right-click next to tab, check `Menu Bar`).

- Enable bookmarks toolbar (right-click next to tab | `Bookmarks Toolbar` |
  `Always Show`).

##### Edit | Settings | General

###### ... Startup

- Check "Open previous windows and tabs".

###### ... Files and Applications

- Downloads | check "Always ask you where to save files".

###### ... Digital Rights Management (DRM) Content

- Check "Play DRM-controlled content"

###### ... Browsing

- Check "Always show scrollbars".

###### ... Network Settings

- Choose "Settings" button:

  - Uncheck "Enable DNS over HTTPS".
    Reference: <https://support.mozilla.org/en-US/kb/firefox-dns-over-https>

##### Edit | Settings | Home

###### ... New Windows and Tabs

- Set "Homepage and new windows" to "Custom URLs": <https://duckduckgo.com/>

- Set "New tabs" to "Blank Page".

##### Edit | Settings | Search

- Default Search Engine | set to "DuckDuckGo".

- Search Suggestions | uncheck "Show search suggestions in address bar results".

- Search Shortcuts | uncheck all search engines except DuckDuckGo.

##### Edit | Settings | Privacy & Security

- Enhanced Tracking Protection | leave at "Standard".

- Enhanced Tracking Protection | leave "Send websites a “Do Not Track” signal
  that you don’t want to be tracked" set to the default of "Only when Firefox is
  set to block known trackers".

- Logins & Passwords | check "Use a primary password" (then Change Primary
  Password).

- Address Bar - Firefox Suggest | uncheck "Suggestions from sponsors".

- Permissions | Location | Settings, check "Block new requests asking to access
  your location".

- Permissions | Notifications | Settings, check "Block new requests asking to
  allow notifications".

- Firefox Data Collection and Use:

  - Uncheck "Allow Firefox to send technical and interaction data to Mozilla".
  - Uncheck "Allow Firefox to install and run studies".
  - Uncheck "Allow Firefox to send backlogged crash reports on your behalf.

##### Visit URL `about:config`

- Turn off the full-screen notification by setting
  `full-screen-api.warning.timeout` to `0`.

- Change `browser.tabs.closeWindowWithLastTab` to `false`.

- Change `geo.enabled` to `false` to disable "share my location".

- Search for `webno`, disable both of these to avoid push notifications:

      dom.webnotifications.enabled = false
      dom.webnotifications.serviceworker.enabled = false

- (optional) Search for `dom.event.clipboardevents.enabled`, change to
  `false`.

  This setting prevents websites from disabling copy/paste.  It can also cause
  breakage for some sites.  See
  <http://www.ghacks.net/2014/01/08/block-websites-reading-modifying-clipboard-contents-firefox/>

- Disable auto-updates; this can no longer be done via a configuration setting.
  See <https://support.mozilla.org/en-US/questions/1277486>.  It requires a
  `policies.json` file:
  <https://support.mozilla.org/en-US/kb/customizing-firefox-using-policiesjson>

  Policies are defined in
  <https://github.com/mozilla/policy-templates/blob/master/README.md>.

  Article for setting up policies to avoid automatic updates:
  <https://linuxreviews.org/HOWTO_Make_Mozilla_Firefox_Stop_Nagging_You_About_Updates_And_Other_Annoying_Idiocy>

- Change `pdfjs.enableScripting` to `false` to stop running JavaScript within
  PDFs.

  Reference: <https://www.ghacks.net/2021/05/05/how-to-disable-javascript-in-pdf-documents-in-firefox/>

- Change `browser.startup.homepage_override.mstone` to `ignore` instead of a
  version number.

  Reference: <https://kb.mozillazine.org/Startup.homepage_override_url>

  > "If `browser.startup.homepage_override.mstone` is set to "ignore", the
  > browser's homepage will not be overridden after updates."

### Firefox Add-ons

#### vimium-ff

- Install URL: <https://addons.mozilla.org/en-US/firefox/addon/vimium-ff/>

##### vimium-ff Preferences

- Excluded URLs and keys | Patterns:

      https://mail.google.com/*
      https://feedly.com/*

- Custom key mappings:

      map b scrollFullPageUp

- Advanced Options:

  - Check "Don't let pages steal the focus on load".

#### uBlock Origin

- Install URL: <https://addons.mozilla.org/en-US/firefox/addon/ublock-origin/>

#### uBlock Origin Configuration

Tools | Add-ons | Preferences for uBlock Origin:

- Settings | Check "I am an advanced user".
- Filter Lists:
  - EasyList
  - EasyPrivacy
  - Annoyances: check all 7:
    - AdGuard Annoyances
    - AdGuard Social Media
    - Anti-Facebook
    - EasyList Cookie
    - Fanboy’s Annoyance
    - Fanboy’s Social
    - uBlock filters - Annoyances

#### Old Reddit Redirect

Converts <https://www.reddit.com> to <https://old.reddit.com> (much better
interface).

- Install URL:
  <https://addons.mozilla.org/en-US/firefox/addon/old-reddit-redirect/>

#### Absolute Enable Right Click

- For sites that disable right-click, copy, paste, select.
- Install URL:
  <https://addons.mozilla.org/en-US/firefox/addon/absolute-enable-right-click/>

#### Privacy Badger

- Install URL:
  <https://addons.mozilla.org/en-US/firefox/addon/privacy-badger17/>

#### No coin

- Install URL: <https://addons.mozilla.org/en-US/firefox/addon/no-coin/>

#### Tampermonkey

- Install URL:
  <https://addons.mozilla.org/en-US/firefox/addon/tampermonkey/>

#### Temporary Containers

- Install URL:
  <https://addons.mozilla.org/en-US/firefox/addon/temporary-containers/>

#### Make Medium Readable Again

- Install URL:
  <https://addons.mozilla.org/en-US/firefox/addon/make-medium-readable-again/>

### Firefox Bookmark Synchronization

- Use `~/bin2/bookmarks` to push or pull bookmarks.

- Setup cron jobs for push/pull via `crontab -e`.

- On main machine, add this cron job:

      #min hr   dom mon  dow     what

       00  04    *   *    *      ~/bin2/bookmarks push

- On mirror machines, add this cron job:

      #min hr   dom mon  dow     what

       03  04    *   *    *      ~/bin2/bookmarks pull

## Thunderbird

- References:
  - Information about using `user.js` overrides:
    <http://kb.mozillazine.org/User.js_file>

### Thunderbird Installation

- Install:

      agi thunderbird

      yi thunderbird

### Thunderbird Settings

- (mobile) Setup hosts for `mailman.drmikehenry.com`:

      echod -a /etc/hosts '
        #127.0.0.1        mailman.drmikehenry.com mailman
      '

- Can perform following steps, or else bring over entire configuration from
  previous installation:

      mkdir ~/.thunderbird
      rsync -ax old/.thunderbird/ ~/.thunderbird

- Start thunderbird.

- Close the tab "Set Up Your Existing Email Address" (if present).

- Enable menu bar (right-click next to tab, check "Menu Bar").

- Acquire `drmikehenry-ca.crt` certificate authority:
  - Browse to <http://bolt.drmikehenry.com/certs/>.
  - Save `drmikehenry-ca.crt` to a temporary location.

- Add `drmikehenry-ca.crt` certificate authority to Thunderbird:

  - Edit | Preferences | Privacy & Security | Certificates | Manage
    Certificates:
    - Authorities tab | Import | browse to use `drmikehenry-ca.crt`.
    - Check all of these:
      - Trust this CA to identify websites.
      - Trust this CA to identify email users.

- Edit | New | Existing Mail Account:

  - Your full name: Michael Henry
  - Email Address: <drmikehenry@drmikehenry.com>
  - Password: `email password for drmikehenry`
  - Press "Continue"; Thunderbird will probe for servers and configuration, but
    will get things wrong.
  - Choose configure manually.
  - Incoming Server:
    - Protocol: IMAP
    - Hostname: mailman.drmikehenry.com
    - Port: 993
    - Connection security: SSL/TLS
    - Authentication method: Normal password
    - Username: drmikehenry
  - Outgoing Server:
    - Hostname: mailman.drmikehenry.com
    - Port: 25
    - Connection security: none
    - Authentication method: no authentication
  - Choose "Re-test".
  - Choose "Done".
    - Choose "I understand the risks" and "Confirm".
  - Edit | Account Settings:
    - Choose <drmikehenry@drmikehenry.com> | Server Settings:
      - Check for new messages every 1 minutes.
      - Cleanup ("Expunge") Inbox on exit.
    - Choose <drmikehenry@drmikehenry.com> | Junk Settings:
      - Uncheck "Enable adaptive junk mail controls for this account".
      - Check "Trust junk mail headers set by", choose "SpamAssassin".
    - Choose Outgoing Server (SMTP)
      - Edit mailman.drmikehenry.com.
      - Authentication method: No authentication

- Create other accounts using same IMAP and SMTP settings:

  - <sarah@henryzone.com>
  - <andrew@henryzone.com>

- Edit | Preferences

  - General | Incoming Mails | Uncheck "Show an alert".
  - General | Incoming Mails | Uncheck "Play a sounds".
  - General | Reading & Display | Uncheck "Show only display name for people in
    my address book".
  - Composition | Composition | Forward messages inline.
  - Composition | Composition | Send Options button | Text Format | When
    sending messages...: Ask me what to do.
  - Composition | Composition | Uncheck "Use paragraph format instead of Body
    Text by default".
  - General | Config Editor (button at bottom):
    - Set `mailnews.send_plaintext_flowed` to false (avoids screwy quoting when
      using external editor add-on).

- Close Thunderbird

- For each Incoming folder, right-click | Properties and check "When getting new
  messages for this account, always check this folder" (Can do via Edit | Folder
  Properties using keyboard).

- For each Incoming folder, View | Sorted by | Threaded.

### Thunderbird Profile Name

Thunderbird creates profiles with random, unpredictable names.  Many files embed
the random name in the settings, so renaming the directory is insufficient.  For
example, `~/.thunderbird/profiles.ini` contains something like this:

```ini
[Profile1]
Name=default
IsRelative=1
Path=svewashc.default
Default=1

[InstallFDC34C9F024745EB]
Default=htjceelp.default-release
Locked=1

[Profile0]
Name=default-release
IsRelative=1
Path=htjceelp.default-release

[General]
StartWithLastProfile=1
Version=2
```

The `Default=1` in `Profile1` marks this profile as the default; the associated
path is then `svewashc.default`.

The easiest way to create a predictable name is by creating a symlink:

      cd ~/.thunderbird
      ln -s svewashc.default mike

### Thunderbird Add-ons

#### Thunderbird Nostalgy++

- Install Nostalgy++ add-on:

  - Tools | Add-ons | Search for "Nostalgy++" | Install.
  - Configure:
    - Tools | Add-ons | Extensions | choose Nostalgy++ preferences:
      - Keys tab:
        - Disable `B` ("Save message and go there").
        - Disable `Shift-B` ("Save message as suggested and go there").
        - Disable `N` ("Create new rule").
        - Disable `E` ("Convert to new rule").

### Thunderbird Additional Accounts

For POP-based removal of stuck emails, add these accounts:

User:

    postmaster%drmikehenry.com@mail.drmikehenry.com

User:

    postmaster%henryzone.com@mail.drmikehenry.com

- Use POP3, get rid of anything that says "auto" in the dialog box so it will
  allow you to manually configure things.
- Use port 995 with SSL/TLS encryption.

Leave mail on server until manual deletion.

### Thunderbird Address Book Synchronization

- Use `~/bin2/abook` to push or pull address book.

- Setup cron jobs for push/pull via `crontab -e`.

- On main machine, add this cron job:

      #min hr   dom mon  dow     what

       00  04    *   *    *      ~/bin2/abook push

- On mirror machines, add this cron job:

      #min hr   dom mon  dow     what

       03  04    *   *    *      ~/bin2/abook pull

# Desktop Automation

## wmctrl

- Used by `activate` script (for keyboard shortcuts).

- Install `:role:workstation`:

      agi wmctrl

      yi wmctrl

## xdotool

- Install `:role:workstation`:

      agi xdotool

- Use:

      # Simulate pressing of middle button:
      xdotool click 2

## Clipboard Piping

### xclip Clipboard Piping

- Install `:role:workstation`:

      agi xclip

      yi xclip

- Use:

      xclip-copyfile some/file
      xclip-pastefile

### xsel Clipboard Piping

- Install `:role:workstation`:

      agi xsel

      yi xsel

- Use:

      ls | xsel
      # middle-click somewhere to paste the result.

      xsel | grep string

- Also, setup a Bash script `clip` that just does:

      xsel -b "$@"

  That makes it easier to use the clipboard instead of the primary X selection.

## autokey

- Install `:role:workstation`:

      agi autokey-gtk

- Example: script named `paste12` to paste into 12 gnucash columns:

  - Run `autokey-gtk`.

  - Show main window | Sample Scripts, new script named "paste12":

        # 1. Ensure clipboard has desired text.
        # 2. Paste into first column, hit <Enter>.
        # 3. Invoke via Ctrl-Shift-v.
        d=0.020
        for i in range(11):
            keyboard.send_keys("<enter>")
            time.sleep(d)
            keyboard.send_keys("<ctrl>+v")
            time.sleep(d)
            keyboard.send_keys("<enter>")
            time.sleep(d)
            keyboard.send_keys("<right>")
            time.sleep(d)
        keyboard.send_keys("<enter>")
        time.sleep(d)
        keyboard.send_keys("<ctrl>+v")
        time.sleep(d)
        keyboard.send_keys("<enter>")

    Old version without delays:

        for i in range(11):
            keyboard.send_keys("<enter>")
            keyboard.send_keys("<ctrl>+v")
            keyboard.send_keys("<enter>")
            keyboard.send_keys("<right>")
        keyboard.send_keys("<enter>")
        keyboard.send_keys("<ctrl>+v")
        keyboard.send_keys("<enter>")

- Example: `east-enders-delete` script:

  - Hotkey: `<f12>`

  - Window Filter: `mythfrondend.real.mythfrontend`

  - Script:

        import time

        d=0.12
        keyboard.send_keys("m")
        time.sleep(d)
        keyboard.send_keys("<up>")
        time.sleep(d)
        keyboard.send_keys("<enter>")
        time.sleep(d)
        keyboard.send_keys("<up>")
        time.sleep(d)
        keyboard.send_keys("<enter>")

# Plasma Setup

## Setup Plasma System Settings Configuration

**NOTE** Don't try this via remote X11; some portions attach to the X server
side, which can affect settings on the client machine.

Invoke System Settings via K | Applications | System | System Settings menu
or via `systemsettings5`.

### System Settings | Appearance | Global Theme

(manual)

- Launch Feedback: Stop animation after 1 second

- Colors | Breeze Classic (this has better highlighting for the active window's
  title bar).

### System Settings | Workspace | Workspace Behavior

#### ... Screen Edges

- Set top-left corner to "No Action" (defaults to "Present Windows - All
  Desktops").

  Ansible `:role:user-plasma`:

  ```yaml
  - name: Disable "Present windows on top-left screen corner"
    kconfig:
      file: kwinrc
      group: "Effect-PresentWindows"
      key: "BorderActivateAll"
      value: "9"
  ```

- Uncheck "Maximize Windows dragged to top edge".

  Ansible `:role:user-plasma`:

  ```yaml
  - name: Disable "Maximize windows dragged to top edge"
    kconfig:
      file: kwinrc
      group: "Windows"
      key: "ElectricBorderMaximize"
      value: "false"
  ```

- Uncheck "Tile Windows dragged to left or right edge".

  Ansible `:role:user-plasma`:

  ```yaml
  - name: Disable "Tile Windows dragged to left or right edge"
    kconfig:
      file: kwinrc
      group: "Windows"
      key: "ElectricBorderTiling"
      value: "false"
  ```

#### ... Screen Locking

- Lock screen automatically after: 30 minutes

  Ansible `:role:user-plasma`:

  ```yaml
  - name: Lock screen automatically after (minutes)
    kconfig:
      file: kscreenlockerrc
      group: "Daemon"
      key: "Timeout"
      value: "60"
  ```

- Allow unlocking without password for: 60 seconds

  Ansible `:role:user-plasma`:

  ```yaml
  - name: Allow unlocking without password for (seconds)
    kconfig:
      file: kscreenlockerrc
      group: "Daemon"
      key: "LockGrace"
      value: "60"
  ```

#### ... Screen Locking | Appearance

- Uncheck "Show Media controls".

  Ansible `:role:user-plasma`:

  ```yaml
  - name: Disable "Show Media controls" on lock screen.
    kconfig:
      file: kscreenlockerrc
      groups:
      - "Greeter"
      - "LnF"
      - "General"
      key: "showMediaControls"
      value: "false"
  ```

- Choose "Darkest Hour" for lock screen image.

  (Note: "Honey Wave" is the default.)

  Ansible `:role:user-plasma`:

  ```yaml
  - name: Choose "Darkest Hour" for lock screen image.
    kconfig:
      file: kscreenlockerrc
      groups:
      - "Greeter"
      - "Wallpaper"
      - "org.kde.image"
      - "General"
      key: "Image"
      value: "/usr/share/wallpapers/DarkestHour/"
  ```

#### ... Virtual Desktops

- Add five more Desktops; name them "Desktop 2" through "Desktop 6".

  Ansible `:role:user-plasma`:

  ```yaml
  - name: Configure additional Virtual Desktops
    kconfig:
      file: kwinrc
      group: "Desktops"
      key: "Number"
      value: "6"
  ```

- Set to "2 Rows".

  Ansible `:role:user-plasma`:

  ```yaml
  - name: Set number of Virtual Desktop rows
    kconfig:
      file: kwinrc
      group: "Desktops"
      key: "Rows"
      value: "2"
  ```

### System Settings | Workspace | Window Management | Window Behavior

#### ... Focus

- Set "Window activation policy" to "Focus Follows Mouse".

  Note: tried out but didn't like "Focus Follows Mouse - Mouse Precedence". With
  that mode, if a window is manually focused, then another window pops up and is
  then closed, the focus falls to the window under the mouse instead of back to
  the original manually focused window.

  Ansible `:role:user-plasma`:

  ```yaml
  - name: Set Focus Follows Mouse
    kconfig:
      file: kwinrc
      group: "Windows"
      key: "FocusPolicy"
      value: "FocusFollowsMouse"
  ```

- Delay focus by: 0 ms

  Ansible `:role:user-plasma`:

  ```yaml
  - name: Disable focus delay
    kconfig:
      file: kwinrc
      group: "Windows"
      key: "DelayFocusInterval"
      value: "0"
  ```

- Raising windows | Uncheck "Click raises active window".

  Ansible `:role:user-plasma`:

  ```yaml
  - name: Disable "Click raises active window"
    kconfig:
      file: kwinrc
      group: "Windows"
      key: "ClickRaise"
      value: "false"
  ```

### ... Window Actions

- Inactive Inner Window Actions | Left click "Activate".

  Ansible `:role:user-plasma`:

  ```yaml
  - name: Set "Left click" to only "Activate" window
    kconfig:
      file: kwinrc
      group: "MouseBindings"
      key: "CommandWindow1"
      value: "Activate"
  ```

- Inactive Inner Window Actions | Middle click "Activate".

  Ansible `:role:user-plasma`:

  ```yaml
  - name: Set "Middle click" to only "Activate" window
    kconfig:
      file: kwinrc
      group: "MouseBindings"
      key: "CommandWindow2"
      value: "Activate"
  ```

- Inactive Inner Window Actions | Right click "Activate".

  Ansible `:role:user-plasma`:

  ```yaml
  - name: Set "Right click" to only "Activate" window
    kconfig:
      file: kwinrc
      group: "MouseBindings"
      key: "CommandWindow3"
      value: "Activate"
  ```

- Inner Window, Titlebar and Frame Actions | Set "Modifier key" to "Alt":

  Ansible `:role:user-plasma`:

  ```yaml
  - name: Set "Modifier key" to "Alt"
    kconfig:
      file: kwinrc
      group: "MouseBindings"
      key: "CommandAllKey"
      value: "Alt"
  ```

### System Settings | Workspace | Shortcuts

#### ... Shortcuts | Applications | KRunner | Default shortcuts

- Uncheck "Alt+Space"

  Ansible `:role:user-plasma`:

  ```yaml
  - name: Keep KRunner RunClipboard shortcut
    kconfig:
      file: kglobalshortcutsrc
      group: "org.kde.krunner.desktop"
      key: "RunClipboard"
      value: "Alt+Shift+F2,Alt+Shift+F2,Run command on clipboard contents"

  - name: Keep KRunner friendly name
    kconfig:
      file: kglobalshortcutsrc
      group: "org.kde.krunner.desktop"
      key: "_k_friendly_name=KRunner"
      value: "KRunner"

  - name: Remove Alt+Space shorcut from KRunner
    kconfig:
      file: kglobalshortcutsrc
      group: "org.kde.krunner.desktop"
      key: "_launch"
      value: "Alt+F2\tSearch,Alt+Space\tAlt+F2\tSearch,KRunner"

  ```

#### ... Shortcuts | System Services | KWin

- Lower Window: Alt+2

  Ansible `:role:user-plasma`:

  ```yaml
  - name: Shortcut for "Lower Window"
    kconfig:
      file: kglobalshortcutsrc
      group: "kwin"
      key: "Window Lower"
      value: "Alt+2,,Lower Window"
  ```

- Maximize Window Horizontally: Alt+4

  Ansible `:role:user-plasma`:

  ```yaml
  - name: Shortcut for "Maximize Window Horizontally"
    kconfig:
      file: kglobalshortcutsrc
      group: "kwin"
      key: "Window Maximize Horizontal"
      value: "Alt+4,,Maximize Window Horizontally"
  ```

- Maximize Window Vertically: Alt+3

  Ansible `:role:user-plasma`:

  ```yaml
  - name: Shortcut for "Maximize Window Vertically"
    kconfig:
      file: kglobalshortcutsrc
      group: "kwin"
      key: "Window Maximize Vertical"
      value: "Alt+3,,Maximize Window Vertically"
  ```

- Move Window Down: Meta+Ctrl+Down

  Ansible `:role:user-plasma`:

  ```yaml
  - name: Shortcut for "Move Window Down"
    kconfig:
      file: kglobalshortcutsrc
      group: "kwin"
      key: "Window Pack Down"
      value: "Meta+Ctrl+Down,,Move Window Down"
  ```

- Move Window Left: Meta+Ctrl+Left

  Ansible `:role:user-plasma`:

  ```yaml
  - name: Shortcut for "Move Window Left"
    kconfig:
      file: kglobalshortcutsrc
      group: "kwin"
      key: "Window Pack Left"
      value: "Meta+Ctrl+Left,,Move Window Left"
  ```

- Move Window Right: Meta+Ctrl+Right

  Ansible `:role:user-plasma`:

  ```yaml
  - name: Shortcut for "Move Window Right"
    kconfig:
      file: kglobalshortcutsrc
      group: "kwin"
      key: "Window Pack Right"
      value: "Meta+Ctrl+Right,,Move Window Right"
  ```

- Move Window Up: Meta+Ctrl+Up

  Ansible `:role:user-plasma`:

  ```yaml
  - name: Shortcut for "Move Window Up"
    kconfig:
      file: kglobalshortcutsrc
      group: "kwin"
      key: "Window Pack Up"
      value: "Meta+Ctrl+Up,,Move Window Up"
  ```

- Raise Window: Alt+1

  Ansible `:role:user-plasma`:

  ```yaml
  - name: Shortcut for "Raise Window"
    kconfig:
      file: kglobalshortcutsrc
      group: "kwin"
      key: "Window Raise"
      value: "Alt+1,,Raise Window"
  ```

- Window Operations Menu: Alt+Space

  Ansible `:role:user-plasma`:

  ```yaml
  - name: Shortcut for "Window Operations Menu"
    kconfig:
      file: kglobalshortcutsrc
      group: "kwin"
      key: "Window Operations Menu"
      value: "Alt+Space,Alt+F3,Window Operations Menu"
  ```

#### ... Custom Shortcuts

To bind a shortcut key to an arbitrary command:

- Create a `.desktop` file (residing in `~/.local/share/applications/`) with
  `Exec=` set to the command and arguments.  For example, for a command of:

    echo "hello, this is Mike!"

  The file `~/.local/share/applications/hello.desktop` would contain:

      [Desktop Entry]
      Type=Application
      Name=hello
      Exec=echo "hello, this is Mike!"

  More details on the `Exec=` key are found at:
  <https://specifications.freedesktop.org/desktop-entry-spec/desktop-entry-spec-latest.html#exec-variables>

- Use `kmenuedit` (right-click Start | Edit Applications) to associate a
  keyboard shortcut with the `.desktop` file.

  Note that the `.desktop` file will probably wind up in `Lost & Found` within
  the menu tree.

  Select the desired `.desktop` file and use the Advanced tab to associate a
  shortcut key.

  The resulting shortcut key configuration lines are stored in
  `~/.config/kglobalshortcutsrc`.  For example, to give `hello.desktop` a
  shortcut of `Ctrl+Alt+h`, add the following lines to that file:

      [hello.desktop]
      _launch=Ctrl+Alt+H,none,Launch hello

- Create `~/.local/share/applications/`:

      mkdir -p ~/.local/share/applications/

  Ansible `:role:user-plasma`:

  ```yaml
  - name: Create `~/.local/share/applications/`
    file:
      dest: .local/share/applications
      state: directory
  ```

- `copysel` shortcut: Meta+Ctrl+C

  Ansible `:role:user-plasma`:

  ```yaml
  - name: Create 'copysel.desktop'
    copy:
      dest: .local/share/applications/copysel.desktop
      content: |
        [Desktop Entry]
        Type=Application
        Name=copysel
        Exec=copysel
  - name: Shortcut for 'copysel.desktop'
    kconfig:
      file: kglobalshortcutsrc
      group: "copysel.desktop"
      key: "_launch"
      value: "Meta+Ctrl+C,none,Copy Primary X Selection to Clipboard"
  ```

- `activate-firefox` shortcut: Ctrl+Alt+F

  Ansible `:role:user-plasma`:

  ```yaml
  - name: Create 'activate-firefox.desktop'
    copy:
      dest: .local/share/applications/activate-firefox.desktop
      content: |
        [Desktop Entry]
        Type=Application
        Name=Activate or Launch Firefox
        Exec=activate firefox navigator.firefox
  - name: Shortcut for 'activate-firefox.desktop'
    kconfig:
      file: kglobalshortcutsrc
      group: "activate-firefox.desktop"
      key: "_launch"
      value: "Ctrl+Alt+F,none,Activate or Launch Firefox"
  ```

- `activate-thunderbird` shortcut: Ctrl+Alt+T

  Ansible `:role:home-user-plasma`:

  ```yaml
  - name: Create 'activate-thunderbird.desktop'
    copy:
      dest: .local/share/applications/activate-thunderbird.desktop
      content: |
        [Desktop Entry]
        Type=Application
        Name=Activate or Launch Thunderbird
        Exec=activate thunderbird Mail.Thunderbird
  - name: Shortcut for 'activate-thunderbird.desktop'
    kconfig:
      file: kglobalshortcutsrc
      group: "activate-thunderbird.desktop"
      key: "_launch"
      value: "Ctrl+Alt+T,none,Activate or Launch Thunderbird"
  ```

- `activate-chrome` shortcut: Ctrl+Alt+C

  Ansible `:role:home-user-plasma`:

  ```yaml
  - name: Create 'activate-chrome.desktop'
    copy:
      dest: .local/share/applications/activate-chrome.desktop
      content: |
        [Desktop Entry]
        Type=Application
        Name=Activate or Launch Chrome
        Exec=activate chrome chrome
  - name: Shortcut for 'activate-chrome.desktop'
    kconfig:
      file: kglobalshortcutsrc
      group: "activate-chrome.desktop"
      key: "_launch"
      value: "Ctrl+Alt+C,none,Activate or Launch Chrome"
  ```

- `activate-gvim0` shortcut: Ctrl+Alt+0

  Ansible `:role:user-plasma`:

  ```yaml
  - name: Create 'activate-gvim0.desktop'
    copy:
      dest: .local/share/applications/activate-gvim0.desktop
      content: |
        [Desktop Entry]
        Type=Application
        Name=Activate or Launch Gvim0
        Exec=activate "gvim --servername GVIM0 --name GVIM0" "GVIM0.Gvim"
  - name: Shortcut for 'activate-gvim0.desktop'
    kconfig:
      file: kglobalshortcutsrc
      group: "activate-gvim0.desktop"
      key: "_launch"
      value: "Ctrl+Alt+0,none,Activate or Launch Gvim0"
  ```

- `activate-gvim)` shortcut: Ctrl+Alt+)

  Ansible `:role:user-plasma`:

  ```yaml
  - name: Create 'activate-gvim).desktop'
    copy:
      dest: .local/share/applications/activate-gvim).desktop
      content: |
        [Desktop Entry]
        Type=Application
        Name=Activate or Launch Gvim)
        Exec=activate "gvim --servername GVIM) --name GVIM)" "GVIM).Gvim"
  - name: Shortcut for 'activate-gvim).desktop'
    kconfig:
      file: kglobalshortcutsrc
      group: "activate-gvim).desktop"
      key: "_launch"
      value: "Ctrl+Alt+),none,Activate or Launch Gvim)"
  ```

- `activate-gvim-email` shortcut: Ctrl+Alt+o

  Ansible `:role:home-user-plasma`:

  ```yaml
  - name: Create 'activate-gvim-email.desktop'
    copy:
      dest: .local/share/applications/activate-gvim-email.desktop
      content: |
        [Desktop Entry]
        Type=Application
        Name=Activate or Launch Gvim-Email
        Exec=activate "gvim --servername GVIMo --name GVIMo tmp/email.eml" "GVIMo.Gvim"
  - name: Shortcut for 'activate-gvim-email.desktop'
    kconfig:
      file: kglobalshortcutsrc
      group: "activate-gvim-email.desktop"
      key: "_launch"
      value: "Ctrl+Alt+o,none,Activate or Launch Gvim-Email"
  ```

- Launch Konsole shortcut: Ctrl+Alt+4

  Ansible `:role:user-plasma`:

  ```yaml
  - name: Shortcut for Launch Konsole
    kconfig:
      file: kglobalshortcutsrc
      group: "org.kde.konsole.desktop"
      key: "_launch"
      value: "Ctrl+Alt+4,none,Launch Konsole"
  ```

- `activate-konsole1` shortcut: Ctrl+Alt+1

  Ansible `:role:user-plasma`:

  ```yaml
  - name: Create 'activate-konsole1.desktop'
    copy:
      dest: .local/share/applications/activate-konsole1.desktop
      content: |
        [Desktop Entry]
        Type=Application
        Name=Activate or Launch Konsole1
        Exec=activate "konsole --name konsole-1" "konsole-1.Konsole"
  - name: Shortcut for 'activate-konsole1.desktop'
    kconfig:
      file: kglobalshortcutsrc
      group: "activate-konsole1.desktop"
      key: "_launch"
      value: "Ctrl+Alt+1,none,Activate or Launch Konsole1"
  ```

- `activate-konsole2` shortcut: Ctrl+Alt+2

  Ansible `:role:user-plasma`:

  ```yaml
  - name: Create 'activate-konsole2.desktop'
    copy:
      dest: .local/share/applications/activate-konsole2.desktop
      content: |
        [Desktop Entry]
        Type=Application
        Name=Activate or Launch Konsole2
        Exec=activate "konsole --name konsole-2" "konsole-2.Konsole"
  - name: Shortcut for 'activate-konsole2.desktop'
    kconfig:
      file: kglobalshortcutsrc
      group: "activate-konsole2.desktop"
      key: "_launch"
      value: "Ctrl+Alt+2,none,Activate or Launch Konsole2"
  ```

- `activate-konsole3` shortcut: Ctrl+Alt+3

  Ansible `:role:user-plasma`:

  ```yaml
  - name: Create 'activate-konsole3.desktop'
    copy:
      dest: .local/share/applications/activate-konsole3.desktop
      content: |
        [Desktop Entry]
        Type=Application
        Name=Activate or Launch Konsole3
        Exec=activate "konsole --name konsole-3" "konsole-3.Konsole"
  - name: Shortcut for 'activate-konsole3.desktop'
    kconfig:
      file: kglobalshortcutsrc
      group: "activate-konsole3.desktop"
      key: "_launch"
      value: "Ctrl+Alt+3,none,Activate or Launch Konsole3"
  ```

- `activate-konsole8` shortcut: Ctrl+Alt+8

  Ansible `:role:user-plasma`:

  ```yaml
  - name: Create 'activate-konsole8.desktop'
    copy:
      dest: .local/share/applications/activate-konsole8.desktop
      content: |
        [Desktop Entry]
        Type=Application
        Name=Activate or Launch Konsole8
        Exec=activate "konsole --name konsole-8" "konsole-8.Konsole"
  - name: Shortcut for 'activate-konsole8.desktop'
    kconfig:
      file: kglobalshortcutsrc
      group: "activate-konsole8.desktop"
      key: "_launch"
      value: "Ctrl+Alt+8,none,Activate or Launch Konsole8"
  ```

- `activate-konsole9` shortcut: Ctrl+Alt+9

  Ansible `:role:user-plasma`:

  ```yaml
  - name: Create 'activate-konsole9.desktop'
    copy:
      dest: .local/share/applications/activate-konsole9.desktop
      content: |
        [Desktop Entry]
        Type=Application
        Name=Activate or Launch Konsole9
        Exec=activate "konsole --name konsole-9" "konsole-9.Konsole"
  - name: Shortcut for 'activate-konsole9.desktop'
    kconfig:
      file: kglobalshortcutsrc
      group: "activate-konsole9.desktop"
      key: "_launch"
      value: "Ctrl+Alt+9,none,Activate or Launch Konsole9"
  ```

- `activate-speedcrunch` shortcut: Ctrl+Alt+=

  Ansible `:role:user-plasma`:

  ```yaml
  - name: Create 'activate-speedcrunch.desktop'
    copy:
      dest: .local/share/applications/activate-speedcrunch.desktop
      content: |
        [Desktop Entry]
        Type=Application
        Name=Activate or Launch Speedcrunch
        Exec=activate speedcrunch speedcrunch
  - name: Shortcut for 'activate-speedcrunch.desktop'
    kconfig:
      file: kglobalshortcutsrc
      group: "activate-speedcrunch.desktop"
      key: "_launch"
      value: "Ctrl+Alt+=,none,Activate or Launch Speedcrunch"
  ```

### System Settings | Personalization | Applications

#### ... Default Applications

- Web Browser: Firefox Web Browser
- Email client: Thunderbird Mail

### System Settings | Hardware | Input Devices

#### ... Keyboard

- Delay: 250 ms
- Rate: 32 repeats/sec

### System Settings | Hardware | Power Management

(manual)

- (desktop) Energy Saving:
  - Uncheck `Screen Energy Saving`.
- (mobile) Energy Saving | On AC power:
  - Uncheck `Screen Brightness`.
  - Uncheck `Dim Screen`.
  - Uncheck `Screen Energy Saving`.
  - Button events handling | When laptop lid closed | Lock screen.
- (mobile) Energy Saving | Adjust settings for `On Battery` to taste.

## Desktop and Wallpaper Settings

(manual)

- Right-click on the Desktop, choose `Desktop and Wallpaper Settings`:

  - Choose "Darkest Hour" image. (Note: "Honey Wave" is the default.)
  - Repeat for each monitor.

## Task Bar Settings

(manual)

- Right-click on the task bar, choose `Show Alternatives`, change to `Task
  Manager` (instead of the now-default "icons only" variant).

- Right-click on the task bar, choose `Configure Task Manager`:
  - Behavior:
    - Set `Group` to `Do Not Group`.
    - Set `Sort` to `Manually`.
    - Check `Show only tasks from current desktop`.
    - Check `Show only tasks from current activity`.

- Right-click on taskbar, choose `Enter Edit Mode`.  Increase "panel height"
  until date and time are comfortable to read.

## Clock Settings

- Right-click on clock, choose `Configure Digital Clock`
  (Note: the defaults are correct now):
  - Appearance:
    - Check "Show date"
    - Date format: Short date

## Klipper

(manual) Disable Klipper entirely (interacts badly with Gvim on Ubuntu 22.04):

- Right-click on the System Tray | Configure System Tray.  This is difficult
  because most of the tray's area is covered with "entries" (like Klipper's
  icon).  Try right-clicking at the edge of the System Tray (between the tray
  and the clock, for example).

- Entries | System Services | Clipboard, choose `Disabled`.

Right-click on Klipper, choose "Configure Clipboard":

- (automated) Disable "Save clipboard contents on exit":
  Uncheck "Save clipboard contents on exit".

  Ansible `:role:user-plasma`:

  ```yaml
  - name: Disable "Save clipboard contents on exit"
    kconfig:
      file: klipperrc
      group: "General"
      key: "KeepClipboardContents"
      value: "false"
  ```

- (automated) Disable "Prevent empty clipboard":
  Uncheck "Prevent empty clipboard".

  Ansible `:role:user-plasma`:

  ```yaml
  - name: Disable "Prevent empty clipboard"
    kconfig:
      file: klipperrc
      group: "General"
      key: "PreventEmptyClipboard"
      value: "false"
  ```

- (automated) Enable "Ignore selection":
  Check "Ignore selection".

  Ansible `:role:user-plasma`:

  ```yaml
  - name: Enable "Ignore selection"
    kconfig:
      file: klipperrc
      group: "General"
      key: "IgnoreSelection"
      value: "true"
  ```

  This fixes a crash with GVim on Plasma when selecting large amounts of text
  (<https://github.com/vim/vim/issues/1023>).

- (automated) Set "Clipboard history size":
  Set "Clipboard history size" to "1 entry".

  Ansible `:role:user-plasma`:

  ```yaml
  - name: Set "Clipboard history size"
    kconfig:
      file: klipperrc
      group: "General"
      key: "MaxClipItems"
      value: "1"
  ```

## dconf-editor

Useful for viewing/editing GTK-related settings in `~/.config/dconf/`.

- Install:

      agi dconf-editor

## Synaptics Touchpad

- System Settings | Hardware | Input Devices | Touchpad:
  - Scrolling:
    - For touchpads *with* two-finger scrolling:
      - Enable Vertical Two-Fingers Scrolling.
      - Enable Horizontal Two-Fingers Scrolling.
      - Disable Vertical Edge Scrolling.
      - Disable Horizontal Edge Scrolling.
    - For touchpads *without* two-finger scrolling:
      - Enable Vertical Edge Scrolling.
      - Enable Horizontal Edge Scrolling.
      - Disable Vertical Two-Fingers Scrolling.
      - Disable Horizontal Two-Fingers Scrolling.
  - Tapping:
    - Disable Tapping (on machines that are too sensitive to accidental taps).
    - Tapping | One Finger means Left Button

To test whether tapping will work:

    synclient TapButton1=1

View all Synaptics settings:

    synclient -l

For more information:

    man synaptics
    https://fedoraproject.org/wiki/Input_device_configuration

# Fonts

## Font References

- Reference articles:

  - <https://gist.github.com/Earnestly/7024056>
  - <http://www.rastertragedy.com/>

- Font setup may end up with this error:

      Fontconfig warning: "/etc/fonts/conf.d/50-user.conf", line 14:
      reading configurations from ~/.fonts.conf is deprecated.

  This occurs because the old location `~/.fonts.conf` is now deprecated.
  Apparently this gets created by installing a font via Plasma's GUI. So after
  that file is created, it can be moved to the new location as follow:

      mkdir -p ~/.config/fontconfig
      mv ~/.fonts.conf ~/.config/fontconfig/fonts.conf

  This should solve the error message. The fonts themselves will still live in
  `~/.fonts` without problem.

- Top font from this article:
  <http://hivelogic.com/articles/top-10-programming-fonts/>

  - Inconsolata
  - Consolas (non-free Microsoft font)
  - Deja Vu Sans Mono

- In my order of preference:

  - Hack
  - Deja Vu Sans Mono
  - Inconsolata

## Font Installation

- Install fixed-width fonts `:role:workstation`:

      agi fonts-inconsolata ttf-bitstream-vera fonts-dejavu fonts-hack-ttf

      yi google-droid-sans-fonts google-droid-sans-mono-fonts \
        levien-inconsolata-fonts bitstream-vera-sans-mono-fonts

- Install an individual font file via:

  - Launch `systemsettings5` | Font | Font Management:
    - If the is already installed, delete the old version.
    - Choose "Add" button.
    - Add fonts as "Personal" fonts (to ensure they are properly probed by Vim
      in `~/.fonts/`).

## Microsoft Core Fonts Installation

- Ref: <http://mscorefonts2.sourceforge.net/>

- Provides the following twelve fonts:

  Andale, Arial, Arial Bold, Comic Sans, Courier New, Georgia, Impact, Times New
  Roman, Trebuchet, Verdana, Tahoma, Wingdings

- Install `:role:workstation`:

      agi ttf-mscorefonts-installer

- Also have cached copy of the fonts here:

      ~/download/fonts/corefonts/

## Font Detection

Bookmarklets to detect the font on a web page:

- <http://code.stephenmorley.org/articles/whats-that-font-bookmarklet/>
- This one doesn't work, except on its own site (?):
  <http://chengyinliu.com/whatfont.html>

Upload an image to detect the font:

- <http://www.myfonts.com/WhatTheFont/>

Font identifier tools:

- <http://www.vandelaydesign.com/font-identifier-tools/>

# Terminals

## Konsole

- (centos) Install extra terminfo entries:

      yi ncurses-term

  Provides many extra terminfo entries, e.g. `screen-256color-bce`.

### Konsole Custom Profile

#### Konsole Custom Profile Creation

Create `Custom` profile to adjust profile-related settings.

In Konsole, choose Settings | Manage Profiles | New:

- Choose name `Custom`.

- Check "Default profile".

- Choose OK.

Ansible `:role:user-plasma`:

```yaml
- name: Create `Custom` Konsole Profile
  kconfig:
    file: ../.local/share/konsole/Custom.profile
    group: "General"
    key: "Name"
    value: "Custom"
- name: Set `Custom` Konsole Profile Parent
  kconfig:
    file: ../.local/share/konsole/Custom.profile
    group: "General"
    key: "Parent"
    value: "FALLBACK/"
- name: Use `Custom` Konsole Profile
  kconfig:
    file: konsolerc
    group: "Desktop Entry"
    key: "DefaultProfile"
    value: "Custom.profile"
```

#### Konsole Custom Profile Settings

In Konsole, choose Settings | Edit Current Profile:

- Scrolling | Scrollback | Set "Fixed size" to "100000 lines".

Ansible `:role:user-plasma`:

```yaml
- name: Create `Custom` Konsole Profile
  kconfig:
    file: ../.local/share/konsole/Custom.profile
    group: "Scrolling"
    key: "HistorySize"
    value: "100000"
```

### Konsole Keyboard Shortcuts

In Konsole, choose Settings | Configure Keyboard Shortcuts:

- (manual) Set "What's This?" shortcut to None (default: Shift+F1).

  TODO Ansible perform above configuration by adding these lines in
  `~/.local/share/kxmlgui5/konsole/konsoleui.rc`:

      <gui name="konsole" version="19">
       <ActionProperties scheme="Default">
        <Action shortcut="" name="help_whats_this"/>
       </ActionProperties>
      </gui>

### Konsole Configuration

In Konsole, choose Settings | Configure Konsole, then continue.

#### ... Make current tab more distinguishable

- (homegit) Create file `~/.config/konsole.css` with contents:

      QTabBar::tab::selected {
          background: lightblue;
          color: black;
          font: bold;
      }

- Settings | Configure Konsole | Tab Bar / Splitters | Appearance:

  - Check "Show: Always".
  - Check "Use user-defined stylesheet".
  - Browse for `~/.config/konsole.css`.

  Ansible `:role:user-plasma`:

  ```yaml
  - name: Always show Konsole Tab Bar
    kconfig:
      file: konsolerc
      group: "TabBar"
      key: "TabBarVisibility"
      value: "AlwaysShowTabBar"
  - name: Konsole Use Style Sheet
    kconfig:
      file: konsolerc
      group: "TabBar"
      key: "TabBarUseUserStyleSheet"
      value: "true"
  - name: Konsole Set Style Sheet File
    kconfig:
      file: konsolerc
      group: "TabBar"
      key: "TabBarUserStyleSheetFile"
      value: "file:.config/konsole.css"
  ```

## XTerm

- References:

  - <https://unix.stackexchange.com/questions/219370/larger-xterm-fonts-on-hidpi-displays>

- On a 4K monitor, the fonts are *way* too small. XTerm normally uses bitmap
  fonts, but it can use TrueType fonts as well. The easiest solution is to
  configure XTerm in `~/.Xresources`:

      xterm*renderFont: true
      xterm*faceName: Hack
      xterm*faceSize: 10

- Then reload via:

      xrdb -merge ~/.Xresources

## tmux

- Install `:role:workstation`:

      agi tmux

      yi tmux

- Create `~/.tmux.conf` with contents:

      set-option -g prefix C-j
      unbind-key C-b
      bind-key C-j send-prefix
      bind-key -r Space next-layout

      # Global options.
      set-option -g default-terminal screen-256color

      # Enable extra key code for shifted functions keys, xterm-style.
      set-option -g xterm-keys on
      set-option -g display-panes-time 1500
      set-option -g display-time 1500
      set-option -g history-limit 100000
      set-option -g repeat-time 750
      set-option -g set-titles on

      # Server options.
      set-option -s escape-time 5

## GNU Screen

- Install:

      agi screen

      yi screen

- Create `~/.screenrc` with contents:

      # Change default ctrl-A to ctrl-@ for escape key.
      escape ^Jj

      # Kill unnecessary license message.
      startup_message off

## GNOME Terminal

- Install:

      agi gnome-terminal

## rxvt

- Install:

      agi rxvt rxvt-unicode-256color

      yi rxvt rxvt-unicode

## terminator

- Install:

      agi terminator

      yi terminator

## tack (Terminfo Action Checker)

- Install:

      agi tack

      yi tack

# Graphical File Browsers

## dolphin

- Launch `dolphin`, then use menu Control | Configure Dolphin | General, check
  "Use common view properties for all folders". This eliminates littering
  `.directory` files everywhere.

## Konqueror

- Install `:role:workstation`:

      agi konqueror

      yi konqueror

# GPG

## GPG Support

Most parts are already installed for use with `kleopatra` or `kgpg`.

- Install:

      yi gnupg2-smime

## seahorse

- A GNOME-based app for encryption key management.

- Install:

      agi seahorse

## kgpg

- Install:

      agi kgpg

      # CentOS, Fedora: already installed.

## kleopatra GPG Support

- (fedora) (centos) Already installed with Plasma.

- Install:

      agi kleopatra

      # (fedora) (centos) Already installed with Plasma.

- Launch `kleopatra`.

- If already have a personal OpenGPG key pair, import it (probably from KeepassX
  thumb drive `drmikehenry.asc` file); then make sure to mark it as "my
  certificate" so the trust chain works right (still figuring this out).

- Create a new personal OpenGPG key pair:

  - Name: Michael Henry
  - Email: <drmikehenry@drmikehenry.com>
  - Use standard GPG passphrase.

- Choose "Make a Backup of Your Key Pair" using ASCII armor, save to
  `drmikehenry.asc`. Copy to KeypassX thumb drives.

# Printing

## Printer Setup

References:

- <https://www.cups.org/doc/network.html>
- <https://www.cups.org/doc/admin.html>
- "Deprecate printer drivers #5270":
  <https://github.com/apple/cups/issues/5270>
- "FUTURE: Remove printer driver and raw queue support. #5271":
  <https://github.com/apple/cups/issues/5271>

As of 2009 or so, network printers can use the "everywhere" driver instead of a
specific PPD.  Eventually, custom PPD support will be removed from CUPS and
printer-specific driver support will be done via separate applications.

- `lpadmin` switches:

  - `-p NAME`: printer name
  - `-E`: enable printer (when used after `-p`)
  - `-v device-uri`: URI to printer (determines connection method)
  - `-L location`: printer's physical location
  - `-D description`: printer's description
  - `-o Name=Value`: set default value for named PPD option
  - `-d`: set the default printer

### HP Color LaserJet M553n

- Install hplip `:role:home`:

      agi hplip

      yi hplip

- (manual) Create printers:

      # (ubuntu)
      for p in {crayon,pencil}; do
        lpadmin -p $p \
          -E \
          -v ipp://192.168.254.128 \
          -m everywhere \
          -L 'Computer room'
      done

- (manual) Configure printers:

      lpadmin -p pencil  -D 'Black & White printer'
      lpadmin -p crayon  -D 'Color printer'

      lpadmin -p pencil  -o 'HPColorAsGray=True'

      # Set the default printer.
      lpadmin -d crayon

- View printer options:

    lpoptions -p pencil -l

### HP Color LaserJet M553n (alternate setup using HP GUI)

Run `hp-setup`, answer questions:

- Network/Ethernet/Wireless network
- Show Advanced Options
- Choose Manual discovery
- Enter IP address: 192.168.254.128
- Choose Next
- Choose Next again
- Printer name: crayon
- Description: HP Color LaserJet M553n
- Location: Computer room
- PPD file (default):
  `postscript-hp:0/ppd/hplip/HP/hp-color_laserjet_m553-ps.ppd`
- Add printer

More configuration via `systemsettings5` | Printers:

- Check "Default printer".

- For black & white printers:

  > - Configure | Printer Options | Color | Print Color as Gray: On

## Printing Text from the Command Line

- Recommended on LUG mailing list:

      enscript -P myprinter -fTimes-Roman12 mydoc.txt

  "Since enscript can't handle UTF-8 I use":

      paps | lpr

  "with my own wrapper since I don't like the paps defaults and it takes an
  awful lot of options to get what I like."

# Admin

## (ubuntu) Disable Dynamic motd

- Reference:

  - <https://raymii.org/s/tutorials/Disable_dynamic_motd_and_motd_news_spam_on_Ubuntu_18.04.html>

- Turn off undesirable portions of dynamic motd:

      chmod -x /etc/update-motd.d/10-help-text
      chmod -x /etc/update-motd.d/50-motd-news
      chmod -x /etc/update-motd.d/90-updates-available

  Ansible `:role:workstation`:

  ```yaml
  - name: Disable execution for motd files
    file:
      path: "/etc/update-motd.d/{{ item }}"
      mode: -x
    loop:
      - "10-help-text"
      - "50-motd-news"
      - "90-updates-available"
    when: ansible_distribution == 'Ubuntu'
  ```

## (ubuntu) cron Schedule

- Ubuntu default times for daily, weekly, and monthly jobs is during the 6 a.m.
  hour. Correct this to 2 a.m.:

      vim /etc/crontab

      25 2    * * *   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.daily )
      47 2    * * 7   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.weekly )
      52 2    1 * *   root    test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.monthly )

## logwatch

- Install:

      agi logwatch

      yi logwatch

- Optionally configure (but defaults are good):

      vim /usr/share/logwatch/default.conf/logwatch.conf

## Journal Limits

- Set limits for systemd journal size and make the storage persistent:

      vim /etc/systemd/journald.conf

      [Journal]
      Storage=persistent
      SystemMaxUse=200M
      SystemMaxFileSize=32M

# Snapshot

- Install rsnapshot:

      agi rsnapshot

      yi rsnapshot

- Create snapshot root mount point; make it immutable:

      mkdir /snapshot
      chattr +i /snapshot

- (bolt) Using zfs: create separate volume for snapshots:

      zfs create -o mountpoint=/snapshot bolt/snapshot

- Using LVM: create separate volume for snapshots, format, mount:

  **Note**: LVM volumes starting with "snapshot" are reserved :-(

  - (bolt):

        lvcreate bolt -L 459G -n lv_snapshot
        mke2fs -t ext4 /dev/bolt/lv_snapshot
        mount /dev/bolt/lv_snapshot /snapshot

  - (casey):

        lvcreate casey_spinner -L 500G -n lv_snapshot
        mke2fs -t ext4 /dev/casey_spinner/lv_snapshot
        mount /dev/casey_spinner/lv_snapshot /snapshot

  - Edit `/etc/fstab` for snapshots:

        vim /etc/fstab

        /dev/mapper/bolt-lv_snapshot /snapshot ext4  defaults  0 2

    or:

        /dev/mapper/casey_spinner-lv_snapshot /snapshot ext4  defaults  0 2

- Adjust configuration file as follows, **using tab characters** to separate
  fields:

      cp -a /etc/rsnapshot.conf{,.orig}
      vim /etc/rsnapshot.conf

      ## NOTE: Ensure paths in .conf file are correct; particularly, use
      ## /bin/cp and /bin/rm (they are not in /usr/bin).

      snapshot_root  /snapshot/
      no_create_root 1

      retain       hourly  10
      retain       daily   7
      retain       weekly  4
      retain       monthly 12

      include             /home/*/.vim/
      exclude             /**/.swp
      exclude             /**/.*.swp
      exclude             /**/.dropbox.cache
      exclude             /home/**/*-tmp/
      exclude             /home/*/.*/
      exclude             /home/*/.xsession-errors
      exclude             /home/*/vms/
      exclude             /home/*/mail/.imap/

      # Just for bolt.
      exclude             /m/**/*-tmp/
      exclude             /m/torrent/
      exclude             /m/tmp/
      exclude             /m/srv/nfs/
      exclude             /m/**/iTunes/**/*[cC]ache*
      exclude             /m/**/thunderbird/**/*[cC]ache*

      # bolt backups:
      backup  /m/             bolt/
      backup  /etc/           bolt/
      backup  /home/          bolt/
      backup  /usr/local/     bolt/

      # casey backups:
      backup  /etc/           casey/
      backup  /home/          casey/
      backup  /usr/local/     casey/

- Setup cron for proper intervals:

      vim /etc/crontab

      # min hour     dom         mon dow  user  what
        00  23        1           *   *   root  rsnapshot monthly
        10  23        1,8,15,22   *   *   root  rsnapshot weekly
        20  23        *           *   *   root  rsnapshot daily
        30  7-23      *           *   *   root  rsnapshot hourly

# Simple Mail Setup

## postfix for Satellite Nodes

- Install postfix:

      agi postfix

- (ubuntu):

  - When installing, answer the configuration questions as:
    - Choose `satellite` email system if not installing for
      bolt.drmikehenry.com.
    - Choose FQDN for System mail name (e.g., `mobi.drmikehenry.com`).
    - Choose `mailman.drmikehenry.com` for SMTP relay host.
    - Leave remaining questions (if any) at their defaults.
  - Can also do `dpkg-reconfigure postfix` to answer these questions again.

- To allow `/etc/hosts` to override `mailman.drmikehenry.com`, add this line to
  the postfix configuration and reload:

      echod -a /etc/postfix/main.cf '
        # Use "native" DNS (allowing /etc/hosts to work).
        smtp_host_lookup = native
      '

      systemctl restart postfix

## Mail Aliases

- Ensure `root` and `mike` aliases exists on all boxes:

      echod -a /etc/aliases '
        root:   drmikehenry@drmikehenry.com
        mike:   drmikehenry@drmikehenry.com
        '

- Enable new aliases:

      newaliases

## Mail Tools

Note: Ubuntu 16.04 uses mailutils now for the `mail` command.

- Install tools:

      agi mutt mailutils

      yi mutt mailx

  Provides enhanced `mail` command.

- (all):

  - Test sending an email:

        date | mail -s 'testing' drmikehenry@drmikehenry.com

## Mail Over ssh

- When on the road, can use ssh as follows:

  - Kill the local postfix:

        systemctl stop postfix

  - Uncomment `mailman` to use `localhost` in `/etc/hosts`:

        127.0.0.1        mailman.drmikehenry.com mailman

  - Setup ssh tunnel, forwarding ports 25 and 993 for email:

        rbolt -L 25:127.0.0.1:25 -L 993:127.0.0.1:993

  - Use Thunderbird normally.

- After return:

  - Comment `mailman` line in `/etc/hosts`:

        #127.0.0.1        mailman.drmikehenry.com mailman

  - Restart postfix:

        systemctl restart postfix

  **Note** It's important to restart postfix, since `/etc/init.d/postfix` copies
  files like `/etc/hosts` into `/var/spool/postfix/etc/hosts`.

# Productivity

## LibreOffice

(manual)

- Install from PPA:

  - Reference: <https://launchpad.net/~libreoffice/+archive/ubuntu/ppa>

  - Add PPA repository and install:

        add-apt-repository -y --update ppa:libreoffice/ppa
        agi libreoffice

- Install:

      agi libreoffice

      yi libreoffice

- Install database tools (for `*.mbd` access):

      agi mdbtools

- Configure:

  - Tools | Options | LibreOffice | General:
    - Check "Use LibreOffice dialogs"

## gnucash

References:

- <https://wiki.gnucash.org/wiki/FAQ>

  - Version compatibility:
    - Q: Can I exchange Gnucash file with any other version of GnuCash?

      A: Not quite:

          You can always upgrade from versions >= 1.8 to a higher release. In
          most cases you can go back-and-forth between adjacent major releases:
          You can read 2.0 in 1.8.x fine.  Reading 2.2 in 2.0 will not work, if
          you have scheduled transactions.  2.4 and 2.2 files are
          interchangeable 2.6 and 2.4 files are interchangeable unless you use
          the Credit Notes feature in 2.6

- <https://wiki.gnucash.org/wiki/Configuration_Locations>

- These variables control where gnucash stores settings:

      GNC_DATA_HOME   /home/<user>/.local/share/gnucash
      GNC_CONFIG_HOME /home/<user>/.config/gnucash

      GTK_DATA_HOME   /home/<user>/.local/share/gtk-3.0
      GTK_CONFIG_HOME /home/<user>/.config/gtk-3.0

  - Don't care about the gtk-related settings, but want to share the others
    because `GNC_DATA_HOME` houses saved report configurations.
  - Can use the same directory for `CONFIG` and `DATA`; this is always done on
    Windows. Still, it's easy to make `data` and `config` subdirectories.

- (one-time) Create `data` and `config` areas:

      mkdir -p /m/data/money/gnucash-config/data
      mkdir -p /m/data/money/gnucash-config/config
      sudo chown -R beth:data /m/data/money/gnucash-config

- (home2git) Create Plasma environment variable script:

      mkdir -p ~/.config/plasma-workspace/env
      vim ~/.config/plasma-workspace/env/gnucash.sh

  with contents:

      export GNC_DATA_HOME=/m/data/money/gnucash-config/data
      export GNC_CONFIG_HOME=/m/data/money/gnucash-config/config

  (lovelace) Create manually.

- (home2git) To share with console logins, place the following in `.profile2`:

      echo '. $HOME/.config/plasma-workspace/env/gnucash.sh' >> ~/.profile2

  (lovelace) Place at end of `~/.bashrc`.

- Logout/login again to make variables take effect.

- Install `:role:home` (Ubuntu 22.04 has version 4.8):

      agi gnucash gnucash-common gnucash-docs python3-gnucash

- Run gnucash with shared money file:

      gnucash /m/data/money/gnucash/money.gnucash

- Configure:

  - Edit | Preferences:
    - Numbers/Date/Time | Date Format: ISO
    - Register Defaults | Check "Double Line mode".

### (one-time) Save Reports

- Budget (Discretionary)
  - Report name: Budget (Discretionary)
  - Budget: 2019
  - Start Date (start of accounting period)
  - End Date (adjust for each month)
  - Show full account names (checked)
  - Report for a range of budget periods:
    - Range start: First (eventually, move up a few months)
    - Range End: Previous
    - Check: Include collapsed periods before selected
    - Uncheck: Include collapsed periods after selected
  - Display:
    - Show Budget, Actual, Difference
    - Group periods together
    - Show Column with totals
    - Include accounts with zero balances and budget values
  - Accounts:
    - Display depth: 2
    - accounts to show:
      - Computer
      - Date
      - Dining
      - Ohio/all
      - Special Events
      - Food and Supplies
      - Home Improvement
      - Beth spending money
      - Birthdays
      - Lunch Money
      - Mike Spending Money
- Budget (full year)
  - Pretty much everything
  - Covers previous year, with previous year's budget
  - Report for range of budget periods:
    - Range Start: Last
    - Range End: Last
    - Check: Include collapsed periods before selected
    - Check: Include collapsed periods after selected
  - Display:
    - Show Difference
    - Show Column with Totals
- Tutoring Income Statement
  - Type: Income statement
  - Account: only Tutoring
  - Covers previous year in entirety

## anki

- Reference: <https://apps.ankiweb.net/docs/manual.html>

- Install:

      agi anki

## kalarm

- Install:

      agi kalarm

## Fitbit Synchronization

- Reference:

  - <https://bitbucket.org/benallard/galileo>
  - <http://linuxaria.com/article/how-to-sync-your-fitbit-under-linux>

- Install Galileo:

      pipi galileo

# Drawing

## Dia

- Install:

      agi dia

      yi dia

## xfig

- Install:

      agi xfig

      yi xfig

# Optical Character Recognition (OCR)

## tesseract

- Install:

      agi tesseract-ocr

      yi tesseract

## gocr

- **NOTE** Results aren't great.

- Install:

      agi gocr

      yi gocr

# Chat

## Konversation IRC Client

- Install:

      agi konversation

      yi konversation

# Video Conferencing

## Skype

- Download the installer as a `.deb` file: <https://www.skype.com/en/get-skype/>

- Install:

      dpkg -i skypeforlinux-64.deb

- Run:

      skypeforlinux

# Remote Desktop

## TeamViewer

- (ubuntu) Install:

  - Visit <https://www.teamviewer.com/en/download/linux/>

  - Download 64-bit .deb file and save in download area, e.g.:

        ~mike/download/internet/teamviewer/teamviewer_15.35.7_amd64.deb

  - Install .deb file:

        dpkg -i ~mike/download/internet/teamviewer/teamviewer_15.35.7_amd64.deb

- (fedora) Install:

  - Install 32-bit library for xrandr:

        yi libXrandr-0:1.4.2-2.fc22.i686

  - Install:

        dnf install ~mike/download/internet/teamviewer/teamviewer_11.0.53191.i686.rpm

- Install on client machine as well (perhaps Windows VM).

- Execute TeamViewer tool and configure with account information:

      teamviewer &

- On Windows, may have problems seeing the mouse cursor. Can change the mouse
  pointer scheme via Control Panel | Hardware and Sound | Devices and Printers
  | Mouse | Pointers | Scheme:

  - Set to "Windows Black (system scheme)" instead of default "Windows Aero
    (system scheme)".

  - Alternatively, keep the original scheme but fix the text cursor to be
    something like this:

        beam_i.cur

### Setting up TeamViewer on Client Machine

- Put `teamviewer.com` into URL bar (alt-d or whatever)
- Choose "Download for Free"
- Save file `TeamViewer_Setup.exe` to Desktop.
- Run `TeamViewer_Setup.exe`.
- Choose "Default installation"; choose "Accept - next".
- I want to use the free version for personal use; Finish.
- Minimize any web browser window that showed up with "How to Use TeamViewer".
- TeamViewer window should be showing:
  - May have to close an advertisement window from TeamViewer.
  - Remote Control (on left)
- Default installation; Accept.
- I want to use the free version for personal use; Finish.
- Minimize any web browser window that showed up with "How to Use TeamViewer".
- TeamViewer window should be showing:
  - Remote Control (on left), with "Allow Remote Control" in middle:

    - Your ID: 1 016 697 217 (for example)
    - Password: b5rh82

    Tell ID and password to Mike.
- On Mike's TeamViewer:
  - Remote Control (on left), with "Control Remote Computer" on right:
    - Enter remote computer's "Your ID" as "Partner ID".
    - Choose "Remote Control".
    - Choose "Connect".
- After controlling remotely, can setup automated remote connection:
  - Visit remote PC's TeamViewer app
  - Still on "Remote Control" on left, with "Allow Remote Control" in middle:
    - Check "Start TeamViewer with Windows"
    - Check "Grant easy access"
    - Enter email and password:
      - Email: <teamviewer@drmikehenry.com>
      - Password: Mike's password (not the Help one)
      - Choose "Assign".
  - Now can reboot remote machine, should be able to connect again later.

# Network Filesystems

## wdfs

### (ubuntu) wdfs

**NOTE** Need to install libneon27-gnutls-dev to avoid this bug:
<http://bugs.debian.org/cgi-bin/bugreport.cgi?bug=622140>

- Get dependencies:

      agi libfuse-dev libneon27-gnutls libneon27-gnutls-dev \
        libglib2.0-dev libglib2.0-doc checkinstall

- Perform these steps to install:

      # As normal user:
      wget http://noedler.de/projekte/wdfs/wdfs-1.4.2.tar.gz
      tar -zxf wdfs-1.4.2.tar.gz
      cd wdfs-1.4.2
      ./configure
      make
      sudo checkinstall

  Answers to checkinstall questions:

  - Create default set of package docs? Yes

  - Description of the package:

    > WebDAV-based fuse filesystem.

  Using `checkinstall` instead of `make install` builds a .deb package
  (`wdfs_1.4.2-1_amd64.deb` in this case) and then installs the package.

### (fedora) wdfs

- Install:

      yi wdfs

### (all) wdfs

- Optional test server: <https://webdavserver.com/>

  Visit above link, get URL of test data.

- Test the mount:

      mkdir -p ~/tmp/dav/

      # Use URL of some DAV server:
      wdfs https://webdavserver.com/User66f27c7 ~/tmp/dav/

      ls ~/tmp/dav/

- Unmount:

      fusermount -u ~/tmp/dav/

## cadaver

- Install:

      agi cadaver

      yi cadaver

## davfs2

- Install:

      agi davfs2

      yi davfs2

  (ubuntu) Allow unprivileged users to mount.

## jmtpfs

- Fuse-based MTP (Media Transfer Protocol) filesystem. Useful for phone picture
  importation.

- Install:

      agi jmtpfs

- Mount:

      mkdir -p ~/phone
      jmtpfs ~/phone

- Unmount:

      fusermount -u ~/phone

- Seems to work OK.

## Android File Transfer for Linux

(manual)

- <https://github.com/whoozle/android-file-transfer-linux/releases>

- Grab the .AppImage, e.g.:
  <https://github.com/whoozle/android-file-transfer-linux/releases/download/v4.2/Android_File_Transfer-cce42ee-x86_64.AppImage>

- Save directly into `/usr/local/bin` under the original name, then symlink to a
  convenient version-independent name:

      sudo cp ~/tmp/Android_File_Transfer-cce42ee-x86_64.AppImage /usr/local/bin

      sudo chmod +x /usr/local/bin/Android_File_Transfer-cce42ee-x86_64.AppImage

      sudo ln -s /usr/local/bin/Android_File_Transfer{-cce42ee-x86_64.AppImage,}

# Utilities

## Search Tools

### findx/ffg

- Install `:role:workstation`:

      pipxg install findx

### Ripgrep

- Install `:role:workstation`:

      agi ripgrep

- (optional) Install latest via `cargo install ripgrep`.

- Download a release from <https://github.com/BurntSushi/ripgrep/releases>;
  typically, install from .deb, e.g.:

      wget https://github.com/BurntSushi/ripgrep/releases/download/11.0.1/ripgrep_11.0.1_amd64.deb

      dpkg -i ripgrep_11.0.1_amd64.deb

- Use a `~/.ignore` file to configure ripgrep to ignore patterns below `$HOME`.
  Simplest is to symlink from `~/.agignore`, as both files use the `.gitignore`
  syntax:

      ln -s ~/.agignore ~/.ignore

### ack

- Install `:role:workstation`:

      agi ack

      yi ack

### The Silver Searcher

- Install `:role:workstation`:

      agi silversearcher-ag

      yi the_silver_searcher

### The Platinum Searcher

- From: <https://github.com/monochromegane/the_platinum_searcher>

- Release area:
  <https://github.com/monochromegane/the_platinum_searcher/releases>

- Install:

      curl -L https://github.com/monochromegane/the_platinum_searcher/releases/download/v2.1.5/pt_linux_amd64.tar.gz | sudo tar -C /opt -zx
      sudo ln -sf /opt/pt_linux_amd64/pt /usr/local/bin/pt

### Locate Database (locatedb) for "all"

- The default database for the `locate` command is too encompassing, since it
  includes `/snapshot`.

- Backup original configuration:

      cp /etc/updatedb.conf{,.dist}

- Enable `PRUNENAMES` and append `/snapshot` to `PRUNEPATHS` as follows:

      vim /etc/updatedb.conf

        PRUNENAMES = ".git .bzr .hg .svn"
        PRUNEPATHS="/tmp /var/spool /media /home/.ecryptfs /var/lib/schroot /snapshot"

- Create new cron job for `mlocate-all` by cloning original:

      cp -a /etc/cron.daily/mlocate{,-all}

- Edit new version to change lockfile and adjust invocation:

      vim /etc/cron.daily/mlocate-all

  Change this:

      flock --nonblock /run/mlocate.daily.lock $IONICE /usr/bin/updatedb.mlocate

  To this:

      flock --nonblock /run/mlocate-all.daily.lock \
        $IONICE /usr/bin/updatedb.mlocate \
        --prunenames '' \
        --prunepaths '/tmp /var/spool /media /home/.ecryptfs /var/lib/schroot' \
        --output /var/lib/mlocate/mlocate-all.db

- Create command to use new database:

      echod -o /usr/local/bin/locate-all '
        #!/bin/sh

        locate --database /var/lib/mlocate/mlocate-all.db "$@"
      '
      chmod +x /usr/local/bin/locate-all

- Invocation:

      # "Normal" search (excludes the snapshots):
      locate stuff

      # Exhaustive search (include the snapshots, .git/.svn/etc.):
      locate-all stuff

### recoll Desktop Search

- Install:

      agi recoll

      yi recoll

### zeal

- Install:

      agi zeal

      yi zeal

- Bound to Win-Z by default.

## Diff Tools

### meld

- Install `:role:workstation`:

      agi meld

      yi meld

### kdiff3

- Install `:role:workstation`:

      agi kdiff3

      yi kdiff3

### colordiff

- Install `:role:workstation`:

      agi colordiff

      yi colordiff

- Setup colordiff settings:

      echod -o ~/.colordiffrc '
        # Settings for colordiff.
        plain=darkwhite
        newtext=darkgreen
        oldtext=darkred
        diffstuff=darkcyan
        cvsstuff=white
      '

  Add to git as well:

      git add -f ~/.colordiffrc

### kompare

- Install:

      agi kompare

      yi kdesdk-kompare

## Shells

### zsh

- Install:

      agi zsh

      yi zsh

### fish

- Install:

      agi fish

## Console File Browsers

### ranger (Console-based File Manager)

- Install:

      agi ranger

      yi ranger

### Midnight Commander

- Install:

      agi mc

      yi mc

## Filesystem Utilities

### SMB Mounts

- Setup `/etc/fstab` for a CIFS mount:

      //host/share  /mnt/share   cifs    noauto,user,owner,uid=mike,gid=mike,username=mike,workgroup=toyland 0 0

- (bolt) Setup mounts of Windows machines:

      echod -a -o /etc/fstab '
        //descartes/c_drive  /mnt/descartes_c   cifs    noauto,user,owner,uid=beth,gid=beth,username=beth,workgroup=toyland 0 0
        //socksbox/c_drive  /mnt/socksbox_c   cifs    noauto,user,owner,uid=andrew,gid=andrew,username=andrew,workgroup=toyland 0 0
        //ella/c_drive  /mnt/ella_c   cifs    noauto,user,owner,uid=sarah,gid=sarah,username=sarah,workgroup=toyland 0 0

      '

  Create mount points:

      mkdir /mnt/{socksbox_c,descart_c,ella_c}

### USB Flash Drives

- See help at: <https://help.ubuntu.com/community/RenameUSBDrive>

- Ensure `gparted` is installed.

- If necessary, unmount partition of interest.

- Use `gparted` menu Partition | Label to change the label.

  Note that **the volume must not be mounted when changing the label**.

- For FAT volumes, should also be able to use `mtools`.

- Pre-setup to ignore errors like this one:

      Total number of sectors (15638656) not a multiple of sectors per track (63)!

  by skipping the check:

      echo mtools_skip_check=1 >> ~/.mtoolsrc

- Check existing label:

      mlabel -i /dev/sde1 -s ::

- Change label:

      mlabel -i /dev/sde1 ::NEW_LABEL

### archivemount

- Install:

      agi archivemount

      yi archivemount

- Use:

      sudo mkdir /mnt/archive
      archivemount archive.tar.gz /mnt/archive
      sudo umount /mnt/archive

## Hardware/Disk Utilities

### lshw

Displays hardware-related information.

- Install `:role:workstation`:

      agi lshw lshw-gtk

      yi lshw lshw-gui

### lstopo

Display computer block diagram graphically.

- Install:

      agi hwloc

      yi hwloc-gui

### SMART Disk Support

- Install `:role:workstation`:

      agi smartmontools

      yi smartmontools

### hdparm

- Install `:role:workstation`:

      agi hdparm

      yi hdparm

### Temperature Sensors

- Install:

      agi lm-sensors

      yi lm_sensors

- Install GUIs for sensors:

      agi conky xsensors

      yi conky xsensors

- Check:

      sensors

- Display GUI temperature:

      xsensors

## Misc Utilities

### ptee

- Install `:role:workstation`:

      pipxg install ptee

### dos2unix, unix2dos

- Install `:role:workstation`:

      agi tofrodos

      yi dos2unix

- (ubuntu) Create the traditional names `unix2dos`, `dos2unix`:

      sudo ln -s /usr/bin/{todos,unix2dos}
      sudo ln -s /usr/bin/{fromdos,dos2unix}

  Ansible `:role:workstation`:

  ```yaml
  - name: Make symlinks for `unix2dos`/`dos2unix`
    file:
      src: "/usr/bin/{{ item.src_name }}"
      dest: "/usr/local/bin/{{ item.dest_name }}"
      state: link
    loop:
      - src_name: todos
        dest_name: unix2dos
      - src_name: fromdos
        dest_name: dos2unix
  ```

### tree

- Install `:role:workstation`:

      agi tree

### Dictionaries

- Install various dictionaries of words for `/usr/share/dict`:

      agi wamerican-huge wamerican-insane wamerican-large wamerican-small

      yi words

### (ubuntu) Language support

(manual)

- The notification "Language Support is Incomplete" indicates that some language
  packages are not installed.  To report the list of missing packages:

      check-language-support

- To install these missing packages:


      apt install $(check-language-support)

### Most

- Install this 'more'-like, 'less'-like pager:

      agi most

      yi most

### stress

- Install `:role:workstation`:

      agi stress

      yi stress

- Invoke:

      stress --cpu 8 --io 4 --vm 2 --vm-bytes 128M

### strace

- Install `:role:workstation`:

      yi strace

### rlwrap (GNU readline Support Wrapper)

- Install:

      agi rlwrap

- Invocation:

      rlwrap some_program

### pigz (Parallel Implementation of GZip)

- During compression, uses all cores for substantial speedups while being gzip
  compatible.

- Can handle zlib-compressed data as well.

- Install:

      agi pigz

- Switch-compatible with gzip/gunzip:

      tar -cf . | pigz > file.tar.gz

      unpigz < file.gz > file

### snmp

- Helps to avoid errors like this in the logs:

      Cannot adopt OID in UCD-DLMOD-MIB

- Install:

      agi snmp

### Choose

- Combines `cut` and `awk` features; written in Rust by John Hagen's friend.

- Source: <https://github.com/theryangeary/choose>

- Install:

      cargo install choose

- Examples:

      choose -f ':' 0 3 5  # print the 0th, 3rd, and 5th item from a line, where
                           # items are separated by ':' instead of whitespace

### cookiecutter

- Install `:role:workstation`:

      pipxg install cookiecutter

- Configure `~/.cookiecutterrc` with:

      abbreviations:
          cc: https://github.com/drmikehenry/cookiecutter-{0}.git

  This allows invocations such as:

      cookiecutter cc:pythonapp

  Resulting in:

      cookiecutter https://github.com/drmikehenry/cookiecutter-pythonapp.git

- Test:

      mkdir ~/tmp/cookiecutter
      cd ~/tmp/cookiecutter
      cookiecutter https://github.com/audreyr/cookiecutter-pypackage/

### moreutils

Provides `errno` and other utilities.

- Install `:role:workstation`:

      agi moreutils

### uncrustify

- Uncrustify source code beautifier: <http://uncrustify.sourceforge.net/>

- Install:

      agi uncrustify

      yi uncrustify

- Might also like UniversalIndentGUI (but it wasn't that great):

      # (later)
      agi universalindentgui

### Checkinstall

- Builds custom package, instead of just using `make install`.

- Reference: <https://help.ubuntu.com/community/CheckInstall>

- Install:

      agi checkinstall

- After building a package, use `sudo checkinstall` instead of
  `sudo make install` to build a .deb file.

# Web Browsers

## Google Chrome

- Google Chrome home: <http://www.google.com/chrome/>

### (ubuntu) Google Chrome

- Instructions: <https://itslinuxfoss.com/install-google-chrome-ubuntu-22-04/>

- Install key:
  **TODO** Avoid `apt-key add`:

      #wget -q -O - https://dl.google.com/linux/linux_signing_key.pub |
      #  sudo apt-key add -

- Chrome sets up the cron job `/opt/google/chrome/cron/google-chrome` to
  periodically update `/etc/apt/sources.list.d/google-chrome.list`. To bootstrap
  the process, pre-create that file:

      echod -o /etc/apt/sources.list.d/google-chrome.list '
        deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main
      '

- Update and install stable version:

      apt-get update
      agi google-chrome-stable

- **Until the defaults change**, always run with `--password-store=detect` to
  ensure stored passwords are encrypted. Facilitated via a wrapper script
  `~/bin/chrome` that does:

      /opt/google/chrome/chrome --password-store=detect "$@"

Note: Installation of the open-source Chromium browser may be done via:

    # agi chromium-browser

For differences between Chrome and Chromium:
<http://code.google.com/p/chromium/wiki/ChromiumBrowserVsGoogleChrome>

At present, chromium-browser for Ubuntu doesn't seem to have kwallet support.

### (fedora) Google Chrome

- Instructions from:
  <http://www.if-not-true-then-false.com/2010/install-google-chrome-with-yum-on-fedora-red-hat-rhel/>

- Create repo file for Google Chrome:

      echod -o /etc/yum.repos.d/google-chrome.repo '
        [google-chrome]
        name=google-chrome - \$basearch
        baseurl=http://dl.google.com/linux/chrome/rpm/stable/\$basearch
        enabled=1
        gpgcheck=1
        gpgkey=https://dl-ssl.google.com/linux/linux_signing_key.pub
      '

- Install:

      yi google-chrome-stable

### (all) Google Chrome

- Configure: Choose icon to right of URL bar | Settings (same as visiting the
  URL <chrome://chrome/settings/>):
  - Settings section (on the left):
    - "Appearance": Check "Show Home button", change from New Tab page to
      <https://duckduckgo.com>.
    - "On Startup": choose "Continue where you left off"
    - Downloads | check "Ask where to save each file...".

## Dedicated Chrome for Zoom

- Use fake `$HOME` for Google Chrome for use with <https://zoom.us>.

- `~/bin2/zoom` launched google-chrome with temporary home directory:

      #!/bin/sh

      ZOOM_CHROME_HOME=$HOME/tmp/zoom_chrome_home mkdir -p "$ZOOM_CHROME_HOME"

      HOME="$ZOOM_CHROME_HOME" google-chrome

- See KeePassX for login details for zoom.us.

## Links

- Install:

      agi links

      yi links

# Network Apps/Tools

## liferea RSS Reader

- Install:

      agi liferea

      yi liferea

## portquiz.net

- Nice tool to verify outbound port connectivity, e.g.:

      $ telnet portquiz.net 8080
      Trying ...
      Connected to portquiz.net.
      Escape character is '^]'.

      $ nc -v portquiz.net 8080
      Connection to portquiz.net 8080 port [tcp/daytime] succeeded!

      $ curl portquiz.net:8080
      Port 8080 test successful!
      Your IP: 1.2.3.4

      $ wget -qO- portquiz.net:8080
      Port 8080 test successful!
      Your IP: 1.2.3.4

- Here is the content of `/etc/iptables/rules.v4`:

      # Generated by iptables-save v1.4.14 on Sun Aug 25 12:43:34 2013
      *nat
      :PREROUTING ACCEPT [0:0]
      :POSTROUTING ACCEPT [0:0]
      :OUTPUT ACCEPT [0:0]
      -A PREROUTING -i lo -j RETURN
      -A PREROUTING -p icmp -j RETURN
      -A PREROUTING -m state --state RELATED,ESTABLISHED -j RETURN
      -A PREROUTING -p tcp -m tcp --dport 22 -j RETURN
      -A PREROUTING -p tcp -m tcp --dport 21 -j RETURN
      -A PREROUTING -p tcp -m tcp --dport 25 -j RETURN
      -A PREROUTING -p tcp -m tcp --dport 80 -j RETURN
      -A PREROUTING -p tcp -m tcp --dport 443 -j RETURN
      -A PREROUTING -p tcp -j DNAT --to-destination :80
      COMMIT
      # Completed on Sun Aug 25 12:43:34 2013
      # Generated by iptables-save v1.4.14 on Sun Aug 25 12:43:34 2013
      *filter
      :INPUT ACCEPT [0:0]
      :FORWARD ACCEPT [0:0]
      :OUTPUT ACCEPT [0:0]
      -A INPUT -p icmp -j ACCEPT
      -A INPUT -i lo -j ACCEPT
      -A INPUT -m state --state RELATED,ESTABLISHED -j ACCEPT
      -A INPUT -p tcp -m state --state NEW -m tcp --dport 22 -j ACCEPT
      -A INPUT -p tcp -m state --state NEW -m tcp --dport 21 -j ACCEPT
      -A INPUT -p tcp -m state --state NEW -m tcp --dport 25 -j ACCEPT
      -A INPUT -p tcp -m state --state NEW -m tcp --dport 80 -j ACCEPT
      -A INPUT -p tcp -m state --state NEW -m tcp --dport 443 -j ACCEPT
      -A INPUT -j DROP
      COMMIT
      # Completed on Sun Aug 25 12:43:34 2013

  The filter table is classical: ACCEPT a few services, then DROP the rest.

  Portquiz.net logic is in the nat table:

      Forward connection on any port to port 80 (DNAT –to-destination :80)
      Except for normal services (just RETURN for normal activity)

## (ubuntu) Netcat (OpenBSD variant)

- Install:

      # Ubuntu 18.04 appears to have this installed already.

      agi netcat-openbsd

  (Takes priority over netcat-traditional by default)

## socat

- Install `:role:workstation`:

      agi socat

      yi socat

## traceroute

- Install `:role:workstation`:

      agi traceroute

      yi traceroute

## nmap

- Install `:role:workstation`:

      agi nmap

      yi nmap

## socks proxy

- Tunnel via ssh to setup a socks5 proxy:

      ssh -D1234 destination.server

  Now localhost:1234 is a SOCKS5 proxy.

- Install `tsocks`:

      agi tsocks

- Configure:

      echod -o /etc/tsocks.conf '
        server = 127.0.0.1
        server_type = 5
        server_port = 1234
      '

- Wrap `tsocks` around any app, e.g.:

      tsocks apt-get install some-package

**NOTE** Some indications are that tsocks doesn't push DNS queries through the
socks proxy, so if DNS isn't working properly, this won't work either.

## sshfs

- Install:

      agi sshfs

      yi sshfs

- To mount `/m` from bolt, for example:

      mkdir -p ~/tmp/m
      sshfs mike@bolt:/m ~/tmp/m

      ls ~/tmp/m
      sudo umount ~/tmp/m

## wireshark

- Install `:role:workstation`:

      agi wireshark

      yi wireshark

  (ubuntu) Allow non-superusers to capture packets.

## telnet

- Install:

      agi telnet

      yi telnet

## AWS Command-line Tool (S3 Bucket Support)

- AWS CLI tool is here: <https://github.com/aws/aws-cli>

- Install latest version:

      pipxg install awscli

- Example invocation to list `rustup` versions:

      aws s3 ls --no-sign-request s3://static-rust-lang-org/rustup/archive/

  Use `--recursive` for recursive directory listing.

- Example download of `release-stable.toml` for `rustup`:

      aws s3 cp --no-sign-request \
        s3://static-rust-lang-org/rustup/release-stable.toml .

# Version Control

## Git

- Install `:role:workstation`:

      agi git-doc git-svn git-gui qgit

      yi git-gui qgit

## Subversion

### svnwrap

- Install `:role:workstation`:

      pipxg install svnwrap

### Subversion svnshell

- Install `svnshell`:

      agi python-subversion

- Configure (probably just take saved config file).

- Test with svnserve:

  - Edit `path/to/repo/conf/svnserve.conf`:

        # Ensure this is uncommented:
        password-db = passwd

        # To disable anonymous access entirely, use these lines:
        anon-access = none
        auth-access = write

  - Setup dummy password file `path/to/repo/conf/passwd`:

        [users]
        mike = password

  - Run `svnserve` in "daemon-mode", but in foreground with a log file:

        svnserve -d --foreground --log-file /tmp/svnserve.log

  - Use absolute path with `svn:`. For example:

        cd ~/tmp/svn
        svnadmin create test.repo
        svn ls svn://localhost/home/mike/tmp/svn/test.repo

## Mercurial

- Install:

      agi mercurial

      yi mercurial

## Bazaar

- Install:

      agi bzr

      yi bzr

## CVS

- Install:

      agi cvs

      yi cvs

# Development Tools

## General Build Tools

- Install `:role:workstation`:

      agi build-essential linux-headers-generic cmake ddd automake autopoint \
          make-doc manpages-dev perl-doc texinfo texi2html

      yi @'Development Tools' \
        @'Development Libraries' \
        @'C Development Tools and Libraries'

      yi scons cmake cmake-gui ddd texinfo gcc-c++ man-pages

## Clang tools

- Install `:role:workstation`:

      agi clang clang-format clang-tidy clang-tools clangd

- Install clang docs (requires explicit version) `:role:workstation`:

      agi clang-14-doc

- Update alternatives if necessary:

    for i in clang clang++ clangd clang-format clang-tidy; do
      update-alternatives \
        --install \
        /usr/bin/$i \
        $i \
        /usr/bin/$i-14 \
        100
    done

- Create per-project `.clang-format` file with:

      BasedOnStyle: Google
      AlignEscapedNewlines: DontAlign
      BinPackArguments: false
      BinPackParameters: false
      IndentCaseLabels: false
      AlwaysBreakAfterReturnType: All
      AllowShortFunctionsOnASingleLine: None
      AllowShortIfStatementsOnASingleLine: false
      AllowShortLoopsOnASingleLine: false
      AlignOperands:   false
      AlignAfterOpenBracket: AlwaysBreak
      DerivePointerAlignment: false
      PointerAlignment: Right
      SortIncludes:  false
      ReflowComments:  false
      IndentWidth:     4
      BreakBeforeBraces: Custom
      BraceWrapping:
        AfterClass:      true
        AfterControlStatement: true
        AfterEnum:       true
        AfterFunction:   true
        AfterNamespace:  true
        AfterObjCDeclaration: true
        AfterStruct:     true
        AfterUnion:      true
        AfterExternBlock: false
        BeforeCatch:     true
        BeforeElse:      true
        SplitEmptyFunction: true
        SplitEmptyRecord: true
        SplitEmptyNamespace: true


- Create global per-user `~/.clang-format` with the above content.

## compiledb

Creates `compile-commands.json` (for Clangd):

- Install `:role:workstation`:

      pipxg install compiledb

- Usage:

      compiledb --help

## Exuberant ctags

- Install `:role:workstation`:

      agi exuberant-ctags

      yi ctags

## Universal ctags

TODO: Figure out the incompatibilities with Exuberant ctags and migrate to
Universal ctags.

- Install:

      agi universal-ctags

## 32-bit Libraries

- Install `:role:workstation`:

      agi gcc-multilib g++-multilib

## PowerPC cross compiler

- Install:

      agi gcc-powerpc-linux-gnu

## Arm cross compiler

- Install:

      agi gcc-arm-linux-gnueabihf

## bmake

NetBSD make for POSIX compatibility testing.

- Install `:role:workstation`:

      agi bmake

# Programming

## Editors

### Vim

#### Stock Vim with Plugin Dependencies

- Install `:role:workstation`:

      agi vim vim-gtk exuberant-ctags ruby ruby-dev

      yi vim vim-X11 ctags ruby ruby-devel perl-ExtUtils-Embed

#### Build Vim from Source

- Follow instructions in Vimfiles `:help notes_build_vim`.

### Neovim

- References:

  - <https://github.com/neovim/neovim/wiki/Installing-Neovim>

- Add PPA:

      add-apt-repository -y --update ppa:neovim-ppa/stable

- Install:

      agi neovim

### Emacs

- Install:

      agi emacs

      yi emacs

### Bless Hex Editor

- Install:

      agi bless

## Python

### ipython

Install using `pipxg`/`pipsig2` for isolation. Any additional packages that are
interesting globally can be installed into the `ipython` virtual environments as
needed.

- Install `:role:workstation`:

      pipxg install ipython

- Install for optional Python 2 support:

      # 5.8.0 is the newest version that works with Python2.
      pipsig2 install ipython==5.8.0

- Create default configuration (shared for Python 2, Python 3):

      ipython profile create

  (manual)

- Backup configuration:

      cp ~/.ipython/profile_default/ipython_config.py{,.dist}

- Edit configuration:

      vim ~/.ipython/profile_default/ipython_config.py

      c.TerminalInteractiveShell.confirm_exit = False

### Python Development versions

- Install development versions of Python along with documentation:

      agi python-dev python-doc \
        python3-dev python3-doc

### Python GUIs

#### Python TK

- Ubuntu packages TK support separately.

- Install:

      agi python-tk python3-tk

#### Python PyQt

- Install:

      agi python-qt4 python-qt4-dev python-qt4-doc qt4-doc qt4-dev-tools

      yi PyQt4 PyQt4-devel

### Pygame

- Ref:
  <https://stackoverflow.com/questions/51159099/pip-install-pygame-on-ubuntu-18-04-using-pyenv-python-3-7>

- Install dependencies:

      apt-get build-dep -y python-pygame

- Install pygame into per-project virtual environment:

      mktmpenv
      pip install pygame

### Python tox

- Install `:role:workstation`:

      pipxg install tox

### Python pytest

- Install `:role:workstation`:

      pipxg install pytest

### Python checkers

#### Python mypy

- Install `:role:workstation`:

      pipxg install mypy

#### Python flake8

- Python 3-based flake8:

  (automated)

      pipxg install flake8
      # Now install add-ons into flake8 virtualenv:
      pipxg inject flake8 flake8-quotes pep8-naming

  Configure flake8-quotes to match the style enforced by the black formatter:

      echod -o ~/.config/flake8 '
        [flake8]
        inline-quotes = double
        ignore = E203
        # Match python-language-server default McCabe complexity.
        max-complexity = 15
      '

- Optional Python 2-based flake8:

      pipsig2 install flake8

      # Now install add-ons into Python 2-based flake8 virtualenv:
      . /usr/local/lib/pipsi2/flake8/bin/activate
      pip install flake8-quotes pep8-naming
      deactivate

      # Create flake82 wrapper for Python 2-based flake8::
      echod -o ~/bin/flake82 '
        #!/bin/sh

        exec /usr/local/lib/pipsi2/bin/flake8 "$@"
      '
      chmod +x ~/bin/flake82

#### Python Black

- Install `:role:workstation`:

      pipxg install black

#### Python isort

(manual)

- Install:

      pipxg install isort

#### Python Language Server

(automated)

- Install:

      pipxg install 'python-language-server[mccabe,pycodestyle,pydocstyle,pyflakes,rope]'

  Note: Not recommended yet; `pyls-mypy` doesn't seem to handle local imports
  correctly:

      # Not recommended yet:
      # pipxg inject python-language-server pyls-mypy

### Python Hatch

- Install:

      pipxg install hatch

### Python pip-tools

- Install:

      pipxg install pip-tools

### Python Dependency Tool (pydeps)

- Install:

      pipxg install pydeps

### Multiple Python Interpreters via pyenv

(manual)

- `pyenv` tools: <https://github.com/pyenv/pyenv>

- Also see instructions in <https://github.com/drmikehenry/pythonsource>.

- Install dependencies, e.g.:

      sudo apt-get build-dep python2.7
      sudo apt-get build-dep python3.10

- Clone repository to become `~/.pyenv`:

      git clone https://github.com/pyenv/pyenv ~/.pyenv

- Read pyenv instructions:

      less ~/.pyenv/README.md

- Add to `~/.profile`:

      echod -a ~/.profile '
        # pyenv support.
        pyenvactivate() {
            if [ -d "$HOME/.pyenv" ]; then
                export PYENV_ROOT="$HOME/.pyenv"
                PATH="$PYENV_ROOT/bin:$PATH"
                eval "$(pyenv init --path)"
                eval "$(pyenv init -)"
            else
                echo "Missing $HOME/.pyenv; can't activate"
                return 1
            fi
        }
      '

- Determine versions to support and squirrel into an environment variable:

      pyversions='2.7.15 3.5.6 3.6.7 3.7.1'

  **NOTE** Older python versions (3.0 - 3.4, 2.x except newer 2.7.y) require
  libssl1.0-dev instead of libssl-dev. Build for those versions separately; see
  later build steps.

  Ref: <https://github.com/pyenv/pyenv/issues/945>

- Install sources for the newest of each point release, e.g.:

      for i in $pyversions; do
        pyenv install $i
      done

- Build optional older versions here. **NOTE** This requires uninstalling
  `libssl-dev`; may want to check first to see what will be uninstalled (if
  anything) so it can be reinstalled afterward:

      agi libssl1.0-dev
      pyenv install 3.4.9
      agi libssl-dev
      pyversions="$pyversions 3.4.9"

- Setup global defaults to allow additional versions to show through. Use the
  system versions first followed by other desired versions:

      pyenv global system $pyversions

- List available interpreter versions:

      pyenv versions

### Python Shebang Lines

- There are two kinds of shebangs:
  - `#!/usr/bin/env python3`:
    - For installed-in-place scripts like `~/bin/script` that have no
      dependencies, and can therefore run with any-old-python3.
    - For source files in installable packages, including those installed via
      `pipx`/`pipsi`.
  - `#!/usr/bin/python3`:
    - Indicates dependencies are needed, so you care about which python
      environment.
    - But dependencies must be manually managed via `pip install --user`.

### wxWidgets

- Install:

      agi libwxgtk3.0

### wxPython

- Install:

      agi python3-wxgtk4.0

## C/C++

### boost

- Install:

      agi libboost-all-dev

      yi boost-devel

### Qt

- Install:

      agi qtbase5-dev qtbase5-examples

      yi qt5-qtbase-devel qt5-qtbase-examples

### SDL

- Install:

      agi libsdl2-dev

### Django

- Install:

      agi python-django

      yi python-django{,-doc}

## Shell Scripting

### shellcheck Linter

- Reference: <https://www.shellcheck.net/>

- Install `:role:workstation`:

      agi shellcheck

### shfmt Formatter

(manual) TODO Ansible

- Reference: <https://github.com/mvdan/sh>

- Ensure "golang" is installed.

- Install as normal user:

      go install mvdan.cc/sh/cmd/shfmt@latest

## Zig

- From <https://ziglang.org/download/>

- Install:

      mkdir /opt/zig
      cd /opt/zig
      tar -xf .../zig-linux-x86_64-0.10.0-dev.1669+c21f046a8.tar.xz
      chmod +x zig-linux-x86_64-0.10.0-dev.1669+c21f046a8/zig
      ln -sf $PWD/zig-linux-x86_64-0.10.0-dev.1669+c21f046a8/zig /usr/local/bin

- Test:

      zig version

- zls:

  - CI workflows: <https://github.com/zigtools/zls/actions>

  - Download `builds.zip` from desired CI workflow.

  - Install:

        mkdir /opt/zig/zls
        cd /opt/zig/zls
        unzip .../builds.zip
        tar -xf x86_64-linux.tar.xz
        ln -sf $PWD/bin/zls /usr/local/bin

## Ruby

- Reference: <https://github.com/rvm/ubuntu_rvm>

- Add repository for Ubuntu package for `rvm`:

      add-apt-repository -y ppa:rael-gc/rvm
      apt-get update
      agi rvm

- Add `mike` to `rvm` group:

      gpasswd -a mike rvm

- As normal user, login (to activate the `rvm` group and source the script
  `etc/profile.d/rvm.sh`).

- Install latest ruby:

      rvm install ruby

- Setup to use version 2.4.1 by default:

      rvm use ruby-2.4.1 --default

  To remove the default:

      # NOTE: this doesn't work well yet.
      rvm alias delete default

- Generate documentation:

      rvm docs generate

### Ruby Gems

- Install `pry`:

      gem install pry

- Install Rubocop:

      gem install rubocop

- Install BinData:

      gem install bindata

## Doxygen

- Install `:role:workstation`:

      agi doxygen doxygen-doc graphviz graphviz-doc mscgen

      yi doxygen graphviz mscgen

## Java

### (ubuntu) Java

- <https://help.ubuntu.com/community/Java>
- Trying out OpenJDK for now (it's already installed).
- openjdk-8-jre is installed. See other packages such as openjdk-8-jdk for more
  options.

### (fedora) Java

#### Oracle Java

- Oracle Java instructions from:
  <http://www.if-not-true-then-false.com/2014/install-oracle-java-8-on-fedora-centos-rhel/>

- Download from:
  <http://www.oracle.com/technetwork/java/javase/downloads/index.html>

  Direct link (may not work unless accept license):
  <http://download.oracle.com/otn-pub/java/jdk/8u45-b14/jdk-8u45-linux-x64.rpm>

- Install:

      rpm -Uvh ~mike/download/programming/java/jdk-8u40-linux-x64.rpm

- Install alternatives:

      ## java ##
      alternatives --install /usr/bin/java java /usr/java/latest/bin/java 20000

      ## javaws ##
      alternatives --install /usr/bin/javaws javaws /usr/java/latest/bin/javaws 20000

      ## Java Browser (Mozilla) Plugin 64-bit ##
      alternatives --install /usr/lib64/mozilla/plugins/libjavaplugin.so libjavaplugin.so.x86_64 /usr/java/latest/jre/lib/amd64/libnpjp2.so 20000

      ## Install javac only if you installed JDK (Java Development Kit) package ##
      alternatives --install /usr/bin/javac javac /usr/java/latest/bin/javac 20000
      alternatives --install /usr/bin/jar jar /usr/java/latest/bin/jar 20000

- Choose alternative java implementation (one at a time):

      alternatives --config java
      alternatives --config javaws
      alternatives --config libjavaplugin.so.x86_64
      alternatives --config javac
      alternatives --config jar

- A fix for `failed to read link /usr/bin/javaws`:
  <http://johnglotzer.blogspot.com/2012/09/alternatives-install-gets-stuck-failed.html>

  Essentially, remove the contents of `/var/lib/alternatives/SOMETHING` if the
  invocation of `alternatives --install /usr/bin/SOMETHING` fails, then try
  again (do the `--install` over again).

#### OpenJDK

- Doesn't work for chess.com.

- Can leave it installed anyway if needed to fulfill dependencies.

- Fedora FAQ recommends OpenJDK version:
  <https://fedoraproject.org/wiki/Java/FAQ>

- Install:

      yi java-1.7.0-openjdk{,-devel,-javadoc,-demo} icedtea-web

## Haskell

- Install Haskell Platform:

      agi haskell-platform haskell-platform-doc

      yi haskell-platform

## golang

For the "Go" programming language.

- (ubuntu) For old distro, setup PPA:

      add-apt-repository -y --update ppa:longsleep/golang-backports

- Install `:role:workstation`:

      agi golang

      yi golang

- Setup `~/.profile`:

      echod -a ~/.profile '
        # Go support.
        if [ -d "$HOME/go" ]; then
            export GOPATH=$HOME/go
            pathprepend "$GOPATH/bin"
        fi
      '

- (manual) Pre-create `~/go/bin` so that it will be added to `PATH` at next
  login:

      mkdir -p ~/go/bin

## Node.js

References:

- <https://nodejs.org/en/>
- <https://yarnpkg.com/getting-started/install>

### Install node.js

- Download:

      curl -O https://nodejs.org/dist/v16.15.1/node-v16.15.1-linux-x64.tar.xz

- Extract:

      cd /opt
      tar -xf .../node-v16.15.1-linux-x64.tar.xz

- Install symlinks:

      ln -s /opt/node-v16.15.1-linux-x64/bin/* /usr/local/bin

### Install yarn

- As root:

      corepack enable

## Rust

- Reference: <https://rustup.rs/>

- `https://static.rust-lang.org` is the default server for Rust toolchains and
  tools like `rustup`.

- (automated) Acquire `rustup`:

      curl -o /tmp/rustup-init \
        https://static.rust-lang.org/rustup/dist/x86_64-unknown-linux-gnu/rustup-init

- (automated) Make `rustup-init` executable:

      chmod +x /tmp/rustup-init

- (automated) Invoke `rustup-init` to install `rustup`:

      /tmp/rustup-init -q -y --no-modify-path

  Use `--no-modify-path` because (homegit) has version-controlled settings for
  `PATH` that include `~/.cargo/bin`.

  Note that `rustup-init` installs a toolchain and various tools in
  `~/.cargo/bin`, e.g.:

      cargo
      cargo-clippy
      cargo-fmt
      cargo-miri
      clippy-driver
      rls
      rustc
      rustdoc
      rustfmt
      rust-gdb
      rust-lldb
      rustup

- Install additional components if desired:

      rustup component add rls rust-src

- View components (installed and available):

      rustup component list

- Install nightly toolchain for a given date:

      rustup install nightly-2022-05-30

  Set as default toolchain:

      rustup default nightly-2022-05-30

  Add components:

      rustup component add rls rust-src

- (homegit) Setup global rustfmt.toml:

      mkdir -p ~/.config/rustfmt
      echod -o ~/.config/rustfmt/rustfmt.toml '
        edition = "2018"
        max_width = 100
      '

### Rust Analyzer

- Available from: <https://rust-analyzer.github.io/>

- Download from releases area.

- Expand into directory in the path, e.g.:

      sudo cp rust-analyzer-x86_64-unknown-linux-gnu.gz /usr/local/bin
      sudo gunzip /usr/local/bin/rust-analyzer-x86_64-unknown-linux-gnu.gz
      sudo chmod +x /usr/local/bin/rust-analyzer-x86_64-unknown-linux-gnu
      sudo ln -s \
        /usr/local/bin/rust-analyzer-x86_64-unknown-linux-gnu \
        /usr/local/bin/rust-analyzer

## MIT-scheme

- Useful for "Structure and Interpretation of Computer Programs" (SICP).

- Install:

      agi mit-scheme mit-scheme-doc

- Execute:

      mit-scheme

# Markup

## reStructuredText

### docutils

- Install `:role:workstation`:

      pipxg install sphinx

- Use:

      sphinx-quickstart

### sphinx with pygments

(automated)

- Install:

      pipxg install docutils &&
        pipxg inject docutils pygments

- Use:

      rst2html.py

### rstcheck Linter

- Install `:role:workstation`:

      pipxg install rstcheck

## markdown

### markdown lint

- Install:

      gem install mdl

- Usage:

      mdl some_file.md

  To restrict to only rules `MD024` and `MD046` (for example):

      mdl -r MD024,MD046 some_file.md

  To use all rules except `MD046`:

      mdl -r '~MD046' some_file.md

## pandoc

- Markup conversions (e.g., Mediawiki to reStructuredText).

- Install `:role:workstation`:

      agi pandoc

      yi pandoc

- (optional) Get latest version from Github releases page, e.g.:
  <https://github.com/jgm/pandoc/releases/tag/2.17.1.1/>

  Get amd64 version:

      pandoc-2.17.1.1-1-amd64.deb

- Usage hints:

  - To convert to Github-flavored Markdown:

        pandoc INPUTFILE -t gfm -o OUTPUTFILE.md

  - For `.md` to `.html`:

        pandoc file.md -o file.html

- (optional) Build from source:

  - Need 2022-05-14 pandoc to convert with two-character indentation in output
    Markdown using pandoc compiled from source on Ubuntu 22-04 (the latest
    release as of 2022-06-18, version 2.18, is not new enough).

        pandoc  -s linux.rst -t gfm -o linux-pandoc.md

  - Ensure Haskell is installed (requires GHC >= 7.10 and cabal >= 2.0; Ubuntu
    22.04 has GCH 8.8.4 and cabal 3.0.1.0).  See Haskell instructions.

  - Clone sources:

        mkdir -p ~/build
        cd ~/build
        git clone https://github.com/jgm/pandoc.git
        cd pandoc

  - Build (very slow):

        cabal install

  - Binary `pandoc` will be in `$CABALDIR/bin` (`~/.cabal/bin`).
    Can be copied into `/usr/local/bin/`.

- (optional) Install using cabal for latest version (fedora 17 is too old):

      sudo cabal update
      sudo cabal install pandoc

## HTML tidy

- Install `:role:workstation`:

      agi tidy

      yi tidy

## html2text

- Install `:role:workstation`:

      agi html2text

## linuxdoc-tools

- For generating documentation (a.k.a. sgmltools on some distros).

- Install:

      agi linuxdoc-tools{,-latex,-text}

      yi linuxdoc-tools

## JSON

- Install jq (command-line tool for JSON querying/pretty-printing/parsing):

      agi jq

- Install glom (path-based data access in Python; similar to jq):

      pipxg install glom

- Install gron (for grepping JSON; reduces hierarchy to single-line values):

      pipxg install gron

- Install jc (for parsing CLI output into JSON):

      pipxg install jc

  Example:

      $ ls -l /usr/bin | jc --ls | jq '.[] | select(.size > 50000000)'
      {
        "filename": "docker",
        "flags": "-rwxr-xr-x",
        "links": 1,
        "owner": "root",
        "group": "root",
        "size": 68677120,
        "date": "Aug 14 19:41"
      }

  More:

      jc ifconfig
      ifconfig | jc --ifconfig

- Install jtbl (for displaying JSON data in tables):

      pipxg install jtbl

  Example:

      ls -l /usr/bin | jc --ls | jq '.[] | select(.size > 50000000)' -c | jtbl

      filename    flags         links  owner    group         size  date
      ----------  ----------  -------  -------  -------  ---------  ------------
      docker      -rwxr-xr-x        1  root     root      89221056  Mar 10 21:24
      dockerd     -rwxr-xr-x        1  root     root     104999776  Mar 10 21:24
      pandoc      -rwxr-xr-x        1  root     root      51859776  Jan 26 2018

- Install jello (for filtering JSON and JSON Linux data with Python syntax):

      pipxg install jello

- Install mario (for Python pipelines in the shell):

      pipxg install mario

  **NOTE** This actually requires Python 3.7+, so not tried yet.

# Emulation

## VirtualBox

- Oracle instructions from: <http://www.virtualbox.org/wiki/Linux_Downloads>

### (ubuntu) VirtualBox

(manual)

- Instructions:

  - <https://help.ubuntu.com/community/VirtualBox>
  - <https://askubuntu.com/questions/1029198/skipping-acquire-of-configured-file-contrib-binary-i386-packages-as-repository>
  - <https://askubuntu.com/questions/41478/how-do-i-install-the-virtualbox-version-from-oracle-to-install-an-extension-pack/41487#41487>
  - <https://www.virtualbox.org/wiki/Linux_Downloads>

- (one-time) Acquire Oracle 2016 key:

    wget https://www.virtualbox.org/download/oracle_vbox_2016.asc

  Copy `oracle_vbox_2016.asc` contents into below command.

- Dearmor Oracle 2016 key into `/etc/apt/keyrings/oracle_vbox_2016.gpg`:

    echod '
      -----BEGIN PGP PUBLIC KEY BLOCK-----
      Version: GnuPG v1.4.12 (GNU/Linux)

      mQINBFcZ9OEBEACSvycoAEIKJnyyIpZ9cZLCWa+rHjXJzPymndnPOwZr9lksZVYs
      12YnsEy7Uj48rTB6mipbIuDDH9VBybJzpu3YjY7PFTkYAeW6WAPeJ8RcSGXsDvc0
      fQ8c+7/2V1bpNofc9vDSdvcM/U8ULQcNeEa6DI4/wgy2sWLXpi1DYhuUOSU10I97
      KHPwmpWQPsLtLHEeodeOTvnmSvLX1RRl32TPFLpLdjTpkEGS7XrOEXelqzMBQXau
      VUwanUzQ2VkzKnh4WecmKFT7iekOFVHiW0355ErL2RZvEDfjMjeIOOa/lPmW7y4F
      fHMU3a3sT3EzpD9ST/JGhrmaZ+r5yQD4s4hn1FheYFUtUN0dqHe9KgPDecUGgh4w
      rGnm0nUQsmQLKGSFXskqt26IiERdRt1eXpR9C5yufCVZfYpSsoG/mIHAt9opXFqi
      ryJqzx5pfQkOLTz9WErThHK1399jyXJwYGKLyddHFQEdy3u3ELM8Kfp7SZD/ERVq
      t2oA8jsr24IOyL16cydzfSP2kAV1r30bsF/1Q4qq6ii/KfDLaI0KEliBLQuB9jrA
      6XQ69VLtkNPgiWzVMclg+qW1pA8ptXqXLMxi4h5EmE5GOhsihuwkwhhBmFqGT1RJ
      EGlc/uiHWQskOW3nhQ3Epd6xhCUImy8Eu83YRxS6QriH6K8z5LgRSdg9nwARAQAB
      tElPcmFjbGUgQ29ycG9yYXRpb24gKFZpcnR1YWxCb3ggYXJjaGl2ZSBzaWduaW5n
      IGtleSkgPGluZm9AdmlydHVhbGJveC5vcmc+iQI3BBMBCgAhBQJXGfThAhsDBQsJ
      CAcDBRUKCQgLBRYDAgEAAh4BAheAAAoJEKL2g8UpgK7P49QP/39dH+lFqlD9ruCV
      apBKVPmWTiwWbqmjxAV35PzG9reO7zHeZHil7vQ6UCb6FGMgZaYzcj4Sl9xVxfbH
      Zk7lMgyLDuNMTTG4c6WUxQV9UH4i75E1IBm9lOJw64bpbpfEezUF/60PAFIiFBvD
      34qUAoVKe49PbvuTy98er5Kw6Kea880emWxU6I1Q1ZA80+o2dFEEtQc+KCgfWFgd
      O757WrqbTj6gjQjBAD5B4z5SwBYMg1/TiAYF0oa+a32LNhQIza/5H3Y+ufMfO3tY
      B/z1jLj8ee5lhjrv0jWvvfUUeIlq5pNoOmtNYFS+TdkO0rsqEC6AD0JRTKsRHOBu
      eSj7SLt8gmqy7eEzRCMlYIvoQEzt0/JuTQNJjHCuxH1scV13Q3bK6SmxqlY46tf5
      Ljni9Z4lLJ7MB1BF2MkHuwQ7OcaEgUQBZSudzPkpRnY0AktiQYYP4Q1uDp+vfvFp
      GTkY1pqz3z2XD66fLz0ea5WIBBb3X/uq9zdHu8BTwDCiZlWLaDR5eQoZWWe+u+5J
      NUx1wcBpC1Hr2AnmuXBCRq+bzd8iaB8qxWfpCAFZBksSIW2aGhigSeYdx1jpjOob
      xog4qbuo5w1IUh8YLHwQ6uM12CqwC1nZadLxG0Fj4KoYbvp0T5ryBM3XD+TVGjKB
      m/QHLqabxZBbuJT0Cw2dRtW/ty5ZuQINBFcZ9OEBEADEY+YveerQjzzy5nA1FjQG
      XSaPcjy4JlloRxrUyqlATA0AIuK7cwc7PVrpstV8mR9qb38fdeIoY1z1dD3wnQzJ
      lbDfZhS5nGMzk9AANd6eJ2KcWI3qLeB//4fr2pPS0piOG4qyW4IhY4KeuCwusE6d
      IyDBg2XEdpG1IesSDaqNsvLZjPFEBNiCIkqrC7XSmoPNwHkKGj5LeD1wAE914cn2
      a04IlbXiT46V9jjJFnNem/Co0u+2e2J3oReNmHvbb62OC57rqeBxqBplXg9tvJk/
      w0A3bXxUrfz83tY6vDYoFdwJDudaJJWQjvqpYnySXMJYT6KoE4Xgl5fNcbNIVUpU
      k74BcWD9PZVadSMN7FWZzMfVsbTMmUA22tuDKD6hrF6ysCelex4YO44kSH7dhXu5
      ANtZ2BFfRZvdjTQoblOI8C9cy/iX74vvG8OZarFG+u/kon3+xcAgY5KceUVbostO
      0n3V8iK0gMQWH8sR8vXH+oV4GqHUEQURax2XM2Tt7Ra5XGcQaYDIkNPKSVVVtTk5
      3OU/bNoBofAbwd4eOZOf9ag5ZVIIaoubMOEiveGYde4AEVE7krSNcYh/C48iCVKr
      eOyS26AVA15dAvnKTAqxJqICUSQ9zjGfTp1obhXCkMAy0m+AxNVEfSzFznQLHtWK
      zEGr+zCsvj1R8/qlMpHBXQARAQABiQIfBBgBCgAJBQJXGfThAhsMAAoJEKL2g8Up
      gK7PKpQP+wY9zLgnJeqrvNowmd70afd8SVge9BvhLh60cdG+piM5ZuEV5ZmfTFoX
      XPHzOo2dgt6VYTE9JO72Jv7MyzJj3zw3G/IcJQ6VuQwzfKkFTD+IeOiXX2I2lX1y
      nFv24rs1MTZ4Px1NJai7fdyXLiCl3ToYBmLafFpfbsVEwJ8U9bCDrHE4KTVc9IXO
      KQ5/86JaIPN+JJLHJoO2EBQC08Cw3oxTDFVcWZ/IWvEFeqyqRSyoFMoDkjLYsqHS
      we1kEoMmM2qN20otpKYq8R+bIEI5KKuJvAts/1xKE2cHeRvwl5kcFw/S3QQjKj+b
      LCVTSRZ6EgcDDmsAPKt7o01wmu+P3IjDoiyMZJQZpZIA2pYDxruY+OLXpcmw78Gq
      lTXb4Q9Vf47sAE8HmHfkh/wrdDeEiY9TQErzCBCufYbQj7sgttGoxAt12N+pUepM
      MBceAsnqkF6aEa4n8dUTdS2/nijnyUZ2rDVzikmKc0JlrZEKaw8orDzg8fXzfHIc
      pTrXCmFLX5BzNQ4ezAlw0NZG/qvhSBCuAkFiibfQUal8KLYwswvGJFghuQHsVTkf
      gF8Op7Br7loTNnp3yiI0jo2D+7DBFqtiSHCq1fIgktmKQoVLCfd3wlBJ/o9cguT4
      Y3B83Y34PxuSIq2kokIGo8JhqfqPB/ohtTLHg/o9RhP8xmfvALRD
      =Rv7/
      -----END PGP PUBLIC KEY BLOCK-----
    ' | gpg --dearmor --yes -o /etc/apt/keyrings/oracle_vbox_2016.gpg

- Create a `.sources` file for virtualbox:

      echod -o /etc/apt/sources.list.d/virtualbox.sources "
        Types: deb
        Architectures: amd64
        URIs: https://download.virtualbox.org/virtualbox/debian/
        Suites: $(lsb_release -cs)
        Components: contrib
        Signed-By: /etc/apt/keyrings/oracle_vbox_2016.gpg
      "

- Update APT cache:

      apt-get update

- Install virtualbox and extension pack:

      agi virtualbox-6.1

  **NOTE** virtualbox-ext-pack is apparently an Ubuntu-provided package that
  should not be mixed with virtualbox installed directly from Oracle's
  repository.

- For information on installing the extension pack:

  - <https://askubuntu.com/questions/754815/can-i-install-the-virtualbox-extension-pack-from-the-ubuntu-repositories>

- Based on the above, this will upgrade the extension pack:

      VBOXVERSION=`VBoxManage --version | sed -r 's/([0-9])\.([0-9])\.([0-9]{1,2}).*/\1.\2.\3/'`
      wget -q -N "http://download.virtualbox.org/virtualbox/$VBOXVERSION/Oracle_VM_VirtualBox_Extension_Pack-$VBOXVERSION.vbox-extpack"
      VBoxManage extpack install --replace Oracle*.vbox-extpack

      # Wait for license acceptance.

      rm Oracle*.vbox-extpack

- Verify extension pack:

      VBoxManage list extpacks

### (fedora) VirtualBox

- Instructions from:
  <http://www.if-not-true-then-false.com/2010/install-virtualbox-with-yum-on-fedora-centos-red-hat-rhel/>

- Setup Oracle repository:

      cd /etc/yum.repos.d/
      wget http://download.virtualbox.org/virtualbox/rpm/fedora/virtualbox.repo

- Install prerequisites:

      yi gcc kernel-devel dkms

- Install:

      yi VirtualBox-5.0

- Install extension pack: <https://www.virtualbox.org/wiki/Downloads>

  `Oracle_VM_VirtualBox_Extension_Pack-5.0.14-105127.vbox-extpack`

  - Stupidly, this is now separate from VirtualBox itself and so it requires a
    manual installation of the extension pack.

  - Save `Oracle_VM_VirtualBox_Extension_Pack-5.0.14-105127.vbox-extpack` to
    download directory.

  - *As root*, execute virtualbox directly on the extension pack:

        sudo virtualbox Oracle_VM_VirtualBox_Extension_Pack-5.0.14-105127.vbox-extpack

    Alternatively, *as root*, run VirtualBox, choose menu File | Preferences |
    Extensions, click on blue diamond and browse to .vbox-extpack file to
    install.

### (all) VirtualBox

(manual)

- Add user(s) to vboxusers group:

      sudo gpasswd -a mike vboxusers

- Logout/login, or ssh localhost for group `vboxusers` to take effect.

- To run:

      virtualbox

- Configure:

  - Choose menu File | Preferences:
    - General | Default Machine Folder, choose `~/vms`.
    - Update | Uncheck "Check for Updates"

- VirtualBox EFI support is incomplete.  The boot order menu doesn't
  apply in EFI mode, and you can't press Escape fast enough to bring up
  an EFI boot prompt.  BIOS mode may just be easiest:
  <https://forums.virtualbox.org/viewtopic.php?t=106935>

- **Display scaling for 4k monitor**:

  - Per VM:

    - Setting | Display | Scale Factor | 200%

  - Also can experiment with environment variables:

        # For Qt scaling:
        export PLASMA_USE_QT_SCALING=1

        # For GTK3 scaling:
        export GDK_SCALE=2
        export GDK_DPI_SCALE=0.5

- For using physical hard drive (including USB flash drive):

  - Create a copy of the raw device node:

        sudo mkdir -p /xdev
        for i in a b c d e; do
          sudo cp -a /dev/sd$i /xdev/raw_sd$i
        done
        sudo chown -hR mike: /xdev

  - Create a raw VirtualBox disk:

        for i in a b c d e; do
        VBoxManage internalcommands createrawvmdk \
          -filename /xdev/raw_sd$i.vmdk \
          -rawdisk /xdev/raw_sd$i
        done

- Create new Virtual Machine using now-existing disk `sde.vmdk`.

- Might have to disable VT-x bit for Windows 2000 guest to fix this blue screen:

      ntoskrnl.exe KMODE_EXCEPTION_NOT_HANDLED at boot

  Didn't help to turn on I/O APIC (as had been suggested online).

### Compacting VirtualBox Virtual Disk

- <http://eight.wikia.com/wiki/How_To_Shrink_VirtualBox_Windows_8_VDI_File>

- <http://www.netreliant.com/news/9/17/Compacting-VirtualBox-Disk-Images-Windows-Guests.html>

- Run administrator cmd.exe and perform degragment operation:

      defrag C: /U /V /X

- Run `sdelete` tool from
  <http://technet.microsoft.com/en-us/sysinternals/bb897443>:

      cd \apps\sdelete
      sdelete64 -z c:

- Shutdown the VM, then at command prompt:

      cd ~/vms/windows8.1pro64bit
      VBoxManage modifyvdi $PWD/windows8.1pro64bit.vdi compact

## Docker

- References:

  - <https://docs.docker.com/>
  - <https://docs.docker.com/engine/>
  - <https://docs.docker.com/engine/install/ubuntu/>
  - <https://docs.docker.com/engine/install/linux-postinstall/>
  - <https://docs.docker.com/get-started/>
  - "Containers from Scratch", Liz Rice, GOTO 2018:
    <https://youtu.be/8fi7uSYlOdc>

- Install key:

  **TODO** Avoid `apt-key add`:

      #curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -

- Verify key:

      apt-key fingerprint 0EBFCD88

- Add repository:

      add-apt-repository \
        -y --update \
        "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
        $(lsb_release -cs) \
        stable"

- Install "Docker Engine - Community" and containerd:

      agi docker-ce docker-ce-cli containerd.io docker-compose-plugin

- Add user to `docker` group:

      usermod -aG docker mike

- Logout and login `mike` user (or use `newgrp docker`).

- Verify installation:

      docker run hello-world

- Longer demo:

      docker run -d -p 80:80 docker/getting-started

### Docker Container Example

- Perform as unprivileged user.
  - Download example:

        mkdir ~/tmp/docker
        cd ~/tmp/docker
        git clone https://github.com/dockersamples/node-bulletin-board
        cd node-bulletin-board/bulletin-board-app

  - Build the image:

        docker image build -t bulletinboard:1.0 .

  - Run image as a container:

        docker container run --publish 8000:8080 --detach \
          --name bb bulletinboard:1.0

  - Browser local service at: <http://localhost:8000>

  - Delete container:

        docker container rm --force bb

### Docker Compose Example

- Reference: <https://docs.docker.com/compose/gettingstarted/>

- Commands:

      docker compose up
      docker compose down

## dosbox

- Install:

      agi dosbox

      yi dosbox

- Run a program:

      dosbox /path/to/program.exe

## wine

- Install:

      agi wine-stable

      yi wine

- (optional; obsolete for our home network) Work-around for invalid `.local`
  domains that aren't just for zeroconf/bonjour stuff:

      vim /etc/nsswitch.conf

  Remove `mdns4_minimal [NOTFOUND=return]` from `hosts:` section:

      #hosts:      files dns mdns4_minimal
      hosts:      files dns

  Note: historically, `mdns4_minimal` was installed only as a dependency of
  `wine`; but these days, it's often installed by default and already a problem
  for `.local` domains. Not sure where these instructions ought to live now.

- Run a program:

      wine /path/to/winprog.exe

## vice (Commodore Emulator)

- Install:

      agi vice

      yi vice

# Multimedia

## PDF Editors

- Reference: PDF Form Example:
  <http://foersom.com/net/HowTo/data/OoPdfFormExample.pdf>

- <https://stackoverflow.com/questions/63199763/maintained-alternatives-to-pypdf2>

  - <https://github.com/pymupdf/PyMuPDF>

- <https://pythonawesome.com/performing-the-following-operations-using-python-on-pdf/>

  - Example script using `reportlab` to create and then `pdfrw` to fill a form.

### Libre Office

- Can use Libre Office for editing PDFs:

      lowriter SomeDocument.pdf

  Double-click to edit various text boxes.  Probably need to adjust the font
  size to make things fit in the space allowed.

  Afterward, `Export As` PDF to "save".

## PDF Viewers

### okular

- Install `:role:workstation`:

      agi okular

      yi okular

### zathura

- Install:

      agi zathura

      yi zathura zathura-plugins-all

## Audio

### Sound Setup

Microphone testing:

<https://bbs.archlinux.org/viewtopic.php?id=196525>

View audio input devices:

    arecord -l

Capture microphone with verbose output (shows amplitude):

    arecord -vvv -f dat /dev/null

e.g.:

    Max peak (12000 samples): 0x000001d5 #                    1%
    Max peak (12000 samples): 0x00000108 #                    0%
    Max peak (12000 samples): 0x00007896 ###################  94%

Record five seconds to a file, then play it back:

    arecord -d 5 test-mic.wav
    aplay test-mic.wav

### Pithos Pandora Client

- Install `:role:home`:

      agi pithos

### Pulseaudio Tools

- References:

  - Online microphone test: <https://www.onlinemictest.com/>

- Use `pavucontrol` to fix input/output (microphone/speaker) settings.

- Install volume control `:role:home`:

      agi pavucontrol

- Install preferences tool `:role:home`:

      agi paprefs

- Install volume meter `:role:home`:

      agi pavumeter

### Audacity

- Install `:role:home`:

      agi audacity

      yi audacity

### mpg321

- Install `:role:home`:

      agi mpg321

### sox

- Install:

      agi sox

      yi sox

### timidity MIDI Playback

- Reference:
  <https://wiki.winehq.org/MIDI#Selecting_the_Output_-_the_MIDI_mapper>

- Install:

      agi timidity

- Verify MIDI ports are not yet available (run as normal user):

      $ aconnect -o
      client 14: 'Midi Through' [type=kernel]
          0 'Midi Through Port-0'

- Original permissions on /etc/timidity:

      ll -d /etc/timidity/

      drwxr-xr-x 2 root root 4096 Sep 18 09:43 /etc/timidity/

- Need write access to create /etc/timidity/.config/ when running as timidity
  user:

      sudo chown -h timidity /etc/timidity

- Restart the daemon:

      sudo systemctl restart timidity

- Verify timidity ports are available (run as normal user):

      aconnect -o

      client 14: 'Midi Through' [type=kernel]
          0 'Midi Through Port-0'
      client 128: 'TiMidity' [type=user]
          0 'TiMidity port 0 '
          1 'TiMidity port 1 '
          2 'TiMidity port 2 '
          3 'TiMidity port 3 '

- Play sample MIDI file:

      aplaymidi -p 128:0 ~/x/sound/beetfure.mid

### Sound Converter

- For converting sound and ripping CDs.

- Install:

      agi soundconverter

      yi soundconverter

- Install transcode (used for k3b-based ripping):

      agi transcode

      yi transcode

- Software for ripping: <https://help.ubuntu.com/community/CDRipping>

### abcde

- A Better CD Encoder. For ripping CDs.

- Install `abcde`:

      agi abcde

      yi abcde

## Image

### Geeqie Image Viewer

- Install `:role:workstation`:

      agi geeqie

      yi geeqie

- Run `geeqie` and configure via Edit | Preferences | Preferences (though at
  present, nothing to configure).

### Gwenview Image Viewer

- Install `:role:home`:

      agi gwenview

- Also can go phone picture importation over MTP (Media Transfer Protocol):

      gwenview_importer camera:/

  **NOTE** Wants to delete the pictures by default, so be careful!

### gthumb Image Viewer

- Install `:role:home`:

      agi gthumb

### The GIMP

- Install `:role:home`:

      agi gimp

      yi gimp

### Pinta

- Simple image editor. Seems OK.

- Install:

      agi pinta

### Krita

- Simple image editor.

- Install:

      agi krita

### Inkscape

- Illustration editor.

- Install:

      agi inkscape

### Xpaint

- Install:

      agi xpaint

### exiftran

Transform jpeg exif data (e.g., losslessly rotate jpeg file).

- Install:

      agi exiftran

- Rotate all losslessly to match exif orientation tag, in-place:

      exiftran -ai *.jpg

### jhead

**NOTE** This one works well.

Manipulate jpeg files (e.g., losslessly rotate jpeg file).

- Install:

      agi jhead

- Rotate all losslessly to match exif orientation tag, in-place:

      jhead -autorot *.jpg

  Note: requires `jpegtran`.

### shotwell

- Install:

      agi shotwell

### digikam

- Install:

      agi digikam

## Video

### frei0r Video Plugins

- Install:

      agi frei0r-plugins

      yi frei0r-plugins

### ffmpeg

- Install `:role:home`:

      agi ffmpeg

- Converting a .mp4 file to better compression in two passes:

      ffmpeg -i infile.mp4 -strict -2 -vcodec libx264 -ac 1 -b:v 500k -bt 500k -pass 1 -passlogfile logfile.log outfile.mp4

      ffmpeg -i infile.mp4 -strict -2 -vcodec libx264 -ac 1 -b:v 500k -bt 500k -pass 2 -passlogfile logfile.log outfile.mp4

- Transcoding to make a video fit for devede (2 hours is too long for the
  version that I have on Ubuntu 16.04):

      ffmpeg -i 1021_20180619000000.ts -target ntsc-dvd 1021_20180619000000.mpg

#### (ubuntu) (alternative) Custom Build ffmpeg from Source

Custom build for ffmpeg.

- Build dependencies:

      apt-get build-dep ffmpeg

- Acquire and build:

      cd ~/build
      git clone git://git.videolan.org/ffmpeg.git
      cd ffmpeg
      ./configure
      make

- Build the `cws2fws` tool (uncompresses .swf files):

      make tools/cws2fws

- Execute:

      tools/cws2fws input.swf output.swf

### devede

- Create DVDs from video files.

- Install `:role:home`:

      agi devede

**IMPORTANT** Change the default video format from PAL to NTSC!

### mplayer

- Install `:role:home`:

      agi mplayer mplayer-gui

- (ubuntu) Configure gnome-mplayer:

  - Launch via `gnome-mplayer`.
  - Edit | Preferences (to configure).

### vlc

- Video LAN Controller. Playback of videos.

- Install vlc `:role:home`:

      agi vlc

- Configure vlc:

  - Launch via `vlc`.
  - Tools | Preferences | Input & Codecs:
    - Set Default optical device to `/dev/sr0`.

### xine

Video player.

- Install:

      agi xine-ui

      yi xine

### kdenlive

- Insert clips, create video.

- Can extract audio, then re-import and render to new video file.

- Install:

      agi kdenlive

      yi kdenlive

### openshot

- Insert clips, create video.

- Install:

      agi openshot

      yi openshot

### pitivi

- For video editing.

- Install:

      agi pitivi

### avidemux

- Useful for trimming length of a video.

- Install:

      yi avidemux

## DVD Burning

### k3b

- Install `:role:home`:

      agi k3b

### brasero

- Install `:role:home`:

      agi brasero

  **NOTE** Edit | Plugins, then uncheck `File Checksum` and `Image Checksum`
  plugins (they take a very long time and don't do anything useful).

### xfburn

- Install:

      agi xfburn

### growisofs

- Quite possibly already installed as a dependency of GUI-based burning tools.

- Install:

      agi growisofs

- Invoke:

      growisofs -dvd-compat -Z /dev/sr0=myimage.iso

## Screen Casting

- The best tool so far that seems to work is `ffmpeg`, though there is a bit of
  manual effort to determine the coordinates.

- This site explains options for Ubuntu screencasting:
  <http://ubuntuguide.org/wiki/Screencasts>

- The key point is to run `pavucontrol` (or `vucontrol`), then begin a capture
  with your chosen software (`ffmpeg`, for example), then setup the recording
  device in `pavucontrol`:

  - Make sure "Input Devices" includes "Monitor of Internal Audio Analog
    Stereo", and set this as the default.
  - Bring up "Recording" tab, and let it sit there while you begin a recording
    session with some application.
  - Once application is recording, the Recording tab should allow selection of
    the "Monitor of Internal Audio Analog Stereo" channel.
  - This should be remembered until next logout (or something like that).

- Presuming a rectangle at (1920, 0), with dimensions 980x500, the following
  invocation will record video and audio to an .mp4 file:

      ffmpeg -t 01:03:00 -f alsa -i pulse -f x11grab -s 980x500 -sameq -i :0.0+1920,0 screencast.mp4

  The `-i` switch limits the recording time.

### recordMyDesktop

**NOTE** No success with this tool

- Install:

      agi gtk-recordmydesktop

      yi qt-recordmydesktop

- Invocation:

      qt-recordMyDesktop

      gtk-recordMyDesktop

### Webcam Video Capture

- Install cheese:

      agi cheese

- Install guvcview:

      agi guvcview

### cheese

Takes pictures and other things with webcam.

- Reference: <https://wiki.gnome.org/Apps/Cheese>

- Install:

      agi cheese

# Scanning

- Install `:role:home`:

      agi libsane libsane-common libsane-dev libsane1 sane-utils

- (manual) Look for scanner:

      sane-find-scanner
      scanimage -L

- Install Gscan2pdf front end `:role:home`:

      agi gscan2pdf

  This has a lot of powerful features, including OCR via tesseract.

## Scanning alternative front-ends

### xsane scanning front-end

Seems to have lots of complexity.

- Install:

      agi xsane

### simple-scan scanning front-end

Very minimalistic.

- Install::

      agi simple-scan

### skanlite scanning front-end

This one seems to have a sluggish GUI.

- Install:

      agi skanlite

### xscanimage scanning front-end

Trivial GUI for scanning to a file; no preview or editing.

`xscanimage` comes with SANE utils; it's the GUI version of `scanimage`.

# Games

## Maelstrom

- Install `:role:home`:

      agi maelstrom

      yi Maelstrom

## PySol Fan-Club Edition

- Install:

      agi pysolfc pysolfc-cardsets

      yi PySolFC{,-music,-cardsets}

- (ubuntu) PySol 2.6.4-3 is broken on Ubuntu 22.04.  After installation,
  launching causes this exception:

      Traceback (most recent call last):
        File "/usr/games/pysolfc", line 36, in <module>
          from pysollib.main import main  # noqa: E402,I202
        ...
        File "/usr/share/games/pysolfc/pysollib/ui/tktile/tkhtml.py",
          line 24, in <module>
          import formatter
      ModuleNotFoundError: No module named 'formatter'

  `formatter.py` was removed from Python 3.10.

  This is a known issue: <https://github.com/shlomif/PySolFC/issues/217>

  Copying `formatter.py` from Python 3.9 fixes the problem:

      cp .../python3.9/formatter.py /usr/lib/python3.10/formatter.py

  The issue has been fixed in PySol 2.14, but this is not yet available on
  Ubuntu 22.04.

## Chess Games

- Install:

      agi xboard eboard dreamchess gnome-games knights

      yi xboard pychess knights

## term2048

The "2048" game in your terminal.

- Install:

      pip3 install term2048

## logicview

- Install wxPython for Python 3:

      agi python3-wxgtk4.0

- Clone source from bolt:

      mkdir -p ~/projects
      cd ~/projects
      git clone /m/srv/git/projects/logicview

- Create new `Logicview.desktop` file in the per-user applications area:

  - Browse with dolphin to:

        ~/.local/share/applications

  - Right-click | Create New | Link to Application:

    - General tab: Set name to `Logicview`
    - Application tab:
      - Name: Logicview
      - Description: Logic Problem Solving Assistant
      - Command: Browse to `logicview.py` in the checkout above

- Fix the icon in the `Logicview.desktop` file:

  - Right-click on `Logicview.desktop`, choose Open with Kate

  - Change `Icon=exec` to path to the `logicview.ico` file, similar to that
    found in `Exec=...` line. E.g.:

        Icon=/home/beth/projects/logicview/logicview.ico

## Kaser Games

- Install wine (for running the games at all):

      agi wine

- Install timidity (for playing music files in Kaser games):

      agi timidity

- Ensure `/mnt/tmp` exists:

      sudo mkdir -p /mnt/tmp

- Loopback mount the Kaser Games Collection CD .iso file:

      sudo mount /m/sys/disks/iso/kaser-games-collection.iso /mnt/tmp

- Run the Kaser installer via `wine`:

      wine /mnt/tmp/setup.exe

  - Enter Customer number and License ID from
    `/m/sys/disks/iso/kaser-games-collection.txt`.

  - Install all licensed products (already highlighted). Install to `C:\EKS`
    (default location).

- Unmount:

      sudo umount /mnt/tmp

- Run games via K menu:

  Applications | Wine | Programs | Everett Kaser Software

- Right-click on individual game:

  - Add to desktop if desired.

  - Properties shows location of all `.desktop` files:

        /home/beth/.local/share/applications/wine/Programs/Everett Kaser Software/

  - Can browse to the directory with dolphin, then

    - Right-click Desktop | Create new | Link to file or directory:
      - File name: Kaser games (or whatever you like)

      - Enter path of file or directory:

            /home/beth/.local/share/applications/wine/Programs/Everett Kaser Software/
    - Then can browse the Kaser folder easily and double-click to launch any
      games.

  - Can also just press Super (Windows) key and type "kaser"; that will select
    the "Everett Kaser Software" folder and show a list of all the games. Or
    similarly type the name of the actual game to run.

# Math

## speedcrunch

- Install `:role:workstation`:

      agi speedcrunch

      yi speedcrunch

## Reportlab

- Install:

      agi python-reportlab{,-accel,-accel-dbg,-doc}

      yi python-reportlab python-reportlab-docs

- Browse documentation: <http://www.reportlab.com/software/documentation/>

## Maxima

- Install:

      agi wxmaxima

      yi wxmaxima

## Sage

- (ubuntu):

  - <https://help.ubuntu.com/community/SAGE>

  - Setup PPA:

        add-apt-repository -y ppa:aims/sagemath
        apt-get update

- Install:

      # Note: VERY SLOW MIRROR.
      agi sagemath-upstream-binary

      yi sagemath

# Misc

Uncategorized or new items.

## excalidraw

This is a virtual whiteboard for sketching hand-drawn like diagrams.

References:

- <https://github.com/excalidraw/excalidraw>

Installation:

- Ensure `node.js` and `yarn` are installed.

- Acquire sources:

      cd ~/build
      git clone https://github.com/excalidraw/excalidraw
      cd excalidraw

- Run via yarn:

      yarn start
