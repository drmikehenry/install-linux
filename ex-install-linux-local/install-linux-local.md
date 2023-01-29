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

- MANUAL: Configure SSH clients.

      vim /etc/ssh/ssh_config

  Contents (TODO use server-specific port number for `12345` below):

      # Add these lines at the top of the file:
      Host bolt bolt.drmikehenry.com
              Port 12345

      Host dmh drmikehenry.com
              HostName drmikehenry.com
              User drmikehenry

      Host github.com
              ForwardX11 no

      Host *
              ForwardX11 yes
              ServerAliveInterval 300
              SendEnv COLORFGBG
