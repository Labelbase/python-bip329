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


if __name__ == '__main__':
    unittest.main()
