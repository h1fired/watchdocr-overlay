import struct


def int8ub(value: int):
    return value.to_bytes(1, 'big', signed=False)


def int8ul(value: int):
    return value.to_bytes(1, 'little', signed=False)


def int8sb(value: int):
    return value.to_bytes(1, 'big', signed=True)


def int8sl(value: int):
    return value.to_bytes(1, 'little', signed=True)


# 16-bit
def int16ub(value: int):
    return value.to_bytes(2, 'big', signed=False)


def int16ul(value: int):
    return value.to_bytes(2, 'little', signed=False)


def int16sb(value: int):
    return value.to_bytes(2, 'big', signed=True)


def int16sl(value: int):
    return value.to_bytes(2, 'little', signed=True)


# 24-bit
def int24ub(value: int):
    return value.to_bytes(3, 'big', signed=False)


def int24ul(value: int):
    return value.to_bytes(3, 'little', signed=False)


def int24sb(value: int):
    return value.to_bytes(3, 'big', signed=True)


def int24sl(value: int):
    return value.to_bytes(3, 'little', signed=True)


# 32-bit
def int32ub(value: int):
    return value.to_bytes(4, 'big', signed=False)


def int32ul(value: int):
    return value.to_bytes(4, 'little', signed=False)


def int32sb(value: int):
    return value.to_bytes(4, 'big', signed=True)


def int32sl(value: int):
    return value.to_bytes(4, 'little', signed=True)


def readbytes_int(bytes, byteorder='big', unsigned=False):
    data = bytes
    return int.from_bytes(data, byteorder, signed=not unsigned)


def readbytes(bytes, byteorder='big', unsigned=False, as_float=False):
    size = len(bytes) * 8
    new_data = bytes

    if size == 8:
        unpack_format = 'b'
    elif size == 16:
        if as_float:
            unpack_format = 'e'
        else:
            unpack_format = 'h'
    elif size == 24:
        if as_float:
            unpack_format = 'f'
        else:
            unpack_format = 'i'
        new_data = bytearray([0]) + bytes
    elif size == 32:
        if as_float:
            unpack_format = 'f'
        else:
            unpack_format = 'i'

    if byteorder == 'big':
        b_order = '>'
    else:
        b_order = '<'

    if unsigned:
        unpack_format = unpack_format.upper()

    return struct.unpack(b_order + unpack_format, new_data)[0]
