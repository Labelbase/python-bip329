# file: constants.py
# Core BIP-329 required fields
VALID_REQUIRED_KEYS = ("type", "ref")
VALID_TYPE_KEYS = ("tx", "addr", "pubkey", "input", "output", "xpub")


VALID_FIELDS_BY_TYPE = {
    "tx": {"type", "ref", "label", "origin", "height", "time", "fee", "value", "rate"},
    "addr": {"type", "ref", "label", "origin", "keypath", "heights"},
    "pubkey": {"type", "ref", "label", "origin", "keypath"},
    "input": {"type", "ref", "label", "origin", "keypath", "value", "fmv", "height", "time"},
    "output": {"type", "ref", "label", "origin", "spendable", "keypath", "value", "fmv", "height", "time"},
    "xpub": {"type", "ref", "label", "origin"}
}

FIELD_TYPES_BY_TYPE = {
    "tx": {"type": str, "ref": str, "label": str, "origin": str, "height": int, "time": str, "fee": int, "value": int, "rate": dict},
    "addr": {"type": str, "ref": str, "label": str, "origin": str, "keypath": str, "heights": list},
    "pubkey": {"type": str, "ref": str, "label": str, "origin": str, "keypath": str},
    "input": {"type": str, "ref": str, "label": str, "origin": str, "keypath": str, "value": int, "fmv": dict, "height": int, "time": str},
    "output": {"type": str, "ref": str, "label": str, "origin": str, "spendable": bool, "keypath": str, "value": int, "fmv": dict, "height": int, "time": str},
    "xpub": {"type": str, "ref": str, "label": str, "origin": str}
}

# Boolean fields that need special parsing
BOOL_KEYS = {"spendable", }

# Error for missing mandatory fields
MANDATORY_KEYS_ERROR = ValueError("Invalid BIP-329 record: 'type' and 'ref' are required")

# Optional fields from BIP-329 "Additional Fields" section with expected types
OPTIONAL_FIELDS = {
    "height": int,      # Block height for transactions
    "time": str,        # ISO-8601 timestamp
    "fee": int,         # Transaction fee in satoshis
    "value": int,       # Value in satoshis (signed for transactions)
    "rate": dict,       # Exchange rates {currency: rate}
    "keypath": str,     # Key derivation path
    "fmv": dict,        # Fair market value {currency: amount}
    "heights": list,    # Block heights for address activity
}
