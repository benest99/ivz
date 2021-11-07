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
import pickle
import gzip


# Kromě vestavěných knihoven (os, sys, re, requests …) byste si měli vystačit s: gzip, pickle, csv, zipfile, numpy, matplotlib, BeautifulSoup.
# Další knihovny je možné použít po schválení opravujícím (např ve fóru WIS).


class DataDownloader:
    """ TODO: dokumentacni retezce 

    Attributes:
        headers    Nazvy hlavicek jednotlivych CSV souboru, tyto nazvy nemente!  
        regions     Dictionary s nazvy kraju : nazev csv souboru
    """

    types = ["str", np.int32, np.int32, "str", np.int32, np.int32, np.int32, np.int32, np.int32, np.int32, np.int32, np.int32, np.int32, np.int32, np.int32, np.int32, np.int32, np.int32, np.int32, np.int32,
            np.int32, np.int32, np.int32, np.int32, np.int32, np.int32, np.int32, np.int32, np.int32, np.int32, np.int32, np.int32, np.int32, np.int32, str, np.int32, np.int32, np.int32, np.int32, np.int32,
            np.int32, np.int32, np.int32, np.int32, np.int32, float, float, float, float, float, float, "str", "str", "str", "str", "str", "str", float, "str", "str",
            np.int32, np.int32, "str", np.int32]

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
        self.in_memory = dict.fromkeys(self.regions.keys())
    
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
                            if not row[index]:
                                if self.types[index] == float:  
                                    mul_list[index].append(np.nan)
                                elif self.types[index] == np.int32:
                                    mul_list[index].append(-1)
                                else:
                                    mul_list[index].append("")
                            elif self.types[index] == float:
                                new = row[index].replace(",",".")
                                if not re.search("^[+-]?\d*\.\d+|\d+$", new):
                                    mul_list[index].append(None)
                                else:
                                    mul_list[index].append(new)
                            else: 
                                mul_list[index].append(row[index])
        
        for index in range(len(mul_list)):
            reg_dict[self.headers[index]] = np.array(mul_list[index], dtype=self.types[index])
        
        reg_dict['region'] = (np.array([region for _ in range(len(mul_list[0]))]))
        
        return reg_dict

    def get_dict(self, regions=None):
        ret_dict = {} 
                
        if regions == None or regions == []: 
            regions = self.regions.keys()

        for region in regions:
            reg_cache_name = re.sub(r'\{\}', region, self.folder +"/"+ self.cache_filename)
            act_dict = {}
            
            if self.in_memory[region] != None:
                act_dict = self.in_memory[region]
            elif os.path.exists(reg_cache_name):
                with gzip.open(reg_cache_name, 'rb') as file:
                    self.in_memory[region] = pickle.load(file)
                    act_dict = self.in_memory[region]
            else:
                self.in_memory[region] = self.parse_region_data(region)
                
                with gzip.open(reg_cache_name, 'wb') as file:
                    pickle.dump(self.in_memory[region], file)

                act_dict = self.in_memory[region]

            for header in self.headers + ["region"]:
                if header not in ret_dict.keys():
                    ret_dict[header] = act_dict[header]
                else:
                    ret_dict[header] = np.concatenate((ret_dict[header], act_dict[header]), axis=0)
                
        return ret_dict



if __name__ == "__main__":
    downloader = DataDownloader()

    dict_downloaded = downloader.get_dict(["VYS"])
    print("Byly stažený záznamy pro kraje: Středočeský, Liberecký, Zlínský")
    print("Počet stažených záznamů:",len(dict_downloaded["p1"]))
    print("Jednotlivé sloupce ve formátu (label sloupce, datový typ):")
    for key in dict_downloaded:
        print("(",key,", ", dict_downloaded[key].dtype,")", sep="",end=",")
