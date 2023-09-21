import py7zr
import hashlib
import os


def encrypt_files(output_archive, files_to_encrypt, passphrase):
    # Hash the passphrase using SHA256
    # Convert bytes to a hexadecimal string
    key = hashlib.sha256(passphrase.encode()).hexdigest()
    # Create the 7z archive with AES-256 encryption containing the specified files
    with py7zr.SevenZipFile(output_archive, 'w', password=key) as archive:
        for file_to_encrypt in files_to_encrypt:
            archive.write(file_to_encrypt,
                          arcname=os.path.basename(file_to_encrypt))


def decrypt_files(archive_path, output_dir, passphrase):
    # Convert the bytes passphrase to a string
    key = hashlib.sha256(passphrase.encode()).hexdigest()
    # Open the 7z archive for decryption
    with py7zr.SevenZipFile(archive_path, mode='r', password=key) as archive:
        # Extract the contents of the archive to the specified output directory
        archive.extractall(path=output_dir)


"""
# Example usage:

files_to_encrypt = ["/tmp/labels-01.jsonl", "/tmp/labels-02.jsonl", "/tmp/labels-XX.jsonl"]  # List of files to encrypt

encrypted_archive = "/tmp/encrypted-bip329-labels.7z"
output_directory = "/home/satohsi/"  # Replace with your desired output directory path
passphrase = b"your_secret_passphrase"  # Replace with your passphrase

# Encrypt the specified label files into an archive
encrypt_files(encrypted_archive, files_to_encrypt, passphrase)

# Decrypt the encrypted archive into the specified output directory
decrypt_files(encrypted_archive, output_directory, passphrase)

"Export Encrypted"
"Import Encrypted"


"""
