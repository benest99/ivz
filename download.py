#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from re import S
import numpy as np
import zipfile

import os
from bs4 import BeautifulSoup as bs
import requests
import re

# Kromě vestavěných knihoven (os, sys, re, requests …) byste si měli vystačit s: gzip, pickle, csv, zipfile, numpy, matplotlib, BeautifulSoup.
# Další knihovny je možné použít po schválení opravujícím (např ve fóru WIS).


class DataDownloader:
    """ TODO: dokumentacni retezce 

    Attributes:
        headers    Nazvy hlavicek jednotlivych CSV souboru, tyto nazvy nemente!  
        regions     Dictionary s nazvy kraju : nazev csv souboru
    """

    headers = ["p1", "p36", "p37", "p2a", "weekday(p2a)", "p2b", "p6", "p7", "p8", "p9", "p10", "p11", "p12", "p13a",
               "p13b", "p13c", "p14", "p15", "p16", "p17", "p18", "p19", "p20", "p21", "p22", "p23", "p24", "p27", "p28",
               "p34", "p35", "p39", "p44", "p45a", "p47", "p48a", "p49", "p50a", "p50b", "p51", "p52", "p53", "p55a",
               "p57", "p58", "a", "b", "d", "e", "f", "g", "h", "i", "j", "k", "l", "n", "o", "p", "q", "r", "s", "t", "p5a"]

    regions = {
        "PHA": "00",
        "STC": "01",
        "JHC": "02",
        "PLK": "03",
        "ULK": "04",
        "HKK": "05",
        "JHM": "06",
        "MSK": "07",
        "OLK": "14",
        "ZLK": "15",
        "VYS": "16",
        "PAK": "17",
        "LBK": "18",
        "KVK": "19",
    }

    def __init__(self, url="https://ehw.fit.vutbr.cz/izv/", folder="data", cache_filename="data_{}.pkl.gz"):
        self.url = url
        self.folder = folder
        self.cache_filename = cache_filename

    def download_data(self):
        zip_names = []

        # Make Folder if the folder do not exist 
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

        # Get html page from url
        page = bs(requests.get(self.url).text, 'html.parser')

        table_rows = page.table.findChildren('tr')


        for row in table_rows:
            items = row.findChildren('td')
            for item in reversed(items):
                if(item.text == 'ZIP'):
                    name = re.sub(r'(^download\(\')|(\'\))', '', item.button['onclick'])
                    
                    req = requests.get(self.url+name, stream=True)
                    with open(self.folder+"/"+os.path.basename(name),'wb') as file:
                        for chunk in req.iter_content(chunk_size=128):
                            file.write(chunk)
                    break
                
    def parse_region_data(self, region):
        pass

    def get_dict(self, regions=None):
        pass


# TODO vypsat zakladni informace pri spusteni python3 download.py (ne pri importu modulu)

s = DataDownloader()

s.download_data()