#!/usr/bin/env python3.6
import sys
from pprint import pprint
import textwrap

def read_header(path):
    with open(path, 'rb') as f:
        header = b''
        while True:
            c = f.read(2)
            # end of header
            if c == b'\x00\x00':
                break
            header += c
        return header

def parse_header(raw_header):
    raw_crc32 = raw_header[:4]
    crc32 = " ".join([x.upper() for x in textwrap.wrap(raw_crc32.hex(),2)])

    l = raw_header[4:].split(b'\x00')
    header = dict((x.decode().split("=") for x in l[1:] if x))

    return crc32, header


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <PATH>")
        sys.exit(1)

    raw_header = read_header(sys.argv[1])
    crc32, header = parse_header(raw_header)
    print(f"Checksum: {crc32}\n")
    for k,v in header.items():
        print(f"{k}: {v}")
