"""Tests for CCBinary."""
import unittest
from cc_tools.cc_binary import CCBinary


class TestCCBinary(unittest.TestCase):
    def test_write_and_read_byte(self):
        """Test writing and reading a single byte."""
        w = CCBinary.Writer()
        w.byte(123)
        data = w.written()
        self.assertEqual(len(data), 1, "Should have written exactly 1 byte.")

        r = CCBinary.Reader(data)
        self.assertEqual(r.byte(), 123, "Read value should match what was written.")
        self.assertEqual(r.remaining(), 0, "No bytes left after reading one byte.")

    def test_write_and_read_short(self):
        """Test writing and reading a short integer."""
        w = CCBinary.Writer()
        w.short(999)  # 0x03E7
        data = w.written()
        self.assertEqual(len(data), 2, "Should have written exactly 2 bytes for a short.")

        r = CCBinary.Reader(data)
        self.assertEqual(r.short(), 999, "Read short should match 999.")
        self.assertEqual(r.remaining(), 0, "No bytes left after reading one short.")

    def test_write_and_read_shorts(self):
        """Test writing and reading multiple shorts."""
        w = CCBinary.Writer()
        w.shorts([100, 200, 300])
        data = w.written()
        self.assertEqual(len(data), 6, "3 shorts => 6 bytes total.")

        r = CCBinary.Reader(data)
        self.assertEqual(r.short(), 100)
        self.assertEqual(r.short(), 200)
        self.assertEqual(r.short(), 300)
        self.assertEqual(r.remaining(), 0)

    def test_write_and_read_long(self):
        """Test writing and reading a long integer."""
        w = CCBinary.Writer()
        w.long(123456789)  # 0x075BCD15
        data = w.written()
        self.assertEqual(len(data), 4, "A long should be exactly 4 bytes.")

        r = CCBinary.Reader(data)
        self.assertEqual(r.long(), 123456789, "Read long should match 123456789.")
        self.assertEqual(r.remaining(), 0)

    def test_write_and_read_bytes(self):
        """Test writing and reading arbitrary bytes."""
        sample = b'\x01\x02\x03\x04'
        w = CCBinary.Writer()
        w.bytes(sample)
        data = w.written()
        self.assertEqual(len(data), 4, "Should have written exactly 4 bytes.")

        r = CCBinary.Reader(data)
        read_back = r.bytes(4)
        self.assertEqual(read_back, sample, "Should read back the same bytes.")
        self.assertEqual(r.remaining(), 0)

    def test_write_and_read_text(self):
        """Test writing and reading text with windows-1252 encoding."""
        # Example text with extended chars to demonstrate windows-1252 usage
        text_sample = "Åsa 123 – ©Test"  # '–' is present in windows-1252
        w = CCBinary.Writer()

        # Typically you'd write length + text in an actual format.
        encoded = text_sample.encode("windows-1252", errors="replace")
        w.long(len(encoded))     # Write length (4 bytes)
        w.text(text_sample)      # Now write the actual text
        data = w.written()

        r = CCBinary.Reader(data)
        text_length = r.long()
        self.assertEqual(text_length, len(encoded),
                         "The length read must match the size of the text.")

        # Now read that many bytes as text in windows-1252
        read_text = r.text(text_length)
        self.assertEqual(read_text, text_sample,
                         "Read text should match the original text sample.")
        self.assertEqual(r.remaining(), 0)

    def test_seek_and_remaining(self):
        """Test the seek and remaining methods."""
        w = CCBinary.Writer()
        w.short(999)   # 2 bytes
        w.byte(123)    # 1 byte
        data = w.written()

        r = CCBinary.Reader(data)
        self.assertEqual(r.current(), 0, "Reader should start at index 0.")
        self.assertEqual(r.remaining(), 3, "3 bytes total so far (2 + 1).")

        val_short = r.short()    # Move forward 2 bytes
        self.assertEqual(val_short, 999)
        self.assertEqual(r.current(), 2, "We should now be at index 2.")
        self.assertEqual(r.remaining(), 1, "1 byte left to read.")

        val_byte = r.byte()
        self.assertEqual(val_byte, 123)
        self.assertEqual(r.current(), 3)
        self.assertEqual(r.remaining(), 0)

        # Test seeking backward
        r.seek(1)  # Move to position 1
        self.assertEqual(r.current(), 1)
        self.assertEqual(r.remaining(), 2)

    def test_raw(self):
        """Test the raw method to ensure it returns the exact byte sequence."""
        w = CCBinary.Writer()
        w.short(999)
        w.byte(123)
        data = w.written()

        r = CCBinary.Reader(data)
        self.assertEqual(r.raw(), data, "raw() should return the entire underlying data.")
        self.assertEqual(r.size(), len(data))
        self.assertEqual(r.remaining(), len(data), "Haven't read anything yet.")

    def test_combined_write_read(self):
        """
        Test writing multiple data types in sequence, then reading them back
        to confirm they come out in the right order with no corruption.
        """
        w = CCBinary.Writer()
        w.short(999)
        w.byte(123)
        w.long(99999999)
        w.text("Test©")  # '©' is in windows-1252
        data = w.written()

        r = CCBinary.Reader(data)
        val_short = r.short()
        val_byte = r.byte()
        val_long = r.long()

        # The text is "Test©" => 5 characters, all representable in windows-1252
        text_len = r.remaining()
        read_text = r.text(text_len)

        self.assertEqual(val_short, 999,    "Should read 999 from short.")
        self.assertEqual(val_byte, 123,     "Should read 123 from byte.")
        self.assertEqual(val_long, 99999999,"Should read 99999999 from long.")
        self.assertEqual(read_text, "Test©", "Should read back the correct text.")
        self.assertEqual(r.remaining(), 0,  "No bytes left.")

    def test_write_invalid_text(self):
        """Test writing text with characters not in windows-1252."""
        w = CCBinary.Writer()
        invalid_text = "Invalid Character: 😊"  # '😊' is not in windows-1252

        with self.assertRaises(ValueError):
            w.text(invalid_text)

    def test_reader_eof_error(self):
        """Test that Reader raises EOFError when reading beyond data."""
        w = CCBinary.Writer()
        w.byte(1)
        data = w.written()

        r = CCBinary.Reader(data)
        self.assertEqual(r.byte(), 1)

        with self.assertRaises(EOFError):
            r.byte()  # Attempt to read beyond available data

    def test_writer_multiple_text_fields(self):
        """Test writing and reading multiple text fields."""
        texts = ["First Title", "Second Author", "Third Note"]
        w = CCBinary.Writer()

        # Write each text with its length
        for txt in texts:
            encoded = txt.encode("windows-1252")
            w.long(len(encoded))
            w.text(txt)

        data = w.written()

        r = CCBinary.Reader(data)
        for txt in texts:
            text_length = r.long()
            read_text = r.text(text_length)
            self.assertEqual(read_text, txt, f"Read text '{read_text}' should match '{txt}'.")

        self.assertEqual(r.remaining(), 0, "No bytes left after reading all text fields.")


if __name__ == "__main__":
    unittest.main()
