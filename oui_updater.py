import sqlite3
# from pathlib import Path

# CURDIR = Path(__file__).parent

def run(fname, dbname):
    sqlite3.paramstyle = 'named'

    with open(fname, 'r') as file:
        oui = file.read().split('\n\n')

    def butchy(vendor: str) -> dict:
        beef = vendor.split('\n')
        return {
            "hex" : beef[0][:8],
            "base16": beef[1][:6],
            "address" : ('\n'.join(beef[2:])).replace('\t', ''),
            "name1" : beef[0][18:],
            "name2" : beef[1][22:]
        }

    insert_values = [butchy(vendor) for vendor in oui]
    con = sqlite3.connect(dbname)
    cur = con.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS vendors
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                        hex TEXT NOT NULL,
                        base16 TEXT NOT NULL,
                        name1 TEXT NOT NULL,
                        name2 TEXT NOT NULL,
                        address TEXT NOT NULL);''')

    cur.execute('''DELETE FROM vendors;''')

    for values in insert_values:
        cur.execute('''INSERT INTO vendors (hex,  base16,  name1,  name2,  address)
                                    VALUES (:hex, :base16, :name1, :name2, :address)''',
                    values)

    con.commit()
    con.close()
