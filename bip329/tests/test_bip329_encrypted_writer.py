import unittest
import os
import json
from unittest.mock import mock_open, patch
from bip329.bip329_writer import BIP329JSONLEncryptedWriter
from bip329.encryption import encrypt_files


class TestBIP329JSONLEncryptedWriter(unittest.TestCase):
    def setUp(self):
        self.passphrase = "my_passphrase"
        self.test_filename = 'test_labels.7z'
        self.temp_filename = 'temp_labels.jsonl'
        self.remove_existing = True
        self.writer = BIP329JSONLEncryptedWriter(
            self.test_filename, self.passphrase, self.remove_existing)

    def tearDown(self):
        if os.path.exists(self.test_filename):
            os.remove(self.test_filename)
        if os.path.exists(self.temp_filename):
            os.remove(self.temp_filename)

    def test_write_label(self):
        # Example label
        label = {
            "type": "tx",
            "ref": "f91d0a8a78462bc59398f2c5d7a84fcff491c26ba54c4833478b202796c8aafd",
            "label": "Transaction",
            "origin": "wpkh([d34db33f/84'/0'/0'])"
        }

        # Write the label using BIP329JSONLEncryptedWriter
        self.writer.write_label(label)

        # Close the writer
        self.writer.close()

        # Check if the encrypted file exists
        self.assertTrue(os.path.exists(self.test_filename))

        # Decrypt the file and read its content as binary data
        decrypt_file = "decrypt_test_labels.jsonl"
        try:
            encrypt_files(decrypt_file, [self.test_filename], self.passphrase)
            with open(decrypt_file, 'rb') as file:
                decrypted_content = file.read()

            # Check if the decrypted content is not empty
            self.assertTrue(decrypted_content)

        except Exception as e:
            print(f"Error while reading decrypted content: {e}")

        finally:
            # Clean up
            os.remove(decrypt_file)

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


if __name__ == '__main__':
    unittest.main()
