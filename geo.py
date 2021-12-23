#!/usr/bin/python3.8
# coding=utf-8
import pandas as pd
import geopandas
import matplotlib.pyplot as plt
import contextily
import sklearn.cluster
import numpy as np

import pickle
# muzete pridat vlastni knihovny


def make_geo(df: pd.DataFrame) -> geopandas.GeoDataFrame:
    """ Konvertovani dataframe do geopandas.GeoDataFrame se spravnym kodovani"""
    df = df.loc[(df["d"] != None )|( df["e"]!=None)]

    return geopandas.GeoDataFrame(
        df, 
        geometry=geopandas.points_from_xy(df["d"], df["e"]),
        crs = "EPSG:5514"
        )
    

def plot_geo(gdf: geopandas.GeoDataFrame, fig_location: str = None,
             show_figure: bool = False):
    """ Vykresleni grafu s sesti podgrafy podle lokality nehody 
     (dalnice vs prvni trida) pro roky 2018-2020 """
    # Z gdf vybrat rok 2018-2020

    gdf.plot()


    plt.savefig("obrazek.png")

def plot_cluster(gdf: geopandas.GeoDataFrame, fig_location: str = None,
                 show_figure: bool = False):
    """ Vykresleni grafu s lokalitou vsech nehod v kraji shlukovanych do clusteru """
    pass

if __name__ == "__main__":
    # zde muzete delat libovolne modifikace
    gdf = make_geo(pd.read_pickle("accidents.pkl.gz"))
    plot_geo(gdf, "geo1.png", True)
    plot_cluster(gdf, "geo2.png", True)
