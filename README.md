# speedtest-statistics
A CLI and SQLite3 based Python utility that checks your Internet connection speed via [Speedtest.net](https://speedtest.net), then saves information to database for further analysis. Also keeps some info about your hardware and local network.

## How does it work
To start:

```shell
python3 run.py
```

![Checking in progress](https://github.com/trankov/speedtest-statistics/blob/main/readmefiles/speedtest.gif?raw=true)

Then Speedtest begins to work as so as in web interface or mobile/desktop application, but in terminal.

The utility uses double check for greater clarity.

1. First, it checks connection speed using built-in «best server» algorythm. This way based on looking for nearest server with presumably minimum latency.
2. Second, it chooses a random server from the possible options list, then checking connection again.

These two sessions have a different boolean mark in the database for later convinience.

After both checks completed, it shows general info, then store huge information in the database. Actually it keeps 41 parameter for every session (one check consists of two sessions, a «best» one and a «random» one).

![Checking complete](https://github.com/trankov/speedtest-statistics/blob/main/readmefiles/terminal2.png?raw=true)

## Preliminary warnings
1. No Python 2 supported. Let dead bury their own dead.
2. Several parts of statistics scraping from third-party websites. Author cannot guarantee they always be available.
3. The status of the project is :toilet: **work-in-progress**. There is no _alfa_, _beta_ or any other release level. Nevertheless on this fact, you are free to fork it for manual improvement or use as you want — at your own risk, as is.
4. Author well realise that code have to be refactored and tested.

## Requirements

All code exept of official [Speedtest](https://speedtest.net) `speedtest-cli` module works under Python Standard Library (stdlib).

Use `pip install speedtest-cli` or other methods as described in [official repository](https://github.com/sivel/speedtest-cli).

Library version used: `speedtest-cli==2.1.3`

## Database issues
The utility uses two different databases.

**The first one** is nessesary for fast searching of your network hardware manufacturer, using [IEEE OUI](https://en.wikipedia.org/wiki/Organizationally_unique_identifier). You'll find it in `oui.db` file.

Use the `download.py` script for maintaining OUI Database if you want to update vendor's list or if you lost this file for any cause.

```shell
python3 download.py
```
This command automatically download last version of [OUI IEEE list](http://standards-oui.ieee.org) from the Web and place items into database. If database file does not exists, it will be created.

**The second one** stores full information about speed-checking sessions. It contains 41 parameter for each check.
```python
 best: bool             # whether test server best (True) or random (False)
 download: float        # download speed
 upload: float          # upload speed
 ping: float            # ping value
 url: str               # test url
 test_lat: float        # test server latitude
 test_lon: float        # test server longitude
 test_name: str         # test server name
 test_country: str      # test server country
 test_cc: str           # test server 2-letters country code
 sponsor: str           # test server sponsor
 test_id: int           # test server id
 test_host: int         # test host id
 d: float               # param d from Speedtest report
 latency: float         # latency value
 timestamp: str         # 2021-05-23T15:52:54.399142Z
 bytes_sent: int
 bytes_received: int
 client_ip: str         # ↕︎ - the same as param name - ↕︎
 client_lat: float
 client_lon: float
 client_isp: str        # name of internet provider
 client_country: str    # 2-letters country code
 ip_remote: str         # host ip address from outside
 ip_local: str          # host ip address in local network
 name_remote: str       # host name from outside
 name_local: str        # host name in local network
 city: str              # host city name for public ip address
 region: str            # the same but region
 country: str           # the same but country
 timezone: str          # the same but timezone
 public_ip_lat: float   # latitude for public ip address
 public_ip_lon: float   # longitude for public ip address
 organization: str      # the public ip owner
 postal: str            # postal code of organization above
 vendor: str            # hardware manufacturer
 oui_hex: str           # hardware hex oui
 oui_base16: str        # hardware base16 oui
 vendor_address: str    # hardware vendor address
 mac_address: str       # hardware mac address (hex)
 unixtime: str          # timestamp of transaction
```
Every checking session (everytime you run the utility) consists of two checks and provides two table rows: for the «best» and for the «random» ones.

If `speedtest.db` does not exists, it will be created automatically.

**NB:** Data is intentionally written to one table, no related tables. This is because the most of parameters are potentially variable and may change independently and unpredictable.

## Well, then?
There are plenty of ways to use one-table organized data, from [GUI clients](https://yandex.com/search/?text=sqlite%20gui%20clients) to frameworks such as [Pandas](https://pandas.pydata.org). Even [MS Excel](https://www.microsoft.com/ru-ru/microsoft-365/excel) or [Google Sheets](https://sheets.google.com) are applicable.

Use [Notebook](https://jupyter.org/) for analyse and plot data. Or connect the database to [Tableu](https://www.tableau.com/) for constructing reports. Author don't planning to reinvent BI tools or instruments for Pivot tables. The ready ones are perfect, necessary and sufficient
