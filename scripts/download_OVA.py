# This script can be used independently to scrape the latest RC OVA build
# and download it to local system

import requests
from bs4 import BeautifulSoup
import urllib

URL = 'http://ci-artifacts04.vse.rdlabs.hpecorp.net/omni/master/OVA/DCS-CP-synergy/'
r = requests.get(URL)
#print(r.content)

soup = BeautifulSoup(r.content, 'html5lib')
body = soup.find('body')
string = str(body).replace('<body>define([],"', '').replace('");</body>', '')
#print(body)

#to get content for table tag
soup = BeautifulSoup(string, 'html5lib')
table = soup.find('table')

# to retrieve all rows in table
tr = soup.findAll('tr')[-9:-8:]
# print(tr)

td_entries = []
for each_tr in tr:
    td = each_tr.find_all('td')
    # In each tr rown find each td cell
    for each_td in td:
        td_entries.append(each_td)

ova_rc_build = str(td_entries[1]).replace("<td>","").replace("</a>","").replace("</td>","").replace(">","!").split("!")[1]
        
# download OVA and place it in local system       
url1 = URL + ova_rc_build
urllib.request.urlretrieve(url1, "HPEOneView-DCS_6.30.00-0446451-CP-synergy.ova")