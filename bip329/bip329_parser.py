import json

class BIP329_Parser:
    def __init__(self, jsonl_path):
        self.jsonl_path = jsonl_path
        self.entries = []

    def load_entries(self):
        self.entries = []
        with open(self.jsonl_path, 'r') as file:
            for line in file:
                try:
                    entry = json.loads(line.strip())
                    if self.is_valid_entry(entry):
                        self.entries.append(entry)
                except json.JSONDecodeError:
                    print(f"Skipping invalid JSON line: {line.strip()}")
        return self.entries

    @staticmethod
    def is_valid_entry(entry):
        required_keys = {'type', 'ref'}
        valid_types = {'tx', 'addr', 'pubkey', 'input', 'output', 'xpub'}

        if not required_keys.issubset(entry.keys()):
            return False

        if 'type' not in entry or entry['type'] not in valid_types:
            return False

        if entry['type'] == 'output':
            if 'spendable' in entry and entry['spendable'] not in {'true', 'false', True, False}:
                return False

        if 'ref' not in entry:
            return False

        if 'label' in entry and not isinstance(entry['label'], str):
            return False

        if 'origin' in entry and not isinstance(entry['origin'], str):
            #TODO: Verify origin
            return False

        return entry
