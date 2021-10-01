def check_ext(path: str):
    return path.endswith('.png') or path.endswith('.bmp')


def determine_bytes(mode):
    length = len(mode)
    if length > 4:  # YCbCr
        return 3
    else:
        return length


def change_bit(value, bit):
    return (value & ~1) | bit
