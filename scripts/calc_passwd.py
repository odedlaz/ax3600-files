#!/usr/bin/env python3
import sys
import hashlib
import header

if sys.version_info < (3,7):
    print("python version is not supported", file=sys.stderr)
    sys.exit(1)

# credit goes to zhoujiazhao:
# https://blog.csdn.net/zhoujiazhao/article/details/102578244

salt = {'r1d': 'A2E371B0-B34B-48A5-8C40-A7133F3B5D88',
        'others': 'd44fb0960aa0-a5e6-4a30-250f-6d2df50a'}


def get_salt(sn):
    if "/" not in sn:
        return salt["r1d"]

    return "-".join(reversed(salt["others"].split("-")))


def calc_passwd(sn):
    passwd = sn + get_salt(sn)
    m = hashlib.md5(passwd.encode())
    return m.hexdigest()[:8]


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} <PATH>")
        sys.exit(1)

    path = sys.argv[1]
    raw_header = header.extract(path)
    header = header.parse(raw_header)
    print(calc_passwd(header['SN']))
