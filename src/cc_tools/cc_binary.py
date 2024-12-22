"""Class for reading and writing CC1 and CC2 levels in binary format."""
import io
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

        def text(self, txt):
            """
            Writes a string to output, encoded as windows-1252.
            The caller is responsible for writing the length beforehand.
            """
            try:
                encoded = txt.encode("windows-1252")
            except UnicodeEncodeError as e:
                raise ValueError(f"Text contains characters not supported by windows-1252: {e}")
            self.bytes(encoded)

        def written(self):
            """Returns all written bytes."""
            return self.bio.getvalue()

    class Reader:
        """Custom io.BytesIO wrapper for reading bytes."""

        def __init__(self, bytes_to_read):
            self.bio = io.BytesIO(bytes_to_read)

        def byte(self):
            """Read a byte from IO."""
            byte = self.bio.read(1)
            if len(byte) < 1:
                raise EOFError("Unexpected end of data while reading a byte.")
            return struct.unpack("<B", byte)[0]

        def short(self):
            """Read a short (2 bytes) from IO."""
            short = self.bio.read(2)
            if len(short) < 2:
                raise EOFError("Unexpected end of data while reading a short.")
            return struct.unpack("<H", short)[0]

        def long(self):
            """Read a long (4 bytes) from IO."""
            long_bytes = self.bio.read(4)
            if len(long_bytes) < 4:
                raise EOFError("Unexpected end of data while reading a long.")
            return struct.unpack("<L", long_bytes)[0]

        def bytes(self, n_bytes):
            """Read n bytes from IO."""
            data = self.bio.read(n_bytes)
            if len(data) < n_bytes:
                raise EOFError(f"Unexpected end of data while reading {n_bytes} bytes.")
            return data

        def text(self, n_bytes):
            """Read n bytes from IO and convert to windows-1252."""
            return self.bytes(n_bytes).decode("windows-1252")

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