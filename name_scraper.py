from lxml import html
from app import Set,db
import requests
import urllib
from urllib.request import urlopen
from bs4 import BeautifulSoup

for set_obj in Set.query.filter_by(set_name=None):
    url = "https://www.bricklink.com/v2/catalog/catalogitem.page?S="+ str(set_obj.set_number) + "#T=I"

    hdr = {'User-Agent':'Mozilla/5.0'}

    req = urllib.request.Request(url, headers=hdr)

    page = urlopen(req) 

    soup = BeautifulSoup(page,features="lxml")

    #find elements
    find_all_id = soup.find_all(id='item-name-title')

    print(str(set_obj.set_number))

    set_obj.set_name = find_all_id[0].text

    print(str(set_obj.set_number) + "Set Name: ", set_obj.set_name)
    
    db.session.commit()

# url = "https://www.bricklink.com/v2/catalog/catalogitem.page?S="+ "8401" + "#T=I"

# hdr = {'User-Agent':'Mozilla/5.0'}

# req = urllib.request.Request(url, headers=hdr)

# page = urlopen(req) 

# soup = BeautifulSoup(page,features="lxml")

# #find elements
# find_all_id = soup.find_all(id='item-name-title')

# print(find_all_id[0].text)