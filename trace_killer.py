#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=====================================================================
  TRACE_KILLER ☠️  -  CYBER INTELLIGENCE & RECON CONSOLE
  CODED BY BYPASS-CODE
  VERSION: 1.1

  MODULES:
    1) IP/DOMAIN TRACKER   -> resolve + ping + traceroute + geoip
    2) NETWORK SCANNER     -> device discovery + vendor lookup
    3) PORT SCANNER        -> concurrent scan + service names
    4) INTRUSION WATCH     -> ARP monitor, new-device alerts
    5) RADAR DASHBOARD     -> animated system/network intel

  FIXES IN v1.1:
    - smart interface pick (skips VPN/TUN/virtual adapters)
    - ARP filter: no multicast/broadcast/zero MACs
    - network scan shows only live devices (no full-range spam)
    - virtual/VPN environment warning

  PLATFORM: Windows / Linux  (NO ROOT REQUIRED)
  FOR EDUCATIONAL & AUTHORIZED TESTING ONLY.
=====================================================================
"""

import os
import sys
import re
import math
import time
import socket
import threading
import subprocess
import platform
import shutil
import argparse
import concurrent.futures
from datetime import datetime
from colorama import init, Fore, Style

try:
    import requests
except ImportError:
    requests = None

init(autoreset=True)

APP = "TRACE_KILLER"
VERSION = "1.1"

# ═══════════════════════ BANNER FONT ═══════════════════════
_T = ["████████╗", "╚══██╔══╝", "   ██║   ", "   ██║   ", "   ██║   ", "   ╚═╝   "]
_R = ["██████╗  ", "██╔══██╗ ", "██████╔╝ ", "██╔══██╗ ", "██║  ██║ ", "╚═╝  ╚═╝ "]
_A = [" █████╗  ", "██╔══██╗ ", "███████║ ", "██╔══██║ ", "██║  ██║ ", "╚═╝  ╚═╝ "]
_C = [" ██████╗ ", "██╔════╝ ", "██║      ", "██║      ", "╚██████╗ ", " ╚═════╝ "]
_E = ["███████╗ ", "██╔════╝ ", "█████╗   ", "██╔══╝   ", "███████╗ ", "╚══════╝ "]
_K = ["██╗  ██╗ ", "██║ ██╔╝ ", "█████╔╝  ", "██╔═██╗  ", "██║  ██╗ ", "╚═╝  ╚═╝ "]
_I = ["██╗      ", "██║      ", "██║      ", "██║      ", "██║      ", "╚═╝      "]
_L = ["██╗      ", "██║      ", "██║      ", "██║      ", "███████╗ ", "╚══════╝ "]

FONT = {"T": _T, "R": _R, "A": _A, "C": _C, "E": _E, "K": _K, "I": _I, "L": _L}


def build_banner():
    rows = [""] * 6
    for ch in "TRACE KILLER":
        if ch == " ":
            for i in range(6):
                rows[i] += "    "
        elif ch in FONT:
            for i in range(6):
                rows[i] += FONT[ch][i] + " "
    return "\n".join(
        f"{Fore.MAGENTA if i % 2 == 0 else Fore.RED}{Style.BRIGHT}{r}"
        for i, r in enumerate(rows)
    )


BANNER = build_banner() + f"""
{Fore.RED}{Style.BRIGHT}              ═══════════════════════════════════════════════
{Fore.MAGENTA}            ☠️  CYBER INTELLIGENCE & RECON CONSOLE  ☠️
{Fore.RED}                 CODED BY BYPASS-CODE
{Fore.MAGENTA}              ═══════════════════════════════════════════════
{Fore.RED}{Style.BRIGHT}
        ☠️  THIS IS NOT A GAME. THIS IS A WEAPON.  ☠️
        ☠️  USE WISELY. USE ETHICALLY.         ☠️
"""

LINKS = f"""
{Fore.MAGENTA}╔═══════════════════════════════════════════════════════════╗
{Fore.MAGENTA}║{Fore.RED}  ☠️  {Fore.MAGENTA}CONNECT WITH THE DEVIL{Fore.RED}  ☠️                          {Fore.MAGENTA}║
{Fore.MAGENTA}╠═══════════════════════════════════════════════════════════╣
{Fore.MAGENTA}║{Fore.WHITE}  🧠 GitHub    → {Fore.RED}https://github.com/BYPASS-CODEE{Fore.MAGENTA}       ║
{Fore.MAGENTA}║{Fore.WHITE}  📺 YouTube   → {Fore.RED}https://www.youtube.com/@BYPASS_CODEE{Fore.MAGENTA} ║
{Fore.MAGENTA}║{Fore.WHITE}  📸 Instagram → {Fore.RED}https://www.instagram.com/bypass_codee/{Fore.MAGENTA}║
{Fore.MAGENTA}║{Fore.WHITE}  📱 Telegram  → {Fore.RED}https://t.me/BYPASS_CODEE{Fore.MAGENTA}            ║
{Fore.MAGENTA}╚═══════════════════════════════════════════════════════════╝
"""

WARNING = f"""
{Fore.RED}{Style.BRIGHT}╔════════════════════════════════════════════════════════════════╗
{Fore.RED}║{Fore.WHITE}  ☠️  {Fore.RED}W A R N I N G{Fore.WHITE}  ☠️                                       {Fore.RED}║
{Fore.RED}╠════════════════════════════════════════════════════════════════╣
{Fore.RED}║{Fore.WHITE}  THIS TOOL IS FOR EDUCATIONAL & AUTHORIZED TESTING ONLY.     {Fore.RED}║
{Fore.RED}║{Fore.WHITE}  TRACKING / SCANNING WITHOUT PERMISSION IS {Fore.RED}ILLEGAL{Fore.WHITE}.       {Fore.RED}║
{Fore.RED}║{Fore.WHITE}  TEST ONLY YOUR OWN NETWORKS AND PUBLIC INFO.              {Fore.RED}║
{Fore.RED}║{Fore.WHITE}  YOU ARE SOLELY RESPONSIBLE FOR YOUR ACTIONS.              {Fore.RED}║
{Fore.RED}║{Fore.WHITE}  {Fore.RED}DEATH AWAITS THOSE WHO MISUSE THIS TOOL.{Fore.WHITE}              {Fore.RED}║
{Fore.RED}╚════════════════════════════════════════════════════════════════╝
"""

# ═══════════════ SERVICES DB ═══════════════
SERVICES = {
    20: "ftp-data", 21: "ftp", 22: "ssh", 23: "telnet", 25: "smtp", 53: "dns",
    67: "dhcp", 69: "tftp", 80: "http", 110: "pop3", 123: "ntp", 135: "msrpc",
    137: "netbios-ns", 138: "netbios-dgm", 139: "netbios-ssn", 143: "imap",
    161: "snmp", 162: "snmptrap", 389: "ldap", 443: "https", 445: "smb",
    465: "smtps", 514: "syslog", 587: "submission", 636: "ldaps", 873: "rsync",
    993: "imaps", 995: "pop3s", 1080: "socks", 1433: "mssql", 1521: "oracle",
    1723: "pptp", 2049: "nfs", 2181: "zookeeper", 2222: "ssh-alt",
    2375: "docker", 3000: "http-alt", 3128: "squid", 3306: "mysql",
    3389: "rdp", 4369: "erlang", 5000: "upnp", 5060: "sip", 5222: "xmpp",
    5432: "postgresql", 5672: "amqp", 5900: "vnc", 5984: "couchdb",
    6379: "redis", 6443: "kubernetes", 8080: "http-proxy", 8081: "http-alt",
    8443: "https-alt", 8888: "http-alt", 9000: "php-fpm", 9092: "kafka",
    9200: "elasticsearch", 9300: "elasticsearch", 11211: "memcached",
    27017: "mongodb", 27018: "mongodb", 50000: "sap", 50070: "hdfs",
}

# ═══════════════ OUI VENDOR DB ═══════════════
VENDORS = {
    "B827EB": "Raspberry Pi", "DCA632": "Raspberry Pi", "E45F01": "Raspberry Pi",
    "50C7BF": "TP-Link", "14CC20": "TP-Link", "30FC68": "TP-Link",
    "E09971": "TP-Link", "6CE873": "TP-Link", "54AF97": "TP-Link",
    "28107B": "D-Link", "1C7EC5": "D-Link", "3C7D0A": "D-Link",
    "640980": "Xiaomi", "7811DC": "Xiaomi", "8CDEF9": "Xiaomi", "A402B9": "Xiaomi",
    "001A3F": "Samsung", "3CCD93": "Samsung", "080046": "Samsung", "343111": "Samsung",
    "000393": "Apple", "3C0754": "Apple", "5CF9DD": "Apple", "A483E7": "Apple",
    "F01898": "Apple", "C82A14": "Apple", "88665A": "Apple", "FCE8DB": "Apple",
    "001B21": "Intel", "3C970E": "Intel", "98DED0": "Intel", "AC7BA1": "Intel",
    "E0ACCB": "Intel", "A08869": "Intel", "F8A45F": "Intel",
    "00E04C": "Realtek", "001F29": "Realtek", "9C8E99": "Realtek", "04A151": "Realtek",
    "000AF5": "Qualcomm", "446D57": "Qualcomm", "A4B80F": "Qualcomm",
    "000CE7": "MediaTek", "6032B1": "MediaTek", "84FD74": "MediaTek",
    "001C0E": "Huawei", "3C686A": "Huawei", "8C34FD": "Huawei", "04DB56": "Huawei",
    "0019C6": "ZTE", "303152": "ZTE", "0C1DAF": "ZTE",
    "0022B0": "ASUSTek", "F07959": "ASUSTek", "10880F": "ASUSTek",
    "A0F3C1": "Netgear", "7854A0": "Netgear", "9C3DCF": "Netgear",
    "00904C": "Cisco", "001564": "Cisco", "0030F2": "Cisco", "D00C1D": "Cisco",
    "00248C": "Microsoft", "0418D6": "Microsoft", "F8B7E2": "Microsoft",
    "000E8F": "Sony", "00A0DE": "Sony", "A4D18F": "Sony",
    "001E58": "LG", "A0B4A5": "LG", "10474E": "LG",
    "001D7D": "Amazon", "74C246": "Amazon", "9CFFBE": "Amazon", "FC65DE": "Amazon",
    "F0F77B": "Google", "A4C138": "Google", "3C5A37": "Google", "B4EEB4": "Google",
    "00DB70": "Tenda", "C8BE19": "Tenda", "E8B1FC": "Tenda",
}

# ═══════════════ COMMON PORTS ═══════════════
COMMON_PORTS = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 161, 389, 443,
                445, 465, 587, 636, 873, 993, 995, 1080, 1433, 1521, 1723,
                2049, 2181, 2222, 2375, 3000, 3128, 3306, 3389, 5000, 5060,
                5222, 5432, 5672, 5900, 5984, 6379, 6443, 8080, 8081, 8443,
                8888, 9000, 9092, 9200, 9300, 11211, 27017, 27018, 50000, 50070]


# ═══════════════════════════════════════════════════════════
#  CORE CLASS
# ═══════════════════════════════════════════════════════════
class TraceKiller:
    def __init__(self):
        self.log_file = f"trace_killer_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        self.is_windows = platform.system() == "Windows"
        self.known_devices = set()

    # ─────────────── HELPERS ───────────────
    def clear(self):
        os.system("cls" if self.is_windows else "clear")

    def log(self, msg):
        try:
            with open(self.log_file, "a", encoding="utf-8") as f:
                f.write(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}\n")
        except Exception:
            pass

    def header(self, text, color=Fore.MAGENTA):
        print(f"\n{color}{Style.BRIGHT}{'=' * 72}")
        print(f"{Fore.RED}{Style.BRIGHT}☠️ {Fore.WHITE}{Style.BRIGHT}{text.center(68)}{Fore.RED} ☠️")
        print(f"{color}{Style.BRIGHT}{'=' * 72}{Fore.WHITE}")

    def box(self, lines, color=Fore.MAGENTA, title=None):
        w = 72
        print(f"{color}{Style.BRIGHT}╔{'═' * (w - 2)}╗")
        if title:
            print(f"{color}{Style.BRIGHT}║{Fore.WHITE}  {title}{' ' * (w - 4 - len(title))}{color}{Style.BRIGHT}║")
            print(f"{color}{Style.BRIGHT}╠{'═' * (w - 2)}╣")
        for ln in lines:
            clean = re.sub(r"\x1b\[[0-9;]*m", "", str(ln))
            pad = w - 4 - len(clean)
            if pad < 0:
                pad = 0
            print(f"{color}{Style.BRIGHT}║{Fore.WHITE}  {ln}{' ' * pad}{color}{Style.BRIGHT}║")
        print(f"{color}{Style.BRIGHT}╚{'═' * (w - 2)}╝{Fore.WHITE}")

    def run_cmd(self, cmd, timeout=15):
        try:
            return subprocess.run(
                cmd, capture_output=True, text=True, timeout=timeout,
                creationflags=subprocess.CREATE_NO_WINDOW if self.is_windows else 0
            )
        except Exception:
            return None

    def validate_ip(self, ip):
        return bool(re.match(r"^(\d{1,3}\.){3}\d{1,3}$", ip))

    def resolve(self, target):
        try:
            ip = socket.gethostbyname(target)
            return ip, target
        except Exception:
            try:
                ip = socket.gethostbyname_ex(target)
                return ip[2][0], target
            except Exception:
                return None, None

    # ─────────────── SMART INTERFACE DETECTION (v1.1) ───────────────
    def get_local_ip(self):
        """Find the REAL active interface (skip VPN/TUN/virtual adapters)"""
        try:
            if self.is_windows:
                r = self.run_cmd(["ipconfig"], timeout=10)
                if r and r.stdout:
                    blocks = re.split(r"\n(?=[A-Za-z].*adapter )", r.stdout)
                    skip = ["virtual", "tun", "hyper-v", "wsl", "loopback",
                            "bluetooth", "singbox", "tailscale", "wireguard",
                            "vpn", "tap", "default switch", "nordvpn", "openvpn",
                            "proxy", "tunnel", "clash", "v2ray", "nekoray"]
                    best = None
                    for block in blocks:
                        name_m = re.match(r"^(.+?adapter\s+)(.+?):", block)
                        name = name_m.group(2) if name_m else ""
                        low = name.lower()
                        if any(k in low for k in skip):
                            continue
                        ip_m = re.search(r"IPv4 Address[^:]*:\s*([\d.]+)", block)
                        gw_m = re.search(r"Default Gateway[^:]*:\s*([\d.]+)", block)
                        if ip_m and gw_m and gw_m.group(1) != "0.0.0.0":
                            ip = ip_m.group(1)
                            if ip.startswith("169.254"):
                                continue
                            if "wi-fi" in low or "wireless" in low or "ethernet" in low:
                                return ip
                            best = ip
                    if best:
                        return best
            # fallback: UDP method
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def get_public_ip(self):
        if requests is None:
            return "N/A"
        try:
            r = requests.get("http://ip-api.com/json/", timeout=6)
            if r.status_code == 200:
                return r.json().get("query", "N/A")
        except Exception:
            pass
        return "N/A"

    def is_vpn_like(self, ip):
        """Heuristic: common VPN/TUN ranges used by proxies"""
        suspicious = ("172.18.", "172.19.", "172.20.", "172.21.", "172.22.",
                      "172.26.", "10.10.", "10.11.", "10.64.", "10.65.",
                      "100.64.", "100.65.", "100.100.", "100.96.", "25.0.0.")
        return ip.startswith(suspicious)

    # ─────────────── MODULE 1: TRACKER ───────────────
    def ping_host(self, host, count=4):
        print(f"\n{Fore.MAGENTA}📡 PINGING {Fore.RED}{host}{Fore.WHITE}...\n")
        if self.is_windows:
            r = self.run_cmd(["ping", "-n", str(count), host], timeout=30)
        else:
            r = self.run_cmd(["ping", "-c", str(count), host], timeout=30)
        if r and r.stdout:
            for line in r.stdout.splitlines():
                if any(k in line.lower() for k in ["reply from", "bytes=", "time=", "ttl=", "ms", "packet loss", "loss"]):
                    print(f"   {Fore.GREEN}{line.strip()}{Fore.WHITE}")
            return True
        print(f"   {Fore.RED}☠️ PING FAILED / BLOCKED{Fore.WHITE}")
        return False

    def traceroute(self, host, max_hops=15):
        print(f"\n{Fore.MAGENTA}🗺  TRACEROUTE TO {Fore.RED}{host}{Fore.WHITE}...\n")
        if self.is_windows:
            r = self.run_cmd(["tracert", "-h", str(max_hops), host], timeout=60)
        else:
            r = self.run_cmd(["traceroute", "-m", str(max_hops), host], timeout=60)
        if r and r.stdout:
            for line in r.stdout.splitlines():
                stripped = line.strip()
                if not stripped:
                    continue
                print(f"   {Fore.GREEN}{stripped}{Fore.WHITE}")
            print()
            return True
        print(f"   {Fore.RED}☠️ TRACEROUTE FAILED (blocked or unavailable){Fore.WHITE}")
        return False

    def geoip(self, ip):
        print(f"\n{Fore.MAGENTA}🌍 GEOIP LOOKUP → {Fore.RED}{ip}{Fore.WHITE}\n")
        if requests is None:
            self.box(["requests module not installed!", "pip install requests"], Fore.RED)
            return
        try:
            r = requests.get(
                f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,query,reverse,proxy,hosting",
                timeout=8)
            if r.status_code != 200:
                self.box([f"{Fore.RED}API ERROR: HTTP {r.status_code}"], Fore.RED)
                return
            d = r.json()
            if d.get("status") == "fail":
                self.box([f"{Fore.RED}☠️ {d.get('message', 'INVALID IP')}"], Fore.RED)
                return

            lat = d.get("lat", "N/A")
            lon = d.get("lon", "N/A")
            map_lines = [
                f"{Fore.MAGENTA}IP ADDRESS → {Fore.RED}{d.get('query', ip)}",
                f"{Fore.MAGENTA}COUNTRY    → {Fore.RED}{d.get('country', 'N/A')} ({d.get('countryCode', '')})",
                f"{Fore.MAGENTA}REGION     → {Fore.RED}{d.get('regionName', 'N/A')} / {d.get('region', '')}",
                f"{Fore.MAGENTA}CITY       → {Fore.RED}{d.get('city', 'N/A')}",
                f"{Fore.MAGENTA}ZIP CODE   → {Fore.RED}{d.get('zip', 'N/A')}",
                f"{Fore.MAGENTA}COORDS     → {Fore.RED}{lat}, {lon}",
                f"{Fore.MAGENTA}TIMEZONE   → {Fore.RED}{d.get('timezone', 'N/A')}",
                f"{Fore.MAGENTA}ISP        → {Fore.RED}{d.get('isp', 'N/A')}",
                f"{Fore.MAGENTA}ORG        → {Fore.RED}{d.get('org', 'N/A')}",
                f"{Fore.MAGENTA}ASN        → {Fore.RED}{d.get('as', 'N/A')}",
                f"{Fore.MAGENTA}REVERSE    → {Fore.RED}{d.get('reverse', 'N/A')}",
                f"{Fore.MAGENTA}PROXY      → {Fore.RED}{'YES ☠️' if d.get('proxy') else 'NO ✔'}",
                f"{Fore.MAGENTA}HOSTING    → {Fore.RED}{'YES ☠️' if d.get('hosting') else 'NO ✔'}",
            ]
            try:
                lat_f = float(lat)
                lon_f = float(lon)
                emoji = "📍"
                if 35 < lat_f < 42 and 44 < lon_f < 64:
                    emoji = "🔴 IRAN"
                elif lat_f > 0:
                    emoji = "🌍"
                map_lines.append("")
                map_lines.append(f"{Fore.GREEN}🗺  [ {emoji}  {lat_f:.4f}, {lon_f:.4f} ]")
            except Exception:
                pass

            self.box(map_lines, Fore.GREEN, title="TARGET GEOLOCATED ✔")
            self.log(f"GEOIP: {ip} -> {d.get('country', '?')} / {d.get('city', '?')} / {d.get('isp', '?')}")
        except Exception as e:
            self.box([f"{Fore.RED}☠️ GEOIP ERROR: {e}"], Fore.RED)

    def flow_tracker(self):
        self.header("IP / DOMAIN TRACKER", Fore.MAGENTA)
        try:
            target = input(f"\n{Fore.RED}☠️ {Fore.MAGENTA}TARGET (IP or Domain): {Fore.WHITE}").strip()
        except Exception:
            return
        if not target:
            return

        print(f"\n{Fore.RED}☠️ {Fore.MAGENTA}RESOLVING...{Fore.WHITE}")
        ip, host = self.resolve(target)
        if not ip:
            self.box([f"{Fore.RED}☠️ RESOLUTION FAILED: {target}"], Fore.RED)
            return

        self.box([
            f"{Fore.MAGENTA}TARGET     → {Fore.RED}{host}",
            f"{Fore.MAGENTA}RESOLVED   → {Fore.RED}{ip}",
        ], Fore.MAGENTA, title="TARGET LOCKED")
        self.log(f"TRACKER: {target} -> {ip}")

        print(f"\n{Fore.MAGENTA}SELECT ACTION:")
        print(f"   {Fore.RED}☠️ {Fore.WHITE}[1] PING + GEOIP")
        print(f"   {Fore.RED}☠️ {Fore.WHITE}[2] TRACEROUTE + GEOIP")
        print(f"   {Fore.RED}☠️ {Fore.WHITE}[3] FULL RECON (all)")
        try:
            a = input(f"\n{Fore.RED}☠️ {Fore.MAGENTA}CHOICE: {Fore.WHITE}").strip() or "3"
        except Exception:
            a = "3"

        if a in ("1", "3"):
            self.ping_host(ip)
        if a in ("2", "3"):
            self.traceroute(ip)
        self.geoip(ip)
        input(f"\n{Fore.MAGENTA}⏎ {Fore.WHITE}PRESS ENTER TO CONTINUE...{Fore.WHITE}")

    # ─────────────── MODULE 2: NETWORK SCANNER (v1.1) ───────────────
    def vendor_lookup(self, mac):
        if not mac:
            return "Unknown"
        oui = mac.replace(":", "").replace("-", "").upper()[:6]
        return VENDORS.get(oui, "Unknown")

    def get_arp_table(self):
        """Read ARP table, filter multicast/broadcast/zero entries"""
        devices = {}
        r = self.run_cmd(["arp", "-a"], timeout=10)
        if r and r.stdout:
            for line in r.stdout.splitlines():
                parts = line.split()
                for i, p in enumerate(parts):
                    if not self.validate_ip(p):
                        continue
                    ip = p
                    first = int(ip.split(".")[0])
                    if first in (224, 239, 255) or ip.endswith(".255") or ip == "255.255.255.255":
                        continue
                    mac = None
                    for j in (i + 1, i + 2):
                        if j < len(parts) and re.match(r"^([0-9A-Fa-f]{2}[-:]){5}[0-9A-Fa-f]{2}$", parts[j]):
                            mac = parts[j].replace("-", ":").lower()
                            break
                    if mac and mac not in ("ff:ff:ff:ff:ff:ff", "00:00:00:00:00:00"):
                        devices[ip] = mac
        return devices

    def ping_sweep(self, network, threads=64):
        found = {}

        def ping(ip):
            if self.is_windows:
                r = self.run_cmd(["ping", "-n", "1", "-w", "500", ip], timeout=3)
            else:
                r = self.run_cmd(["ping", "-c", "1", "-W", "1", ip], timeout=3)
            return r is not None and r.returncode == 0

        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as ex:
            futures = {ex.submit(ping, f"{network}.{i}"): i for i in range(1, 255)}
            for fut in concurrent.futures.as_completed(futures):
                if fut.result():
                    found[f"{network}.{futures[fut]}"] = None
        return found

    def flow_network_scan(self):
        self.header("NETWORK SCANNER", Fore.MAGENTA)
        local_ip = self.get_local_ip()
        network = ".".join(local_ip.split(".")[:3])

        print(f"\n{Fore.MAGENTA}🌐 LOCAL IP: {Fore.RED}{local_ip}{Fore.WHITE}  →  SCANNING {Fore.RED}{network}.0/24{Fore.WHITE}\n")

        if self.is_vpn_like(local_ip):
            print(f"{Fore.YELLOW}⚠️  WARNING: {local_ip} looks like a VPN/TUN adapter.{Fore.WHITE}")
            print(f"{Fore.YELLOW}   For real results: disconnect VPN/proxy or use your Wi-Fi hotspot.{Fore.WHITE}\n")

        print(f"{Fore.RED}☠️ {Fore.MAGENTA}PING SWEEP IN PROGRESS...{Fore.WHITE}\n")
        live = self.ping_sweep(network)

        print(f"{Fore.RED}☠️ {Fore.MAGENTA}BUILDING ARP MAP...{Fore.WHITE}\n")
        arp_devices = self.get_arp_table()

        # merge: ARP for MACs + ping for live IPs (same subnet only)
        all_ips = {}
        for ip, mac in arp_devices.items():
            if ip.startswith(network + "."):
                all_ips[ip] = mac
        for ip in live:
            if ip not in all_ips:
                all_ips[ip] = None

        if not all_ips:
            self.box([f"{Fore.RED}☠️ NO DEVICES FOUND.", Fore.WHITE + "Check connection / firewall / disable VPN."], Fore.RED)
            return

        print(f"\n{Fore.MAGENTA}{Style.BRIGHT}{'─' * 72}")
        print(f"{Fore.RED}{Style.BRIGHT}☠️ {Fore.WHITE}{'IP':<18}{'MAC ADDRESS':<20}{'VENDOR':<18}{'STATUS':<8}")
        print(f"{Fore.MAGENTA}{Style.BRIGHT}{'─' * 72}{Fore.WHITE}")

        for ip in sorted(all_ips, key=lambda x: [int(p) for p in x.split(".")]):
            mac = all_ips.get(ip)
            vendor = self.vendor_lookup(mac) if mac else "Unknown"
            is_me = "ME ✔" if ip == local_ip else ("ARP" if mac else "PING")
            print(f"{Fore.RED}☠️ {Fore.WHITE}{ip:<18}{str(mac or '—'):<20}{Fore.GREEN}{vendor:<18}{Fore.WHITE}{is_me:<8}")

        print(f"{Fore.MAGENTA}{Style.BRIGHT}{'─' * 72}{Fore.WHITE}")
        self.box([f"{Fore.GREEN}✔ {len(all_ips)} DEVICES FOUND ON {network}.0/24"], Fore.GREEN)
        self.log(f"NETSCAN: {len(all_ips)} devices on {network}.0/24")

        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report = f"netscan_report_{stamp}.txt"
        with open(report, "w", encoding="utf-8") as f:
            f.write(f"TRACE_KILLER NETWORK SCAN REPORT - {datetime.now()}\n")
            f.write(f"Network: {network}.0/24 | Local IP: {local_ip}\n")
            f.write("=" * 50 + "\n")
            for ip in sorted(all_ips, key=lambda x: [int(p) for p in x.split(".")]):
                mac = all_ips.get(ip)
                vendor = self.vendor_lookup(mac) if mac else "Unknown"
                f.write(f"{ip:<18}{str(mac or '—'):<20}{vendor}\n")
        print(f"\n{Fore.MAGENTA}📄 REPORT SAVED → {Fore.RED}{report}{Fore.WHITE}")
        input(f"\n{Fore.MAGENTA}⏎ {Fore.WHITE}PRESS ENTER TO CONTINUE...{Fore.WHITE}")

    # ─────────────── MODULE 3: PORT SCANNER ───────────────
    def scan_port(self, ip, port, timeout=0.4):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            result = s.connect_ex((ip, port))
            s.close()
            return port if result == 0 else None
        except Exception:
            return None

    def flow_port_scan(self):
        self.header("PORT SCANNER", Fore.MAGENTA)
        try:
            target = input(f"\n{Fore.RED}☠️ {Fore.MAGENTA}TARGET IP: {Fore.WHITE}").strip()
        except Exception:
            return
        if not target:
            target = self.get_local_ip()

        ip, _ = self.resolve(target)
        if not ip:
            self.box([f"{Fore.RED}☠️ INVALID TARGET"], Fore.RED)
            return

        print(f"\n{Fore.MAGENTA}SCAN MODE:")
        print(f"   {Fore.RED}☠️ {Fore.WHITE}[1] COMMON PORTS ({len(COMMON_PORTS)} ports)")
        print(f"   {Fore.RED}☠️ {Fore.WHITE}[2] RANGE (start-end)")
        try:
            mode = input(f"\n{Fore.RED}☠️ {Fore.MAGENTA}CHOICE: {Fore.WHITE}").strip() or "1"
        except Exception:
            mode = "1"

        if mode == "2":
            try:
                rng = input(f"{Fore.RED}☠️ {Fore.MAGENTA}RANGE (e.g. 1-1000): {Fore.WHITE}").strip()
                start, end = map(int, rng.split("-"))
                ports = list(range(start, min(end, 65535) + 1))
            except Exception:
                self.box([f"{Fore.RED}☠️ INVALID RANGE"], Fore.RED)
                return
        else:
            ports = COMMON_PORTS

        print(f"\n{Fore.RED}☠️ {Fore.MAGENTA}SCANNING {Fore.RED}{ip}{Fore.MAGENTA} → {Fore.RED}{len(ports)}{Fore.MAGENTA} PORTS...{Fore.WHITE}\n")
        open_ports = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=150) as ex:
            futures = {ex.submit(self.scan_port, ip, p): p for p in ports}
            for fut in concurrent.futures.as_completed(futures):
                p = fut.result()
                if p:
                    open_ports.append(p)
                    svc = SERVICES.get(p, "unknown")
                    print(f"   {Fore.GREEN}✔ PORT {p:<6} OPEN  → {svc}{Fore.WHITE}")

        print(f"\n{Fore.MAGENTA}{Style.BRIGHT}╔{'═' * 62}╗")
        print(f"{Fore.MAGENTA}{Style.BRIGHT}║{Fore.WHITE}  SCAN COMPLETE: {Fore.RED}{len(open_ports)}{Fore.WHITE} OPEN PORTS{' ' * (38 - len(str(len(open_ports))))}{Fore.MAGENTA}║")
        if open_ports:
            for i in range(0, len(open_ports), 3):
                chunk = open_ports[i:i + 3]
                line = "  ".join([f"P{p}" for p in chunk])
                print(f"{Fore.MAGENTA}{Style.BRIGHT}║{Fore.WHITE}  {line:<58}{Fore.MAGENTA}║")
        else:
            print(f"{Fore.MAGENTA}{Style.BRIGHT}║{Fore.RED}  NO OPEN PORTS FOUND.{' ' * 37}{Fore.MAGENTA}║")
        print(f"{Fore.MAGENTA}{Style.BRIGHT}╚{'═' * 62}╝{Fore.WHITE}")

        self.log(f"PORTSCAN: {ip} -> {len(open_ports)} open: {open_ports}")
        input(f"\n{Fore.MAGENTA}⏎ {Fore.WHITE}PRESS ENTER TO CONTINUE...{Fore.WHITE}")

    # ─────────────── MODULE 4: INTRUSION WATCH ───────────────
    def flow_intrusion_watch(self):
        self.header("INTRUSION WATCH — LIVE", Fore.RED)
        print(f"\n{Fore.MAGENTA}👁  MONITORING NETWORK... NEW DEVICE = ALERT{Fore.WHITE}")
        print(f"{Fore.WHITE}PRESS {Fore.RED}CTRL+C{Fore.WHITE} TO STOP\n")

        self.known_devices = set(self.get_arp_table().keys())
        print(f"{Fore.GREEN}✔ BASELINE: {len(self.known_devices)} DEVICES KNOWN{Fore.WHITE}\n")

        try:
            while True:
                current = set(self.get_arp_table().keys())
                new = current - self.known_devices
                gone = self.known_devices - current

                if new:
                    print(f"\n{Fore.RED}{Style.BRIGHT}⚠️  INTRUSION DETECTED — NEW DEVICE JOINED!{Fore.WHITE}")
                    table = self.get_arp_table()
                    for ip in new:
                        mac = table.get(ip, "?")
                        vendor = self.vendor_lookup(mac) if mac else "Unknown"
                        print(f"   {Fore.RED}☠️ {Fore.WHITE}IP: {Fore.RED}{ip}{Fore.WHITE}  MAC: {Fore.RED}{mac}{Fore.WHITE}  VENDOR: {Fore.RED}{vendor}{Fore.WHITE}")
                        self.log(f"INTRUSION: NEW DEVICE {ip} ({mac}) {vendor}")
                    self.known_devices |= new

                if gone:
                    for ip in gone:
                        print(f"   {Fore.YELLOW}⬇  DEVICE LEFT: {ip}{Fore.WHITE}")
                    self.known_devices -= gone

                time.sleep(4)
        except KeyboardInterrupt:
            print(f"\n\n{Fore.RED}☠️ WATCH STOPPED{Fore.WHITE}")
            input(f"\n{Fore.MAGENTA}⏎ {Fore.WHITE}PRESS ENTER TO CONTINUE...{Fore.WHITE}")

    # ─────────────── MODULE 5: RADAR DASHBOARD ───────────────
    def radar_frame(self, angle, devices, label):
        rows = []
        size = 9
        grid = [["  " for _ in range(size)] for _ in range(size)]
        c = size // 2
        grid[c][c] = "◎"

        for i, (ip, mac) in enumerate(devices.items()):
            if i >= 6:
                break
            r = (i % 3) + 1
            a = (angle + i * 97) % 360
            rad = math.radians(a)
            x = c + int(round(r * math.cos(rad)))
            y = c + int(round(r * math.sin(rad)))
            if 0 <= x < size and 0 <= y < size:
                grid[y][x] = "●"

        rad = math.radians(angle)
        for dist in range(1, c + 1):
            x = c + int(round(dist * math.cos(rad)))
            y = c + int(round(dist * math.sin(rad)))
            if 0 <= x < size and 0 <= y < size:
                if grid[y][x] == "  ":
                    grid[y][x] = "·"

        radar = "\n".join(f"     {Fore.GREEN}{' '.join(row)}{Fore.WHITE}" for row in grid)

        sys_info = []
        try:
            import psutil
            sys_info.append(f"CPU   {psutil.cpu_percent():>4.0f}%")
            sys_info.append(f"RAM   {psutil.virtual_memory().percent:>4.0f}%")
        except ImportError:
            sys_info.append("CPU   N/A")
            sys_info.append("RAM   N/A (pip install psutil)")

        os_name = platform.system()
        sys_info.append(f"OS    {os_name:<6} {platform.release()}")
        sys_info.append(f"LOCAL {self.get_local_ip()}")
        sys_info.append(f"PUB   {self.get_public_ip()}")

        panel = f"""
{Fore.MAGENTA}{Style.BRIGHT}╔══════════════════════════════════════════════════╗
{Fore.MAGENTA}{Style.BRIGHT}║{Fore.RED}  ☠️  {Fore.WHITE}RADAR // {label}{' ' * (36 - len(label))}{Fore.MAGENTA}║
{Fore.MAGENTA}{Style.BRIGHT}╠══════════════════════════════════════════════════╣"""
        for s in sys_info:
            pad = 50 - len(s)
            panel += f"\n{Fore.MAGENTA}{Style.BRIGHT}║{Fore.WHITE}  {s}{' ' * pad}{Fore.MAGENTA}║"
        panel += f"""
{Fore.MAGENTA}{Style.BRIGHT}║{' ' * 50}║
{Fore.MAGENTA}{Style.BRIGHT}║{Fore.GREEN}  DEVICES ON RADAR: {len(devices)}{' ' * (31 - len(str(len(devices))))}{Fore.MAGENTA}║
{Fore.MAGENTA}{Style.BRIGHT}╚══════════════════════════════════════════════════╝"""

        return radar + "\n" + panel

    def flow_radar(self):
        self.header("RADAR DASHBOARD", Fore.MAGENTA)
        print(f"\n{Fore.WHITE}PRESS {Fore.RED}CTRL+C{Fore.WHITE} TO STOP\n")
        try:
            devices = self.get_arp_table()
            angle = 0
            while True:
                if angle % 360 == 0:
                    devices = self.get_arp_table()
                frame = self.radar_frame(angle, devices, "NETWORK SCAN")
                print("\033[H\033[J", end="")
                print(BANNER.split("\n")[0])
                print(frame)
                angle = (angle + 8) % 360
                time.sleep(0.1)
        except KeyboardInterrupt:
            print(f"\n\n{Fore.RED}☠️ RADAR STOPPED{Fore.WHITE}")
            input(f"\n{Fore.MAGENTA}⏎ {Fore.WHITE}PRESS ENTER TO CONTINUE...{Fore.WHITE}")

    # ─────────────── MAIN MENU ───────────────
    def run(self):
        while True:
            self.clear()
            print(BANNER)
            print(LINKS)
            print(WARNING)

            local = self.get_local_ip()
            pub = self.get_public_ip()

            print(f"\n{Fore.MAGENTA}{Style.BRIGHT}╔{'═' * 70}╗")
            print(f"{Fore.MAGENTA}{Style.BRIGHT}║{Fore.RED}  ☠️  {Fore.WHITE}MAIN MENU{Fore.RED}  ☠️{' ' * 51}{Fore.MAGENTA}║")
            print(f"{Fore.MAGENTA}{Style.BRIGHT}╠{'═' * 70}╣")
            print(f"{Fore.MAGENTA}{Style.BRIGHT}║{Fore.WHITE}  [1] 🎯 IP / DOMAIN TRACKER  (ping · trace · geoip){Fore.MAGENTA}║")
            print(f"{Fore.MAGENTA}{Style.BRIGHT}║{Fore.WHITE}  [2] 📡 NETWORK SCANNER      (devices · vendors){Fore.MAGENTA}║")
            print(f"{Fore.MAGENTA}{Style.BRIGHT}║{Fore.WHITE}  [3] 🔌 PORT SCANNER         (concurrent · services){Fore.MAGENTA}║")
            print(f"{Fore.MAGENTA}{Style.BRIGHT}║{Fore.WHITE}  [4] 👁  INTRUSION WATCH      (live new-device alerts){Fore.MAGENTA}║")
            print(f"{Fore.MAGENTA}{Style.BRIGHT}║{Fore.WHITE}  [5] 📡 RADAR DASHBOARD      (animated sweep){Fore.MAGENTA}║")
            print(f"{Fore.MAGENTA}{Style.BRIGHT}║{Fore.WHITE}  [0] 💀 EXIT{Fore.MAGENTA}║")
            print(f"{Fore.MAGENTA}{Style.BRIGHT}╠{'═' * 70}╣")
            print(f"{Fore.MAGENTA}{Style.BRIGHT}║{Fore.WHITE}  🌐 LOCAL: {Fore.RED}{local:<18}{Fore.WHITE}  🌍 PUBLIC: {Fore.RED}{pub:<18}{Fore.MAGENTA}║")
            print(f"{Fore.MAGENTA}{Style.BRIGHT}╚{'═' * 70}╝{Fore.WHITE}")

            try:
                choice = input(f"\n{Fore.RED}☠️ {Fore.MAGENTA}SELECT: {Fore.WHITE}").strip()
            except Exception:
                choice = "0"

            if choice == "1":
                self.flow_tracker()
            elif choice == "2":
                self.flow_network_scan()
            elif choice == "3":
                self.flow_port_scan()
            elif choice == "4":
                self.flow_intrusion_watch()
            elif choice == "5":
                self.flow_radar()
            else:
                break

        print(f"\n{Fore.RED}☠️ {Fore.WHITE}BYE. STAY DANGEROUS.{Fore.WHITE}\n")


if __name__ == "__main__":
    try:
        TraceKiller().run()
    except KeyboardInterrupt:
        print(f"\n\n{Fore.RED}☠️ PROGRAM TERMINATED{Fore.WHITE}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Fore.RED}☠️ ERROR: {e}{Fore.WHITE}")
        sys.exit(1)