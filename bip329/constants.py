
VALID_SPENDABLE_VALUES = (True, False, "true", "false")
VALID_REQUIRED_KEYS = ("type", "ref", "label")
VALID_TYPE_KEYS = ("tx", "addr", "pubkey", "input", "output", "xpub")

MANDATORY_KEYS_ERROR = ValueError(
    "Mandatory keys 'type', 'ref', and 'label' are required in BIP-329 record")
