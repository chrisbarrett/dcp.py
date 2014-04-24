#!/usr/bin/env python3
"""Format a drive for use as a Digital Cinema Package.
"""

import argparse
import sys
from   subprocess  import CalledProcessError
import dcp.bytesize as bytesize

from   dcp.__init__    import __version__
from   dcp.drive       import attached_drives, drive_size, unmount
from   dcp.drive       import partition, dcp_init, ntfs_init
from   dcp.interactive import read_choice, read_number, read_y_or_n


# Use this module's docstring as the program description.
DESCRIPTION = sys.modules[__name__].__doc__
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
              'Must be less than drive capacity ({:g2} GB).'.format(
                  default.gigabytes))

        return read_dcp_size(capacity, default)
    else:
        return size


def print_drive_list (drives):
    """Print a list of available drives for formatting.

    drives -- is the list of drives to print.
    """
    lines = []
    for drive in drives:
        size = drive_size(drive)
        line = '{}\t {.gigabytes:>8.2f} GB'.format(drive, size)
        lines.append(line)

    print('''
Available drives:
--------------------------------
{}
    '''.format('\n'.join(lines)))


def process_args (args):
    """Process program args. Interactively read any args that were not supplied.

    args -- The arguments object output by argparse.

    Returns:
    The modified args object.
    """
    # Select the drive to format.
    #
    # As a basic sanity check, only offer to format drives that have a capacity
    # of 10 GB or greater. This should exclude CDs, DVDs etc.

    drives = [drive for drive in attached_drives()
              if drive_size(drive) >= bytesize.from_gb(10)]

    if not args.drive:
        print_drive_list(drives)
        default_drive = next(reversed(drives))
        args.drive = read_choice(
            'Select drive to format', drives, default=default_drive)
    elif not args.drive in drives:
        exit('Error: Invalid drive path ({})'.format(args.drive))


    args.capacity = drive_size(args.drive)

    # Set the size of the DCP partition.

    if not args.dcp_size:
        default_size = args.capacity - bytesize.from_mb(600)
        args.dcp_size = read_dcp_size(args.capacity, default=default_size)
    else:
        args.dcp_size = bytesize.from_gb(args.dcp_size)

    # Infer the size of the NTFS partition.
    args.ntfs_size = args.capacity - args.dcp_size

    return args


def main ():
    """Program entrypoint.
    """

    # Parse program arguments.

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

    group.add_argument(
        '-y', '--no-confirm',
        default=False,
        action='store_true',
        help='skip confirmation dialogs')

    group = parser.add_argument_group('help')

    group.add_argument(
        '-h', '--help',
        action='help',
        help='show usage')

    group.add_argument(
        '-v', '--version',
        action='version',
        version=__version__,
        help='show version')

    try:
        args = parser.parse_args()
        args = process_args(args)
    except KeyboardInterrupt:
        exit('\nNo changes made.')

    # Summarise options.

    print ('''
The drive will be repartitioned as follows:

{}\t\t{.gigabytes:>8.2f} GB
 |
 |-- 1: DCP \t ext2 \t{.gigabytes:>8.2f} GB
 `-- 2: NTFS\t ntfs \t{.gigabytes:>8.2f} GB

    '''.format(args.drive, args.capacity, args.dcp_size, args.ntfs_size))

    # Prompt before continuing.

    accepted = args.no_confirm or read_y_or_n(
        'The drive will be erased. Continue?')

    if not accepted:
        exit('\nNo changes made.')

    # Initialise drive.

    print('--> Unmounting drive...')
    unmount(args.drive)

    print('--> Partitioning...')
    try:
        partition(args.drive, args.dcp_size, args.ntfs_size)
    except CalledProcessError:
        exit('\nError: partitioning failed')

    print('--> Initialising DCP partition...')
    try:
        dcp_init('DCP', args.drive)
    except CalledProcessError:
        exit('\nError: DCP initialisation failed')

    print('--> Initialising NTFS partition...')
    try:
        ntfs_init('NTFS', args.drive)
    except CalledProcessError:
        exit('\nError: NTFS initialisation failed')

    print('--> Unmounting drive...')
    unmount(args.drive)

    print('--> Finished')
    return 0
