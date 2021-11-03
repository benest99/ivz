#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from re import A, S
import numpy as np
import zipfile

import os
from bs4 import BeautifulSoup as bs
import requests
import re
import csv
import io


import datetime

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
    
    def get_actual_arch_names(self):
        # Get html page from url
        page = bs(requests.get(self.url).text, 'html.parser')

        table_rows = page.table.findChildren('tr')

        names = []

        for row in table_rows:
            items = row.findChildren('td')
            for item in reversed(items):
                if(item.text == 'ZIP'):
                    names.append(re.sub(r'(^download\(\')|(\'\))', '', item.button['onclick']))
                    break

        return names

    def download_data(self):
        # Make Folder if the folder do not exist 
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)

        for name in self.get_actual_arch_names(): 
            req = requests.get(self.url+name, stream=True)
            with open(self.folder+"/"+os.path.basename(name),'wb') as file:
                for chunk in req.iter_content(chunk_size=128):
                    file.write(chunk)
                
    def parse_region_data(self, region):
        # Získání čísla regionu z tříznakého kódu 
        try:
            region_no = self.regions[region]
        except KeyError as err:
            print(f"Region is not set correctly. {err} is not known region.")
            return -1 

        # Kontrola toho jestli jsou data pro zadaný kraj již dsaženy ve složce folder
        archive_names = self.get_actual_arch_names() 
        for archive_name in archive_names:                                                                  # Stáhnou se aktuální jména nejnovějších archivů pro každý rok
            if(not os.path.isfile(self.folder+"/"+os.path.basename(archive_name))):                         # Pokud některý z archivů neexistuje, tak se stáhne aktuální
                self.download_data()
                break
            else:                                                                                           # Pokud archiv existuje, tak se zjistí jestli je .csv soubor pro region stažen
                with zipfile.ZipFile(self.folder+"/"+os.path.basename(archive_name), 'r') as archive:
                    if(region_no+'.csv' not in archive.namelist()):                                         # Archivy se znovu stáhnou pokud v některém z nich chybí .scv soubor pro region
                        self.download_data()
                        break


        mul_list = [[]for rows in range(len(self.headers))] # List listů pro jednotlivé položny v .csv souborech 
        reg_dict = dict.fromkeys(self.headers+['region'])   # Výsledný slovník

        for archive_name in archive_names:
            with zipfile.ZipFile(self.folder+"/"+os.path.basename(archive_name), 'r') as archive:
                with archive.open(region_no+'.csv', 'r') as file:
                    reader = csv.reader(io.TextIOWrapper(file,'cp1250'), delimiter=';', quotechar='"')
                    for row in reader:
                        for index in range(len(row)):
                            mul_list[index].append(row[index])

        for index in range(len(mul_list)):
            try: 
                reg_dict[self.headers[index]] = np.array(mul_list[index], dtype=int)
            except ValueError:
                try: 
                    reg_dict[self.headers[index]] = np.array(mul_list[index], dtype=float)
                except ValueError:
                    reg_dict[self.headers[index]] = np.array(mul_list[index], dtype=str)

        reg_dict['region'] = (np.array([region for _ in range(len(mul_list[0]))]))

    def get_dict(self, regions=None):
        if regions == None or regions == []: 
            print("not_list")
            regions = self.regions.keys()
        
        
        

# TODO vypsat zakladni informace pri spusteni python3 download.py (ne pri importu modulu)

s = DataDownloader()

#s.download_data()

#s.parse_region_data("JHM")

s.get_dict(["asdf", "IRDD", "IEJ"])