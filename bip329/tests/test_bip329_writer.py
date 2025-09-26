# file: test_bip329_writer.py
import unittest
import json
import os
from bip329.bip329_writer import BIP329JSONLWriter

class TestBIP329JSONLWriter(unittest.TestCase):
    def setUp(self):
        # Create a temporary file for testing
        self.test_filename = 'test_labels.jsonl'
        self.writer = BIP329JSONLWriter(self.test_filename)

    def tearDown(self):
        # Clean up the temporary file
        if os.path.exists(self.test_filename):
            os.remove(self.test_filename)

    def test_write_labels(self):
        # Example labels
        labels = [
            {"type": "tx", "ref": "f91d0a8a78462bc59398f2c5d7a84fcff491c26ba54c4833478b202796c8aafd",
                "label": "Transaction", "origin": "wpkh([d34db33f/84'/0'/0'])"},
            {"type": "addr", "ref": "bc1q34aq5drpuwy3wgl9lhup9892qp6svr8ldzyy7c",
                "label": "Address"},
            {"type": "pubkey", "ref": "0283409659355b6d1cc3c32decd5d561abaac86c37a353b52895a5e6c196d6f448",
                "label": "Public Key"},
            {"type": "input", "ref": "f91d0a8a78462bc59398f2c5d7a84fcff491c26ba54c4833478b202796c8aafd:0", "label": "Input"},
            {"type": "output", "ref": "f91d0a8a78462bc59398f2c5d7a84fcff491c26ba54c4833478b202796c8aafd:1",
                "label": "Output", "spendable": False},
            {"type": "output", "ref": "0000000078462bc59398f2c5d7a84fcff491c26ba54c4833478b202796c8aafd:1",
                "label": "Output", "spendable": True},
            {"type": "xpub", "ref": "xpub661MyMwAqRbcFtXgS5sYJABqqG9YLmC4Q1Rdap9gSE8NqtwybGhePY2gZ29ESFjqJoCu1Rupje8YtGqsefD265TMg7usUDFdp6W1EGMcet8",
                "label": "Extended Public Key"},
            {"type": "tx", "ref": "f546156d9044844e02b181026a1a407abfca62e7ea1159f87bbeaa77b4286c74",
                "label": "Account #1 Transaction", "origin": "wpkh([d34db33f/84'/0'/1'])"}
        ]

        # Write the labels using your BIP329JSONLWriter
        for label in labels:
            self.writer.write_label(label)

        # Read the written labels from the file and parse them
        written_labels = []
        with open(self.test_filename, 'r', encoding='utf-8') as file:
            for line in file:
                label = json.loads(line)
                written_labels.append(label)

        # Assert that the written labels match the expected labels
        self.assertEqual(written_labels, labels)

    def test_write_labels_with_optional_fields(self):
        """Test writing labels with optional fields"""
        labels = [
            {
                "type": "tx",
                "ref": "f91d0a8a78462bc59398f2c5d7a84fcff491c26ba54c4833478b202796c8aafd",
                "label": "Transaction with metadata",
                "height": 800000,
                "time": "2025-01-23T11:40:35Z",
                "fee": 1500,
                "value": -50000
            },
            {
                "type": "addr",
                "ref": "bc1q34aq5drpuwy3wgl9lhup9892qp6svr8ldzyy7c",
                "label": "Address with keypath",
                "keypath": "/1/123",
                "heights": [800000, 800001]
            },
            {
                "type": "output",
                "ref": "f91d0a8a78462bc59398f2c5d7a84fcff491c26ba54c4833478b202796c8aafd:1",
                "label": "Output with value",
                "spendable": True,
                "value": 25000,
                "fmv": {"USD": 1233.45}
            }
        ]

        # Write the labels
        for label in labels:
            self.writer.write_label(label)

        # Read and verify
        written_labels = []
        with open(self.test_filename, 'r', encoding='utf-8') as file:
            for line in file:
                label = json.loads(line)
                written_labels.append(label)

        # Verify all optional fields were preserved
        self.assertEqual(len(written_labels), 3)

        # Check first entry has all tx optional fields
        self.assertEqual(written_labels[0]['height'], 800000)
        self.assertEqual(written_labels[0]['time'], "2025-01-23T11:40:35Z")
        self.assertEqual(written_labels[0]['fee'], 1500)
        self.assertEqual(written_labels[0]['value'], -50000)

        # Check addr optional fields
        self.assertEqual(written_labels[1]['keypath'], "/1/123")
        self.assertEqual(written_labels[1]['heights'], [800000, 800001])

        # Check output optional fields
        self.assertEqual(written_labels[2]['value'], 25000)
        self.assertEqual(written_labels[2]['fmv'], {"USD": 1233.45})

    def test_write_labels_with_invalid_optional_fields(self):
        """Test writing labels with invalid optional field types"""
        labels = [
            {
                "type": "tx",
                "ref": "f91d0a8a78462bc59398f2c5d7a84fcff491c26ba54c4833478b202796c8aafd",
                "label": "Transaction with invalid fields",
                "height": "not_an_int",  # Invalid
                "fee": 1500,            # Valid
                "time": 12345           # Invalid type
            },
            {
                "type": "addr",
                "ref": "bc1q34aq5drpuwy3wgl9lhup9892qp6svr8ldzyy7c",
                "label": "Address with invalid fields",
                "keypath": "/1/123",    # Valid
                "heights": "not_a_list" # Invalid
            }
        ]

        # Should log warnings but still write records
        with self.assertLogs(level='WARNING') as log:
            for label in labels:
                self.writer.write_label(label)

        # Read and verify
        written_labels = []
        with open(self.test_filename, 'r', encoding='utf-8') as file:
            for line in file:
                label = json.loads(line)
                written_labels.append(label)

        # Both records should be written
        self.assertEqual(len(written_labels), 2)

        # Invalid fields should be removed, valid ones kept
        self.assertNotIn('height', written_labels[0])
        self.assertNotIn('time', written_labels[0])
        self.assertEqual(written_labels[0]['fee'], 1500)

        self.assertNotIn('heights', written_labels[1])
        self.assertEqual(written_labels[1]['keypath'], "/1/123")

        # Check warnings were logged
        log_output = ''.join(log.output)
        self.assertIn('Invalid height field type', log_output)
        self.assertIn('Invalid time field type', log_output)
        self.assertIn('Invalid heights field type', log_output)


    def test_field_validation_by_type_in_writer(self):
        """Test that writer validates fields by type and removes invalid ones"""
        labels = [
            {
                "type": "tx",
                "ref": "abc123",
                "label": "TX with invalid fields",
                "spendable": False,  # Invalid for tx - should be removed
                "heights": [1, 2, 3]  # Invalid for tx - should be removed
            }
        ]

        # Should log warnings about invalid fields
        with self.assertLogs(level='WARNING') as log:
            self.writer.write_label(labels[0])

        # Verify warnings were logged
        log_output = ''.join(log.output)
        self.assertIn("Field 'spendable' not valid for type 'tx', removing", log_output)
        self.assertIn("Field 'heights' not valid for type 'tx', removing", log_output)

        # Read and verify - invalid fields should be removed
        with open(self.test_filename, 'r') as file:
            written_label = json.loads(file.read().strip())

        # Invalid fields should NOT be present (fixed behavior)
        self.assertNotIn('spendable', written_label)
        self.assertNotIn('heights', written_label)

    def test_invalid_entry_types(self):
        """Test writer rejects invalid entry types"""
        invalid_label = {
            "type": "invalid_type",
            "ref": "abc123",
            "label": "Invalid Type"
        }

        with self.assertRaises(AssertionError):
            self.writer.write_label(invalid_label)

    def test_missing_mandatory_fields_in_writer(self):
        """Test writer rejects entries missing required fields"""
        invalid_labels = [
            # Remove the first one since {"type": "tx", "ref": "abc123"} is now valid (label is optional)
            {"ref": "def456", "label": "Missing type"},  # Missing type
            {"type": "addr", "label": "Missing ref"}  # Missing ref
        ]

        for invalid_label in invalid_labels:
            with self.assertRaises(ValueError) as context:
                self.writer.write_label(invalid_label)
            self.assertIn("Invalid BIP-329 record", str(context.exception))


    def test_spendable_field_validation(self):
        """Test spendable field validation behavior"""
        # These should work (writer accepts these)
        valid_spendable_values = [True, False]

        for valid_value in valid_spendable_values:
            label = {
                "type": "output",
                "ref": "abc123:1",
                "label": "Test",
                "spendable": valid_value
            }
            self.writer.write_label(label)  # Should not raise

        # This should fail (invalid type that writer rejects)
        invalid_label = {
            "type": "output",
            "ref": "abc123:1",
            "label": "Test",
            "spendable": "invalid_string"
        }

        with self.assertRaises(ValueError):
            self.writer.write_label(invalid_label)

    def test_origin_field_validation(self):
        """Test origin field validation"""
        # Valid origin
        valid_label = {
            "type": "tx",
            "ref": "abc123",
            "label": "Valid origin",
            "origin": "wpkh([d34db33f/84'/0'/0'])"
        }
        self.writer.write_label(valid_label)  # Should not raise

        # Invalid origins
        invalid_origins = [123, None, "", []]
        for invalid_origin in invalid_origins:
            label = {
                "type": "tx",
                "ref": "def456",
                "label": "Invalid origin",
                "origin": invalid_origin
            }

            with self.assertRaises(ValueError) as context:
                self.writer.write_label(label)
            self.assertIn("Invalid 'origin' field", str(context.exception))

    def test_write_object_style_labels(self):
        """Test writing labels using object-style access (callable methods)"""
        class MockLabel:
            def __init__(self, type_val, ref_val, label_val, **kwargs):
                self._type = type_val
                self._ref = ref_val
                self._label = label_val
                self._kwargs = kwargs

            def type(self): return self._type
            def ref(self): return self._ref
            def label(self): return self._label
            def origin(self): return self._kwargs.get('origin')

            # Fix: Only return spendable if it exists and has a valid value
            def spendable(self):
                value = self._kwargs.get('spendable')
                return value if value is not None else None

            # Add __contains__ method to make 'in' operator work
            def __contains__(self, key):
                return key in self._kwargs and self._kwargs[key] is not None

            # Add hasattr override to work with the writer's hasattr check
            def __getattribute__(self, name):
                if name == 'spendable':
                    # Only claim to have spendable if it has a valid value
                    spendable_val = self._kwargs.get('spendable')
                    if spendable_val is None:
                        raise AttributeError("'MockLabel' object has no attribute 'spendable'")
                    return lambda: spendable_val
                return super().__getattribute__(name)

        mock_label = MockLabel(
            "tx", "abc123", "Mock Transaction",
            origin="wpkh([d34db33f/84'/0'/0'])"
            # Note: no spendable value provided
        )

        self.writer.write_label(mock_label)

        # Verify it was written correctly
        with open(self.test_filename, 'r') as file:
            written_label = json.loads(file.read().strip())

        self.assertEqual(written_label['type'], 'tx')
        self.assertEqual(written_label['ref'], 'abc123')
        self.assertEqual(written_label['label'], 'Mock Transaction')
        self.assertEqual(written_label['origin'], "wpkh([d34db33f/84'/0'/0'])")
        # spendable should not be in output since it wasn't provided
        self.assertNotIn('spendable', written_label)

    def test_write_invalid_object_style(self):
        """Test writer rejects invalid object-style inputs"""
        class InvalidLabel:
            pass  # Missing required methods

        invalid_obj = InvalidLabel()

        with self.assertRaises(ValueError) as context:
            self.writer.write_label(invalid_obj)
        self.assertIn("Invalid BIP-329 record", str(context.exception))

    def test_remove_existing_behavior(self):
        """Test remove_existing parameter behavior"""
        # Create existing file
        existing_content = "existing data"
        with open(self.test_filename, 'w') as file:
            file.write(existing_content)

        # Test remove_existing=True (default)
        writer1 = BIP329JSONLWriter(self.test_filename, remove_existing=True)
        label = {"type": "tx", "ref": "abc123", "label": "Test"}
        writer1.write_label(label)

        with open(self.test_filename, 'r') as file:
            content = file.read()

        # Should not contain existing content
        self.assertNotIn(existing_content, content)
        self.assertIn('"label": "Test"', content)

    def test_backup_existing_file(self):
        """Test remove_existing=False creates backup"""
        # Create existing file
        existing_content = "existing data"
        with open(self.test_filename, 'w') as file:
            file.write(existing_content)

        # Test remove_existing=False
        writer2 = BIP329JSONLWriter(self.test_filename, remove_existing=False)  # noqa: F841

        # Check backup was created
        backup_files = [f for f in os.listdir('.') if f.startswith(self.test_filename) and f.endswith('.bak')]
        self.assertEqual(len(backup_files), 1)

        # Clean up backup
        os.remove(backup_files[0])

        if os.path.exists(self.test_filename):
            os.remove(self.test_filename)

    def test_field_type_validation(self):
        """Test that writer logs warnings for invalid optional field types"""
        invalid_label = {
            "type": "tx",
            "ref": "abc123",
            "label": "Test",
            "height": "not_an_int",  # should be int
            "fee": "1500"  # should be int
        }

        # Should log warnings, not raise exceptions
        with self.assertLogs(level='WARNING') as log:
            self.writer.write_label(invalid_label)

        # Check that warnings were logged
        log_output = ''.join(log.output)
        self.assertIn('Invalid height field type', log_output)
        self.assertIn('Invalid fee field type', log_output)

        # Verify the label was written but invalid fields were removed
        with open(self.test_filename, 'r') as file:
            written_label = json.loads(file.read().strip())

        self.assertEqual(written_label['type'], 'tx')
        self.assertEqual(written_label['ref'], 'abc123')
        self.assertEqual(written_label['label'], 'Test')
        # Invalid fields should be removed
        self.assertNotIn('height', written_label)
        self.assertNotIn('fee', written_label)

    def test_writer_field_validation_by_type(self):
        """Test that writer validates fields by entry type"""
        writer = BIP329JSONLWriter(self.test_filename)

        # This should log warnings and remove invalid fields
        with self.assertLogs(level='WARNING') as log:
            writer.write_label({
                "type": "tx",
                "ref": "abc123",
                "label": "TX with invalid fields",
                "spendable": False,  # Invalid for tx
                "heights": [1, 2, 3]  # Invalid for tx
            })

        # Verify warnings were logged
        log_output = ''.join(log.output)
        self.assertIn("not valid for type", log_output)

        # Verify invalid fields were removed
        with open(self.test_filename, 'r') as f:
            written_label = json.loads(f.read().strip())

        self.assertNotIn('spendable', written_label)
        self.assertNotIn('heights', written_label)

    def test_rate_field_edge_cases(self):
        """Test rate field validation edge cases"""
        from bip329.validation_utils import validate_rate_field

        # Valid cases
        self.assertTrue(validate_rate_field({"USD": 100.50}))
        self.assertTrue(validate_rate_field({"USD": 100, "EUR": 85.25}))

        # Invalid cases
        self.assertFalse(validate_rate_field({}))  # Empty dict
        self.assertFalse(validate_rate_field({"FOO": 100}))  # Invalid currency
        self.assertFalse(validate_rate_field({"USD": -100}))  # Negative value
        self.assertFalse(validate_rate_field({"USD": 0}))  # Zero value
        self.assertFalse(validate_rate_field({"USD": "100"}))  # String value

    def test_concurrent_operations(self):
        """Test behavior with concurrent file operations"""
        import threading
        import time

        def write_labels(thread_id):
            filename = f'concurrent_test_{thread_id}.jsonl'
            try:
                writer = BIP329JSONLWriter(filename)
                for i in range(10):
                    writer.write_label({
                        "type": "tx",
                        "ref": f"tx_{thread_id}_{i}",
                        "label": f"Thread {thread_id} TX {i}"
                    })
                    time.sleep(0.001)  # Small delay to encourage race conditions
            finally:
                if os.path.exists(filename):
                    os.remove(filename)

        # Start multiple threads writing to different files
        threads = []
        for i in range(3):
            t = threading.Thread(target=write_labels, args=(i,))
            threads.append(t)
            t.start()

        # Wait for all threads to complete
        for t in threads:
            t.join()
        # Test passes if no exceptions were raised

    def test_label_truncation_option(self):
        """Test label truncation option in writer"""
        writer_truncate = BIP329JSONLWriter(self.test_filename, truncate_labels=True)
        long_label = "A" * 300

        with self.assertLogs(level='WARNING') as log:
            writer_truncate.write_label({
                "type": "tx",
                "ref": "abc123",
                "label": long_label
            })

        # Should log truncation warning
        self.assertIn('truncated', ''.join(log.output))

        # Verify label was truncated to 255 chars
        with open(self.test_filename, 'r') as f:
            written_label = json.loads(f.read().strip())

        self.assertEqual(len(written_label['label']), 255)

if __name__ == '__main__':
    unittest.main()
