#!/usr/bin/env python3.9
# coding=utf-8
from matplotlib import pyplot as plt
import pandas as pd
from pandas.core.indexes import category
import seaborn as sns
import numpy as np
import os

# muzete pridat libovolnou zakladni knihovnu ci knihovnu predstavenou na prednaskach
# dalsi knihovny pak na dotaz

""" Ukol 1:
načíst soubor nehod, který byl vytvořen z vašich dat. Neznámé integerové hodnoty byly mapovány na -1.

Úkoly:
- vytvořte sloupec date, který bude ve formátu data (berte v potaz pouze datum, tj sloupec p2a)
- vhodné sloupce zmenšete pomocí kategorických datových typů. Měli byste se dostat po 0.5 GB. Neměňte však na kategorický typ region (špatně by se vám pracovalo s figure-level funkcemi)
- implementujte funkci, která vypíše kompletní (hlubkou) velikost všech sloupců v DataFrame v paměti:
orig_size=X MB
new_size=X MB

Poznámka: zobrazujte na 1 desetinné místo (.1f) a počítejte, že 1 MB = 1e6 B. 
"""

type_of_df = {"t":"category", "q":"category","p":"category","o":"category","n":"category","l":"category","k":"category","i":"category","h":"category"}


def get_dataframe(filename: str, verbose: bool = False) -> pd.DataFrame:
    """Gets data from file thet name is given in 'filename'.
    Print the size of dataframe in MB before and after adjustment if 'verbose' is True.
    """
    df = pd.read_pickle(filename)
    MB_SIZE=1048576

    if(verbose):
        memory_usage = df.memory_usage(index=False, deep=True).sum()
        print("orig_size=" + str(round(memory_usage/MB_SIZE, 1))+" MB") 
    
    df["date"] = pd.to_datetime(df["p2a"])
    df = df.astype(type_of_df)

    if(verbose):
        memory_usage = df.memory_usage(index=False, deep=True).sum()
        print("new_size=" + str(round(memory_usage/MB_SIZE, 1))+" MB") 

    return df

# Ukol 2: počty nehod v jednotlivých regionech podle druhu silnic

def plot_roadtype(df: pd.DataFrame, fig_location: str = None, show_figure: bool = False):
    """Make graph from data given in 'df' dataframe.
    This graph shows Accidents by type of communication.
    Graph will be saved to file at 'fig_location'. If 'fig_location' is None then nothing will be saved.
    Graph will be plotted if the 'show_figure' is True.
    """
    # Data sorting and filtration
    df = df[df["region"].isin(["VYS", "OLK", "MSK", "KVK"])]
    
    df.p21 = df.p21.map({1: "Dvouproudová komunikace", 2:"Tříproudová komunikace", 3:"Čtyřproudová kominikace", 4:"Čtyřproudová kominikace", 5:"Víceproudová komunikace", 6:"Rychlostní komunikace", 0:"Jiná komunikace"})
    df = df.groupby(["p21", "region"]).size().reset_index(name="Počet nehod")

    df.region = df.region.map({"KVK": "Karlovarský", "VYS": "Kraj Vysočina", "OLK": "Olomoucký", "MSK": "Moravskoslezský"})

    # Graph plotting
    sns.set_style("darkgrid") 
    g = sns.catplot(
        x="region",
        y="Počet nehod",
        col="p21",
        kind="bar",
        palette="deep",
        data=df,
        color="bright",
        sharex=False,
        sharey=False,
        col_wrap=3,
        col_order=["Dvouproudová komunikace", "Tříproudová komunikace", "Čtyřproudová kominikace", "Rychlostní komunikace", "Víceproudová komunikace", "Jiná komunikace"]
        ) 
    g.fig.subplots_adjust(top=0.9, bottom=0.1, wspace=0.3, hspace=0.5)
    g.set(xlabel="Kraj")
    g.set_xticklabels(rotation=30)
    g.set_titles(template="{col_name}")

    g.fig.suptitle("Nehody podle druhu komunikace")

    # Save file 
    if(fig_location != None):
        g.fig.savefig(fig_location)

    # Show figure
    if(show_figure):
        plt.show()

# Ukol3: zavinění zvěří
def plot_animals(df: pd.DataFrame, fig_location: str = None, show_figure: bool = False):
    """Make graph from data given in 'df' dataframe.
    This graph shows accidents caused by game.
    Graph will be saved to file at 'fig_location'. If 'fig_location' is None then nothing will be saved.
    Graph will be plotted if the 'show_figure' is True.
    """
    # Data sorting and filtration
    df = df[df["p58"] == 5]
    df = df[df["region"].isin(["JHM", "KVK", "VYS", "ZLK"])]

    df.p10 = df.p10.map({1: "řidičem", 2:"řidičem", 3:"jiné", 4:"zvěří", 5:"jiné", 6:"jiné", 7:"jiné", 0:"jiné"})
    df.region = df.region.map({"JHM": "Jihomoravský", "KVK": "Karlovarský", "VYS": "Kraj Vysočina", "ZLK": "Zlínský"})

    df = df[pd.DatetimeIndex(df["date"]).year != 2021]
    df["date"] = pd.DatetimeIndex(df["date"]).month 

    # Graph plotting
    sns.set_style("darkgrid") 
    g= sns.catplot(
        x="date",
        col="region",
        hue="p10",
        kind="count",
        palette="deep",
        data=df,
        col_wrap=2,
        sharex=False,
        sharey=False
        ) 
    
    g.set(ylabel="Počet nehod", xlabel="Měsíc") 
    g.fig.subplots_adjust(top=0.9, bottom=0.1, wspace=0.3, hspace=0.3)
    g._legend.set_title("Zavinění") 
    
    g.set_titles(template="Kraj: {col_name}")
    
    g.fig.suptitle("Nehody zaviněné zvěří")
    
    # Save file 
    if(fig_location != None):
        g.fig.savefig(fig_location)

    # Show figure
    if(show_figure):
        plt.show()

   
# Ukol 4: Povětrnostní podmínky
def plot_conditions(df: pd.DataFrame, fig_location: str = None, show_figure: bool = False):
    """Make graph from data given in 'df' dataframe.
    This graph shows the number of accidents according to weather conditions.
    Graph will be saved to file at 'fig_location'. If 'fig_location' is None then nothing will be saved.
    Graph will be plotted if the 'show_figure' is True.
    """
    # Data sorting and filtration
    df = df[df["p18"] != 0]
    df = df[df["region"].isin(["JHM", "KVK", "VYS", "ZLK"])]
    df = df[pd.DatetimeIndex(df["date"]).year != 2021]

    df.p18 = df.p18.map({1: "neztížené", 2:"mlha", 3:"na počátku deště, slabý déšť, mrholení apod.", 4:"déšť", 5:"sněžení", 6:"tvoří se námraza, náledí", 7:"nárazový vítr"})
    df.region = df.region.map({"JHM": "Jihomoravský", "KVK": "Karlovarský", "VYS": "Kraj Vysočina", "ZLK": "Zlínský"})
    df["date"] = pd.DatetimeIndex(df["date"]).to_period("M")
    df["Počet nehod"] = 0 
    
    df = pd.pivot_table(df, index=["date","region"], values="Počet nehod", columns=[ "p18"], aggfunc=len, fill_value=0)
    df = df.stack(level="p18").reset_index(name="Počet nehod")

    df = df.astype({"date":"str", "region":"category", "p18":"category"})

    # Graph plotting
    sns.set_style("darkgrid") 
    g= sns.relplot(
        x="date",
        y="Počet nehod",
        col="region",
        hue="p18",
        kind="line",
        palette="deep",
        col_wrap=2,
        data=df,
        facet_kws={'sharex':False, 'sharey': True}
        ) 
    g.set(xlabel=None) 
    g.fig.subplots_adjust(top=0.9, bottom=0.1, wspace=0.3, hspace=0.3)
    g._legend.set_title("Podmínky") 
    g.set_titles(template="Kraj: {col_name}")

    g.fig.suptitle("Počty nehod podle povětrnostních podmínek")

    # Set labels for all x axes 
    header_name = ["1/16","1/17","1/18","1/19","1/20", "1/21"]
    x_tick_interval = 12
    value_tick = range(0,6*12, x_tick_interval)
    for ax in g.axes.flat:
        ax.set_xticks(ticks=value_tick)
        ax.set_xticklabels(labels=header_name) 

    # Save file 
    if(fig_location != None):
        g.fig.savefig(fig_location)

    # Show figure
    if(show_figure):
        plt.show()


if __name__ == "__main__":
    # zde je ukazka pouziti, tuto cast muzete modifikovat podle libosti
    # skript nebude pri testovani pousten primo, ale budou volany konkreni ¨
    # funkce.
    df = get_dataframe("accidents.pkl.gz",True) # tento soubor si stahnete sami, při testování pro hodnocení bude existovat
    plot_roadtype(df, fig_location="01_roadtype.png", show_figure=False)
    plot_animals(df, "02_animals.png", False)
    plot_conditions(df, "03_conditions.png", False)
