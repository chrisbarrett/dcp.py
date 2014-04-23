#!/usr/bin/env python3
"""Format a drive for use as a Digital Cinema Package.
"""

import argparse
import sys
from   subprocess  import CalledProcessError

import dcp.bytesize as bytesize
from   dcp.drive       import attached_drives, drive_size, unmount
from   dcp.drive       import partition, dcp_init, ntfs_init
from   dcp.interactive import read_choice, read_number, read_y_or_n


# Use this module's docstring as the program description.
DESCRIPTION = sys.modules[__name__].__doc__
VERSION = 0.1
EPILOGUE = 'Requires external programs for drive formatting.'


def read_dcp_size (capacity, default):
    """Read the size of the DCP partition from the user.

    capacity -- the total capacity of the drive as a ByteSize object.
    default -- the default size in bytes.

    Returns:
    The size of the DCP partition as a ByteSize.
    """
    gigs = round(default.gigabytes, 2)
    size = read_number('DCP partition size (GB)', gigs)
    size = bytesize.from_gb(int(size))
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

    #### Parse program arguments.

    parser = argparse.ArgumentParser(
        description=DESCRIPTION,
        epilog=EPILOGUE,
        add_help=False)

    group = parser.add_argument_group('formatting options')

    group.add_argument(
        '-d', '--drive',
        help='the absolute path to the drive to format')

    group.add_argument(
        '-s', '--dcp_size',
        type=float,
        metavar='GB',
        help='the size of the DCP partition in gigabytes')

    group = parser.add_argument_group('help')
    group.add_argument(
        '-h', '--help',
        action='help',
        help='show usage')

    group.add_argument(
        '-v', '--version',
        action='version',
        version=VERSION,
        help='show version')


    args = parser.parse_args()


    #### Interactively read arguments that were not supplied.


    # Select the drive to format.

    drives = attached_drives()

    if not args.drive:
        default_drive = next(reversed(drives))
        args.drive = read_choice(
            'Select drive to format', drives, default=default_drive)
    elif not args.drive in drives:
        exit('Error: Invalid drive path ({})'.format(args.drive))


    capacity = drive_size(args.drive)

    # Set the size of the DCP partition.

    if not args.dcp_size:
        default_size = capacity - bytesize.from_mb(600)
        args.dcp_size = read_dcp_size(capacity, default=default_size)
    else:
        args.dcp_size = bytesize.from_gb(args.dcp_size)

    # Infer the size of the NTFS partition.
    args.ntfs_size = capacity - args.dcp_size


    #### Summarise options.


    print ('''
    Summary
    -------
    Drive device\t{dr}
    Drive capacity\t{cap} GB
    DCP partition size\t{dcp_sz} GB
    NTFS partition size\t{ntfs_sz} GB
    '''.format(dr=args.drive,
               cap=round(capacity.gigabytes, 2),
               dcp_sz=round(args.dcp_size.gigabytes, 2),
               ntfs_sz=round(args.ntfs_size.gigabytes, 2)))

    if not read_y_or_n('The drive will be erased. Continue?'):
        exit('Aborted')


    #### Initialise drive.


    print('--> Unmounting drive...')
    unmount(args.drive)

    print('--> Partitioning...')
    try:
        partition(args.drive, args.dcp_size, args.ntfs_size)
    except CalledProcessError:
        exit('Error: partitioning failed')

    print('--> Initialising DCP partition...')
    try:
        dcp_init('DCP', args.drive)
    except CalledProcessError:
        exit('Error: DCP initialisation failed')

    print('--> Initialising NTFS partition...')
    try:
        ntfs_init('NTFS', args.drive)
    except CalledProcessError:
        exit('Error: NTFS initialisation failed')

    print('--> Unmounting drive...')
    unmount(args.drive)

    print('--> Finished')
    return 0


if __name__ == '__main__':
    main()
