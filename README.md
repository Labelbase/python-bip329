# BIP-329 Python Library

**BIP-329** is a Bitcoin Improvement Proposal that defines a standardized format for exporting, importing, and syncing Bitcoin wallet labels.

This Python library provides a set of tools for working with BIP-329 compliant label files.

Whether you want to **parse**, **write**, **write encrypted**, or **decrypt** BIP-329 labels, this library has you covered.

## Installation

You can install the `python-bip329` library using pip:

`pip install python-bip329`



## Usage

### Parsing BIP-329 Label Files

The `BIP329_Parser` class allows you to parse BIP-329 label files. Here's an example of how to use it:

```python
from bip329.bip329_parser import BIP329_Parser

# Specify the path to your BIP-329 label file
filename = "/path/to/bip-329-labels.jsonl"

# Create a BIP329_Parser instance
parser = BIP329_Parser(filename)

# Load and parse the entries from the label file
entries = parser.load_entries()

# Iterate through the parsed entries
for entry in entries:
    print(entry)
```

### Writing BIP-329 Label Files

To write BIP-329 label files, you can use the `BIP329JSONLWriter class. This class allows you to create or overwrite BIP-329 label files. You can choose whether to remove existing files or create backups when necessary. Here's an example:

```python
from bip329.bip329_writer import BIP329JSONLWriter

# Specify the filename for the BIP-329 label file
filename = "/path/to/bip-329-labels.jsonl"

# Create a BIP329JSONLWriter instance
label_writer = BIP329JSONLWriter(filename, remove_existing=True)

# Write a BIP-329 label entry (replace with your label data)
label_entry = {
    "type": "tx",
    "ref": "transaction_id",
    "label": "Transaction Label"
}

# Write the label entry to the file
label_writer.write_label(label_entry)

# Close the writer when finished
label_writer.close()
```



### Encrypting BIP-329 Label Files

If you want to encrypt your BIP-329 label files, you can use the `BIP329JSONLEncryptedWriter` class.

This class allows you to create encrypted BIP-329 label files.

You can also choose whether to remove existing files or create backups when necessary.

Here's an example:


```python
from bip329.bip329_writer import BIP329JSONLEncryptedWriter

# Specify the filename for the encrypted BIP-329 label file
encrypted_filename = "/path/to/encrypted-bip-329-labels.7z"

# Specify your passphrase for encryption (replace with your passphrase)
passphrase = "your_secret_passphrase"

# Create a BIP329JSONLEncryptedWriter instance
encrypted_writer = BIP329JSONLEncryptedWriter(encrypted_filename, passphrase, remove_existing=True)

# Write a BIP-329 label entry (replace with your label data)
label_entry = {
    "type": "tx",
    "ref": "transaction_id",
    "label": "Transaction Label"
}

# Write the label entry to the encrypted file
encrypted_writer.write_label(label_entry)

# Close the encrypted writer when finished
encrypted_writer.close()

```


### Decrypting BIP-329 Label Files

To decrypt encrypted BIP-329 label files, you can use the decrypt_files function from the library.

Provide the path to the encrypted file, the output directory, and the passphrase used for encryption.

Here's an example:

```python
from bip329.bip329_writer import decrypt_files

# Specify the path to the encrypted BIP-329 label file
encrypted_file = "/path/to/encrypted-bip-329-labels.7z"

# Specify the output directory for decrypted files
output_directory = "/path/to/output_directory"

# Specify your passphrase for decryption (replace with your passphrase)
passphrase = "your_secret_passphrase"

# Decrypt the encrypted file into the output directory
decrypt_files(encrypted_file, output_directory, passphrase)
```

Please replace the placeholders with your actual file paths and data as needed.

## Running Tests

To ensure the correctness of the library, you can run the provided unit tests.



---

## Disclaimer

This project is provided "as-is," without any express or implied warranty. In no event shall the authors or contributors be held liable for any damages arising from the use of this software.

This project may contain bugs, and its functionality may not always meet your requirements. You are responsible for assessing its suitability for your use case.

Contributions to this project are welcomed and encouraged, but they may not always be accepted, and the maintainers retain the right to make decisions about code contributions.

By using this project, you agree to accept all risks associated with its use, and you agree not to hold the authors, contributors, or maintainers responsible for any issues that may arise.

## Notes


* If you encounter any issues or have questions about the library, please feel free to open an issue on this GitHub repository.
* We welcome contributions and feedback from the community.
*
