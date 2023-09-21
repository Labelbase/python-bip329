import json
import tempfile
import os
import hashlib
import py7zr
import shutil
import time

from .constants import VALID_SPENDABLE_VALUES
from .constants import VALID_REQUIRED_KEYS
from .constants import VALID_TYPE_KEYS
from .constants import MANDATORY_KEYS_ERROR

from .encryption import encrypt_files


class BIP329JSONLWriter:
    def __init__(self, filename, remove_existing=True):
        """
        If `remove_existing` is `True` any existing files with the same name will be overwritten/replaced.

        Setting it to `False` will preserve any previously exported files by creating a backup if necessary.
        """
        self.filename = filename
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

    def write_label(self, line):
        # Check if the line is a valid BIP-329 record
        if (
            (isinstance(line, dict) and "type" in line and "ref" in line and "label" in line) or
            (callable(getattr(line, "type", None)) and callable(
                getattr(line, "ref", None)) and hasattr(line, "label"))
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
                "label": line.label() if callable(getattr(line, "label", None)) else line["label"],
            }

            # Check if all mandatory keys are present
            if not all(key in label_dict for key in VALID_REQUIRED_KEYS):
                raise MANDATORY_KEYS_ERROR

            # Check and add "origin" if present and valid
            if callable(getattr(line, "origin", None)):
                origin = line.origin()
                if isinstance(origin, str) and origin:
                    label_dict["origin"] = origin
                else:
                    raise ValueError(
                        "Invalid 'origin' field in BIP-329 record")

            elif "origin" in line:
                origin = line["origin"]
                if isinstance(origin, str) and origin:
                    label_dict["origin"] = origin
                else:
                    raise ValueError(
                        "Invalid 'origin' field in BIP-329 record")

            # Check and add "spendable" if present and valid
            if callable(getattr(line, "spendable", None)):
                spendable = line.spendable()
                if spendable in VALID_SPENDABLE_VALUES:
                    label_dict["spendable"] = "true" if spendable in [
                        "true", True] else "false"
                else:
                    raise ValueError(
                        "Invalid 'spendable' field in BIP-329 record")
            elif "spendable" in line:
                spendable = line["spendable"]
                if spendable in VALID_SPENDABLE_VALUES:
                    label_dict["spendable"] = "true" if spendable in [
                        "true", True] else "false"
                else:
                    raise ValueError(
                        "Invalid 'spendable' field in BIP-329 record")

            with open(self.filename, mode='a', encoding='utf-8') as writer:
                writer.write(json.dumps(label_dict) + '\n')
        else:
            raise ValueError(
                "Invalid BIP-329 record: 'type', 'ref', and 'label' attributes or keys are required, and only valid fields are exported.")


class BIP329JSONLEncryptedWriter:
    def __init__(self, filename, passphrase, remove_existing=True):
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
        self.jsonl_writer = BIP329JSONLWriter(
            self.temp_file.name, remove_existing=True)
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
        self.temp_file.close()
        encrypt_files(self.filename, [self.temp_file.name], self.passphrase)
        os.remove(self.temp_file.name)
        self.is_closed = True
