import re


def validate_email(email):
    return re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email) is not None


def validate_port(port):
    return isinstance(port, int) and 0 < port < 65536


def validate_nonempty(s):
    return isinstance(s, str) and len(s.strip()) > 0
