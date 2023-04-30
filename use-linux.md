---
title: Using Linux
---

# Ubuntu desktop "Try Ubuntu" for pre-installation

- Boot Ubuntu desktop installer.

  **NOTE** server installation media does **not** allow using apt.

- "Try Ubuntu without installing".

- Update the apt cache:

      apt-get update

- Install ssh server:

      apt-get install -y openssh-server

- Set password for `ubuntu` user to `ubuntu`:

      passwd ubuntu

- Get IP address of machine:

      ip addr

- On another machine:

      ssh ubuntu@ip_address_of_install_machine

# Windows Password Reset from Linux

- Boot from Ubuntu Live USB drive.

- Software Center: Enable universe repository.

- Install:

      apt install chntpw

- Mount Windows volume:

      # Find partition:
      lsblk

      # Mount:
      mount /dev/sda3 /mnt

- Enter `C:\Windows\System32\config` directory:

      cd /mnt/WINDOWS/System32/config

- Run utility for desired user, modifying the hive file `SAM`:

      chntpw -u username_to_change SAM

- Choose "clear password" option, then quit and save changes.

# Package management

## Ubuntu package management

- References:

  - <https://help.ubuntu.com/community/Repositories/CommandLine>
  - <https://help.ubuntu.com/community/MetaPackages>

### Update list of available packages

    apt-get update

### Install a package

    apt-get install packagename
    # Can also remove using "install" command:
    apt-get install PACKAGE_TO_REMOVE-

To avoid most interactive prompting, set `DEBIAN_FRONTEND=noninteractive`:

    DEBIAN_FRONTEND=noninteractive apt-get install packagename

### Reinstallation

    apt-get --reinstall install PACKAGE

### Remove a package

    apt-get remove packagename
    # Can also install using "remove" command:
    apt-get remove PACKAGE_TO_INSTALL+

Full removal, including config files:

    apt-get --purge remove PACKAGE

Full removal after partial removal:

    apt-get purge PACKAGE

### Upgrade packages (no additions or removals)

    apt-get upgrade

### Show list of packages to be upgraded

    apt-get -u upgrade
    apt-get --dry-run upgrade

### Upgrade one more more packages (allow additions and removals)

    apt-get dist-upgrade

Show list of packages to be upgraded, without doing it:

    apt-get -u dist-upgrade
    apt-get --dry-run dist-upgrade

### List versions of installed package

    apt-show-versions PACKAGE

### List packages that are upgradeable

    apt-show-versions -u

### Search for packages

    apt-cache search KEYWORD_OR_PACKAGE

### See details of particular package to install

    apt-cache show PACKAGE

### More general information (fewer details)

    apt-cache showpkg PACKAGE

### Just show dependency information

    apt-cache depends PACKAGE

### Just show reverse dependency information

    apt-cache rdepends PACKAGE

### Map filenames back to packages

    apt-file search FILENAME

(similar to `dpkg -S`, but works on uninstalled packages too)

### List contents of a package

    apt-file list PACKAGE

### Update database of package files

    apt-file update

### Installing source packages

    apt-get source PACKAGE

### Install and auto-build source package

    apt-get -b source PACKAGE

### Build source package later, after downloading

    dpkg-buildpackage -rfakeroot -uc -b

### Install a local PACKAGE.deb file

    dpkg -i PACKAGE.deb

Auto-fix missing dependencies after `dpkg -i` failure:

    apt-get install -f

### Install packages needed to build source PACKAGE

    apt-get build-dep PACKAGE

Note: must have enabled the corresponding source repository.

### Just show the packages needed to build source PACKAGE

    apt-cache showsrc PACKAGE

### Query package owning a file

    dpkg --search filename-pattern
    dpkg -S filename-pattern
    dpkg -S /path/to/file

### Query installed packages

    dpkg --list
    dpkg -l

    dpkg --list package-name-pattern
    dpkg -l package-name-pattern

### Query installed package contents

    dpkg --listfiles packageName
    dpkg -L packageName

### Query installed package info

    dpkg --status packageName
    dpkg -s packageName

### Query package file contents

    dpkg --contents packageFile.deb

### Query package file info

    dpkg --info packageFile.deb

### Display updates for existing packages

    apt-get dist-upgrade --dry-run

### Configuration of repositories via command-line

<https://help.ubuntu.com/community/Repositories/CommandLine>

### Add a Personal Package Archive (ppa)

- The general forms for PPA identifiers for a given `USER` and `PPA` name are:

    ppa:USER/PPA
    USER/PPA
    USER

  If `PPA` is not given, it defaults to `ppa`.

  The corresponding URL for a PPA named `ppa:USER/PPA` is:

      https://launchpad.net/~USER/+archive/ubuntu/PPA

  For example, a user of `mozillateam` with the default PPA name of `ppa` would
  be given by any of these:

      ppa:mozillateam/ppa
      mozillateam/ppa
      mozillateam

  With an associated URL of:

      https://launchpad.net/~mozillateam/+archive/ubuntu/ppa

  And the PPA `ppa:neovim-ppa/stable` refers to:

      https://launchpad.net/~neovim-ppa/+archive/ubuntu/stable

- For a given `ppa:USER/PPA`, the corresponding location for the PPA's contents
  are:

      https://ppa.launchpadcontent.net/USER/PPA/ubuntu/

  with contents similar to:

      dists/
        jammy/
          InRelease
          Release
          Release.gpg
          by-hash/
          main/
      pool/
        main/
        universe/

- `mozillateam` is used as an example PPA in the below discussion.

- Obsolete method (makes PPA key usable everywhere):

    # DON'T use this anymore:
    # add-apt-repository -y --update ppa:mozillateam

- References:

  - <https://stackoverflow.com/questions/68992799/warning-apt-key-is-deprecated-manage-keyring-files-in-trusted-gpg-d-instead>
  - <https://discourse.ubuntu.com/t/spec-apt-deb822-sources-by-default/29333>
  - <https://www.digitalocean.com/community/tutorials/how-to-handle-apt-key-and-add-apt-repository-deprecation-using-gpg-to-add-external-repositories-on-ubuntu-22-04>
  - <https://github.com/elprup/ppa-mirror>
  - <https://www.linuxuprising.com/2021/01/apt-key-is-deprecated-how-to-add.html>
  - <https://unix.stackexchange.com/questions/332672/how-to-add-a-third-party-repo-and-key-in-debian/582853#582853>
  - <https://askubuntu.com/questions/1286545/what-commands-exactly-should-replace-the-deprecated-apt-key/1307181#1307181>

- `ppa:mozillateam` points to:
  <https://launchpad.net/~mozillateam/+archive/ubuntu/ppa>

- Visiting the above URL and choosing "Technical Details about this PPA", and
  choosing an appropriate Ubuntu version (e.g., `Jammy (22.04)`) leads to these
  sources lines:

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

### Add third-party repository

- Acquire key and place into `/etc/apt/keyrings/` after dearmoring:

      wget https://www.virtualbox.org/download/oracle_vbox_2016.asc |
        gpg --dearmor --yes -o /etc/apt/keyrings/oracle_vbox_2016.gpg

- Create a corresponding `.sources` file:

      echod -o /etc/apt/sources.list.d/virtualbox.sources "
        Types: deb
        Architectures: amd64
        URIs: https://download.virtualbox.org/virtualbox/debian/
        Suites: $(lsb_release -cs)
        Components: contrib
        Signed-By: /etc/apt/keyrings/oracle_vbox_2016.gpg
      "

### Purge everything from a PPA

- Install the ppa-purge tool:

      agi ppa-purge

- Purge as follows:

      ppa-purge ppa:someppa/ppa

### Reconfigure a package

    dpkg-reconfigure PACKAGE

This runs `/var/lib/dpkg/info/PACKAGE.postinst configure` (so-called
"configure" mode).

## Fedora package management

- In Fedora 22, `yum` became obsolete. It is replaced with `dnf` (Dandified
  Yum). Mostly, they have compatible syntax.

- See `man yum2dnf` for details on changes.

### To examine groups in detail

      dnf group list -v

  The Group Name comes first (e.g., `KDE Plasma Workspaces`), and the groupid
  (GID) comes next (e.g., `kde-desktop-environment`).

## CentOS package management

- CentOS still uses `yum`.

- Can use `yumdb` to view yum database information. E.g.:

      yumdb info cabextract

  yielding the following (note the `from_repo` field):

      Loaded plugins: fastestmirror, langpacks
      cabextract-1.5-1.el7.x86_64
           checksum_data = 844c5274f2c7fae5a35f62f566f4030c3bdec3fd7544d8edcdbaff111ea5b794
           checksum_type = sha256
           command_line = -y install curl cabextract xorg-x11-font-utils fontconfig
           from_repo = epel
           from_repo_revision = 1509287263
           from_repo_timestamp = 1509289057
           installed_by = 0
           origin_url = http://mirror.cs.pitt.edu/epel/7/x86_64/Packages/c/cabextract-1.5-1.el7.x86_64.rpm
           reason = user
           releasever = 7
           var_infra = stock
           var_uuid = 5e782d19-b783-4bb3-b78b-1322a030107b

# Firewall rules

## Ubuntu firewall rules

- Uncomplicated Firewall (`ufw`) is installed by default.

- See helpful Wiki page for examples: <https://help.ubuntu.com/community/UFW>

- To enable logging:

      ufw logging on

  Then watch log:

      tail --follow=name /var/log/kern.log

  Disable logging via:

      ufw logging off

- General syntax to allow or deny access:

  - Use `udp` and `tcp` for `PROTO`.
  - Use `any` to wildcard `IP` or `PORT`.

  - Simplified syntax:

        ufw allow PORT[/PROTO]

  - Full syntax:

        ufw deny [proto PROTO] [from IP [port PORT]] [to IP [port PORT]]

- Example: Display current rules:

      ufw status

- Example: Deny all to port 53 (TCP and UDP):

      ufw deny 53

- Example: Deny TCP port 80:

      ufw deny 80/tcp

- Example: Allow access from IP address 1.2.4.5 to UDP port 80:

      ufw allow proto udp from 1.2.3.4 to any port 80

- Example: Setup to "deny" everything by default, then allow ssh, then enable
  firewall:

      ufw default deny
      ufw allow ssh
      ufw enable

## Fedora, CentOS firewall rules

- **WARNING** You have to invoke `firewall-cmd` **TWICE** to make changes; the
  first invocation will update the running firewall, and the second will use
  `--permanent` to make the same change in the permanent files.

- Get the status of firewalld:

      firewall-cmd --state

- List everything added for or enabled:

      firewall-cmd --list-all

  Might have this as one of the lines:

      services: dhcpv6-client mdns samba-client ssh

- Reload without losing state:

      firewall-cmd --reload

- Complete reload, losing state (only in case of severe firewall problems):

      firewall-cmd --complete-reload

- Get list of zones:

      firewall-cmd --get-zones

- Get list of services:

      firewall-cmd --get-services

- List all zones with details:

      firewall-cmd --list-all-zones

- Add a service:

      firewall-cmd --add-service ssh
      firewall-cmd --permanent --add-service ssh

- Remove a service:

      firewall-cmd --remove-service ssh
      firewall-cmd -permanent --remove-service ssh

- Query a service (exit code is one if enabled, zero otherwise; no output):

      firewall-cmd --query-service ssh

- Add/remove/query a port number (instead of a service name):

      firewall-cmd --add-port 22
      firewall-cmd --permanent --add-port 22
      firewall-cmd --remove-port 22
      firewall-cmd --permanent --remove-port 22
      firewall-cmd --query-port 22
      firewall-cmd --permanent --query-port 22

# Systemd boot targets

- With systemd, it's not longer `/etc/inittab` that determines the "run level"
  for booting; instead, the default target determines that.

- Determining default boot target:

      systemctl get-default

- Setup for text-only login at next boot:

      systemctl set-default multi-user.target

- Setup for graphical login at next boot:

      systemctl set-default graphical.target

- Make a target active right now:

      systemctl isolate graphical.target

# SSD secure erase

- Use Ubuntu desktop "Try Ubuntu".

  (Note: Do not use the server installer, since it doesn't seem to like putting
  the machine to sleep using `echo -n mem > /sys/power/state`, and the sleep
  trick is often necessary to unfreeze the SSDs.)

- Devices must not be frozen; if they *are* frozen, can try:

  - Use external USB-connected SATA adapter and hotplug the drives after booting
    to avoid BIOS freezing as explained here:
    <https://ata.wiki.kernel.org/index.php/ATA_Secure_Erase>

  - After booting, suspend to RAM and resume (which hopefully unfreezes the
    drives).

  - Check for "not frozen":

        hdparm -I /dev/sda | grep frozen

  - If frozen, try to sleep the machine (suspend to RAM) by pressing sleep
    button or by trying:

        echo -n mem > /sys/power/state

    Wake machine back up by pressing power button.

    (Works for mobi, casey)

- Set a user password:

      hdparm --user-master u --security-set-pass password /dev/sda

  With output:

      security_password="password"

      /dev/sdd:
      Issuing SECURITY_SET_PASS command, password="password", user=user, mode=high

  Verify it succeeded:

      hdparm -I /dev/sda

  Should see similar to below in `Security` section (with `enabled` on line by
  itself):

      Security:
         Master password revision code = 65534
                 supported
                 enabled
         not     locked
         not     frozen
         not     expired: security count
                 supported: enhanced erase
         Security level high
         2min for SECURITY ERASE UNIT. 2min for ENHANCED SECURITY ERASE UNIT.

- Issue erase command:

      time hdparm --user-master u --security-erase password /dev/sda

  With output similar to:

      security_password="password"

      /dev/sdd:
        Issuing SECURITY_ERASE command, password="password", user=user

      real  0m17.148s
      user  0m0.002s
      sys   0m0.003s

- Can also discard all blocks on the device (which may help in lieu of secure
  erase):

      blkdiscard /dev/sda

# Configure SSD TRIM

- Reference "How To Configure Periodic TRIM for SSD Storage on Linux Servers":
  <https://www.digitalocean.com/community/tutorials/how-to-configure-periodic-trim-for-ssd-storage-on-linux-servers>

- `fstrim -va` trims (verbosely) all suitable filesystems.

# Partitioning

## gdisk type codes

    0700 Microsoft basic data
    0c01 Microsoft reserved
    2700 Windows RE
    4100 PowerPC PReP boot
    4200 Windows LDM data
    4201 Windows LDM metadata
    7501 IBM GPFS
    7f00 ChromeOS kernel
    7f01 ChromeOS root
    7f02 ChromeOS reserved
    8200 Linux swap
    8300 Linux filesystem
    8301 Linux reserved
    8302 Linux /home
    8400 Intel Rapid Start
    8e00 Linux LVM
    a500 FreeBSD disklabel
    a501 FreeBSD boot
    a502 FreeBSD swap
    a503 FreeBSD UFS
    a504 FreeBSD ZFS
    a505 FreeBSD Vinum/RAID
    a580 Midnight BSD data
    a581 Midnight BSD boot
    a582 Midnight BSD swap
    a583 Midnight BSD UFS
    a584 Midnight BSD ZFS
    a585 Midnight BSD Vinum
    a800 Apple UFS
    a901 NetBSD swap
    a902 NetBSD FFS
    a903 NetBSD LFS
    a904 NetBSD concatenated
    a905 NetBSD encrypted
    a906 NetBSD RAID
    ab00 Apple boot
    af00 Apple HFS/HFS+
    af01 Apple RAID
    af02 Apple RAID offline
    af03 Apple label
    af04 AppleTV recovery
    af05 Apple Core Storage
    be00 Solaris boot
    bf00 Solaris root
    bf01 Solaris /usr & Mac Z
    bf02 Solaris swap
    bf03 Solaris backup
    bf04 Solaris /var
    bf05 Solaris /home
    bf06 Solaris alternate se
    bf07 Solaris Reserved 1
    bf08 Solaris Reserved 2
    bf09 Solaris Reserved 3
    bf0a Solaris Reserved 4
    bf0b Solaris Reserved 5
    c001 HP-UX data
    c002 HP-UX service
    ea00 Freedesktop $BOOT
    eb00 Haiku BFS
    ed00 Sony system partitio
    ef00 EFI System
    ef01 MBR partition scheme
    ef02 BIOS boot partition
    fb00 VMWare VMFS
    fb01 VMWare reserved
    fc00 VMWare kcore crash p
    fd00 Linux RAID

## General partitioning information

- Arch notes:

  - <https://wiki.archlinux.org/index.php/Unified_Extensible_Firmware_Interface>
  - <https://wiki.archlinux.org/index.php/GRUB>

- Use `gdisk` to manipulate partitions on a GPT disk interactively:

      gdisk /dev/sda

  Use `sgdisk` for scripted operations.

- Make sure every partition starts on a 1 MB boundary (typically 2048 sectors).
  By default, `gdisk` will start the first partition at sector 2048 to stay
  aligned, but it's worth verifying this during partitioning.

- For BIOS-based systems, a BIOS boot partition is required as the first part of
  any GPT drive (at the start of the drive). Use 1 MB as the size. Use hex code
  `ef02` for BIOS boot partition. This partition type is needed for BIOS-based
  motherboards that must boot a GPT-partitioned drive. This is because grub
  needs space to expand beyond the few bytes available in the MBR. It must be at
  minimum 30 KB or so, but 1 MB provides some room to grow. Though a BIOS boot
  partition isn't required on EFI-based systems, it's cheap so it might as well
  be there.

- For EFI-based systems, an EFI System Partition is required. It must be 512 MB
  at minimum, but 1 GB is comfortable for expansion. Use type `ef00` for EFI
  System Partition. It should be FAT32-formatted, which can be accomplished via:

      mkfs.fat -F32 /dev/sda2

- When using Linux RAID or btrfs, a separate `/boot` partition is required. Use
  type `8300` ("Linux"), with 1 GB of space (500 MB at bare minimum).

- Create the "big" partition to take up almost all remaining space (typically
  for RAID, but applies to whichever partition should get the "rest" of the
  drive). This is easiest to do by creating all other partitions first, then
  creating the big partition last. Alternatively, another way is to create a
  temporary dummy partition with size equal to the desired extra space, create a
  temporary "big" partition to determine the size, and measure the size with
  `gdisk` `i` command. Round this number of sectors down to a multiple of 1 MB
  by dividing by 2048, then re-multiplying the integer portion again by 2048.
  Finally, delete both and re-create the RAID volume with the calculated number
  of sectors. Use type `fd00` for Linux software RAID.

- To clone partition tables across drives, use `sgdisk` as follows:

      for i in b c d e f; do
        sgdisk -R /dev/sd$i /dev/sda
        sgdisk -G /dev/sd$i
      done

- To print partition information for a drive:

      sgdisk -p /dev/sda

- To wipe partition information clean, "zap" the drive:

      gdisk /dev/sda

      x  (to use expert's menu)
      z  (to zap and exit)

  Using sgdisk:

      sgdisk --zap-all /dev/sda

## RAID commands

- To create a RAID device:

  - RAID10 far layout (recommended for RAID10):

        mdadm --create /dev/md/0 --level raid10 --layout f2 -n 4 /dev/sd[abcd]1

  - RAID10 near layout:

        mdadm --create /dev/md/1 --level raid10 -n 4 /dev/sd[abcd]1

  - RAID0 (striped volume):

        mdadm --create /dev/md/0 --level raid0 -n 2 /dev/sd[ab]1

- To force synchronization of a RAID volume:

      echo check > /sys/block/md/0/md/sync_action

- To mount udev system on /mnt/alt/root/dev:

      mount -o bind /dev /mnt/alt/root/dev

- To assemble a previously existing RAID array from its pieces:

  - Examine the raw partitions:

        mdadm --examine /dev/sda1

    Note UUID field, e.g.:

        UUID : 40dd77f4:3c31be30:2e1d0dea:7b7155b9

    There will be two or more raw partitions that share this UUID.

  - Assemble the array, specifying the UUID and the desired MD device:

        mdadm --assemble --uuid 40dd77f4:3c31be30:2e1d0dea:7b7155b9 /dev/md/0

  - Re-generate `/etc/mdadm.conf` via a scan:

        mdadm --examine --scan > /etc/mdadm.conf

  - Assemble array using configuration file information:

        mdadm --assemble /dev/md2

- To remove/destroy an existing RAID array:

  - Remove any LVM volume groups:

        vgremove name-of-group

  - Stop the RAID array:

        mdadm --stop /dev/md/0

  - Then zero the superblocks for all associated partitions:

        for i in a b c d e f; do mdadm --zero-superblock /dev/sd${i}1; done

# Booting using grub

- References:

  - <http://dennisk.freeshell.org/cis238dl_grub.html>
  - <https://www.linux.com/learn/how-rescue-non-BOOTING-GRUB-2-LINUX>

- Get to `grub>` prompt.

- Determine partitions via `ls (<tab>`; may get listing something like this:

      lvm/mobi-home lvm-mobi-ubuntu18_04 md/0 hd0 hd1

- Use `ls` to figure out where the `/boot` directory or volume might be. If
  `/boot` is separately mounted, there will be a volume with `vmlinuz*` files;
  otherwise, there will be a `/boot/vmlinuz*` file in the root partition.

  In this example, `(hd0,4)` is the `/boot` volume, with `vmlinuz*` in the
  topmost directory of this volume.

- Determine where the `/` partition is mounted; this will be passed as a kernel
  command-line argument. In this case, the volume is:

      (lvm/mobi-ubuntu18_04)

  This corresponds to `/dev/mapper/mobi-ubuntu18_04`.

- Choose the volume housing the `vmlinuz*` files as Grub's "root" as follows:

      set root=(hd0,gpt4)

- Determine kernel and initrd files to use via:

      ls /

  with select output files:

      vmlinuz-4.15.0-55-generic
      initrd.img-4.15.0-55-generic

- Setup the kernel (note that the path to the `vmlinuz*` file is relative to
  Grub's root directory, not to the ultimate `/` mount point; so when `/boot` is
  a separate mount point, the kernel file will be at `/vmlinuz*`, not at
  `/boot/vmlinuz*`:

      linux /vmlinuz-4.15.0-55-generic root=/dev/mapper/mobi-ubuntu18_04

- Setup the initrd:

      initrd /initrd.img-4.15.0-55-generic

- Boot:

      boot

- After booting into the full Linux environment, rewrite the Grub installation
  appropriately, something like:

      update-grub
      grub-install /dev/sda

- Can manipulate the EFI boot menu via `efibootmgr`; see manpage for details.

# journalctl

- `cat /var/log/messages` becomes `journalctl`.
- `tail -f /var/log/messages` becomes `journalctl -f`.
- `grep foobar /var/log/messages` becomes `journalctl | grep foobar`.

# Memory testing

- Boot Linux distro, execute `memtest86+` for a couple of days.

# Drive testing

- Hard drive burn-in:

  - <https://forums.freenas.org/index.php?threads/how-to-hard-drive-burn-in-testing.21451/>
  - <https://www.thomas-krenn.com/en/wiki/SMART_tests_with_smartctl>
  - <https://wiki.unraid.net/Understanding_SMART_Reports>

- `smartctl -a` shows all information about a drive.

- Test all drives at the same time (but only one test running on each drive at
  one time). Between tests, look at status output via:

      for i in a b c d e f g h; do smartctl -a /dev/sd$i; done | less

  Look for `SMART Self-test log structure` section showing status of completed
  tests, and look for `Self-test execution status` to see if a test is currently
  ongoing.

  Tests:

      for i in a b c d e f g h; do smartctl -t short /dev/sd$i; done
      for i in a b c d e f g h; do smartctl -t conveyance /dev/sd$i; done
      for i in a b c d e f g h; do smartctl -t long /dev/sd$i; done

  May abort a test via:

      smartctl -X /dev/sd$i

- Destructive read-write tests via badblocks:

  - Execute these in separate login prompts:

        badblocks -p100 -svw /dev/sda
        badblocks -p100 -svw /dev/sdb
        badblocks -p100 -svw /dev/sdc
        badblocks -p100 -svw /dev/sdd
        badblocks -p100 -svw /dev/sde
        badblocks -p100 -svw /dev/sdf

# Disk-related

- For `SMART error (FailedOpenDevice) detected`:

      systemctl restart smartmontools.service

- Use `hdparm` for SATA/IDE drives:

  - Information on `/dev/sdi`:

        hdparm -I /dev/sdi

- Use `blkid` to see the block device UUIDs, e.g.:

      $ blkid
      /dev/sda1: UUID="Z6L1pb-..." TYPE="LVM2_member"
      /dev/mapper/vg_t61-lv_swap: UUID="c1b48db8-..." TYPE="swap"
      /dev/mapper/vg_t61-lv_ubuntu10.10: UUID="25cb5f65-..." TYPE="ext4"

- Check partition information:

      cat /proc/partitions

  Sample output:

      major minor  #blocks  name

         8        0  312571224 sda
         8        1  311564578 sda1
      [...]

- Check size of a block device:

      # In 512-byte sectors:
      blockdev --getsize /dev/sda

      # In bytes:
      blockdev --getsize64 /dev/sda

      # Show report of all block devices or single device::
      blockdev --report
      blockdev --report /dev/sda

      # Report on LV as well::
      blockdev --report /dev/mapper/vg_host1-lv_test

- Can also view UUID via:

      ls -l /dev/disk/by-uuid/

- Rescan a partition via:

      echo 1 > /sys/block/sdc/device/rescan

  Seems likely to work for PCI devices, since this is a symlink:

      readlink /sys/block/sdc
      ../devices/pci0000:00/..../block/sdc

- Show which partitions the kernel thinks it has:

      cat /proc/partitions

      major minor  #blocks  name

         8        0  125034840 sda
         8        1  124022784 sda1
         8        2     488448 sda2
         8       16  125034840 sdb
         8       17  124022784 sdb1
         8       18     512000 sdb2
         9        0  248043520 md0
       253        0   11718656 dm-0
       253        1   25600000 dm-1
       253        2  146481152 dm-2
       253        3   39059456 dm-3

- Mounting a drive image (`dd` image) using loopback device:

  Given file `x.dd` as a raw image of a drive having two partitions with NTFS
  volumes on them:

      DEV=$(sudo losetup --partscan --find --read-only --show x.dd)
      mkdir partition_1 partition_2
      sudo mount -t ntfs -o ro "${DEV}p1" partition_1
      sudo mount -t ntfs -o ro "${DEV}p2" partition_2

# GNU Parted

- Launch against a particular drive:

      parted /dev/sda

- Print out partitions:

      print

- Create a new "disk label" (partition table) for GUID Partition Table (GPT):

      mklabel gpt

- Create a new primary partition for RAID:

      mkpart primary start end

  E.g., using sector units to match:

      mkpart primary 34s 3902343784s

- Set RAID flag on partition #1:

      set 1 raid on

# Info on UUID

- Explanation of a good bit of UUID on-disk layout:
  <http://ubuntuforums.org/showthread.php?t=1286774>

# Hardware-related

- Use `lspci` to scan PCI devices.

- Use `lsusb` to scan USB devices.

- Use `lspcmcia` to scan PC-CARD/PCMCIA devices.

- Use `lshal` to show HAL information.

- Use `lshw` to list hardware information.

  To show just disks:

      lshw -class disk -short

- Use `lshw-gui` FEDORA or `lshw-gtk` (ubuntu) for GUI version.

- Use `dmidecode` to display system DMI table (SMBIOS information).

- Use `cat /proc/scsi/scsi` to see hard disk devices.

- Use `lsscsi` to see SCSI devices (`agi lsscsi`).

# Keyboard repeat rate/delay

- Query current rate/delay settings:

      xset q | grep 'repeat delay'

  With result:

      auto repeat delay:  250    repeat rate:  32

- Change via:

      xset r rate 250 32

# Benchmarking

- Time disk read speed:

      hdparm -t /dev/sda

# Using `/etc/alternatives`

- See the `update-alternatives` tool to manipulate the alternatives symlinks.

- In general, `/etc/alternatives/` are symlinks to the chosen alternatives.

- To install locally compiled Gvim:

      for i in gvim gview gvimdiff; do
        update-alternatives --install /usr/bin/$i $i /usr/local/bin/$i 500
      done

- To change the default for `editor`:

      sudo update-alternatives --config editor

# Unix groups

- In Ubuntu, the group definitions are found in:
  `/usr/share/doc/base-passwd/users-and-groups.html`

- Selected group meanings:

  - adm - for monitoring tasks.
  - dialout - direct access to serial ports.
  - fax - can use fax software.
  - cdrom - direct access to CD-ROM.
  - floppy - direct access to floppy drive.
  - tape - direct access to tape drive.
  - video - direct access to a video device.
  - plugdev - direct access to certain removable devices w/o fstab help.
  - lpadmin - add, modify, remove printers.

  Normal user can get rid of tape, floppy to save space on the 16-group limit
  for NFS3.

# Querying configuration

- The `getconf` tool allows for querying of various variables.
  - To see which variables are available:

        getconf -a

  - To query a particular variable:

        getconf VARIABLE_NAME

  - To query the maximum command-line length (e.g., as used by xargs):

        getconf ARG_MAX

    (Currently on Fedora 17, ARG_MAX is 2 MB.)

# ssh

## ssh obsolete algorithms

- For use with old ssh, can enable obsolete algorithms.  Choose algorithms based
  on error message, e.g.:

      Unable to negotiate with 1.2.3.4 port 22: no matching key exchange
      method found. Their offer:
      diffie-hellman-group-exchange-sha1,diffie-hellman-group14-sha1,diffie-hellman-group1-sha1

  Use this (based also on error about host key algorithm)::

      ssh \
        -oKexAlgorithms=+diffie-hellman-group-exchange-sha1 \
        -oHostKeyAlgorithms=+ssh-rsa \
        1.2.3.4

# wget

- Mirroring via wget:

      wget -m --no-parent http://somesite.com/some/path/

  If robots.txt is stopping things, then either add the following to
  `~/.wgetrc`:

      robots = off

  Or else use `-e` to pass this along:

      wget -e 'robots=off' -m --no-parent http://somesite.com/some/path/

# FEDORA CENTOS SELinux management

- SELinux references:

  - <http://wiki.centos.org/HowTos/SELinux>
  - <http://www.centos.org/docs/5/html/Deployment_Guide-en-US/sec-sel-building-policy-module.html>
  - <http://www.centos.org/docs/5/html/Deployment_Guide-en-US/sec-sel-policy-customizing.html>
  - <http://www.gentoo.org/proj/en/hardened/selinux/selinux-handbook.xml?part=2&chap=5>
  - <http://www.slideshare.net/biertie/how-to-live-with-selinux>

- Determining SELinux failures:

      journalctl | grep --after 5 SELinux

  Typical output:

      Jan 05 04:18:53 host1.domain.com setroubleshoot[31961]: SELinux is
      preventing /usr/bin/python2.7 from getattr access on the file
      /usr/bin/rpm. For complete SELinux messages. run sealert -l
      8998b74b-4d0d-4e58-abd5-46e1a7a03d1f

  To see the details from the above output:

      sealert -l 8998b74b-4d0d-4e58-abd5-46e1a7a03d1f

- Audit to see why an access has failed an access:

      sealert -l 8998b74b-4d0d-4e58-abd5-46e1a7a03d1f | audit2why

      type=AVC msg=audit(1388913532.542:2824): avc:  denied  { getattr } for
      pid=16011 comm="pyzor" path="/usr/bin/rpm" dev="dm-1" ino=1443104
      scontext=system_u:system_r:spamc_t:s0
      tcontext=system_u:object_r:rpm_exec_t:s0 tclass=file

              Was caused by:
                      Missing type enforcement (TE) allow rule.

                      You can use audit2allow to generate a loadable module to
                      allow this access.

- Audit to see allow the failed access:

      sealert -l 8998b74b-4d0d-4e58-abd5-46e1a7a03d1f | audit2allow

      #============= spamc_t ==============
      allow spamc_t rpm_exec_t:file getattr;

- Create module file to hold the result; write resulting "Type Enforcement" (TE)
  policy to stdout:

      sealert -l 8998b74b-4d0d-4e58-abd5-46e1a7a03d1f |
        audit2allow -m local_mail

      module local_mail 1.0;

      require {
              type spamc_t;
              type rpm_exec_t;
              class file getattr;
      }

      #============= spamc_t ==============
      allow spamc_t rpm_exec_t:file getattr;

  Typically this is stored in a "Type Enforcement" file ending in `.te`.

- Compile the Type Enforcement file into a module:

      checkmodule -M -m -o local_mail.mod local_mail.te

- Package this module:

      semodule_package -o local_mail.pp -m local_mail.mod

- Load the package and make it active; this is persistent across reboots:

      semodule -i local_mail.pp

- Remove a module; no longer persists:

      semodule -r local_mail

- Unpackage a module to see what's inside:

      semodule_unpackage local_mail.pp

# FEDORA CENTOS SELinux port management

To enable `name_bind` for a port (e.g., for allowing SSHD to bind to a
non-standard port), use `semanage`.

- To list permitted ports for ssh:

      semanage port -l | grep ssh

  Expect to see:

      ssh_port_t                     tcp      22

- To add a new `name_bind`-capable port (this may take a while; it's unclear why
  it can be so slow):

      semanage port -a -t ssh_port_t -p tcp 12345

  Now expect to see the following ports for ssh:

      ssh_port_t                     tcp      12345, 22

# Installing to USB Flash

- Instructions for creating a bootable USB Flash-based installation:
  <https://www.dionysopoulos.me/portable-ubuntu-on-usb-hdd/>

  Seems like it might have worked; worth checking into further.

  Used the `grub-mkdevicemap`; looks like that may have helped.

# ZFS

## ZFS references

- "Ubuntu 22.04 Root on ZFS" (official instructions):
  <https://openzfs.github.io/openzfs-docs/Getting%20Started/Ubuntu/Ubuntu%2022.04%20Root%20on%20ZFS.html>
  - Reinstalling grub for ZFS-based ubuntu:
    - <https://openzfs.github.io/openzfs-docs/Getting%20Started/Ubuntu/Ubuntu%2022.04%20Root%20on%20ZFS.html#step-5-grub-installation>
    - <https://askubuntu.com/questions/826209/re-initialise-grub-for-non-bootable-uefi-zfs-16-04-installation>
- "Installing UEFI ZFS Root on Ubuntu 22.04":
  <https://www.medo64.com/2022/05/installing-uefi-zfs-root-on-ubuntu-22-04/>
  Notes on a very manual installation process that sets up ZFS with encryption
  and custom partitioning.
- "zfs on root with 22.04 without zsys":
  <https://old.reddit.com/r/Ubuntu/comments/um7h6i/zfs_on_root_with_2204_without_zsys/>
  If purge `zsys`, might need to create snapshots that follow the `zsys` naming
  convention; this has a script to show how that's done, along with notes on
  where the snapshots must be created (script in `/etc/apt/apt.conf.d` for
  before `apt upgrade` and script in `/etc/kernel/preinst.d` for before kernel
  upgrade):
  <https://gist.github.com/kimono-koans/7641ee7bc7ce91f520b324bb08d699c8>
- ZFS 101—Understanding ZFS storage and performance (Jim Salter):
  <https://arstechnica.com/information-technology/2020/05/zfs-101-understanding-zfs-storage-and-performance/>
  Comments:
  - <https://arstechnica.com/information-technology/2020/05/zfs-101-understanding-zfs-storage-and-performance/?comments=1&post=38877866>
  - <https://arstechnica.com/information-technology/2020/05/zfs-101-understanding-zfs-storage-and-performance/?comments=1&post=38878617>

- ZFS replication to the cloud:
  <https://arstechnica.com/information-technology/2015/12/rsync-net-zfs-replication-to-the-cloud-is-finally-here-and-its-fast/>
- ZFS incremental backups:
  <https://serverfault.com/questions/842531/how-to-perform-incremental-continuous-backups-of-zfs-pool/842740#842740>
- Ubuntu ZFS dev's blog articles:
  - <https://didrocks.fr/2020/06/11/zfs-focus-on-ubuntu-20.04-lts-zsys-partition-layout/>
  - <https://didrocks.fr/2020/06/16/zfs-focus-on-ubuntu-20.04-lts-zsys-dataset-layout/>
  - <https://didrocks.fr/2020/06/19/zfs-focus-on-ubuntu-20.04-lts-zsys-properties-on-zfs-datasets/>
  - <https://docs.google.com/document/d/1oV5-ef-fqzML4MGd2LAHRcLdR0USKkOmrJW-AP0CmC4/edit#>
- ZFS trim support is good:
  <https://askubuntu.com/questions/1200172/should-i-turn-on-zfs-trim-on-my-pools-or-should-i-trim-on-a-schedule-using-syste>
  - Autotrim works; may also use `zpool trim rpool` periodically.
- "How data gets imbalanced on ZFS":
  <https://jrs-s.net/2018/04/11/how-data-gets-imbalanced-on-zfs/>
- Use zfs compression:
  <https://jrs-s.net/2015/02/24/zfs-compression-yes-you-want-this/>
- "ZFS Administration, Part XII- Snapshots and Clones":
  <https://pthree.org/2012/12/19/zfs-administration-part-xii-snapshots-and-clones/>
- ZFS sSnapshot rollback:
  <https://docs.oracle.com/cd/E19253-01/819-5461/gbcxk/index.html>
- "Attaching and Detaching Devices in a Storage Pool":
  <https://docs.oracle.com/cd/E19253-01/819-5461/gcfhe/index.html>
- "Upgrading ZFS Storage Pools":
  <https://docs.oracle.com/cd/E19253-01/819-5461/gcikw/index.html>
- "Migrating ZFS Storage Pools":
  <https://docs.oracle.com/cd/E19253-01/819-5461/gbchy/index.html>
- "Displaying Information About ZFS Storage Pools":
  <https://docs.oracle.com/cd/E19253-01/819-5461/gamml/index.html>
- <https://www.thegeekdiary.com/solaris-zfs-how-to-offline-online-detach-replace-device-in-a-storage-pool/>
- <https://wiki.ubuntu.com/Kernel/Reference/ZFS>
- <https://forums.freenas.org/index.php?threads/slideshow-explaining-vdev-zpool-zil-and-l2arc-for-noobs.7775/>
- <https://constantin.glez.de/2010/01/23/home-server-raid-greed-and-why-mirroring-still-best/>
- <http://jrs-s.net/2015/02/06/zfs-you-should-use-mirror-vdevs-not-raidz/>
- <https://pthree.org/2013/01/03/zfs-administration-part-xvii-best-practices-and-caveats/>
- <https://github.com/zfsonlinux/zfs-auto-snapshot>
- <http://blog.programster.org/sharing-zfs-datasets-via-nfs>
- <http://open-zfs.org/wiki/Performance_tuning>
- <https://github.com/zfsnap/zfsnap>
- <https://wiki.archlinux.org/index.php/ZFS>
- <https://wiki.archlinux.org/index.php/ZFS/Virtual_disks>
- <https://github.com/zfsonlinux/zfs/wiki/Ubuntu-16.04-Root-on-ZFS>
- <https://janweitz.de/article/creating-a-zfs-zroot-raid-10-on-ubuntu-16.04/>
- Check health of zfs volume, including scrubbing (for FreeBSD, Ubuntu):
  <https://calomel.org/zfs_health_check_script.html>
- Increasing pool size by replacing with larger disks:
  <https://madaboutbrighton.net/articles/2016/increase-zfs-pool-by-adding-larger-disks>
- ZFS disk usage:
  <https://zedfs.com/all-you-have-to-know-about-reading-zfs-disk-usage/>

## ZFS Utilities

- Install:

      agi zfsutils-linux

## Create a pool

- **Note** Should use `/dev/disk/by-id` names instead of `/dev/sd?` names.

- Data should ideally be power-of-two number of disks. Six disks is nice for
  raidz2 (4 data + 2 parity).

- Assuming partition 1 is for ZFS, create volume named after host:

      zpool create -o ashift=12 \
        -O relatime=on -O canmount=off -O compression=lz4 \
        -O mountpoint=/ -R /mnt \
        host1 raidz2 /dev/disk/by-id/ata-WDC_WD40EFRX-*-part1

## Create a test pool

- Can create a test pool from sparse files, e.g.:

      sudo -i
      mkdir -p /tmp/zfs
      cd /tmp/zfs
      for i in {0..1}; do truncate -s 1G $i.raw; done
      zpool create -o ashift=12 testpool mirror /tmp/zfs/{0,1}.raw

## Show pool statistics (size used, size free)

- Show for all pools:

      zpool list

## Show ZFS datasets

      zfs list

  Restrict to just snapshots:

      zfs list -t snapshot

## Create ZFS snapshot

- Choose snapshot name (e.g., `@1`) for pool `testpool`.
- Create recursive snapshot covering datasets:

      zfs snapshot -r testpool@1

## Send ZFS datasets recursively from snapshot

    zfs send -R testpool@1

Note that snapshot is required if dataset is mounted.

## Show zpool debugging information

    zdb

Restrict to `testpool`:

    zdb testpool

## Show a nice tree of mount points

    findmnt

## Check balance of pool

    zpool iostat -v testpool

with output:

                          capacity     operations     bandwidth
      pool              alloc   free   read  write   read  write
      ----------------  -----  -----  -----  -----  -----  -----
      testpool          50.2M  1.83G      0     13  14.3K   851K
        /tmp/zfs/raw.0  50.2M   910M      0     13  7.15K   815K
        /tmp/zfs/raw.1      0   960M     57    318  3.77M  18.9M
      ----------------  -----  -----  -----  -----  -----  -----

## ZFS snapshot rollback

E.g., to rollback to snapshot `@1` for `testpool:

    zfs rollback testpool@1

## Replace a drive in a volume before failure with a spare drive

- Replace drive sda1 with sdb1, triggering a resilvering operation:

      zpool replace host1 /dev/sda1 /dev/sdb1
      zpool status host1
        pool: host1
       state: ONLINE
        scan: resilvered 276K in 0h0m with 0 errors on Mon Jan  9 00:30:01 2017
      config:

              NAME        STATE     READ WRITE CKSUM
              host1       ONLINE       0     0     0
                sdb1      ONLINE       0     0     0

      errors: No known data errors

## Replace in a raidz volume

- Replace drive sda1 with sdd1, triggering a resilvering operation:

      zpool replace host1 /dev/sda1 /dev/sdd1
      zpool status host1
        pool: host1
       state: ONLINE
        scan: resilvered 188K in 0h0m with 0 errors on Mon Jan  9 00:32:53 2017
      config:

              NAME             STATE     READ WRITE CKSUM
              host1            ONLINE       0     0     0
                raidz1-0       ONLINE       0     0     0
                  replacing-0  ONLINE       0     0     0
                    sda1       ONLINE       0     0     0
                    sdd1       ONLINE       0     0     0
                  sdb1         ONLINE       0     0     0
                  sdc1         ONLINE       0     0     0

  Note how the above shows a temporary mirror named `replacing-0` that binds the
  old sda1 and the new sdd1 together while resilvering.

  After completion:

      zpool status host1
        pool: host1
       state: ONLINE
        scan: resilvered 188K in 0h0m with 0 errors on Mon Jan  9 00:32:53 2017
      config:

              NAME        STATE     READ WRITE CKSUM
              host1       ONLINE       0     0     0
                raidz1-0  ONLINE       0     0     0
                  sdd1    ONLINE       0     0     0
                  sdb1    ONLINE       0     0     0
                  sdc1    ONLINE       0     0     0

## Take a zfs drive offline and bring back online

- Create a volume for testing and a filesystem mounted at /mnt:

      zpool create host1 raidz /dev/sd[abc]1
      zfs create -o mountpoint=/mnt host1/test

- Take a drive offline:

      zpool offline host1 /dev/sda1
      zpool status

        pool: host1
       state: DEGRADED
      status: One or more devices has been taken offline by the administrator.
              Sufficient replicas exist for the pool to continue functioning in a
              degraded state.
      action: Online the device using 'zpool online' or replace the device with
              'zpool replace'.
        scan: none requested
      config:

              NAME        STATE     READ WRITE CKSUM
              host1       DEGRADED     0     0     0
                raidz1-0  DEGRADED     0     0     0
                  sda1    OFFLINE      0     0     0
                  sdb1    ONLINE       0     0     0
                  sdc1    ONLINE       0     0     0

- Generate a big file:

      dd bs=1024k count=4000 if=/dev/urandom of=/mnt/bigfile

- Bring the drive back online and check status:

      zpool online host1 /dev/sda1
      zpool status

  With a large-sized file, you can see the resilvering taking place when the
  drive is brought back online.

- When using `zpool online` to bring back a drive that was previously in the
  pool, the drive is known to the system, and zfs knows which data was already
  on the drive; so resilvering copies only the missing data.

- Remove test volume:

      zfs destroy host1/test

## Initiate a zfs scrub

- To scrub a given volume:

      zpool scrub VOLUME

- To check progress of scrub operation:

      zpool status VOLUME

  Getting back, for example:

      # Output:
        pool: host1
       state: ONLINE
        scan: scrub repaired 0 in 1h27m with 0 errors on Sun Mar 11 01:51:02 2018
      config:

              NAME                   STATE     READ WRITE CKSUM
              host1                  ONLINE       0     0     0
                mirror-0             ONLINE       0     0     0
                  ata-WDC_WD40[...]  ONLINE       0     0     0
                  ata-WDC_WD40[...]  ONLINE       0     0     0
                  ata-WDC_WD40[...]  ONLINE       0     0     0
                mirror-1             ONLINE       0     0     0
                  ata-WDC_WD40[...]  ONLINE       0     0     0
                  ata-WDC_WD40[...]  ONLINE       0     0     0
                  ata-WDC_WD40[...]  ONLINE       0     0     0

      errors: No known data errors

## Attach a new device to an existing ZFS vdev

For a mirror vdev (or a single-drive vdev), this adds `new_device` as another
mirrored disk for the vdev.

    zpool attach pool device new_device

## Test: just add vdevs and try to boot

- Create test area:

      mkdir -p /tmp/zfs
      cd /tmp/zfs

- Setup "raw" drives using sparse files:

      for i in {0..1}; do truncate -s 1G raw.$i; done

- Create single-drive pool to start:

      zpool create testpool /tmp/zfs/raw.0

- Populate the dataset (at `/testpool`) with some random information:

      cat /usr/bin/* | head -c 50M > /testpool/file

- Examine usage:

      zpool list testpool

  with output:

      NAME       SIZE  ALLOC   FREE  ...
      testpool   960M  34.1M   926M  ...

- Add second drive as a new vdev; demonstrate the imbalance:

    zpool add testpool /tmp/zfs/raw.1
    zpool iostat -v testpool

  with output:

                          capacity     operations     bandwidth
      pool              alloc   free   read  write   read  write
      ----------------  -----  -----  -----  -----  -----  -----
      testpool          50.2M  1.83G      0     13  14.3K   851K
        /tmp/zfs/raw.0  50.2M   910M      0     13  7.15K   815K
        /tmp/zfs/raw.1      0   960M     57    318  3.77M  18.9M
      ----------------  -----  -----  -----  -----  -----  -----

- Use `zfs send` and `zfs recv` to save and restore to balance:

      zfs snapshot -r testpool@1
      zfs send -R testpool@1 > /tmp/zfs/testpool.zfs
      zfs destroy -R testpool
      zfs receive testpool -F < /tmp/zfs/testpool.zfs

- Verify balance:

      zpool iostat -v testpool

  with output:

                          capacity     operations     bandwidth
      pool              alloc   free   read  write   read  write
      ----------------  -----  -----  -----  -----  -----  -----
      testpool          50.3M  1.83G      1      7   206K   328K
        /tmp/zfs/raw.0  22.9M   937M      1      5   204K   235K
        /tmp/zfs/raw.1  27.3M   933M      0      2  1.77K   116K
      ----------------  -----  -----  -----  -----  -----  -----

## ZFS notes

- Look into sanoid: <https://github.com/jimsalterjrs/sanoid/>
- Use ZFS NFS for exported files (see docs).
- Maybe ZFS snapshots using autosnapshot script.
- For Debian and Ubuntu, touch the `/etc/init.d/.legacy-bootordering` file, and
  make sure that the `/etc/init.d/zfs` init script is the first to start, before
  all other services in that runlevel.
- Configuring max arc size:

  > When loading the "zfs" kernel module, make sure to set a maximum number for
  > the ARC. Doing a lot of "zfs send" or snapshot operations will cache the
  > data. If not set, RAM will slowly fill until the kernel invokes OOM killer,
  > and the system becomes responsive. I have set in my
  > `/etc/modprobe.d/zfs.conf` file `options zfs zfs_arc_max=2147483648`, which
  > is a 2 GB limit for the ARC. Keep under 1/4 total RAM size.

# X11

## X11 startup

- `~/.xsessionrc` provides a desktop-independent method for starting scripts at
  session startup.

- To simulate a true login at X11 startup, use the following `~/.xsessionrc`:

  ```sh
  if [ -z "$PROFILE_SOURCED" ]; then
      . /etc/profile
      . $HOME/.profile
  fi
  ```

  This uses the environment variable `PROFILE_SOURCED` to prevent multiple
  sourcing of the startup files.  (Note that `PROFILE_SOURCED` is a non-standard
  variable defined in HOMEGIT at the top of `~/.profile`.)

## X11 multi-head via xrandr

- Useful with open-source drivers and standard XRandR model.
- Use `xrandr` to configure side-by-side displays.
  - Outputs:

    - LVDS1 - Low Voltage Differential Signaling (Internal LCD).
    - DVI1 - External DVI port.
    - VGA1 - External VGA port.

  - Show current configuration:

        xrandr -q

  - Configure `LVDS1` (laptop screen) and `DVI1` (external DVI #1) to be
    clones:

        xrandr --output LVDS1 --auto --output --DVI1 --auto --same-as LVDS1

  - Turn off `LVDS1` output:

        xrandr --output LVDS1 --off

  - Configure `DVI1` (external DVI #1) and `VGA1` (external VGA #1) to be
    extended desktop:

        xrandr --output DVI1 --auto --output VGA1 --auto --right-of DVI1

# Desktop

## xdg Setup of Directories

- freedesktop.org is site for X-related standardization.

- xdg-user-dirs is package for using standardized directories for users (e.g.,
  Downloads, Documents, ...):
  <http://freedesktop.org/wiki/Software/xdg-user-dirs>

- Default settings for user directories are taken from
  `/etc/xdg/user-dirs.defaults`.   These values are relative to the user's home
  directory:

      DESKTOP=Desktop
      DOWNLOAD=Downloads
      TEMPLATES=Templates
      PUBLICSHARE=Public
      DOCUMENTS=Documents
      MUSIC=Music
      PICTURES=Pictures
      VIDEOS=Videos

- Query these variables via `xdg-user-dir`, e.g.:

      xdg-user-dir DOWNLOAD

  The above produces (by default):

      /home/mike/Downloads

- `xdg-user-dirs-update --set VARIABLE_NAME` records variable overrides in
  `~/.config/user-dirs.dirs`.  For example:

      xdg-user-dirs-update --set DOWNLOAD   ~/download

  Resulting in `~/.config/user-dirs.dirs` with defaults constructed from
  `/etc/xdg/user-dirs.defaults` and with `XDG_DOWNLOAD_DIR` changed:

      XDG_DESKTOP_DIR="$HOME/Desktop"
      XDG_DOWNLOAD_DIR="$HOME/download"
      XDG_TEMPLATES_DIR="$HOME/Templates"
      XDG_PUBLICSHARE_DIR="$HOME/Public"
      XDG_DOCUMENTS_DIR="$HOME/Documents"
      XDG_MUSIC_DIR="$HOME/Music"
      XDG_PICTURES_DIR="$HOME/Pictures"
      XDG_VIDEOS_DIR="$HOME/Videos"

# KDE Plasma

## Setting an environment variable for Plasma

- References:

  - <https://userbase.kde.org/Session_Environment_Variables>

- Create `$HOME/.config/plasma-workspace/env/SOMETHING.sh` containing:

      export SOME_VARIABLE=yadda
      export ANOTHER_VARIABLE=yiddi

  This shell script will be sourced early in Plasma startup.

## Simulate a Login

- For Plasma-X11, `~/.xsessionrc` (as described elsewhere) will be invoked; but
  for Plasma-Wayland, this file is ignored.

  To simulate a true login in a Plasma-specific way, create
  `~/.config/plasma-workspace/env/source-profile.sh` with the same contents as
  `~/.xsessionrc` above:

  ```sh
  if [ -z "$PROFILE_SOURCED" ]; then
      . /etc/profile
      . $HOME/.profile
  fi
  ```

  As before, the environment variable `PROFILE_SOURCED` prevents multiple
  sourcing of the startup files.  (This is important for X11-based Plasma, which
  uses both `~/.xsessionrc` and `~/.config/plasma-workspace/env/`.

## Application Launch at Startup

The FreeDesktop standard specifies `.desktop` files that describe applications:

- <https://specifications.freedesktop.org/desktop-entry-spec/desktop-entry-spec-latest.html>
- <https://wiki.archlinux.org/title/Desktop_entries>

All `.desktop` files found in the standard directory `~/.config/autostart/` will
be launched at startup:

- <https://specifications.freedesktop.org/autostart-spec/autostart-spec-latest.html>
- <https://wiki.archlinux.org/title/XDG_Autostart>

## Automatic Migration of `~/.config/autostart-scripts/` Scripts

At least on Fedora 36, Plasma will automatically migrate scripts from the
obsolete directory `~/.config/autostart-scripts/`.

A file named `~/.config/autostart-scripts/original_name` will be moved to
`~/.config/old-autostart-scripts/original_name`, and
`~/.config/autostart/original_name.desktop` will be created to launch the script
using a standard `.desktop` file in the standard directory
`~/.config/autostart/`.
