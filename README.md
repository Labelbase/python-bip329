# BIP-329 Parser

A Python parser for handling [BIP-329](https://github.com/bitcoin/bips/blob/master/bip-0329.mediawiki) JSONP files, designed to efficiently read, validate, and process JSON lines following the BIP-329 specification.

## Overview

[BIP-329](https://github.com/bitcoin/bips/blob/master/bip-0329.mediawiki) (Bitcoin Improvement Proposal 329) defines a lightweight, human-readable, and well-structured format for exporting, importing and syncing labels.


## Features

- Read and parse BIP-329 JSONP files.
- Validates entries according to the BIP-329 specification.
- Supports both required and optional key-value pairs.
- Ensures that "spendable" is only checked when "type" is "output."
- Easy-to-use Python class for integration into your projects.

## Installation

You can install the BIP-329 JSONP Parser using pip:

```bash
pip install python-bip329 (not pushed to PyPI yet!)
```

## Usage

```python
from bip329_parser import BIP329_Parser
filename = "/Users/satoshi/bip-329-labels.jsonp"
parser = BIP329_Parser(filename)
entries = parser.load_entries()
for entry in entries:
    print(entry)
```
