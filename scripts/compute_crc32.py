#!/usr/bin/env python3.6
import sys
import zlib
import textwrap

with open(sys.argv[1], "rb") as f:
    data = f.read(0xffff+1)
    crc32 = hex(zlib.crc32(data[0x4:]) & 0xffffffff)
    reversed_crc32 = "".join(reversed(textwrap.wrap('0' + crc32[2:], 2)))
    original_crc32 = "0x" + data[:0x4].hex()
    new_crc32 = "0x" + reversed_crc32
    print(new_crc32)
    print(original_crc32)
    assert original_crc32 == new_crc32
