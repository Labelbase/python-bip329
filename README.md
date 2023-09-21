# BIP-329 Python Library

**BIP-329** is a Bitcoin Improvement Proposal that defines a standardized format for exporting, importing, and syncing Bitcoin wallet labels. This Python library provides a set of tools for working with BIP-329 compliant label files. Whether you want to parse, write, encrypt, or decrypt BIP-329 labels, this library has you covered.

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

To write BIP-329 label files, you can use the BIP329JSONLWriter class. This class allows you to create or overwrite BIP-329 label files. You can choose whether to remove existing files or create backups when necessary. Here's an example:
