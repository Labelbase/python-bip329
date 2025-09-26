# file: test_bip329_encrypted_writer.py
import unittest
import os
import json
import tempfile
from unittest.mock import mock_open, patch
from bip329.bip329_writer import BIP329JSONLEncryptedWriter
from bip329.encryption import encrypt_files
from bip329.encryption import decrypt_files


class TestBIP329JSONLEncryptedWriter(unittest.TestCase):
    def setUp(self):
        self.passphrase = "my_passphrase"
        self.test_filename = 'test_labels.7z'
        self.temp_filename = 'temp_labels.jsonl'
        self.remove_existing = True
        self.writer = BIP329JSONLEncryptedWriter(
            self.test_filename, self.passphrase, self.remove_existing)
        self.created_files = [self.test_filename]

    def tearDown(self):
        # Clean up the writer if still open
        if hasattr(self.writer, 'temp_file') and not self.writer.is_closed:
            try:
                self.writer.close()
            except:
                pass

        # Clean up all test files
        test_files = [self.test_filename, self.temp_filename] + getattr(self, 'created_files', [])
        for filename in test_files:
            if os.path.exists(filename):
                try:
                    os.remove(filename)
                except:
                    pass

    def test_write_label(self):
        # Example label
        label = {
            "type": "tx",
            "ref": "f91d0a8a78462bc59398f2c5d7a84fcff491c26ba54c4833478b202796c8aafd",
            "label": "Transaction",
            "origin": "wpkh([d34db33f/84'/0'/0'])"
        }

        self.writer.write_label(label)
        self.writer.close()

        # Check if the encrypted file exists
        self.assertTrue(os.path.exists(self.test_filename))

        with tempfile.TemporaryDirectory() as temp_dir:
            decrypt_files(self.test_filename, temp_dir, self.passphrase)

            # Find the decrypted file (should match original temp file basename)
            decrypted_files = os.listdir(temp_dir)
            self.assertEqual(len(decrypted_files), 1)

            decrypted_file_path = os.path.join(temp_dir, decrypted_files[0])
            with open(decrypted_file_path, 'r', encoding='utf-8') as file:
                decrypted_content = file.read().strip()

            # Verify the content matches what we wrote
            expected_json = json.dumps(label)
            self.assertEqual(decrypted_content, expected_json)

    def test_existing_file(self):
        # Create a temporary file for testing
        with open(self.temp_filename, 'w', encoding='utf-8') as file:
            file.write("Some data")

        # Create the writer with remove_existing set to False
        writer = BIP329JSONLEncryptedWriter(
            self.temp_filename, self.passphrase, remove_existing=False)

        # Check if the existing file was moved to a backup location
        self.assertTrue(os.path.exists(writer.backup_filename))

        # Clean up
        os.remove(writer.backup_filename)

    def test_existing_file_removal(self):
        # Create a temporary file for testing
        with open(self.temp_filename, 'w', encoding='utf-8') as file:
            file.write("Some data")

        # Create the writer with remove_existing set to True
        BIP329JSONLEncryptedWriter(
            self.temp_filename, self.passphrase, remove_existing=True)

        # Check if the existing file was removed
        self.assertFalse(os.path.exists(self.temp_filename))

    def test_write_multiple_labels(self):
        """Test writing multiple labels to encrypted file"""
        labels = [
            {"type": "tx", "ref": "abc123", "label": "First Transaction"},
            {"type": "addr", "ref": "bc1q...", "label": "My Address"},
            {"type": "output", "ref": "def456:1", "label": "Change Output", "spendable": False}
        ]

        for label in labels:
            self.writer.write_label(label)
        self.writer.close()

        # Decrypt and verify all labels were written
        with tempfile.TemporaryDirectory() as temp_dir:
            decrypt_files(self.test_filename, temp_dir, self.passphrase)
            decrypted_file = os.path.join(temp_dir, os.listdir(temp_dir)[0])

            with open(decrypted_file, 'r') as file:
                lines = file.readlines()

            self.assertEqual(len(lines), 3)
            for i, line in enumerate(lines):
                parsed_label = json.loads(line.strip())
                self.assertEqual(parsed_label['type'], labels[i]['type'])
                self.assertEqual(parsed_label['label'], labels[i]['label'])

    def test_invalid_passphrase_decryption(self):
        """Test that wrong passphrase fails decryption"""
        label = {"type": "tx", "ref": "abc123", "label": "Test"}
        self.writer.write_label(label)
        self.writer.close()

        with tempfile.TemporaryDirectory() as temp_dir:
            with self.assertRaises(Exception):
                decrypt_files(self.test_filename, temp_dir, "wrong_passphrase")

    def test_writer_with_optional_fields(self):
        """Test writing labels with optional fields"""
        label = {
            "type": "tx",
            "ref": "abc123",
            "label": "Transaction with extras",
            "height": 800000,
            "time": "2025-01-23T11:40:35Z",
            "fee": 1500,
            "value": -50000
        }

        self.writer.write_label(label)
        self.writer.close()

        with tempfile.TemporaryDirectory() as temp_dir:
            decrypt_files(self.test_filename, temp_dir, self.passphrase)
            decrypted_file = os.path.join(temp_dir, os.listdir(temp_dir)[0])

            with open(decrypted_file, 'r') as file:
                written_label = json.loads(file.read().strip())

            # Verify all fields were preserved
            for key, value in label.items():
                self.assertEqual(written_label[key], value)

    def test_empty_file_encryption(self):
        """Test encrypting a file with no labels"""
        # Don't close immediately - the temp file needs to exist
        # Instead, just ensure temp file is written (even if empty)
        self.writer.temp_file.flush()  # Ensure any buffered content is written
        self.writer.close()
        self.assertTrue(os.path.exists(self.test_filename))

        with tempfile.TemporaryDirectory() as temp_dir:
            decrypt_files(self.test_filename, temp_dir, self.passphrase)
            decrypted_files = os.listdir(temp_dir)
            self.assertEqual(len(decrypted_files), 1)
            decrypted_file = os.path.join(temp_dir, decrypted_files[0])
            with open(decrypted_file, 'r') as file:
                content = file.read()
            self.assertEqual(content.strip(), "")

    def test_write_after_close_raises_exception(self):
        """Test that writing after close raises an exception"""
        label = {"type": "tx", "ref": "abc123", "label": "stack more sats"}
        # Write something first so temp file exists..
        self.writer.write_label(label)
        self.writer.close()

        # Now try to write after close
        with self.assertRaises(Exception) as context:
            self.writer.write_label(label)

        self.assertIn("Writer is closed", str(context.exception))

if __name__ == '__main__':
    unittest.main()
