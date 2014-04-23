"""Commands for working with attached drives.
"""

import os
from   subprocess import check_call, call, getoutput

import dcp.bytesize as bytesize


def attached_drives ():
    """Return a list of attached drives.
    """
    output = getoutput('df')
    lines = output.strip().split('\n')
    info = [line.split() for line in lines if '/dev/' in line]
    return [fields[0] for fields in info]


def drive_size (drive):
    """Return the raw capacity of `drive` as a ByteSize.
    """
    output = getoutput('df')
    lines = output.strip().split('\n')
    info = [line.split() for line in lines if drive in line][0]
    blocks = int(info[1])
    blocksize = 512
    return bytesize.from_b(blocks * blocksize)


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
