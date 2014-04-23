#!/usr/bin/env python3
"""Format a drive for use as a Digital Cinema Package.

Requires external programs for EXT-formatting. Tested on Debian.

(c) Chris Barrett 2014
"""

import bytesize
from   drive       import attached_drives, drive_size, unmount
from   drive       import partition, dcp_init, ntfs_init
from   interactive import read_choice, read_number, read_y_or_n
from   subprocess  import CalledProcessError


def read_dcp_size (capacity, default):
    """Read the size of the DCP partition from the user.

    capacity -- the total capacity of the drive as a ByteSize object.
    default -- the default size in bytes.

    Returns:
    The size of the DCP partition as a ByteSize.
    """
    gigs = round(default.gigabytes, 2)
    size = read_number('DCP partition size (GB)', gigs)
    size = bytesize.from_gb(size)
    if size >= capacity:
        print('Invalid partition size. ' +
              'Must be less than drive capacity ({} GB).'.format(
                  default.gigabytes))

        return read_dcp_size(capacity, default)
    else:
        return size


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
