import re

def is_valid_isbn(isbn):
    """
    Check if the given ISBN (10 or 13 digits) is valid.
    """
    isbn = re.sub(r'[^0-9X]', '', isbn.upper())
    if len(isbn) == 10:
        return _is_valid_isbn_10(isbn)
    elif len(isbn) == 13:
        return _is_valid_isbn_13(isbn)
    return False

def _is_valid_isbn_10(isbn):
    """
    Check if the given 10-digit ISBN is valid.
    """
    check_sum = sum((10 - i) * (int(digit) if digit != 'X' else 10) for i, digit in enumerate(isbn))
    return check_sum % 11 == 0

def _is_valid_isbn_13(isbn):
    """
    Check if the given 13-digit ISBN is valid.
    """
    check_sum = sum((3 if i % 2 else 1) * int(digit) for i, digit in enumerate(isbn))
    return check_sum % 10 == 0

def normalize_isbn(isbn):
    """
    Normalize ISBN by removing hyphens and converting to ISBN-13 if it's ISBN-10.
    """
    isbn = re.sub(r'[^0-9X]', '', isbn.upper())
    if len(isbn) == 10:
        return isbn_10_to_13(isbn)
    return isbn

def isbn_10_to_13(isbn_10):
    """
    Convert ISBN-10 to ISBN-13.
    """
    if len(isbn_10) != 10:
        raise ValueError("Invalid ISBN-10")
    
    isbn_13 = '978' + isbn_10[:-1]
    check_sum = sum((3 if i % 2 else 1) * int(digit) for i, digit in enumerate(isbn_13))
    check_digit = (10 - (check_sum % 10)) % 10
    return isbn_13 + str(check_digit)

def isbn_13_to_10(isbn_13):
    """
    Convert ISBN-13 to ISBN-10 if possible.
    """
    if len(isbn_13) != 13 or not isbn_13.startswith('978'):
        raise ValueError("Invalid ISBN-13 or cannot be converted to ISBN-10")
    
    isbn_10 = isbn_13[3:-1]
    check_sum = sum((10 - i) * int(digit) for i, digit in enumerate(isbn_10))
    check_digit = (11 - (check_sum % 11)) % 11
    return isbn_10 + ('X' if check_digit == 10 else str(check_digit))