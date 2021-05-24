import os, sys
import filecmp

from urllib.request import urlretrieve
from datetime import datetime
from pathlib import Path

import oui_updater

CURDIR = Path(__file__).parent

def oui():
    try:
        destination = Path(CURDIR) / '{}.ieee_oui.tsv'.format(int(datetime.now().timestamp()))
        urlretrieve('http://standards-oui.ieee.org/oui/oui.txt', destination)
        return {'sucess': True,
                'result': destination}
    except Exception as e:
        return {'sucess': False,
                'result': e}

# http://test.lu01.servers.com/100mb.bin
# http://standards-oui.ieee.org/oui/oui.txt

if __name__ == '__main__':
    print ('Download last version of oui list from ieee.org...')
    fname = oui()

    if not fname{'success'}:
        print ('Download was unsecsessfull :(')
        print (fname{'result'})
        sys.exit()

    print('File downloaded, checking the necessity of updates...')

    flist = sorted(
              list(
                filter(
                    lambda x: 'ieee_oui' in x,
                    os.listdir(CURDIR))
            ))[:2]
    if not filecmp.cmp(*[Path(CURDIR) / i for i in flist]):
        print('OUI list changed since last check, updating database...')
        oui_updater.run(Path(CURDIR) / name{'result'}, Path(CURDIR) / 'oui.db')
        print('Database was updated and now ready to work.')
    else:
        print('No updates nessessary, checking process finished.')
