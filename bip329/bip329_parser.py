# file: bip329_parser.py
import json
import logging
from datetime import datetime
from .constants import BOOL_KEYS
from .constants import VALID_REQUIRED_KEYS
from .constants import VALID_TYPE_KEYS
from .constants import VALID_FIELDS_BY_TYPE
from .constants import MANDATORY_KEYS_ERROR
from .constants import OPTIONAL_FIELDS
from .validation_utils import validate_rate_field
from .validation_utils import validate_fmv_field
from .validation_utils import validate_iso8601_time
from .validation_utils import validate_label_length
from .validation_utils import validate_utf8_encoding

class BIP329_Parser:
    def __init__(self, jsonl_path, allow_boolsy=False, replace_non_utf8=False):
        self.jsonl_path = jsonl_path
        self.allow_boolsy = allow_boolsy
        self.replace_non_utf8 = replace_non_utf8
        self.entries = []

    def load_entries(self):
        self.entries = []
        line_number = 0 # Track line numbers for error reporting
        try:
            with open(self.jsonl_path, 'r') as file:
                for line in file:
                    line_number += 1
                    if not line.strip():
                        continue
                    try:
                        entry = json.loads(line.strip())
                    except json.JSONDecodeError as e:
                        logging.warning(f"Malformed JSON at line {line_number}: {e}")
                        continue
                    try:
                        if self.is_valid_entry(entry):
                            self.entries.append(entry)
                    except (TypeError, ValueError) as validation_error:
                        # Log validation errors but continue processing other entries
                        logging.warning(f"Validation error at line {line_number}: {validation_error}")
                        continue
        except json.JSONDecodeError as e:
            logging.error(f"Error parsing JSON at line {line_number}: {e}")
        except FileNotFoundError as e:
            logging.error(f"File not found: {e}")
        except Exception as e:
            logging.error(f"Error reading file: {e}")
        return self.entries


    def is_valid_entry(self, entry):
        if not all(key in entry for key in VALID_REQUIRED_KEYS):
            raise MANDATORY_KEYS_ERROR

        if entry['type'] not in VALID_TYPE_KEYS:
            # silently drop record types we don't understand
            return False

        if 'label' in entry:
            if not isinstance(entry['label'], str):
                raise TypeError('label must be string')
            validate_label_length(entry['label'])

        # Get valid fields for this entry type and remove invalid ones
        valid_fields = VALID_FIELDS_BY_TYPE[entry['type']]
        fields_to_remove = []
        for field_name in entry.keys():
            if field_name not in valid_fields:
                logging.warning(f"Field '{field_name}' not valid for type '{entry['type']}', removing")
                fields_to_remove.append(field_name)

        for field_name in fields_to_remove:
            del entry[field_name]

        # handle boolean, incl. boolsy values
        for k in list(entry.keys()):
            if k in BOOL_KEYS:
                v = entry[k]
                if isinstance(v, bool):
                    continue  # Already correct JSON boolean
                elif self.allow_boolsy:
                    # Extended boolean conversion for practical use
                    if isinstance(v, (int, float)):
                        entry[k] = bool(v)
                    elif isinstance(v, str):
                        lv = v.strip().lower()
                        if lv in ("true", "1", "yes", "y"):
                            entry[k] = True
                        elif lv in ("false", "0", "no", "n"):
                            entry[k] = False
                        elif lv == "":
                           logging.info(f"Empty string for {k} converted to False")
                           entry[k] = False
                        else:
                            logging.warning(f"Invalid boolean string for {k}: {v}")
                            del entry[k]
                    elif v is None:
                        entry[k] = False
                    else:
                        logging.warning(f"Invalid boolean type for {k}: {type(v).__name__}")
                        del entry[k]
                else:
                    # Strict BIP-329: only accept JSON booleans
                    logging.warning(f"Invalid boolean type for {k}: expected bool, got {type(v).__name__}")
                    del entry[k]

        # Validate and clean up optional fields
        optional_fields_to_remove = []
        for field_name, field_value in list(entry.items()):
            if field_name in OPTIONAL_FIELDS:
                expected_type = OPTIONAL_FIELDS[field_name]

                # Special handling for complex validation fields
                if field_name == 'time':
                    if not isinstance(field_value, str):
                        logging.warning(f"Invalid time field type: expected str, got {type(field_value).__name__}")
                        optional_fields_to_remove.append(field_name)
                    elif not validate_iso8601_time(field_value):
                        logging.warning(f"Invalid ISO-8601 time format: {field_value}")
                        optional_fields_to_remove.append(field_name)
                elif field_name == 'rate':
                    if not isinstance(field_value, dict):
                        logging.warning(f"Invalid rate field type: expected dict, got {type(field_value).__name__}")
                        optional_fields_to_remove.append(field_name)
                    elif not validate_rate_field(field_value):
                        logging.warning(f"Invalid rate field format: must contain ISO 4217 currency codes and numeric values")
                        optional_fields_to_remove.append(field_name)
                elif field_name == 'fmv':
                    if not isinstance(field_value, dict):
                        logging.warning(f"Invalid fmv field type: expected dict, got {type(field_value).__name__}")
                        optional_fields_to_remove.append(field_name)
                    elif not validate_fmv_field(field_value):
                        logging.warning(f"Invalid fmv field format: must contain ISO 4217 currency codes and numeric values")
                        optional_fields_to_remove.append(field_name)
                # Standard type validation for all other optional fields
                elif not isinstance(field_value, expected_type):
                    logging.warning(f"Invalid {field_name} field type: expected {expected_type.__name__}, got {type(field_value).__name__}")
                    optional_fields_to_remove.append(field_name)

        # Remove invalid optional fields
        for field_name in optional_fields_to_remove:
            del entry[field_name]

        if 'label' in entry:
            validate_label_length(entry['label'])


        if 'origin' in entry and not isinstance(entry['origin'], str):
            raise TypeError('origin must be string')

        # TODO: Verify origin
        return True
