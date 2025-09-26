# file: test_encryption.py
import os
import shutil
import tempfile
import unittest
from bip329.encryption import encrypt_files
from bip329.encryption import decrypt_files


class TestEncryption(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.temp_out = tempfile.mkdtemp()

        self.input_file = os.path.join(self.temp_dir, 'test.txt')
        self.output_archive = os.path.join(self.temp_dir, 'test.7z')
        self.passphrase = "secret_passphrase"
        self._msg = "Buy more bitcoin"

        # Create a test file with some content
        with open(self.input_file, 'w', encoding='utf-8') as f:
            f.write(self._msg)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)
        shutil.rmtree(self.temp_out)

    def test_encrypt_and_decrypt(self):
        # Encrypt the file
        encrypt_files(self.output_archive, [self.input_file], self.passphrase)

        # Ensure that the encrypted file exists
        self.assertTrue(os.path.exists(self.output_archive))

        # Decrypt the file
        decrypt_files(self.output_archive, self.temp_out, self.passphrase)

        # Ensure that the decrypted file exists
        decrypted_file = os.path.join(self.temp_out, 'test.txt')
        self.assertTrue(os.path.exists(decrypted_file))

        # Verify the content of the decrypted file
        with open(decrypted_file, 'r', encoding='utf-8') as f:
            decrypted_content = f.read()

        self.assertEqual(decrypted_content, self._msg)

    def test_wrong_passphrase_decryption(self):
        """Test that wrong passphrase fails decryption"""
        # Encrypt with correct passphrase
        encrypt_files(self.output_archive, [self.input_file], self.passphrase)

        # Try to decrypt with wrong passphrase
        with self.assertRaises(Exception):
            decrypt_files(self.output_archive, self.temp_out, "wrong_passphrase")

    def test_encrypt_nonexistent_file(self):
        """Test encrypting a file that doesn't exist"""
        nonexistent_file = os.path.join(self.temp_dir, 'nonexistent.txt')

        with self.assertRaises(FileNotFoundError):
            encrypt_files(self.output_archive, [nonexistent_file], self.passphrase)

    def test_decrypt_nonexistent_archive(self):
        """Test decrypting an archive that doesn't exist"""
        nonexistent_archive = os.path.join(self.temp_dir, 'nonexistent.7z')

        with self.assertRaises(FileNotFoundError):
            decrypt_files(nonexistent_archive, self.temp_out, self.passphrase)

    def test_encrypt_multiple_files(self):
        """Test encrypting multiple files in one archive"""
        # Create multiple test files
        file1 = os.path.join(self.temp_dir, 'file1.txt')
        file2 = os.path.join(self.temp_dir, 'file2.txt')

        with open(file1, 'w', encoding='utf-8') as f:
            f.write("Content of file 1")
        with open(file2, 'w', encoding='utf-8') as f:
            f.write("Content of file 2")

        # Encrypt both files
        encrypt_files(self.output_archive, [file1, file2], self.passphrase)

        # Decrypt and verify both files exist
        decrypt_files(self.output_archive, self.temp_out, self.passphrase)

        decrypted_file1 = os.path.join(self.temp_out, 'file1.txt')
        decrypted_file2 = os.path.join(self.temp_out, 'file2.txt')

        self.assertTrue(os.path.exists(decrypted_file1))
        self.assertTrue(os.path.exists(decrypted_file2))

        # Verify content
        with open(decrypted_file1, 'r', encoding='utf-8') as f:
            self.assertEqual(f.read(), "Content of file 1")
        with open(decrypted_file2, 'r', encoding='utf-8') as f:
            self.assertEqual(f.read(), "Content of file 2")

    def test_empty_file_encryption(self):
        """Test encrypting an empty file"""
        empty_file = os.path.join(self.temp_dir, 'empty.txt')
        with open(empty_file, 'w', encoding='utf-8') as f:
            pass  # Create empty file

        encrypt_files(self.output_archive, [empty_file], self.passphrase)
        decrypt_files(self.output_archive, self.temp_out, self.passphrase)

        decrypted_file = os.path.join(self.temp_out, 'empty.txt')
        self.assertTrue(os.path.exists(decrypted_file))

        with open(decrypted_file, 'r', encoding='utf-8') as f:
            content = f.read()
        self.assertEqual(content, "")

    def test_large_file_encryption(self):
        """Test encrypting a larger file"""
        large_content = "A" * 10000  # 10KB of 'A's
        large_file = os.path.join(self.temp_dir, 'large.txt')

        with open(large_file, 'w', encoding='utf-8') as f:
            f.write(large_content)

        encrypt_files(self.output_archive, [large_file], self.passphrase)
        decrypt_files(self.output_archive, self.temp_out, self.passphrase)

        decrypted_file = os.path.join(self.temp_out, 'large.txt')
        with open(decrypted_file, 'r', encoding='utf-8') as f:
            decrypted_content = f.read()

        self.assertEqual(len(decrypted_content), 10000)
        self.assertEqual(decrypted_content, large_content)

    def test_special_characters_in_content(self):
        """Test encrypting files with special characters"""
        special_content = "Special chars: àáâãäåæçèéêë 中文 🚀 \n\t\r"
        special_file = os.path.join(self.temp_dir, 'special.txt')

        with open(special_file, 'w', encoding='utf-8') as f:
            f.write(special_content)

        encrypt_files(self.output_archive, [special_file], self.passphrase)
        decrypt_files(self.output_archive, self.temp_out, self.passphrase)

        decrypted_file = os.path.join(self.temp_out, 'special.txt')
        with open(decrypted_file, 'r', encoding='utf-8') as f:
            decrypted_content = f.read()

        # Normalize line endings for comparison since they may get converted
        expected_normalized = special_content.replace('\r\n', '\n').replace('\r', '\n')
        actual_normalized = decrypted_content.replace('\r\n', '\n').replace('\r', '\n')

        self.assertEqual(actual_normalized, expected_normalized)

    def test_different_passphrase_types(self):
        """Test encryption with different passphrase formats"""
        test_cases = [
            "simple",
            "complex_P@ssw0rd!",
            "very long passphrase with spaces and numbers 123456789",
            "短密码",  # 'short password' in Chinese (based on deepl.)
            ""  # Empty passphrase
        ]

        for i, passphrase in enumerate(test_cases):
            with self.subTest(passphrase=passphrase):
                archive_name = f"test_{i}.7z"
                archive_path = os.path.join(self.temp_dir, archive_name)

                encrypt_files(archive_path, [self.input_file], passphrase)

                temp_out_sub = tempfile.mkdtemp()
                try:
                    decrypt_files(archive_path, temp_out_sub, passphrase)

                    decrypted_file = os.path.join(temp_out_sub, 'test.txt')
                    with open(decrypted_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    self.assertEqual(content, self._msg)
                finally:
                    shutil.rmtree(temp_out_sub)

    def test_archive_is_encrypted(self):
        """Test that the archive is actually encrypted (not plaintext)"""
        encrypt_files(self.output_archive, [self.input_file], self.passphrase)

        # Read the archive as binary and ensure it doesn't contain plaintext
        with open(self.output_archive, 'rb') as f:
            archive_content = f.read()

        # The original message should not appear in the encrypted archive
        self.assertNotIn(self._msg.encode('utf-8'), archive_content)

        # Should be a valid 7z file (starts with 7z signature)
        self.assertTrue(archive_content.startswith(b'7z\xbc\xaf\x27\x1c'))

if __name__ == '__main__':
    unittest.main()
