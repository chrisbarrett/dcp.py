"""
Represents a size in bytes.
"""

class ByteSize (object):
    '''Represents a size in bytes.'''
    def __init__ (self, n_bytes):
        assert(isinstance(n_bytes, int))
        self.bytes = n_bytes
        self.kilobytes = self.bytes / 1024.0
        self.megabytes = self.kilobytes / 1024.0
        self.gigabytes = self.megabytes / 1024.0

    def __add__(self, other):
        return ByteSize(self.bytes + other.bytes)

    def __sub__(self, other):
        return ByteSize(self.bytes - other.bytes)

    def __mul__(self, other):
        return ByteSize(self.bytes * other.bytes)

    def __eq__(self, other):
        return self.bytes == other.bytes


def from_b (n_b):
    '''Construct a new ByteSize representing `n_b` bytes.'''
    return ByteSize(n_b)

def from_kb (n_kb):
    '''Construct a new ByteSize representing `n_kb` kilobytes.'''
    return ByteSize(n_kb * 1024)

def from_mb (n_mb):
    '''Construct a new ByteSize representing `n_kb` megabytes.'''
    return ByteSize(n_mb * 1024**2)

def from_gb (n_gb):
    '''Construct a new ByteSize representing `n_kb` gigabytes.'''
    return ByteSize(n_gb * 1024**3)
