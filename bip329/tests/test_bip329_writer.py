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
                "label": "Output", "spendable": "false"},
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


if __name__ == '__main__':
    unittest.main()
