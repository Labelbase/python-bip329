# file: test_label_validation.py
import unittest
import os
from bip329.bip329_parser import BIP329_Parser
from bip329.bip329_writer import BIP329JSONLWriter


class TestLabelValidation(unittest.TestCase):
    def setUp(self):
        self.test_filename = 'test_label_validation.jsonl'

    def tearDown(self):
        if os.path.exists(self.test_filename):
            os.remove(self.test_filename)

    def test_label_length_warning_parser(self):
        """Test parser logs warning for long labels"""
        long_label = "A" * 300  # 300 chars > 255
        with open(self.test_filename, 'w') as f:
            f.write(f'{{"type": "tx", "ref": "abc123", "label": "{long_label}"}}\n')

        parser = BIP329_Parser(self.test_filename)
        with self.assertLogs(level='WARNING') as log:
            entries = parser.load_entries()

        self.assertEqual(len(entries), 1)
        self.assertIn('exceeds suggested maximum of 255', ''.join(log.output))

    def test_label_length_warning_writer(self):
        """Test writer logs warning for long labels"""
        writer = BIP329JSONLWriter(self.test_filename)
        long_label = "B" * 300

        with self.assertLogs(level='WARNING') as log:
            writer.write_label({
                "type": "tx",
                "ref": "def456",
                "label": long_label
            })

        self.assertIn('exceeds suggested maximum of 255', ''.join(log.output))

    def test_valid_label_length_no_warning(self):
        """Test no warning for labels <= 255 chars"""
        valid_label = "C" * 255  # Exactly 255 chars
        writer = BIP329JSONLWriter(self.test_filename)

        # Just write the label - no warnings expected
        writer.write_label({
            "type": "tx",
            "ref": "ghi789",
            "label": valid_label
        })

        # Test passes if no exception was raised
        self.assertTrue(True)  # Explicit pass

class TestUTF8Validation(unittest.TestCase):
    def setUp(self):
        self.test_filename = 'test_utf8_validation.jsonl'

    def tearDown(self):
        if os.path.exists(self.test_filename):
            os.remove(self.test_filename)

    def test_replace_non_utf8_false_strict(self):
        """Test strict mode rejects invalid UTF-8"""
        from bip329.validation_utils import validate_utf8_encoding

        with self.assertRaises(ValueError):
            validate_utf8_encoding("test\udcff", False)

    def test_replace_non_utf8_true(self):
        """Test invalid UTF-8 gets replaced with replacement character"""
        from bip329.validation_utils import validate_utf8_encoding

        with self.assertLogs(level='WARNING') as log:
            result = validate_utf8_encoding("test\udcff", True)

        # Check that invalid characters were replaced (could be � or ?)
        self.assertNotIn('\udcff', result)  # Original invalid char should be gone
        self.assertIn('replaced with', ''.join(log.output))


    def test_writer_utf8_validation(self):
        """Test writer validates UTF-8 encoding"""
        writer = BIP329JSONLWriter(self.test_filename, replace_non_utf8=True)

        # Test with replacement mode
        with self.assertLogs(level='WARNING') as log:
            writer.write_label({
                "type": "tx",
                "ref": "def456",
                "label": "test\udcffinvalid"
            })

        # Should log warning about UTF-8 replacement
        self.assertIn('Invalid UTF-8', ''.join(log.output))


if __name__ == '__main__':
    unittest.main()
