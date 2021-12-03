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

types = { "p5a":"category", "p6":"category", "p7":"category", "p8":"category", "p9":"category", 
        "p10":"category", "p11":"category", "p12":"category", "p15":"category", "p16":"category",
        "p17":"category", "p18":"category", "p19":"category", "p20":"category", "p21":"category", "p22":"category",
        "p23":"category", "p24":"category", "p27":"category", "p28":"category",
        "p36":"category", "p39":"category",
        "p44":"category", "p45a":"category", "p48a":"category", "p49":"category",
        "p50a":"category", "p50b":"category", "p51":"category", "p55a":"category", "p57":"category",
        "p58":"category", "t":"category", "s":"category", "r":"category","p":"category",
        "q":"category","n":"category","l":"category",
        }



def get_dataframe(filename: str, verbose: bool = False) -> pd.DataFrame:
    df = pd.read_pickle(filename)
    MB_SIZE=1048576

    if(verbose):
        memory_usage = df.memory_usage(index=False, deep=True).sum()
        print("orig_size=" + str(round(memory_usage/MB_SIZE, 1))+" MB") 
    
    dates = pd.to_datetime(df["p2a"])
    df["date"] = dates
    
    df = df.astype(types)
    
    if(verbose):
        memory_usage = df.memory_usage(index=False, deep=True).sum()
        print("new_size=" + str(round(memory_usage/MB_SIZE, 1))+" MB") 

    return df

# Ukol 2: počty nehod v jednotlivých regionech podle druhu silnic

def plot_roadtype(df: pd.DataFrame, fig_location: str = None,
                  show_figure: bool = False):
    df.p21 = df.p21.map({1: "Dvouproudová komunikace", 2:"Tříproudová komunikace", 3:"Čtyřproudová kominikace", 4:"Čtyřproudová kominikace", 5:"Víceproudová komunikace", 6:"Rychlostní komunikace", 0:"Jiná komunikace"})
    df = df[df["region"].isin(["VYS", "OLK", "MSK", "KVK"])]
    
    df = df.groupby(["p21", "region"]).size().reset_index(name="Počet nehod")

    g = sns.catplot(x="region", y="Počet nehod", col="p21", kind="bar", data=df, col_wrap=3, sharex=False, sharey=False,  col_order=["Dvouproudová komunikace", "Tříproudová komunikace", "Čtyřproudová kominikace", "Rychlostní komunikace", "Víceproudová komunikace", "Jiná komunikace"]) 
    g.fig.set_size_inches(15,8) 
    g.fig.subplots_adjust(top=0.9, bottom=0.1, wspace=0.3, hspace=0.3)
    g.set(xlabel="Kraj")
    g.set_titles(template="{col_name}")
    g.fig.suptitle("Nehody podle druhu komunikace")

    if(fig_location != None):
        g.fig.savefig(fig_location)

    if(show_figure):
        plt.show()

# Ukol3: zavinění zvěří
def plot_animals(df: pd.DataFrame, fig_location: str = None,
                 show_figure: bool = False):
    df.p10 = df.p10.map({1: "řidičem", 2:"řidičem", 3:"jiné", 4:"zvěří", 5:"jiné", 6:"jiné", 7:"jiné", 0:"jiné"})
    #df = df[df["region"].isin(["VYS", "OLK", "MSK", "KVK"])]
    df = df[df["region"].isin(["JHM", "KVK", "VYS", "ZLK"])]
    df = df[df["p58"] == 5]

    df = df[pd.DatetimeIndex(df["date"]).year != 2021]
    df["date"] = pd.DatetimeIndex(df["date"]).month 

    print(df)

    g= sns.catplot(x="date", col="region", hue="p10", kind="count",data=df, col_wrap=2, sharex=False, sharey=False) 

    if(fig_location != None):
        g.fig.savefig(fig_location)

    if(show_figure):
        plt.show()

   
# Ukol 4: Povětrnostní podmínky
def plot_conditions(df: pd.DataFrame, fig_location: str = None,
                    show_figure: bool = False):
    df = df[df["region"].isin(["JHM", "KVK", "VYS", "ZLK"])]
    df = df[df["p18"] != 0]
    df = df[pd.DatetimeIndex(df["date"]).year != 2021]
    df.p18 = df.p18.map({1: "neztížené", 2:"mlha", 3:"na počátku deště, slabý déšť, mrholení apod.", 4:"déšť", 5:"sněžení", 6:"tvoří se námraza, náledí", 7:"nárazový vítr"})

    df["date"] = pd.DatetimeIndex(df["date"]).to_period("M")
    df["Počet nehod"] = 0 
    
    neco = pd.pivot_table(df, index=["date","region"], values="Počet nehod", columns=[ "p18"], aggfunc=len, fill_value=0)
    neco = neco.stack(level="p18").reset_index(name="Počet nehod")

    neco = neco.astype({"date":"str", "region":"category", "p18":"category"})

    g= sns.relplot(x="date", y="Počet nehod", col="region", hue="p18", kind="line", col_wrap=2, data=neco) 
    
    if(fig_location != None):
        g.fig.savefig(fig_location)

    if(show_figure):
        plt.show()


if __name__ == "__main__":
    # zde je ukazka pouziti, tuto cast muzete modifikovat podle libosti
    # skript nebude pri testovani pousten primo, ale budou volany konkreni ¨
    # funkce.
    df = get_dataframe("accidents.pkl.gz",False) # tento soubor si stahnete sami, při testování pro hodnocení bude existovat
    plot_roadtype(df, fig_location="data/01_roadtype.png", show_figure=True)
    plot_animals(df, "02_animals.png", True)
    plot_conditions(df, "03_conditions.png", True)
