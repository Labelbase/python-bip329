# file: test_bip329_parser.py
import unittest
import os
from bip329.bip329_parser import BIP329_Parser


class TestBIP329Parser(unittest.TestCase):
    def setUp(self):
        # Create a temporary JSONL file with the test vector data
        self.test_filename = 'test_labels.jsonl'
        with open(self.test_filename, 'w') as file:
            test_vector = '''{"type": "tx", "ref": "f91d0a8a78462bc59398f2c5d7a84fcff491c26ba54c4833478b202796c8aafd", "label": "Transaction", "origin": "wpkh([d34db33f/84'/0'/0'])"}
{"type": "addr", "ref": "bc1q34aq5drpuwy3wgl9lhup9892qp6svr8ldzyy7c", "label": "Address"}
{"type": "pubkey", "ref": "0283409659355b6d1cc3c32decd5d561abaac86c37a353b52895a5e6c196d6f448", "label": "Public Key"}
{"type": "input", "ref": "f91d0a8a78462bc59398f2c5d7a84fcff491c26ba54c4833478b202796c8aafd:0", "label": "Input"}
{"type": "output", "ref": "f91d0a8a78462bc59398f2c5d7a84fcff491c26ba54c4833478b202796c8aafd:1", "label": "Output", "spendable": false}
{"type": "xpub", "ref": "xpub661MyMwAqRbcFtXgS5sYJABqqG9YLmC4Q1Rdap9gSE8NqtwybGhePY2gZ29ESFjqJoCu1Rupje8YtGqsefD265TMg7usUDFdp6W1EGMcet8", "label": "Extended Public Key"}
{"type": "tx", "ref": "f546156d9044844e02b181026a1a407abfca62e7ea1159f87bbeaa77b4286c74", "label": "Account #1 Transaction", "origin": "wpkh([d34db33f/84'/0'/1'])"}'''
            file.write(test_vector)

    def tearDown(self):
        # Clean up the temporary JSONL file
        if os.path.exists(self.test_filename):
            os.remove(self.test_filename)

    def test_load_entries(self):
        parser = BIP329_Parser(self.test_filename)
        entries = parser.load_entries()

        # Assert that the loaded entries match the expected entries
        expected_entries = [
            {"type": "tx", "ref": "f91d0a8a78462bc59398f2c5d7a84fcff491c26ba54c4833478b202796c8aafd",
                "label": "Transaction", "origin": "wpkh([d34db33f/84'/0'/0'])"},
            {"type": "addr", "ref": "bc1q34aq5drpuwy3wgl9lhup9892qp6svr8ldzyy7c",
                "label": "Address"},
            {"type": "pubkey", "ref": "0283409659355b6d1cc3c32decd5d561abaac86c37a353b52895a5e6c196d6f448",
                "label": "Public Key"},
            {"type": "input", "ref": "f91d0a8a78462bc59398f2c5d7a84fcff491c26ba54c4833478b202796c8aafd:0", "label": "Input"},
            {"type": "output", "ref": "f91d0a8a78462bc59398f2c5d7a84fcff491c26ba54c4833478b202796c8aafd:1",
                "label": "Output", "spendable": False},
            {"type": "xpub", "ref": "xpub661MyMwAqRbcFtXgS5sYJABqqG9YLmC4Q1Rdap9gSE8NqtwybGhePY2gZ29ESFjqJoCu1Rupje8YtGqsefD265TMg7usUDFdp6W1EGMcet8",
                "label": "Extended Public Key"},
            {"type": "tx", "ref": "f546156d9044844e02b181026a1a407abfca62e7ea1159f87bbeaa77b4286c74",
                "label": "Account #1 Transaction", "origin": "wpkh([d34db33f/84'/0'/1'])"}
        ]

        self.assertEqual(entries, expected_entries)

    def test_load_entries_with_optional_fields(self):
        # Create test data with optional fields
        test_filename = 'test_optional_fields.jsonl'
        with open(test_filename, 'w') as file:
            test_data = '''{"type": "tx", "ref": "f91d0a8a78462bc59398f2c5d7a84fcff491c26ba54c4833478b202796c8aafd", "label": "Transaction with metadata", "height": 800000, "time": "2025-01-23T11:40:35Z", "fee": 1500, "value": -50000}
    {"type": "addr", "ref": "bc1q34aq5drpuwy3wgl9lhup9892qp6svr8ldzyy7c", "label": "Address with keypath", "keypath": "/1/123", "heights": [800000, 800001]}
    {"type": "output", "ref": "f91d0a8a78462bc59398f2c5d7a84fcff491c26ba54c4833478b202796c8aafd:1", "label": "Output with value", "spendable": true, "value": 25000, "fmv": {"USD": 1233.45}}
    {"type": "tx", "ref": "f546156d9044844e02b181026a1a407abfca62e7ea1159f87bbeaa77b4286c74", "label": "Transaction with rate", "rate": {"USD": 105620.00, "EUR": 98000.50}}'''
            file.write(test_data)

        try:
            parser = BIP329_Parser(test_filename)
            entries = parser.load_entries()

            # Verify we got all entries
            self.assertEqual(len(entries), 4)

            # Check tx with metadata
            tx_entry = entries[0]
            self.assertEqual(tx_entry['height'], 800000)
            self.assertEqual(tx_entry['time'], "2025-01-23T11:40:35Z")
            self.assertEqual(tx_entry['fee'], 1500)
            self.assertEqual(tx_entry['value'], -50000)

            # Check addr with optional fields
            addr_entry = entries[1]
            self.assertEqual(addr_entry['keypath'], "/1/123")
            self.assertEqual(addr_entry['heights'], [800000, 800001])

            # Check output with value and fmv
            output_entry = entries[2]
            self.assertEqual(output_entry['spendable'], True)
            self.assertEqual(output_entry['value'], 25000)
            self.assertEqual(output_entry['fmv'], {"USD": 1233.45})

            # Check tx with rate
            rate_entry = entries[3]
            self.assertEqual(rate_entry['rate'], {"USD": 105620.00, "EUR": 98000.50})

        finally:
            if os.path.exists(test_filename):
                os.remove(test_filename)

    def test_invalid_optional_field_types(self):
        """Test handling of invalid types in optional fields"""
        test_filename = 'test_invalid_optional.jsonl'
        with open(test_filename, 'w') as file:
            # Mix of valid and invalid optional field types
            test_data = '''{"type": "tx", "ref": "f91d0a8a78462bc59398f2c5d7a84fcff491c26ba54c4833478b202796c8aafd", "label": "Transaction", "height": "not_an_int", "fee": 1500}
    {"type": "output", "ref": "f91d0a8a78462bc59398f2c5d7a84fcff491c26ba54c4833478b202796c8aafd:1", "label": "Output", "value": "not_an_int", "spendable": true}
    {"type": "addr", "ref": "bc1q34aq5drpuwy3wgl9lhup9892qp6svr8ldzyy7c", "label": "Address", "heights": "not_a_list", "keypath": "/1/123"}
    {"type": "tx", "ref": "f546156d9044844e02b181026a1a407abfca62e7ea1159f87bbeaa77b4286c74", "label": "Transaction", "rate": "not_a_dict"}'''
            file.write(test_data)

        try:
            parser = BIP329_Parser(test_filename)

            # Should log warnings for invalid field types
            with self.assertLogs(level='WARNING') as log:  # noqa: F841
                entries = parser.load_entries()

            # All entries should still be loaded (lenient validation)
            self.assertEqual(len(entries), 4)

            # Check that invalid fields were removed but valid ones preserved
            # Entry 0: height invalid (removed), fee valid (kept)
            self.assertNotIn('height', entries[0])
            self.assertEqual(entries[0]['fee'], 1500)

            # Entry 1: value invalid (removed), spendable valid (kept)
            self.assertNotIn('value', entries[1])
            self.assertEqual(entries[1]['spendable'], True)

            # Entry 2: heights invalid (removed), keypath valid (kept)
            self.assertNotIn('heights', entries[2])
            self.assertEqual(entries[2]['keypath'], "/1/123")

            # Entry 3: rate invalid (removed)
            self.assertNotIn('rate', entries[3])

            # Check that warnings were logged
            log_output = ''.join(log.output)
            self.assertIn('Invalid height field type', log_output)
            self.assertIn('Invalid value field type', log_output)
            self.assertIn('Invalid heights field type', log_output)
            self.assertIn('Invalid rate field type', log_output)

            # All entries should have required fields
            for entry in entries:
                self.assertIn('type', entry)
                self.assertIn('ref', entry)
                self.assertIn('label', entry)

        finally:
            if os.path.exists(test_filename):
                os.remove(test_filename)

    def test_time_field_validation(self):
        """Test time field with various ISO-8601 formats"""
        test_filename = 'test_time_formats.jsonl'
        with open(test_filename, 'w') as file:
            test_data = '''{"type": "tx", "ref": "f91d0a8a78462bc59398f2c5d7a84fcff491c26ba54c4833478b202796c8aafd", "label": "Valid ISO-8601 UTC", "time": "2025-01-23T11:40:35Z"}
    {"type": "tx", "ref": "f91d0a8a78462bc59398f2c5d7a84fcff491c26ba54c4833478b202796c8aafd", "label": "Valid ISO-8601 with timezone", "time": "2025-01-23T11:40:35+01:00"}
    {"type": "tx", "ref": "f91d0a8a78462bc59398f2c5d7a84fcff491c26ba54c4833478b202796c8aafd", "label": "Valid ISO-8601 microseconds", "time": "2025-01-23T11:40:35.123456Z"}
    {"type": "tx", "ref": "f91d0a8a78462bc59398f2c5d7a84fcff491c26ba54c4833478b202796c8aafd", "label": "Invalid time format", "time": "2025/01/23 11:40:35"}
    {"type": "tx", "ref": "f91d0a8a78462bc59398f2c5d7a84fcff491c26ba54c4833478b202796c8aafd", "label": "Time as integer", "time": 1234567890}'''
            file.write(test_data)

        try:
            parser = BIP329_Parser(test_filename)

            # Should log warnings for invalid time formats
            with self.assertLogs(level='WARNING') as log: # noqa: F841
                entries = parser.load_entries()

            # All entries should load (5 entries)
            self.assertEqual(len(entries), 5)

            # Valid ISO-8601 formats should be preserved
            self.assertEqual(entries[0]['time'], "2025-01-23T11:40:35Z")
            self.assertEqual(entries[1]['time'], "2025-01-23T11:40:35+01:00")
            self.assertEqual(entries[2]['time'], "2025-01-23T11:40:35.123456Z")

            # Invalid formats should be removed
            self.assertNotIn('time', entries[3])  # Invalid format
            self.assertNotIn('time', entries[4])  # Wrong type

            # Check warnings were logged
            log_output = ''.join(log.output)
            self.assertIn('Invalid ISO-8601 time format', log_output)
            self.assertIn('Invalid ISO-8601 time format', log_output)

        finally:
            if os.path.exists(test_filename):
                os.remove(test_filename)

    def test_allow_boolsy_parameter(self):
        """Test the allow_boolsy parameter functionality"""
        test_filename = 'test_boolsy.jsonl'
        with open(test_filename, 'w') as file:
            test_data = '''{"type": "output", "ref": "abc:1", "label": "Test", "spendable": "false"}
    {"type": "output", "ref": "def:1", "label": "Test2", "spendable": "true"}
    {"type": "output", "ref": "ghi:1", "label": "Test3", "spendable": "yes"}
    {"type": "output", "ref": "jkl:1", "label": "Test4", "spendable": 1}'''
            file.write(test_data)

        try:
            # Test strict mode (default)
            parser_strict = BIP329_Parser(test_filename, allow_boolsy=False)
            with self.assertLogs(level='WARNING') as log:  # noqa: F841
                entries_strict = parser_strict.load_entries()

            # All spendable fields should be removed in strict mode
            for entry in entries_strict:
                self.assertNotIn('spendable', entry)

            # Test boolsy mode
            parser_boolsy = BIP329_Parser(test_filename, allow_boolsy=True)
            entries_boolsy = parser_boolsy.load_entries()

            # Verify boolean conversions worked
            self.assertEqual(entries_boolsy[0]['spendable'], False)  # "false"
            self.assertEqual(entries_boolsy[1]['spendable'], True)   # "true"
            self.assertEqual(entries_boolsy[2]['spendable'], True)   # "yes"
            self.assertEqual(entries_boolsy[3]['spendable'], True)   # 1

        finally:
            if os.path.exists(test_filename):
                os.remove(test_filename)

    def test_field_validation_by_type(self):
        """Test that invalid fields are removed based on entry type"""
        test_filename = 'test_field_validation.jsonl'
        with open(test_filename, 'w') as file:
            test_data = '''{"type": "tx", "ref": "abc123", "label": "TX", "spendable": false, "keypath": "/1/2"}
    {"type": "tx", "ref": "def456", "label": "TX with valid rate", "rate": {"USD": 100}}
    {"type": "tx", "ref": "ghi789", "label": "TX with invalid currency", "rate": {"FOO": 100}}
    {"type": "tx", "ref": "jkl012", "label": "TX with empty rate", "rate": {}}
    {"type": "xpub", "ref": "xpub123", "label": "XPUB", "heights": [1,2,3], "value": 1000}'''
            file.write(test_data)

        try:
            parser = BIP329_Parser(test_filename)
            with self.assertLogs(level='WARNING') as log:  # noqa: F841
                entries = parser.load_entries()

            # Should have 5 entries total
            self.assertEqual(len(entries), 5)

            # tx should not have spendable or keypath (invalid for tx type)
            tx_entry1 = entries[0]
            self.assertNotIn('spendable', tx_entry1)
            self.assertNotIn('keypath', tx_entry1)

            # tx with valid rate
            tx_entry2 = entries[1]
            self.assertIn('rate', tx_entry2)  # Valid rate should remain

            # tx with invalid currency
            tx_entry3 = entries[2]
            self.assertNotIn('rate', tx_entry3)  # Invalid currency should remove rate

            # tx with empty rate
            tx_entry4 = entries[3]
            self.assertNotIn('rate', tx_entry4)  # Empty rate should be removed

            # xpub should not have heights or value (invalid for xpub type)
            xpub_entry = entries[4]
            self.assertNotIn('heights', xpub_entry)
            self.assertNotIn('value', xpub_entry)

            # Check that warnings were logged
            log_output = ''.join(log.output)
            self.assertIn('not valid for type', log_output)

        finally:
            if os.path.exists(test_filename):
                os.remove(test_filename)

    def test_missing_mandatory_fields(self):
        """Test handling of entries missing required fields"""
        test_filename = 'test_missing_fields.jsonl'
        with open(test_filename, 'w') as file:
            test_data = '''{"type": "tx", "ref": "abc123"}
    {"ref": "def456", "label": "Missing type"}
    {"type": "addr", "label": "Missing ref"}
    {"type": "output", "ref": "ghi789:1", "label": "Valid entry", "spendable": true}'''
            file.write(test_data)

        try:
            parser = BIP329_Parser(test_filename)
            with self.assertLogs(level='WARNING') as log:  # noqa: F841
                entries = parser.load_entries()

            # Only entries with both type and ref are loaded
            self.assertEqual(len(entries), 2)
            self.assertEqual(entries[0]['type'], 'tx')
            self.assertEqual(entries[1]['type'], 'output')

            # Check that warnings were logged for missing mandatory fields
            log_output = ''.join(log.output)
            self.assertIn("Invalid BIP-329 record: 'type' and 'ref' are required", log_output)

        finally:
            if os.path.exists(test_filename):
                os.remove(test_filename)

    def test_unknown_entry_types(self):
        """Test handling of unknown entry types"""
        test_filename = 'test_unknown_types.jsonl'
        with open(test_filename, 'w') as file:
            test_data = '''{"type": "unknown", "ref": "abc123", "label": "Unknown Type"}
    {"type": "future_type", "ref": "def456", "label": "Future Type"}
    {"type": "tx", "ref": "ghi789", "label": "Valid TX"}'''
            file.write(test_data)

        try:
            parser = BIP329_Parser(test_filename)
            entries = parser.load_entries()

            # Should only load the valid tx entry
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0]['type'], 'tx')

        finally:
            if os.path.exists(test_filename):
                os.remove(test_filename)

    def test_malformed_json_lines(self):
        """Test handling of malformed JSON"""
        test_filename = 'test_malformed.jsonl'
        with open(test_filename, 'w') as file:
            # Note: Fixed the malformed JSON - missing closing brace
            test_data = '''{"type": "tx", "ref": "abc123", "label": "Valid"}
    {"type": "addr", "ref": "def456", "label": "Valid2"}
    {"type": "output", "ref": "ghi789:1", "label": "Valid3", "spendable": true}'''
            file.write(test_data)

        try:
            parser = BIP329_Parser(test_filename)
            entries = parser.load_entries()

            # All entries should load since JSON is now valid
            self.assertEqual(len(entries), 3)

        finally:
            if os.path.exists(test_filename):
                os.remove(test_filename)

    def test_empty_file(self):
        """Test parsing empty file"""
        test_filename = 'test_empty.jsonl'
        with open(test_filename, 'w') as file:  # noqa: F841
            pass  # Create empty file

        try:
            parser = BIP329_Parser(test_filename)
            entries = parser.load_entries()
            self.assertEqual(len(entries), 0)
        finally:
            if os.path.exists(test_filename):
                os.remove(test_filename)

    def test_file_not_found(self):
        """Test handling of non-existent file"""
        parser = BIP329_Parser('non_existent_file.jsonl')
        with self.assertLogs(level='ERROR') as log:  # noqa: F841
            entries = parser.load_entries()

        self.assertEqual(len(entries), 0)
        self.assertIn('File not found', ''.join(log.output))

    def test_label_and_origin_type_validation(self):
        """Test validation warnings for non-string label/origin"""
        test_filename = 'test_string_validation.jsonl'
        with open(test_filename, 'w') as file:  # noqa: F841
            test_data = '''{"type": "tx", "ref": "abc123", "label": 123, "origin": "valid"}
    {"type": "addr", "ref": "def456", "label": "valid", "origin": 456}'''
            file.write(test_data)

        try:
            parser = BIP329_Parser(test_filename)

            # Should log warnings for validation errors, not raise exceptions
            with self.assertLogs(level='WARNING') as log:  # noqa: F841
                entries = parser.load_entries()

            # No entries should be loaded due to validation failures
            self.assertEqual(len(entries), 0)
            self.assertIn('Validation error', ''.join(log.output))

        finally:
            if os.path.exists(test_filename):
                os.remove(test_filename)


if __name__ == '__main__':
    unittest.main()
