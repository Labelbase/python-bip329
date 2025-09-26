# file: bip329_writer.py
import json
import tempfile
import os
import hashlib
import py7zr
import shutil
import time
import logging
from datetime import datetime

from .constants import VALID_REQUIRED_KEYS
from .constants import VALID_TYPE_KEYS
from .constants import MANDATORY_KEYS_ERROR
from .constants import OPTIONAL_FIELDS
from .constants import FIELD_TYPES_BY_TYPE
from .constants import VALID_FIELDS_BY_TYPE

from .encryption import encrypt_files

from .validation_utils import validate_rate_field
from .validation_utils import validate_fmv_field
from .validation_utils import validate_iso8601_time
from .validation_utils import validate_label_length
from .validation_utils import validate_utf8_encoding

class BIP329JSONLWriter:
    def __init__(self, filename,
                    remove_existing=True,
                    replace_non_utf8=False,
                    truncate_labels=False):
        """
        If `remove_existing` is `True` any existing files with the same name will be overwritten/replaced.

        Setting it to `False` will preserve any previously exported files by creating a backup if necessary.
        """
        self.filename = filename
        self.replace_non_utf8 = replace_non_utf8
        self.truncate_labels = truncate_labels
        # Check if the file already exists
        if os.path.exists(self.filename):
            if remove_existing:
                # If it exists and remove_existing is True, remove it
                os.remove(self.filename)
            else:
                # If it exists and remove_existing is False, move it to a backup location with a timestamp
                timestamp = int(time.time())
                backup_filename = f"{self.filename}.{timestamp}.bak"
                shutil.move(self.filename, backup_filename)

    def validate_fields_by_type(self, label_dict, entry_type):
        """Validate that fields are appropriate for the given entry type"""
        valid_fields = VALID_FIELDS_BY_TYPE.get(entry_type, set())
        fields_to_remove = []
        for field_name in list(label_dict.keys()):
            if field_name not in valid_fields:
                logging.warning(f"Field '{field_name}' not valid for type '{entry_type}', removing")
                fields_to_remove.append(field_name)

        # Remove invalid fields
        for field_name in fields_to_remove:
            del label_dict[field_name]

        return label_dict

    def write_label(self, line):
        # Check if the line is a valid BIP-329 record
        if (
            (isinstance(line, dict) and "type" in line and "ref" in line ) or
            (callable(getattr(line, "type", None)) and callable(
                getattr(line, "ref", None)))
        ):
            if callable(getattr(line, "type", None)):
                label_type = line.type()
            else:
                label_type = line["type"]


            assert label_type in VALID_TYPE_KEYS

            if callable(getattr(line, "ref", None)):
                label_ref = line.ref()
            else:
                label_ref = line["ref"]

            label_dict = {
                "type": label_type,
                "ref": label_ref,
            #    "label": line.label() if callable(getattr(line, "label", None)) else line["label"],
            }

            label_value = None
            if callable(getattr(line, "label", None)):
                label_value = line.label()
            elif "label" in line:
                label_value = line["label"]

            # Add label to dict if present and valid
            if label_value is not None:
                if not isinstance(label_value, str):
                    raise ValueError("label must be string")
                label_dict["label"] = label_value

                # Now validate length and UTF-8
                if len(label_value) > 255:
                    if self.truncate_labels:
                        original_length = len(label_value)
                        label_value = label_value[:255]
                        logging.warning(f"Label truncated from {original_length} to 255 characters")
                    else:
                        validate_label_length(label_value)

                # UTF-8 validation
                try:
                    label_dict['label'] = validate_utf8_encoding(label_value, self.replace_non_utf8)
                except ValueError:
                    if not self.replace_non_utf8:
                        raise ValueError("Invalid UTF-8 encoding in label")




            # Check if all mandatory keys are present
            if not all(key in label_dict for key in VALID_REQUIRED_KEYS):
                raise MANDATORY_KEYS_ERROR

            # Handle existing fields (origin, spendable)
            if callable(getattr(line, "origin", None)):
                origin = line.origin()
                if isinstance(origin, str) and origin:
                    label_dict["origin"] = origin
                else:
                    raise ValueError("Invalid 'origin' field in BIP-329 record")
            elif "origin" in line:
                origin = line["origin"]
                if isinstance(origin, str) and origin:
                    label_dict["origin"] = origin
                else:
                    raise ValueError("Invalid 'origin' field in BIP-329 record")

            if ("spendable" in line) or hasattr(line, "spendable"):
                if callable(getattr(line, "spendable", None)):
                    spendable = line.spendable()
                else:
                    spendable = line["spendable"]

                if spendable not in {True, False}:
                    raise ValueError(f"Invalid 'spendable' field in BIP-329 record: {spendable}")

                label_dict["spendable"] = spendable

            # Handle optional fields with validation
            for field_name in OPTIONAL_FIELDS:
                field_value = None

                # Get field value (support both dict and object styles)
                if callable(getattr(line, field_name, None)):
                    field_value = getattr(line, field_name)()
                elif field_name in line:
                    field_value = line[field_name]
                else:
                    continue  # Field not present

                # Validate field type
                expected_type = OPTIONAL_FIELDS[field_name]

                # Special handling for time field (ISO-8601 validation)
                if field_name == 'time':
                    if not isinstance(field_value, str):
                        logging.warning(f"Invalid time field type: expected str, got {type(field_value).__name__}")
                        continue
                    elif not validate_iso8601_time(field_value):
                        logging.warning(f"Invalid ISO-8601 time format: {field_value}")
                        continue
                    label_dict[field_name] = field_value
                elif field_name == 'rate':
                    if not isinstance(field_value, dict):
                        logging.warning(f"Invalid rate field type: expected dict, got {type(field_value).__name__}")
                        continue
                    elif not validate_rate_field(field_value):
                        logging.warning(f"Invalid rate field format: must contain ISO 4217 currency codes and numeric values")
                        continue
                    label_dict[field_name] = field_value
                elif field_name == 'fmv':
                    if not isinstance(field_value, dict):
                        logging.warning(f"Invalid fmv field type: expected dict, got {type(field_value).__name__}")
                        continue
                    elif not validate_fmv_field(field_value):
                        logging.warning(f"Invalid fmv field format: must contain ISO 4217 currency codes and numeric values")
                        continue
                    label_dict[field_name] = field_value

                # Standard type validation for other fields
                elif isinstance(field_value, expected_type):
                    label_dict[field_name] = field_value  # Valid, add to output
                else:
                    logging.warning(f"Invalid {field_name} field type: expected {expected_type.__name__}, got {type(field_value).__name__}")
                    continue

            label_dict = self.validate_fields_by_type(label_dict, label_type)

            with open(self.filename, mode='a', encoding='utf-8') as writer:
                writer.write(json.dumps(label_dict) + '\n')
        else:
            raise ValueError(
                "Invalid BIP-329 record: 'type', 'ref', and 'label' attributes or keys are required, and only valid fields are exported.")

class BIP329JSONLEncryptedWriter:
    def __init__(self, filename, passphrase, remove_existing=True, replace_non_utf8=False):
        """
        Controls whether any existing files should be removed before writing.

        - In BIP329JSONLWriter, `remove_existing` is not applicable due to the use of a temporary file for writing.
          It is always set to `True` by default, meaning any existing files with the same name will be "overwritten".

        - However, in BIP329JSONLEncryptedWriter, `remove_existing` is supported.
          Setting it to `False` will preserve any previously exported files by creating a backup if necessary.
          The path to the backup will stored in self.backup_filename .
        """
        self.temp_file = tempfile.NamedTemporaryFile(
            delete=False, mode='w', encoding='utf-8')
        self.jsonl_writer = BIP329JSONLWriter(self.temp_file.name,
                                              remove_existing=True,
                                              replace_non_utf8=replace_non_utf8)
        self.filename = filename
        self.backup_filename = None
        self.passphrase = passphrase

        # Check if the file already exists
        if os.path.exists(self.filename):
            if remove_existing:
                # If it exists and remove_existing is True, remove it
                os.remove(self.filename)
            else:
                # If it exists and remove_existing is False, move it to a backup location with a timestamp
                timestamp = int(time.time())
                self.backup_filename = f"{self.filename}.{timestamp}.bak"
                shutil.move(self.filename, self.backup_filename)

        self.is_closed = False

    def write_label(self, line):
        if self.is_closed:
            raise Exception("Writer is closed.")
        self.jsonl_writer.write_label(line)

    def close(self):
        if self.is_closed:
            return
        # Ensure temp file is properly closed but not deleted yet
        if not self.temp_file.closed:
            self.temp_file.close()
        # Check if temp file exists before trying to encrypt it
        if os.path.exists(self.temp_file.name):
            encrypt_files(self.filename, [self.temp_file.name], self.passphrase)
            # Clean up temp file after successful encryption
            os.remove(self.temp_file.name)
        else:
            with tempfile.NamedTemporaryFile(mode='w', delete=False) as empty_file:
                pass  # Create empty file
            try:
                encrypt_files(self.filename, [empty_file.name], self.passphrase)
            finally:
                os.remove(empty_file.name)
        self.is_closed = True
