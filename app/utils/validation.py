# app/utils/validation.py
import re

def validate_value(value):
    if len(value) > 255:
        return False
    if not re.match(r'^[a-zA-Z0-9_\-]+$', value):
        return False
    return True
