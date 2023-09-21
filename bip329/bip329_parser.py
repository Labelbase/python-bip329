import json
import logging
from .constants import VALID_SPENDABLE_VALUES
from .constants import VALID_REQUIRED_KEYS
from .constants import VALID_TYPE_KEYS
from .constants import MANDATORY_KEYS_ERROR


class BIP329_Parser:
    def __init__(self, jsonl_path):
        self.jsonl_path = jsonl_path
        self.entries = []

    def load_entries(self):
        self.entries = []
        line_number = 0  # Track line numbers for error reporting
        try:
            with open(self.jsonl_path, 'r') as file:
                for line in file:
                    line_number += 1
                    entry = json.loads(line.strip())
                    if self.is_valid_entry(entry):
                        self.entries.append(entry)
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing JSON at line {line_number}: {e}")
        except Exception as e:
            logging.error(f"Error reading file: {e}")
        return self.entries

    @staticmethod
    def is_valid_entry(entry):
        if not all(key in entry for key in VALID_REQUIRED_KEYS):
            raise MANDATORY_KEYS_ERROR

        if entry['type'] not in VALID_TYPE_KEYS:
            return False

        if entry['type'] == 'output':
            if 'spendable' in entry and entry['spendable'] not in VALID_SPENDABLE_VALUES:
                return False

        if 'label' in entry and not isinstance(entry['label'], str):
            return False

        if 'origin' in entry and not isinstance(entry['origin'], str):
            # TODO: Verify origin
            return False

        return True
