#!/usr/bin/env python3
import sys
import hashlib
import select

# credit goes to zhoujiazhao:
# https://blog.csdn.net/zhoujiazhao/article/details/102578244

salt = {'r1d': 'A2E371B0-B34B-48A5-8C40-A7133F3B5D88',
        'others': 'd44fb0960aa0-a5e6-4a30-250f-6d2df50a'}


def get_salt(sn):
    if "/" not in sn:
        return salt["r1d"]

    return "-".join(reversed(salt["others"].split("-")))


def get_serial_numbers():
    if select.select([sys.stdin, ], [], [], 0.0)[0]:
        return map(str.strip, sys.stdin)


def calc_passwd(sn):
    passwd = sn + get_salt(sn)
    m = hashlib.md5(passwd.encode())
    return m.hexdigest()[:8]


if __name__ == "__main__":
    for sn in get_serial_numbers():
        print(f"{sn}: {calc_passwd(sn)}")
