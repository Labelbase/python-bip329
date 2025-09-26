# file: validation_utils.py
from datetime import datetime
import logging

ISO_4217_KEYS = {'AFN', 'EUR', 'ALL', 'DZD', 'USD', 'EUR', 'AOA', 'XCD', 'XCD', 'XAD', 'ARS', 'AMD', 'AWG', 'AUD', 'EUR', 'AZN', 'BSD', 'BHD', 'BDT', 'BBD', 'BYN', 'EUR', 'BZD', 'XOF', 'BMD', 'INR', 'BTN', 'BOB', 'BOV', 'USD', 'BAM', 'BWP', 'NOK', 'BRL', 'USD', 'BND', 'BGN', 'XOF', 'BIF', 'CVE', 'KHR', 'XAF', 'CAD', 'KYD', 'XAF', 'XAF', 'CLP', 'CLF', 'CNY', 'AUD', 'AUD', 'COP', 'COU', 'KMF', 'CDF', 'XAF', 'NZD', 'CRC', 'XOF', 'EUR', 'CUP', 'XCG', 'EUR', 'CZK', 'DKK', 'DJF', 'XCD', 'DOP', 'USD', 'EGP', 'SVC', 'USD', 'XAF', 'ERN', 'EUR', 'SZL', 'ETB', 'EUR', 'FKP', 'DKK', 'FJD', 'EUR', 'EUR', 'EUR', 'XPF', 'EUR', 'XAF', 'GMD', 'GEL', 'EUR', 'GHS', 'GIP', 'EUR', 'DKK', 'XCD', 'EUR', 'USD', 'GTQ', 'GBP', 'GNF', 'XOF', 'GYD', 'HTG', 'USD', 'AUD', 'EUR', 'HNL', 'HKD', 'HUF', 'ISK', 'INR', 'IDR', 'XDR', 'IRR', 'IQD', 'EUR', 'GBP', 'ILS', 'EUR', 'JMD', 'JPY', 'GBP', 'JOD', 'KZT', 'KES', 'AUD', 'KPW', 'KRW', 'KWD', 'KGS', 'LAK', 'EUR', 'LBP', 'LSL', 'ZAR', 'LRD', 'LYD', 'CHF', 'EUR', 'EUR', 'MOP', 'MGA', 'MWK', 'MYR', 'MVR', 'XOF', 'EUR', 'USD', 'EUR', 'MRU', 'MUR', 'EUR', 'XUA', 'MXN', 'MXV', 'USD', 'MDL', 'EUR', 'MNT', 'EUR', 'XCD', 'MAD', 'MZN', 'MMK', 'NAD', 'ZAR', 'AUD', 'NPR', 'EUR', 'XPF', 'NZD', 'NIO', 'XOF', 'NGN', 'NZD', 'AUD', 'MKD', 'USD', 'NOK', 'OMR', 'PKR', 'USD', 'PAB', 'USD', 'PGK', 'PYG', 'PEN', 'PHP', 'NZD', 'PLN', 'EUR', 'USD', 'QAR', 'EUR', 'RON', 'RUB', 'RWF', 'EUR', 'SHP', 'XCD', 'XCD', 'EUR', 'EUR', 'XCD', 'WST', 'EUR', 'STN', 'SAR', 'XOF', 'RSD', 'SCR', 'SLE', 'SGD', 'XCG', 'XSU', 'EUR', 'EUR', 'SBD', 'SOS', 'ZAR', 'SSP', 'EUR', 'LKR', 'SDG', 'SRD', 'NOK', 'SEK', 'CHF', 'CHE', 'CHW', 'SYP', 'TWD', 'TJS', 'TZS', 'THB', 'USD', 'XOF', 'NZD', 'TOP', 'TTD', 'TND', 'TRY', 'TMT', 'USD', 'AUD', 'UGX', 'UAH', 'AED', 'GBP', 'USD', 'USD', 'USN', 'UYU', 'UYI', 'UYW', 'UZS', 'VUV', 'VES', 'VED', 'VND', 'USD', 'USD', 'XPF', 'MAD', 'YER', 'ZMW', 'ZWG', 'XBA', 'XBB', 'XBC', 'XBD', 'XTS', 'XXX', 'XAU', 'XPD', 'XPT', 'XAG'}


def validate_rate_field(rate_value):
    """
    Validate BIP-329 rate field format.
    Args:
        rate_value: The rate field value to validate
    Returns:
        bool: True if valid, False otherwise
    BIP-329 specifies rate as: {"USD": 105620.00, "EUR": 98000.50}
    - Keys must be ISO 4217 currency codes
    - Values must be positive numeric (int or float)
    """
    if not isinstance(rate_value, dict):
        return False

    if not rate_value:  # Empty dict {}
        return False

    for currency, rate in rate_value.items():
        # Check currency code in LUT
        if currency not in ISO_4217_KEYS:
            return False

        # Check rate is numeric and positive
        if not isinstance(rate, (int, float)) or rate <= 0:
            return False

        # Check decimal places (max 8 for financial precision)
        if isinstance(rate, float):
            decimal_str = f"{rate:.8f}".rstrip('0').rstrip('.')
            decimal_places = len(decimal_str.split('.')[-1]) if '.' in decimal_str else 0
            if decimal_places > 8:
                return False
    return True


def validate_fmv_field(fmv_value):
    """Same validation as rate field"""
    return validate_rate_field(fmv_value)


def validate_iso8601_time(time_value):
    """Validate ISO-8601 time format"""
    if not isinstance(time_value, str):
        return False
    try:
        time_str = time_value.replace('Z', '+00:00')
        datetime.fromisoformat(time_str)
        return True
    except ValueError:
        return False


def validate_label_length(label):
    """Validate label field length per BIP-329 suggestion of 255 chars max"""
    if label and isinstance(label, str):
        if len(label) > 255:
            logging.warning(f"Label {label} with length ({len(label)}) exceeds suggested maximum of 255 characters")


def validate_utf8_encoding(text, replace_non_utf8):
    if not isinstance(text, str):
        return text
    try:
        text.encode('utf-8')
        return text
    except UnicodeEncodeError:
        if replace_non_utf8:
            # Use 'replace' error handler which should produce �
            fixed_text = text.encode('utf-8', errors='replace').decode('utf-8')
            logging.warning("Invalid UTF-8 characters replaced with �")
            return fixed_text
        else:
            logging.error("Invalid UTF-8 encoding")
            raise ValueError("Invalid UTF-8 encoding")
