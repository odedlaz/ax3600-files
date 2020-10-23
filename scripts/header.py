#!/usr/bin/env python3.6
import argparse
import crc32

COMMAND_EXTRACT = "extract"
COMMAND_MODIFY = "modify"

# credit goes to didiaoing: https://www.wutaijie.cn/?p=254
# this script performs the manual steps outlined in his post


def extract(path):
    with open(path, 'rb') as f:
        header = b''
        while True:
            c = f.read(2)
            # end of header
            if c == b'\x00\x00':
                break
            header += c

        return f.tell(), header.rstrip(b'\x00')


def parse(raw_header):
    # strip crc32
    raw_header = raw_header[crc32.CRC32_LEN:].split(b'\x00')
    header = dict((x.decode().split("=") for x in raw_header))
    return header


def parse_arguments():
    parser = argparse.ArgumentParser(description='Header Parser')
    subparsers = parser.add_subparsers(title="commands", dest="command")

    parser_extract = subparsers.add_parser(COMMAND_EXTRACT, help='extract header')
    parser_extract.add_argument('path', metavar='PATH')

    parser_modify = subparsers.add_parser(COMMAND_MODIFY, help='modify header')
    parser_modify.add_argument('src', metavar='SRC')
    parser_modify.add_argument('dst', metavar='DST')
    parser_modify.add_argument('--test', default=False, action='store_true')

    return parser.parse_args()


def extract_command(path):
    _, raw_header = extract(path)
    print(f"CRC32: {crc32.extract_human_readable(raw_header)}")
    header = parse(raw_header)
    for k, v in header.items():
        print(f"{k}: {v}")


def modify_command(src, dst, test=False):
    size, raw_header = extract(src)
    padding = size - len(raw_header)

    header = parse(raw_header)

    # in test mode we don't modify the header
    if not test:
        header['CountryCode'] = 'US'
        for flag in ['telnet_en', 'ssh_en', 'uart_en']:
            header[flag] = 1

    crc32_data = crc32.get_data(src)
    only_data = crc32_data[len(raw_header) + padding:]

    # re-assemble the raw header after modifications
    new_raw_header = b'\x00'.join([f"{k}={v}".encode() for k, v in header.items()])

    # create crc32 data with crc32 prefix reset
    data_without_crc32 = b'\x00' * crc32.CRC32_LEN + new_raw_header + b'\x00' * padding + only_data

    # calculate new crc32 and update the data with it
    new_raw_crc32 = bytes.fromhex(crc32.calculate(data_without_crc32).lstrip("0x"))
    new_crc32_data = new_raw_crc32 + data_without_crc32[crc32.CRC32_LEN:]

    with open(src, "rb") as f:
        bdata = f.read()

    if test:
        if bdata == new_crc32_data + bdata[len(new_crc32_data):]:
            print("successfully re-assembled header without modifications")
        else:
            print("header re-assembly without modifications FAILED")
        return

    with open(dst, "wb") as f:
        f.write(new_crc32_data)
        f.write(bdata[f.tell():])


if __name__ == "__main__":
    args = parse_arguments()

    if args.command == COMMAND_EXTRACT:
        extract_command(args.path)

    if args.command == COMMAND_MODIFY:
        modify_command(args.src, args.dst, args.test)
