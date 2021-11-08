#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#from os import register_at_fork
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from numpy.lib.arraysetops import unique
import argparse
import os

from download import DataDownloader

# povolene jsou pouze zakladni knihovny (os, sys) a knihovny numpy, matplotlib a argparse

def plot_stat(data_source, fig_location=None, show_figure=False):
    """Visualises data in graphs
    'data_source' - Dictionary of numpy arrays. Each numpy array represent records for its key.
    'fig_location' - Location where to save graphs. Nothing will be saved if the given value is None.
    'show_figure' - Show visualised data if its value is set to True. 
    """

    absolute_values = None 
    
    regions = [ 
        "HKK",
        "JHC",
        "JHM",
        "KVK",
        "LBK",
        "MSK",
        "OLK",
        "PAK",
        "PHA",
        "PLK",
        "STC",
        "ULK",
        "VYS",
        "ZLK",
    ]
    upravy = [
        "Přerušovaná žlutá",
        "Semafor mino provoz",
        "Dopravními značky",
        "Přenosné dopravní značky",
        "Nevyznačena",
        "Žádná úprava",
    ]


    for region in regions:
        final = np.zeros(6, dtype=np.float64) 
        i_for_current_reg = np.where(data_source["region"] == region)
        p24_values =  data_source["p24"][i_for_current_reg]
        unique_for_reg = np.unique(p24_values, return_counts=True)
        
        for index in range(len(unique_for_reg[0])):
            final[unique_for_reg[0][index]] = unique_for_reg[1][index]
        
        if absolute_values is None :
            absolute_values = final 
        else:
            absolute_values = np.vstack((absolute_values, final))

    absolute_values = np.roll(absolute_values, -1, axis=1)
    relative_values = absolute_values.T/absolute_values.T.sum(axis=1)[:,None]
    
    relative_values[relative_values == 0.0] = np.nan
    
    fig, (axs1, axs2)= plt.subplots(2, figsize = (7.2, 5.5))
    fig.subplots_adjust(hspace=0.3, left=0.3, right=0.97, top=0.98, bottom=0.02) 

    graf1 = axs1.imshow(absolute_values.T, norm = LogNorm(vmin=1e0, vmax=1e5))
    fig.colorbar(graf1, ax = axs1, label="Počet nehod")
    axs1.set_title("Absolutně")
    
    axs1.set_yticks(range(len(upravy)))
    axs1.set_xticks(range(len(regions)))
    axs1.set_xticklabels(regions)
    axs1.set_yticklabels(upravy)
   

    graf2 = axs2.imshow(relative_values*100, vmin = 0,cmap = plt.get_cmap("plasma"))
    fig.colorbar(graf2, ax = axs2, label="Políl nehod pro danou příčinu [%]")
    axs2.set_title("Relativně vůči příčině")
   
    axs2.set_yticks(range(len(upravy)))
    axs2.set_xticks(range(len(regions)))
    axs2.set_xticklabels(regions)
    axs2.set_yticklabels(upravy)

    if show_figure:
        plt.show() 

    if fig_location:
        dirname = os.path.dirname(fig_location) 
        if not os.path.exists(dirname) and dirname != "":
            os.path.makedirs(os.path.dirname(fig_location))
        
        plt.savefig(fig_location)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Process some intefers')
    parser.add_argument('--fig_location', type=str,  help='Cesta kam se mají uložit grafy. Pokud se tento argument nezadá, tak se grafy nikam neuloží.', default=None)
    parser.add_argument('--show_figure', help='Zobrazí grafy v okně.', action='store_true')
    args = parser.parse_args()

    plot_stat(data_source = DataDownloader().get_dict(), fig_location=args.fig_location, show_figure=args.show_figure)
