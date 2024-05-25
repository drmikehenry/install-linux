---
title: Linux Installation Local
---

# Machine-specific setup

See `machines/` directory for per-machine instructions.

# Network-specific setup

## Setup automount for `/m/`

AUTOMATED:

- NON_BOLT: Create symlink for `/m`:

      ln -s /net/bolt.drmikehenry.com/m /m

  **NOTE** bolt.drmikehenry.com might resolve to public IP.

## Setup automount for `/nfshome/`

MANUAL:

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

- MANUAL Setup not to forward X11 for routers:

    echod -o /etc/ssh/ssh_config.d/10-dewalt.conf '
      Host dewalt dewalt.drmikehenry.com
          ForwardX11 no
    '
    chmod go-w /etc/ssh/ssh_config.d/10-dewalt.conf

    echod -o /etc/ssh/ssh_config.d/10-dewaltguest.conf '
      Host dewaltguest dewaltguest.drmikehenry.com
          ForwardX11 no
    '
    chmod go-w /etc/ssh/ssh_config.d/10-dewaltguest.conf
