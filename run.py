import random
import json
import os
import re
import socket
import sqlite3
import uuid

from dataclasses import dataclass
from datetime import datetime
from urllib.request import urlopen
from pathlib import Path

from speedtest import Speedtest

CURDIR = Path(__file__).parent

@dataclass
class Vendor(object):
    '''Contains vendor info from mac-address.

    NOTE: Run `download.py` to update OUI database from time to time

    Usage examples:
     >>> vendor = Vendor()
     >>> vendor.oui = 'e09467'
     >>> print (vendor.address_list()[-1])
     >>> # prints 2-signs country code or None
    or
     >>> vendor = Vendor('e09467')
     >>> print (vendor.name())
     >>> # prints vendor for mac-address if found or None
    or
     >>> vendor = Vendor()
     >>> print (vendor.name())
     >>> # prints vendor for mac-address in current system or None

    '''

    oui: str = hex(uuid.getnode())[2:8]
    dbname: str = Path(CURDIR) / 'oui.db'

    def __post_init__(self):
        self.con = sqlite3.connect(self.dbname)

    def _sqlite(self):
        cur = self.con.cursor()
        query = cur.execute('SELECT * FROM vendors WHERE vendors.base16 = ?', (self.oui.upper(),))
        answer = query.fetchall()
        return answer[0] if answer else (None, None, None, None, None)

    def name(self) -> str:
        return self._sqlite()[4] # Or [3], it's the same
    def address(self) -> str:
        return self._sqlite()[5]
    def address_line(self, repl=', ') -> str:
        n = self._sqlite()
        return n[5].replace('\n', repl) if n[5] else None
    def address_list(self) -> list:
        n = self._sqlite()
        return n()[5].split('\n') if n[5] else None
    def everything(self) -> list:
        return self._sqlite()
    def oui_hex(self) -> str:
        return self._sqlite()[1]
    def oui_base16(self) -> str:
        return self._sqlite()[2]
    def __del__(self):
        self.con.close()
        del self.con



@dataclass
class Host(object):
    '''Contains info about host in local network and from outside.

     ip_remote: str      ip address from outside
     ip_local: str       ip address in local network
     name_remote: str    host name from outside
     name_local: str     host name in local network
     city: str           city name for public ip address
     region: str         the same but region
     country: str        the same but country
     timezone: str       the same but timezone
     location: list      latitude and longitude for public ip address
     organization: str   the public ip owner
     postal: str         postal code of organization above

    Usage examples:
     >>> print(Host().location)

     >>> host = Host()
     >>> print(host.ip_local)

    '''

    def _get_ip():
        '''Get IP address from http://dydns.com for `class Host()`'''

        # Third-party website dependency, be careful
        html = urlopen('http://checkip.dyndns.com/').read().decode('utf-8')
        return re.findall(r'\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}', html)[0]

    ip_remote: str = _get_ip()

    def _get_ip_info(ip_remote):
        '''Get info for public IP from http://ipinfo.io for `class Host()`'''

        # Third-party website dependency, be careful
        info = urlopen('http://ipinfo.io/{}/json'.format(ip_remote)
                       ).read().decode('utf-8')
        return json.loads(info)

    ip_info = _get_ip_info(ip_remote)

    name_local: str = socket.gethostname()
    ip_local: str = socket.gethostbyname(socket.gethostname())
    name_remote: str = ip_info['hostname']
    city: str = ip_info['city']
    region: str = ip_info['region']
    country: str = ip_info['country']
    location = ip_info['loc'].split(',')
    org: str = ip_info['org']
    postal: str = ip_info['postal']
    timezone: str = ip_info['timezone']



def save_statistics(stats: dict, best: bool, dbname: str = 'speedtest.db') -> bool:
    '''Save `Speedtest()` and other statistics to sqlite3 `dbname` database.

    `TABLE` fields are:
     best: bool             whether test server best (True) or random (False)
     download: float        download speed
     upload: float          upload speed
     ping: float            ping value
     url: string            test url
     test_lat: float        test server latitude
     test_lon: float        test server longitude
     test_name: str         test server name
     test_country: str      test server country
     test_cc: str           test server 2-letters country code
     sponsor: str           test server sponsor
     test_id: int           test server id
     test_host: int         test host id
     d: float               param d from Speedtest report (jitter?)
     latency: float         latency value
     timestamp: str         2021-05-23T15:52:54.399142Z
     bytes_sent: int
     bytes_received: int
     client_ip: str         ↕︎ - the same as param name - ↕︎
     client_lat: float
     client_lon: float
     client_isp: str        name of internet provider
     client_country: str    2-letters country code
     ip_remote: str         host ip address from outside
     ip_local: str          host ip address in local network
     name_remote: str       host name from outside
     name_local: str        host name in local network
     city: str              host city name for public ip address
     region: str            the same but region
     country: str           the same but country
     timezone: str          the same but timezone
     public_ip_lat: float   latitude for public ip address
     public_ip_lon: float   longitude for public ip address
     organization: str      the public ip owner
     postal: str            postal code of organization above
     vendor: str            hardware manufacturer
     oui_hex: str           hardware hex oui
     oui_base16: str        hardware base16 oui
     vendor_address: str    hardware vendor address
     mac_address: str       hardware mac address (hex)
     unixtime: str          timestamp of transaction
    '''

    sqlite3.paramstyle = 'named'
    con = sqlite3.connect(Path(CURDIR) / dbname)
    cur = con.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS sessions
                       (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        best INTEGER NOT NULL,
                        download REAL NOT NULL,
                        upload REAL NOT NULL,
                        ping REAL NOT NULL,
                        url TEXT NOT NULL,
                        test_lat REAL NOT NULL,
                        test_lon REAL NOT NULL,
                        test_name TEXT NOT NULL,
                        test_country TEXT NOT NULL,
                        test_cc TEXT NOT NULL,
                        sponsor TEXT NOT NULL,
                        test_id INTEGER NOT NULL,
                        test_host INTEGER NOT NULL,
                        d REAL NOT NULL,
                        latency REAL NOT NULL,
                        timestamp TEXT NOT NULL,
                        bytes_sent INTEGER NOT NULL,
                        bytes_received INTEGER NOT NULL,
                        client_ip TEXT NOT NULL,
                        client_lat REAL NOT NULL,
                        client_lon REAL NOT NULL,
                        client_isp TEXT NOT NULL,
                        client_country TEXT NOT NULL,
                        ip_remote TEXT NOT NULL,
                        ip_local TEXT NOT NULL,
                        name_remote TEXT NOT NULL,
                        name_local TEXT NOT NULL,
                        city TEXT NOT NULL,
                        region TEXT NOT NULL,
                        country TEXT NOT NULL,
                        timezone TEXT NOT NULL,
                        public_ip_lat REAL NOT NULL,
                        public_ip_lon REAL NOT NULL,
                        organization TEXT NOT NULL,
                        postal TEXT NOT NULL,
                        vendor TEXT NOT NULL,
                        oui_hex TEXT NOT NULL,
                        oui_base16 TEXT NOT NULL,
                        vendor_address TEXT NOT NULL,
                        mac_address TEXT NOT NULL,
                        unixtime REAL NOT NULL
                        );''')

    vendor = Vendor()
    host = Host()
    # Get MAC Address in 1A:2B:3C:4D:5E:6F format
    mc_hex: str = hex(uuid.getnode())[2:].upper()
    macaddress: str = ":".join(mc_hex[i:i+2] for i in range(0, len(mc_hex), 2))

    update_values = {
        'best': best,
        'download': stats['download'],
        'upload': stats['upload'],
        'ping': stats['ping'],
        'url': stats['server']['url'],
        'test_lat': stats['server']['lat'],
        'test_lon': stats['server']['lon'],
        'test_name': stats['server']['name'],
        'test_country': stats['server']['country'],
        'test_cc': stats['server']['cc'],
        'sponsor': stats['server']['sponsor'],
        'test_id': stats['server']['id'],
        'test_host': stats['server']['host'],
        'd': stats['server']['d'],
        'latency': stats['server']['latency'],
        'timestamp': stats['timestamp'],
        'bytes_sent': stats['bytes_sent'],
        'bytes_received': stats['bytes_received'],
        'client_ip': stats['client']['ip'],
        'client_lat': stats['client']['lat'],
        'client_lon': stats['client']['lon'],
        'client_isp': stats['client']['isp'],
        'client_country': stats['client']['country'],
        'ip_remote': host.ip_remote,
        'ip_local': host.ip_local,
        'name_remote': host.name_remote,
        'name_local': host.name_local,
        'city': host.city,
        'region': host.region,
        'country': host.country,
        'timezone': host.timezone,
        'public_ip_lat': host.location[0],
        'public_ip_lon': host.location[1],
        'organization': host.org,
        'postal': host.postal,
        'vendor': vendor.name(),
        'oui_hex': vendor.oui_hex(),
        'oui_base16': vendor.oui_base16(),
        'vendor_address': vendor.address(),
        'mac_address': macaddress,
        'unixtime': datetime.now().timestamp()
    }

    cur.execute('''INSERT INTO sessions (best, download, upload, ping, url, test_lat, test_lon, test_name, test_country, test_cc, sponsor, test_id, test_host, d, latency, timestamp, bytes_sent, bytes_received, client_ip, client_lat, client_lon, client_isp, client_country, ip_remote, ip_local, name_remote, name_local, city, region, country, timezone, public_ip_lat, public_ip_lon, organization, postal, vendor, oui_hex, oui_base16, vendor_address, mac_address, unixtime) VALUES (:best, :download, :upload, :ping, :url, :test_lat, :test_lon, :test_name, :test_country, :test_cc, :sponsor, :test_id, :test_host, :d, :latency, :timestamp, :bytes_sent, :bytes_received, :client_ip, :client_lat, :client_lon, :client_isp, :client_country, :ip_remote, :ip_local, :name_remote, :name_local, :city, :region, :country, :timezone, :public_ip_lat, :public_ip_lon, :organization, :postal, :vendor, :oui_hex, :oui_base16, :vendor_address, :mac_address, :unixtime)''', update_values)

    con.commit()
    con.close()

class ProgressLine(object):
    '''Controls progress bar for multitreading requests'''
    def __init__(self):
        self.status = {
                'start': '\033[48;5;227m \033[0m',
                'end': '\033[0;0;42m \033[0m',
                'empty': '\033[48;5;160m \033[0m'
            }
        self._line = []

    @property
    def line(self):
        return self._line
    @line.setter
    def line(self, value: int):
        '''Initialize progress bar only once, emulating singleton'''
        if self._line == []:
            self._line = [self.status['empty']] * value
        # return self._line

    def update(self, idx, count, **kwargs):
        '''Fill cell `idx`:_int_ with `state`:_str_ via `self.status`:_dict_'''

        if self._line == []:
            self._line = [self.status['empty']] * count

        state = list(kwargs.keys())[0]
        self._line[idx] = self.status[state]
        self.show()

    def show(self):
        print ('\r' + self.__str__(), end='')

    def reset(self):
        self._line = []
        print()

    def __str__(self):
        return ''.join(self._line)

    def __repr__(self):
        return ''.join(self._line)

def print_res(results):
    print('  Download: \033[4m{} Mbit/s\033[0m, Upload: \033[4m{} Mbit/s\033[0m, Ping: \033[4m{} ms\033[0m.\n  Provider: \033[38;5;198m{}, {}, {}\033[0m\n'\
        .format(
            *[round(results[i] * 7.6294E-7, 2) for i in ['download', 'upload', 'ping']],
            # round(results['download'] * 7.6294E-7, 2),
            # round(results['upload'] * 7.6294E-7, 2),
            # round(results['ping'] * 7.6294E-7, 2),

            results['server']['sponsor'],
            results['server']['name'],
            results['server']['country']
            )
        )


if __name__ == '__main__':
    import sys

    speedtest = Speedtest()
    srv = speedtest.get_servers()
    rand_idx = random.choice(list(srv.keys()))
    line = ProgressLine()

    print('\n\033[48;5;197m\033[38;5;220m',
          'Start Speedtest...'.center(65),
          '\033[0;0;m\n',
          sep=''
        )

    # test at best server

    print('  \N{LONG RIGHTWARDS ARROW}  Test download speed from a best server...')
    speedtest.get_best_server()
    speedtest.download(callback=line.update)
    line.reset()

    print('  \N{LONG LEFTWARDS ARROW}  Test upload speed at best server...')
    speedtest.upload(callback=line.update)
    line.reset()

    res_best = speedtest.results.dict()
    print('\n\033[38;5;51mTest speed at best server finished.\033[0m')
    print_res(res_best)

    del speedtest
    speedtest = Speedtest()

    # test at random server

    speedtest.get_servers([srv[rand_idx][0]['id']])

    print('  \N{LONG RIGHTWARDS ARROW}  Test download speed from a random server...')
    speedtest.download(callback=line.update)
    line.reset()

    print('  \N{LONG LEFTWARDS ARROW}  Test upload speed at random server...')
    speedtest.upload(callback=line.update)
    line.reset()

    res_rand = speedtest.results.dict()
    print('\n\033[38;5;51mTest speed at random server finished.\033[0m')
    print_res(res_rand)

    print('Save statistics...')
    save_statistics(stats=res_best, best=True)
    save_statistics(stats=res_rand, best=False)
    print('Statistics saved.')
    print('_'*65)

    # 223710922.210356 * 7.6294E-7 == 170.678010991169
