#!/usr/bin/env python3.6
import argparse
import crc32
import re

COMMAND_EXTRACT = "extract"
COMMAND_MODIFY = "modify"

# credit goes to didiaoing: https://www.wutaijie.cn/?p=254
# this script performs the manual steps outlined in his post


def extract(path):
    with open(path, 'rb') as f:
        header = b''
        while True:
            buf = f.read(10)
            # if buf is only zeroes
            if not buf.strip(b'\x00'):
                break
            header += buf

        return header.rstrip(b'\x00')


def parse(raw_header):
    # strip crc32
    raw_header = raw_header[crc32.CRC32_LEN:].split(b'\x00')
    header = dict((x.decode().split("=") for x in raw_header))
    return header


def validate_country_code(cc):
    # extracted from /etc/init.d/timezone
    if cc in ('EU', 'US', 'KR', 'UK', 'IN', 'CN'):
        return cc

    # otherwise, CountryCode need to be uppercase with two letters
    if not re.match('[A-Z][A-Z]', cc):
        raise argparse.ArgumentTypeError(f"country should consist of two upper case characters")

    return cc


def parse_arguments():
    parser = argparse.ArgumentParser(description='Header Parser')
    subparsers = parser.add_subparsers(title="commands", dest="command")

    parser_extract = subparsers.add_parser(COMMAND_EXTRACT, help='extract header')
    parser_extract.add_argument('path', metavar='PATH')

    parser_modify = subparsers.add_parser(COMMAND_MODIFY, help='modify header')
    parser_modify.add_argument('src', metavar='SRC', help='path to bdata file')
    parser_modify.add_argument('dst', metavar='DST', help='path to modified bdata file')
    parser_modify.add_argument('--country', type=validate_country_code, required=False, metavar='COUNTRY', help='country code')
    parser_modify.add_argument('--test', default=False, action='store_true')

    return parser.parse_args()


def extract_command(path):
    raw_header = extract(path)
    print(f"CRC32: {crc32.extract_human_readable(raw_header)}")
    header = parse(raw_header)
    for k, v in header.items():
        print(f"{k}: {v}")


def modify_command(src, dst, country=None, test=False):
    raw_header = extract(src)

    header = parse(raw_header)

    # in test mode we don't modify the header
    if not test:
        if country:
            header['CountryCode'] = country
        for flag in ['telnet_en', 'ssh_en', 'uart_en']:
            header[flag] = 1
        header['boot_wait'] = "on"

    crc32_data = crc32.get_data(src)
    zero_data = crc32_data[len(raw_header):]

    # re-assemble the raw header after modifications
    new_raw_header = b'\x00'.join([f"{k}={v}".encode() for k, v in header.items()])

    raw_header_no_crc32 = raw_header[crc32.CRC32_LEN:]
    excess_bytes = len(new_raw_header) - len(raw_header_no_crc32)
    if excess_bytes > 0:
        # header grew -> we need remove some zeroes
        # make sure we don't remove anything that's not zeroes (with some extra)
        assert not zero_data[:excess_bytes + 10].strip(b"\x00")
        new_zero_data = zero_data[excess_bytes:]
    else:
        # header shrunk -> pad with zeroes
        new_zero_data = b'\x00' * abs(excess_bytes) + zero_data

    # create crc32 data with crc32 prefix reset
    data_without_crc32 = b'\x00' * crc32.CRC32_LEN + new_raw_header + new_zero_data

    # calculate new crc32 and update the data with it
    new_raw_crc32 = bytes.fromhex(crc32.calculate(data_without_crc32)[2:])
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

    extract_command(dst)

if __name__ == "__main__":
    args = parse_arguments()

    if args.command == COMMAND_EXTRACT:
        extract_command(args.path)

    if args.command == COMMAND_MODIFY:
        modify_command(args.src, args.dst, args.country, args.test)
