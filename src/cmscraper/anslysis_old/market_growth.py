# -*- coding: utf-8 -*-

import pandas as pd
import json
from datetime import datetime
import matplotlib as mpl
import matplotlib.pyplot as plt



def cards_price_info(df):
    # set levels
    quantiles = {'Q1':.25, 'Q2':.5, 'Q3':.75}

    # extract levels on different columns
    price_gb = df.groupby(["url", "condition"])["price"]
    price_series = [price_gb.quantile(quantiles[q]) for q in quantiles]
    price_df = pd.concat(price_series, axis=1)
    price_df.columns = quantiles.keys()
    price_df = price_df.reset_index()

    # compact the levels in a single column
    price_df['comp'] = price_df.apply(lambda x: (x['condition'],{q: x[q] for q in quantiles.keys()}), axis=1)
    price_df = price_df.groupby('url')['comp'].apply(list).apply(lambda x: {pair[0]:pair[1] for pair in x} )
    price_df = price_df.reset_index()
    
    return price_df
  
def prepare_group_df(filelist):  
    datelist = []
    df = pd.DataFrame()
    for i in range(len(filelist)):
        print("\tFile {} of {}".format(i, len(filelist)))
        filename = filelist[i]
        
        datelist.append(datetime.strptime(filename.split('.')[0].split('_')[-2], '%Y-%m-%d' ))
        
        new_df = pd.read_csv("./data/{}".format(filename))
        df = pd.concat([df, new_df])
    
    print("Removing duplicates")
    df = df.drop_duplicates()
    
    meandate = sum([i.timestamp() for i in datelist])/len(datelist)
    meandate = datetime.utcfromtimestamp(meandate).strftime('%Y-%m-%d %H')
    return meandate, df

def load_dfs(groups):
    dfs = []
    for i in range(len(groups)):
        print("List {} of {}".format(i, len(groups)))
        filelist = groups[i]
        
        md, df = prepare_group_df(filelist)
        print("Calculating price stats")
        dfs.append(cards_price_info(df).rename(columns={'comp':md}))
        
    return dfs

def outer_join_list(dfs):
    df = dfs[0]
    for i in range(1,len(dfs)):
        print("Outer join {} of {}".format(i, len(dfs)))
        df = pd.merge(df, dfs[i], how='outer', left_on=['url'], right_on=['url'])
    return df

def market_growth_df():
    with open('./group_data.json') as f:
        data = json.load(f)       
    dfs = load_dfs(data['groups'])  
    return outer_join_list(dfs)

# if in a series of dict we have a nan it is a problem
# we replace it with a proper dict that has keys as keys and nan as values
def series_to_df(s):
    l = list(s)
    keys = set([j for i in l if type(i) == dict for j in i.keys()])
    rep = {i:float('nan') for i in keys}
    return pd.DataFrame([rep if type(i) == float else i for i in l])

cond_dict = {'Poor':'PO','Played':'PL','Light Played':'LP','Good':'GD',
             'Excellent':'EX','Near Mint':'NM','Mint':'MI'}
def rename_df(df,prefix):
    df.columns = [cond_dict[prefix]+i for i in df.columns]
    return df

def parse_row(row):
    url = row.loc['url']
    df = series_to_df(row.drop('url'))
    dfs = [rename_df(series_to_df(df[col]),col) for col in df.columns]
    df = pd.concat(dfs, axis=1)    
    df.index = row.index[1:]
    return df

cmap_dict = {'PO':'Greys','PL':'Purples','LP':'Blues','GD':'spring',
             'EX':'Reds','NM':'Greens','MI':'GnBu'}

def plot_row(row):
    pt = 0.8
    x = [datetime.strptime(i, '%Y-%m-%d %H').timestamp() for i in row.index]
    
    for cond in cmap_dict:
        cname = cmap_dict[cond]
        clr = mpl.cm.get_cmap(cname)(pt)
        try:
            plt.plot(x, row[cond+'Q2'], color=clr, marker='o')
        except KeyError:
            pass
        try:
            plt.fill_between(x, row[cond+'Q1'], row[cond+'Q3'], color=clr, alpha=.5)
        except KeyError:
            pass
        
    return
    





    
