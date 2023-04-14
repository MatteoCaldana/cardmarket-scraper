# -*- coding: utf-8 -*-

import pandas as pd
import os
from datetime import datetime
import matplotlib as mpl
import matplotlib.pyplot as plt

def prepare_df(filename):
    df = pd.read_csv(filename)
    df["set"] = df["url"].apply(lambda x: x.split('/')[-2])
    df["comments"] = df["comments"].apply(lambda x: "" if type(x) == float else x.lower())
    return df

def cleaning_df(df): 
    # cleaning
    #  - NOT reverse
    #  - NOT first edition
    df = df[(~df.comments.str.contains('rev'))&(df.first_ed==0)]

    # split into two markets (NOT a partition!)
    #  - cards in EN
    #  - cards in IT from IT
    it = df[(df.language=='IT') & (df.location=='IT')]
    en = df[df.language=='EN']
    return it, en

def build_price_df(df):
    # set levels
    quantiles = {'Q1':.25, 'Q2':.5, 'Q3':.75}

    # extract levels on different columns
    price_gb = df.groupby(["url", "condition"])["price"]
    
    dfs = []
    for q in quantiles:
        print("\t{}".format(q))
        df = price_gb.quantile(quantiles[q]).reset_index()
        df['q'] = q 
        dfs.append(df)
        
    price_df = pd.concat(dfs, axis=0)

    # compact the levels in a single column
#    start_time = time.time()
#    price_df['dict'] = price_df.apply(lambda x: {q: x[q] for q in quantiles.keys()}, axis=1)
#    price_df = price_df.pivot(index='url',columns='condition',values='dict')
#    print("--- %s seconds ---" % (time.time() - start_time))
   
#    start_time = time.time()
#    price_df = price_df.groupby('url')['comp'].apply(list).apply(lambda x: {pair[0]:pair[1] for pair in x} )
#    price_df = price_df.reset_index()
#    print("--- %s seconds ---" % (time.time() - start_time))
    
    return price_df

def save(pr_df, date, prefix):
    path = "./log/price/{}/price_{}.csv".format(prefix, date)
    pr_df.to_csv(path, index=False)
    return

def prepare_price_df(filename):
    df = pd.read_csv(filename)
    date = filename[-23:-4]
    df['date'] = datetime.strptime(date, '%Y-%m-%d_%H-%M-%S')
    return df

def join_price_dfs(folder):
    path = './log/price/{}/'.format(folder)
    files = os.listdir(path)
    dfs = []
    for f in files:
        dfs.append(prepare_price_df(path+f))
        
    df = dfs[0]
    for i in range(1,len(dfs)):
        print("Outer join {} of {}".format(i, len(dfs)))
        suf=('_{}'.format(i-1), '_{}'.format(i))
        df = pd.merge(df, dfs[i], on=['url','condition','q'], how='outer',suffixes=suf)
    
    df = df.rename(columns={"date": "date_{}".format(len(dfs)-1), "price": "price_{}".format(len(dfs)-1),})
    df.to_csv('./log/price/{}.csv'.format(folder), index=False)
    return df

prefix_it = 'IT_IT_NOrev_NO1stEd'
prefix_en = 'EN_glob_NOrev_NO1stEd'

def clean_log(filename):
    it, en = cleaning_df(prepare_df(filename))

    date = filename[-23:-4]
    
    print("it")
    save(build_price_df(it),date,prefix_it)
    print("en")
    save(build_price_df(en),date,prefix_en)
    return
 
###############################################################################
# plot tools    
###############################################################################

    
def plot_row(row):
    points = (len(row) - 3) // 2
    x = []
    y = []
    for i in range(points):
        try:
            x.append(datetime.strptime(row['date_{}'.format(i)], '%Y-%m-%d %H:%M:%S'))
            y.append(row['price_{}'.format(i)])
        except:
            pass
        
    if row['condition'] < 5:
        cname = 'tab20b'
        pt = row['condition'] / 5 + 0.001 
    else:
        cname = 'tab20c'
        pt = (row['condition'] - 5) / 5 + 0.001
        
    q_delta = (int(row['q'][1]) - 1) / 20
    plt.plot(x, y, marker='o', color=mpl.cm.get_cmap(cname)(pt + q_delta))
        
    return
    
def plot_card(url, prefix):
    df = pd.read_csv('./log/price/{}.csv'.format(prefix))
    df = df[ df.url == url ]
    
    for index, row in df.iterrows():
        plot_row(row)
    
    return
    
###############################################################################
# coarse analysis
###############################################################################

def build_coarse_price_df(df):
    # set levels
    quantiles = {'Q1':.25, 'Q2':.5, 'Q3':.75}

    # extract levels on different columns
    price_gb = df.groupby("url")["price"]
    
    sers = []
    for q in quantiles:
        print("\t{}".format(q))
        ser = price_gb.quantile(quantiles[q]).rename(q)
        sers.append(ser)
            
    return pd.concat(sers, axis=1)

###############################################################################

if __name__ == "__main__":
    #clean_log('./log/log_2020-12-02_13-31-20.csv')
    #join_price_dfs(prefix_it)
    #join_price_dfs(prefix_en)

#    url = 'Base-Set/Charizard'
#    url = 'Team-Rocket/Dark-Charizard-Holo'
#
#    plt.figure()
#    plot_card(url, prefix_en)
#    plt.figure()
#    plot_card(url, prefix_it)
    a=build_coarse_price_df(pd.read_csv('./log/log_2020-12-02_13-31-20.csv'))








