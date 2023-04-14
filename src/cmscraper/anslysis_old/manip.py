import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import utils

def peak_df(df):
    print("Articles dataframe contain")
    print("Condition:", df["condition"].unique())
    print("Language:", df["language"].unique())
    print("Location:", df["location"].unique())
    return

# basic statistics (the ones listed in cols) for each ("url", "condition") combination
def price_df(df, q=0.25):
    cols = {"mean":None, "median":None, "quantile":q}
    price_gb = df.groupby("url")["price"]
    price_series = [getattr(price_gb, i)(cols[i]) if cols[i] else getattr(price_gb, i)() for i in cols]
    glob_price_df = pd.concat(price_series, axis=1)
    glob_price_df.columns = ["glob_"+i for i in cols]
    glob_price_df = glob_price_df.reset_index()
    
    cols = {"min":None, "mean":None, "median":None, "quantile":q}
    price_gb = df.groupby(["url", "condition"])["price"]
    price_series = [getattr(price_gb, i)(cols[i]) if cols[i] else getattr(price_gb, i)() for i in cols]
    price_df = pd.concat(price_series, axis=1)
    price_df.columns = cols
    price_df = price_df.reset_index()
    
    price_df = pd.merge(glob_price_df, price_df, left_on=['url'], right_on=['url'])
    return price_df, glob_price_df

# for each set/expansion add colums describing the macro expansion / generation
def add_expansion_generation(df, table=utils.expansions):
    def invert_table(table):
        result = {}
        for key in table:
            for elem in table[key]:
                result[elem] = key
        return result
    
    table = invert_table(table)
    df["gen"] = df["set"].apply(lambda x: table[x])
    return df

# how many cards each seller sells
def basic_seller_df(df):
    basic_seller_df = df.groupby(["seller", "gen"])["url"].nunique()
    basic_seller_df.name = "count"
    basic_seller_df = basic_seller_df.reset_index()
    return basic_seller_df

# plot pseuto-knapsack for each seller
def plot_pseudo_knapsack(df):
    i = 0
    cmap = plt.get_cmap('nipy_spectral')
    colors = [cmap(i) for i in np.linspace(0, 1, len(df["seller"].unique()))]

    for seller in df["seller"].unique():
        tmp_df = df[df["seller"]==seller]
        tmp_df = tmp_df.sort_values(by=["price_offset"], ascending=False)
    
        price = np.cumsum(tmp_df["price"].to_numpy())
        offset = np.cumsum(tmp_df["price_offset"].to_numpy())
    
        plt.plot(price, offset, marker='o', color=colors[i])
        for j in range(len(price)):
            if (j+1) % 5 == 0:
                plt.text(price[j], offset[j], str(j+1), color='black', fontsize=10)
        i += 1
    

    plt.plot([0, 100], [0, 0], color='black')
    plt.legend(df["seller"].unique())
    
    plt.grid(which='both')
    return

