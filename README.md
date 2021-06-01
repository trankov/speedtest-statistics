# speedtest-statistics
A Command-line interface utility that checks your Internet connection speed via [Speedtest.net](https://speedtest.net), while shows coloured process and testing report. Usefull for ssh administration or automated speed monitoring. The utility saves information to SQLite3 database for further analysis. Also keeps some info about your hardware and local network. Written in Python.

## How does it work
To start:

```shell
python3 run.py
```

![Checking in progress](https://github.com/trankov/speedtest-statistics/blob/main/readmefiles/speedtest.gif?raw=true)

It works similar to web or applications interface, but in terminal. Progress bar shows planned requests as red, current requests as yellow and finished requests as green. The progress bars are not hystograms! For evaluation use report below the progress bars.

The utility uses double check for greater clarity.

1. First, it checks connection speed using built-in «best server» algorythm. This way based on looking for nearest server with presumably minimum latency.
2. Second, it chooses a random server from the possible options list, then checking connection again.

These two sessions have a different boolean mark in the database for later convinience.

Example of full report:

![Checking complete](https://github.com/trankov/speedtest-statistics/blob/main/readmefiles/terminal2.png?raw=true)

## Preliminary warnings
1. No Python 2 supported. Let dead bury their own dead.
2. Several parts of statistics scraping from third-party websites. Report me if something wrong, and I'll fix it.
3. Rolling deployment model. No _alfa_, _beta_ or any other release level.

## Requirements

All code exept of official [Speedtest](https://speedtest.net) `speedtest-cli` module works under Python Standard Library (stdlib) and don't need other additional setup.

Install the library before usage:
```sh
pip install speedtest-cli==2.1.3
```
Other methods described in [official repository](https://github.com/sivel/speedtest-cli).


## Database and check logs
Actaully utility uses two different databases, but you need only one of them.

**The first one** is nessesary for fast searching of your network hardware manufacturer, using [IEEE OUI](https://en.wikipedia.org/wiki/Organizationally_unique_identifier). This is `oui.db` file.

If you got ultimate brand new hardware not presented in local list, you may use the `download.py` script. It will update vendor's list from IEEE website. Or, if you lost this file for any cause, this script will create a new one with latest updates.
```shell
python3 download.py
```


**The second one**, named `speedtest.db`, stores full information about speed-checking sessions. It contains 41 parameter for each check.
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

**NB:** Data is intentionally stores in the single table, not several related tables. This is because the most of values are potentially variable and may changing independently and unpredictable. Also this approach is common for most analysis tools.

## Well, then?
There are plenty of ways to use one-table organized data. It could be [GUI clients](https://yandex.com/search/?text=sqlite%20gui%20clients) or programmatic solutions such as [Pandas](https://pandas.pydata.org) or [R Studio](https://www.r-studio.com/). And even [MS Excel](https://www.microsoft.com/ru-ru/microsoft-365/excel) or [Google Sheets](https://sheets.google.com) are applicable.

Use [Notebook](https://jupyter.org/) for analyse and plot data. Or connect the database to [BI interface](https://yandex.com/search/?text=Top%20BI%20tools) for constructing reports. Author don't planning to reinvent BI tools. The ready ones are perfect, necessary and sufficient. Free or paid, for any choice.
