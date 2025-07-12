from typing import Any


def key_by_value(dictionary: dict, value: Any):
    values = [k for k, v in dictionary.items() if v == value]
    if not len(values):
        raise ValueError('Key by value not found')
    return values[0]
