import unittest
import os
from bip329.bip329_parser import BIP329_Parser


class TestBIP329Parser(unittest.TestCase):
    def setUp(self):
        # Create a temporary JSONL file with the test vector data
        self.test_filename = 'test_labels.jsonl'
        with open(self.test_filename, 'w') as file:
            test_vector = '''{"type": "tx", "ref": "f91d0a8a78462bc59398f2c5d7a84fcff491c26ba54c4833478b202796c8aafd", "label": "Transaction", "origin": "wpkh([d34db33f/84'/0'/0'])"}
{"type": "addr", "ref": "bc1q34aq5drpuwy3wgl9lhup9892qp6svr8ldzyy7c", "label": "Address"}
{"type": "pubkey", "ref": "0283409659355b6d1cc3c32decd5d561abaac86c37a353b52895a5e6c196d6f448", "label": "Public Key"}
{"type": "input", "ref": "f91d0a8a78462bc59398f2c5d7a84fcff491c26ba54c4833478b202796c8aafd:0", "label": "Input"}
{"type": "output", "ref": "f91d0a8a78462bc59398f2c5d7a84fcff491c26ba54c4833478b202796c8aafd:1", "label": "Output", "spendable": "false"}
{"type": "xpub", "ref": "xpub661MyMwAqRbcFtXgS5sYJABqqG9YLmC4Q1Rdap9gSE8NqtwybGhePY2gZ29ESFjqJoCu1Rupje8YtGqsefD265TMg7usUDFdp6W1EGMcet8", "label": "Extended Public Key"}
{"type": "tx", "ref": "f546156d9044844e02b181026a1a407abfca62e7ea1159f87bbeaa77b4286c74", "label": "Account #1 Transaction", "origin": "wpkh([d34db33f/84'/0'/1'])"}'''
            file.write(test_vector)

    def tearDown(self):
        # Clean up the temporary JSONL file
        if os.path.exists(self.test_filename):
            os.remove(self.test_filename)

    def test_load_entries(self):
        parser = BIP329_Parser(self.test_filename)
        entries = parser.load_entries()

        # Assert that the loaded entries match the expected entries
        expected_entries = [
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

        self.assertEqual(entries, expected_entries)


if __name__ == '__main__':
    unittest.main()
