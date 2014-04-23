# dcp.py

Format a drive for use as a Digital Cinema Package (DCP).

## Summary

This tool will reformat the specified drive with an EXT2 partition. It will also
create a small NTFS partition for documentation, tooling or other miscellany for
clients.

The command can be invoked without arguments, in which case you will be guided
through the drive setup interactively.

Requires external programs for drive formatting. Requires Python 3.

Tested on Debian 7.4.

    usage: dcp [-d DRIVE] [-s GB] [-h] [-v]

    formatting options:
      -d DRIVE, --drive DRIVE
                            the absolute path to the drive to format
      -s GB, --dcp_size GB  the size of the DCP partition in gigabytes

    help:
      -h, --help            show usage
      -v, --version         show version


## Installation

Install using `setuptools`.

    python setup.py install

## Contributing

Yes, please do! See CONTRIBUTING for guidelines.

## License

See COPYING. Copyright (c) 2014 Chris Barrett.
