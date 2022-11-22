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
