# import sys
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


def generate_sql(update_values: dict) -> str:
    '''Generate table creation SQL for statistics'''

    # Matching data types Python -> SQLite3
    sql_types = {
        str: "TEXT",
        float: "REAL",
        bool: "INTEGER",
        int: "INTEGER"
    }

    # Making the request string, then return it
    rq: str = ',\n\t'.join('{:<15} {} NOT NULL'.format(
                        k, sql_types[type(v)]) for k, v in update_values.items())

    return 'CREATE TABLE IF NOT EXISTS sessions\n\t' + \
         '(\n\tid INTEGER PRIMARY KEY AUTOINCREMENT,\n\t' + rq + '\n\t);'


def save_statistics(stats: dict, best: bool, dbname: str = 'speedtest.db') -> bool:
    '''Save `Speedtest()` and other statistics to sqlite3 `dbname` database.

    For detailed fields description see `sqlite_strusture.md` document at:
    https://github.com/trankov/speedtest-statistics/blob/main/sqlite_strusture.md

    '''

    # Collecting info about related context
    vendor: object = Vendor()
    host: object = Host()
    # Get MAC Address in 1A:2B:3C:4D:5E:6F format
    mc_hex: str = hex(uuid.getnode())[2:].upper()
    macaddress: str = ":".join(mc_hex[i:i+2] for i in range(0, len(mc_hex), 2))

    # Prepare the data structures

    # Description of the data to be stored
    # We also use explicit type conversion, because all data comes anyhow
    update_values = {
        'best': bool (best),
        'download': float (stats['download']),
        'upload': float (stats['upload']),
        'ping': float (stats['ping']),
        'url': str (stats['server']['url']),
        'test_lat': float (stats['server']['lat']),
        'test_lon': float (stats['server']['lon']),
        'test_name': str (stats['server']['name']),
        'test_country': str (stats['server']['country']),
        'test_cc': str (stats['server']['cc']),
        'sponsor': str (stats['server']['sponsor']),
        'test_id': int (stats['server']['id']),
        'test_host': str (stats['server']['host']),
        'd': float (stats['server']['d']),
        'latency': float (stats['server']['latency']),
        'timestamp': str (stats['timestamp']),
        'bytes_sent': int (stats['bytes_sent']),
        'bytes_received': int (stats['bytes_received']),
        'client_ip': str (stats['client']['ip']),
        'client_lat': float (stats['client']['lat']),
        'client_lon': float (stats['client']['lon']),
        'client_isp': str (stats['client']['isp']),
        'client_country': str (stats['client']['country']),
        'ip_remote': str (host.ip_remote),
        'ip_local': str (host.ip_local),
        'name_remote': str (host.name_remote),
        'name_local': str (host.name_local),
        'city': str (host.city),
        'region': str (host.region),
        'country': str (host.country),
        'timezone': str (host.timezone),
        'public_ip_lat': float (host.location[0]),
        'public_ip_lon': float (host.location[1]),
        'organization': str (host.org),
        'postal': str (host.postal),
        'vendor': str (vendor.name()),
        'oui_hex': str (vendor.oui_hex()),
        'oui_base16': str (vendor.oui_base16()),
        'vendor_address': str (vendor.address()),
        'mac_address': str (macaddress),
        'unixtime': float (datetime.now().timestamp())
    }

    sqlite3.paramstyle = 'named' # for better matching and security reasons
    con = sqlite3.connect(Path(CURDIR) / dbname)
    cur = con.cursor()

    # Create database file and table if they don't exist
    sql_table = generate_sql(update_values)
    cur.execute(sql_table)

    # Save statistics to database.sessions table
    sql_request = '''INSERT INTO sessions ({}) VALUES ({})'''.format(
        ', '.join(update_values),
        ', '.join(f':{i}' for i in update_values)
    )
    cur.execute(sql_request, update_values)

    # cur.execute('''INSERT INTO sessions (best, download, upload, ping, url, test_lat, test_lon, test_name, test_country, test_cc, sponsor, test_id, test_host, d, latency, timestamp, bytes_sent, bytes_received, client_ip, client_lat, client_lon, client_isp, client_country, ip_remote, ip_local, name_remote, name_local, city, region, country, timezone, public_ip_lat, public_ip_lon, organization, postal, vendor, oui_hex, oui_base16, vendor_address, mac_address, unixtime) VALUES (:best, :download, :upload, :ping, :url, :test_lat, :test_lon, :test_name, :test_country, :test_cc, :sponsor, :test_id, :test_host, :d, :latency, :timestamp, :bytes_sent, :bytes_received, :client_ip, :client_lat, :client_lon, :client_isp, :client_country, :ip_remote, :ip_local, :name_remote, :name_local, :city, :region, :country, :timezone, :public_ip_lat, :public_ip_lon, :organization, :postal, :vendor, :oui_hex, :oui_base16, :vendor_address, :mac_address, :unixtime)''', update_values)

    con.commit()
    con.close()

class ProgressLine(object):
    '''Controls progress bar for multitreading requests'''

    def __init__(self):
        self.status = {
                'start': '\033[48;5;227m \033[0m', # yellow space
                'end': '\033[0;0;42m \033[0m',     # green space
                'empty': '\033[48;5;160m \033[0m'  # red space
            }
        self._line = []

    @property
    def line(self):
        return self._line
    @line.setter
    def line(self, value: int):
        '''Just in case. Unnessessary but usefull.'''
        if self._line == []:
            self._line = [self.status['empty']] * value
        return self._line

    def update(self, idx, count, **kwargs):
        '''Marks cells in progress bar.

        Actually callback format is not documented and don't mentioned
        in official documentation, but nevertheless it is available for use.
        Callback getting tuple `(int, int)` and one positional argument,
        which can be `start = True` or `end = True`. First int valued a current
        request, second int contains total number of requests (always the same).

        '''

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

def print_res(results: dict):
    '''Puts out formatted report about the speed test'''

    print('  Download: \033[4m{} Mbit/s\033[0m, Upload: \033[4m{} Mbit/s\033[0m, Ping: \033[4m{} ms\033[0m.\n  Provider: \033[38;5;198m{}, {}, {}\033[0m\n'\
        .format(
            *[round(results[i] / 1048576, 2) for i in ['download', 'upload', 'ping']],
            results['server']['sponsor'],
            results['server']['name'],
            results['server']['country']
            )
        )


if __name__ == '__main__':

    # Initialization of progress bar
    line = ProgressLine()

    # Get the list of optional servers for further testing.
    speedtest = Speedtest()
    srv = speedtest.get_servers()

    # Put out the main header
    print('\n\033[48;5;197m\033[38;5;220m',
          'Start Speedtest...'.center(65),
          '\033[0;0;m\n',
          sep=''
        )

    # test at closest ("best") server

    speedtest.get_best_server()

    # Testing download
    print('  \N{LONG RIGHTWARDS ARROW}  Test download speed from the best server...')
    speedtest.download(callback=line.update)
    line.reset()

    # Testing upload
    print('  \N{LONG LEFTWARDS ARROW}  Test upload speed at the best server...')
    speedtest.upload(callback=line.update)
    line.reset()

    # Memorize the results for database, then show them
    res_best = speedtest.results.dict()
    print('\n\033[38;5;51mTest speed at best server finished.\033[0m')
    print_res(res_best)



    # test at random server

    # object have to be reinitialized for changing the test server
    # due to the peculiarities of the official library
    del speedtest
    speedtest = Speedtest()

    # Now get the random server id
    rand_idx = random.choice(list(srv.keys()))
    if isinstance(srv[rand_idx], list):
       srv_id = srv[rand_idx][0]['id']
    else:
        srv_id = srv[rand_idx]['id']

    speedtest.get_servers([srv_id])

    # Testing download
    print('  \N{LONG RIGHTWARDS ARROW}  Test download speed from the random server...')
    speedtest.download(callback=line.update)
    line.reset()

    # Testing upload
    print('  \N{LONG LEFTWARDS ARROW}  Test upload speed at the random server...')
    speedtest.upload(callback=line.update)
    line.reset()

    res_rand = speedtest.results.dict()
    print('\n\033[38;5;51mTest speed at random server finished.\033[0m')
    print_res(res_rand)

    print('Save statistics...')
    save_statistics(stats=res_best, best=True, dbname='test.db')
    save_statistics(stats=res_rand, best=False, dbname='test.db')
    print('Statistics saved.')
    print('_'*65)

# END
