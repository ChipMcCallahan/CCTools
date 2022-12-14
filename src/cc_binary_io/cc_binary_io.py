"""Custom wrappers for working with io.BytesIO objects."""
import io
import logging
import struct


class CCBinary:
    """Custom wrappers for working with io.BytesIO objects."""
    # pylint: disable=too-few-public-methods
    class Writer:
        """Custom io.BytesIO wrapper for writing bytes."""
        def __init__(self):
            self.bio = io.BytesIO(bytes())

        def byte(self, byte):
            """Writes a byte to output."""
            self.bio.write(struct.pack("<B", byte))

        def short(self, short):
            """Writes a short (2 bytes) to output."""
            self.bio.write(struct.pack("<H", short))

        def shorts(self, shorts):
            """Writes a sequence of shorts (2 bytes) to output."""
            for short in shorts:
                self.short(short)

        def long(self, long):
            """Writes a long (4 bytes) to output."""
            self.bio.write(struct.pack("<L", long))

        def bytes(self, bytes_to_write):
            """Writes an arbitrary sequence of bytes to output."""
            self.bio.write(bytes_to_write)

        def written(self):
            """Returns all written bytes."""
            return self.bio.getvalue()

    class Reader:
        """Custom io.BytesIO wrapper for reading bytes."""
        def __init__(self, bytes_to_read):
            self.bio = io.BytesIO(bytes_to_read)

        def byte(self):
            """Read a byte from IO."""
            return struct.unpack("<B", self.bio.read(1))[0]

        def short(self):
            """Read a short (2 bytes) from IO."""
            return struct.unpack("<H", self.bio.read(2))[0]

        def long(self):
            """Read a long (4 bytes) from IO."""
            return struct.unpack("<L", self.bio.read(4))[0]

        def bytes(self, n_bytes, *, convert_to_utf8=False):
            """Read n bytes from IO."""
            result = self.bio.read(n_bytes)
            try:
                return result.decode("utf-8") if convert_to_utf8 else result
            except UnicodeError:
                # e.g. b'\xc5sa Ehinger Berling\x00' in cc2rejects
                logging.error("error converting %s to utf-8", result)
                return result

        def size(self):
            """The total number of bytes in the reader."""
            return len(self.bio.getvalue())

        def remaining(self):
            """The number of bytes remaining."""
            return self.size() - self.current()

        def current(self):
            """The current index of the reader."""
            return self.bio.tell()

        def raw(self):
            """The raw bytes in the reader."""
            return self.bio.getvalue()

        def seek(self, index):
            """Set the current index of the reader."""
            self.bio.seek(index)
