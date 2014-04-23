#!/usr/bin/env python3

"""Format a drive for use as a Digital Cinema Package.

Requires external programs for EXT-formatting. Tested on Debian.

(c) Chris Barrett 2014
"""

import bytesize
import os
import subprocess
from   interactive import read_choice, read_number, read_y_or_n
from   subprocess  import check_call, call, CalledProcessError


def attached_drives ():
    """Return a list of attached drives.
    """
    output = subprocess.getoutput('df')
    lines = output.strip().split('\n')
    info = [line.split() for line in lines if '/dev/' in line]
    return [fields[0] for fields in info]


def drive_size (drive):
    """Return the raw capacity of `drive` as a ByteSize.
    """
    output = subprocess.getoutput('df')
    lines = output.strip().split('\n')
    info = [line.split() for line in lines if drive in line][0]
    blocks = int(info[1])
    blocksize = 512
    return bytesize.from_b(blocks * blocksize)


def read_dcp_size (capacity, default):
    """Read the size of the DCP partition from the user.

    capacity -- the total capacity of the drive as a ByteSize object.
    default -- the default size in bytes.

    Returns:
    The size of the DCP partition as a ByteSize.
    """
    size = read_number('DCP partition size (GB)', default.gigabytes)
    size = bytesize.from_gb(size)
    if size >= capacity:
        print('Invalid partition size. ' +
              'Must be less than drive capacity ({} GB).'.format(
                  default.gigabytes))

        return read_dcp_size(capacity, default)
    else:
        return size


def mount (volume, mountpoint, fs_type=None):
    """Mount the given volume at `mountpoint`.

    volume -- the device to mount
    mountpoint -- the path to mount the device at.
    fs_type -- the optional filesystem type (e.g. ext2, ntfs)

    Raises:
    CalledProcessError on failure.
    """
    os.makedirs(mountpoint, exist_ok=True)
    mount_type = ['-t', fs_type] if fs_type else []
    check_call(['mount'] + mount_type + [volume, mountpoint])


def unmount (volume):
    """Unmount `volume`.
    """
    call(['unmount', volume])


def partition (drive, capacity, partition_pos):
    """Destructively partition the given drive for DCP.

    drive -- the name of the storage device to partition.
    capacity -- a ByteSize representing the total capacity of the drive.
    partition_point -- a ByteSize at which the second partition starts.

    Raises:
    CalledProcessError on failure.
    """
    check_call(['parted', drive, '-s mklabel msdos'])

    start = 1
    end   = partition_pos.megabytes - 1
    check_call(['parted', drive, '-s mkpart primary', start, end])

    start = end + 1
    end   = capacity.megabytes
    check_call(['parted', drive, '-s mkpart primary', start, end])


def dcp_init (volume, label):
    """Initialise the given volume with an EXT2 filesystem.

    volume -- The drive partition to format.
    label -- The name to give to the partition.

    Raises:
    CalledProcessError on failure.
    """
    check_call(['mkfs.ext2', '-j', '-l', label, '-I 128', volume])
    mountpoint = '/dev/' + label
    mount(volume, mountpoint)
    check_call(['chmod', '-R 777', mountpoint])


def ntfs_init (volume, label):
    """Initialise the given volume with an NTFS filesystem.

    volume -- The drive partition to format.
    label -- The name to give to the partition.

    Raises:
    CalledProcessError on failure.
    """
    check_call(['mkntfs', '-fl', label, volume])
    mountpoint = '/dev/' + label
    mount(volume, mountpoint)
    check_call(['chmod', '-R 755', mountpoint])


def main ():
    """Program entrypoint.
    """
    # Select the drive to format.
    drives = attached_drives()
    drive = reversed(drives)[0]
    drive = read_choice('Select drive to format', drives, default=drive)
    capacity = drive_size(drive)

    # Set the size of the DCP partition.
    dcp_size = capacity - bytesize.from_mb(600)
    dcp_size = read_dcp_size(capacity, default=dcp_size)

    # Infer the size of the NTFS partition.
    ntfs_size = capacity - dcp_size

    # Summarise options.
    print ('''
    Summary
    -------
    Drive device\t{dr}
    Drive capacity\t{cap} GB
    DCP partition size\t{dcp_sz} GB
    NTFS partition size\t{ntfs_sz} GB
    '''.format(dr=drive,
               cap=capacity.gigabytes,
               dcp_sz=dcp_size.gigabytes,
               ntfs_sz=ntfs_size.gigabytes))

    if not read_y_or_n('The drive will be erased. Continue?'):
        exit('Aborted')

    # Initialise drive.

    print('--> Unmounting drive...')
    unmount(drive)

    print('--> Partitioning...')
    try:
        partition(drive, dcp_size, ntfs_size)
    except CalledProcessError:
        exit('Error: partitioning failed')

    print('--> Initialising DCP partition...')
    try:
        dcp_init('DCP', drive)
    except CalledProcessError:
        exit('Error: DCP initialisation failed')

    print('--> Initialising NTFS partition...')
    try:
        ntfs_init('NTFS', drive)
    except CalledProcessError:
        exit('Error: NTFS initialisation failed')

    print('--> Unmounting drive...')
    unmount(drive)

    print('--> Finished')
    return 0


# if __name__ == '__main__':
#     main()
