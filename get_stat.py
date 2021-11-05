#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#from os import register_at_fork
import numpy as np
import matplotlib.pyplot as plt
#from numpy.core.shape_base import vstack
from matplotlib.colors import LogNorm
from numpy.lib.arraysetops import unique

# povolene jsou pouze zakladni knihovny (os, sys) a knihovny numpy, matplotlib a argparse

from download import DataDownloader

#imshow

#1. grag je logaritmický
def plot_stat(data_source,
              fig_location=None,
              show_figure=False):

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

        unique_for_reg = np.unique(data_source["p24"][np.where(data_source["region"] == region)], return_counts=True)
        
        for index in range(len(unique_for_reg[0])):
            final[unique_for_reg[0][index]] = unique_for_reg[1][index]
        
        if absolute_values is None :
            absolute_values = final 
        else:
            absolute_values = np.vstack((absolute_values, final))

    absolute_values = np.roll(absolute_values, -1, axis=1)
    relative_values = absolute_values.T/absolute_values.T.sum(axis=1)[:,None]
    
    absolute_values[absolute_values == 0.0] = np.nan 
    relative_values[relative_values == 0.0] = np.nan
    
    fig, (axs1, axs2)= plt.subplots(2, figsize = (7.2, 5.5))
    fig.subplots_adjust(hspace=0.3, left=0.3, right=0.97, top=0.98, bottom=0.02) 

    graf1 = axs1.imshow(absolute_values.T, norm = LogNorm(vmin=1e0, vmax=1e5))
    fig.colorbar(graf1, ax = axs1, label="Počet nehod")
    axs1.set_title("Absolutně")
    
    axs1.locator_params(axis='y', nbins=6)
    axs1.locator_params(axis='x', nbins=14)
    axs1.set_xticklabels(['']+regions, minor=False)
    axs1.set_yticklabels(['']+upravy, minor=False)
   

    lin_sp = np.linspace(0,100,6, endpoint=True)
    graf2 = axs2.imshow(relative_values*100, cmap = plt.get_cmap("plasma"))
    fig.colorbar(graf2, ax = axs2, label="Políl nehod pro danou příčinu [%]")
    axs2.set_title("Relativně vůči příčině")
   
    axs2.locator_params(axis='y', nbins=6)
    axs2.locator_params(axis='x', nbins=14)
    axs2.set_xticklabels(['']+regions, minor=False)
    axs2.set_yticklabels(['']+upravy, minor=False)
   
    plt.show() 

# TODO pri spusteni zpracovat argumenty

if __name__ == "__main__":

    plot_stat(data_source = DataDownloader().get_dict())
