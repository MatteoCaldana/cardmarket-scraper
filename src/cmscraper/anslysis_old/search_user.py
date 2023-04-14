import requests
import bs4
import time
import pandas as pd
from datetime import datetime
import os

################################################################################
# GIVEN A SELLER CARD FIND ALL THE ARTICLES
################################################################################

def find_articles(user, page):
    url = 'https://www.cardmarket.com/it/Pokemon/Users/{}/Offers/Singles?condition=4&sortBy=price_desc&site={}'
    r = requests.get(url.format(user, page))
    time.sleep(2.0)
    page = r.content.decode('utf-8')
    soup = bs4.BeautifulSoup(page, features='lxml')
    
    page_articles = soup.find_all("div", {"class": "row no-gutters article-row"})
        
    articles = []
    for art in page_articles:
        url = art.find("a")["href"]
        attr_cols = art.find("div", {"class": "product-attributes col"}).find_all("span")
        condition = attr_cols[2]["data-original-title"]
        language = attr_cols[3]["data-original-title"]

        first_ed_tag = "Prima edizione"
        safe_attr_cols = []
        for span in attr_cols:
            try:
                safe_attr_cols.append(span["data-original-title"])
            except:
                pass
        first_ed = any([_==first_ed_tag for _ in safe_attr_cols])


        try:
            comments = art.find("div", {"class": "product-comments"}).text
        except:
            comments = ""

        price = art.find("span", {"class":"font-weight-bold color-primary small text-right text-nowrap"}).text

        count = art.find("span", {"class": "item-count"}).text

        article = {
            'url':url, 
            'condition':condition, 
            'language':language, 
            'price':float(price.split(' ')[0].replace('.','').replace(',','.')), 
            'first_ed':first_ed, 
            'comments':comments, 
            'count':count
        }
        articles.append(article)
     
    return articles

def search_user(user, cut_price):
    print("Page {}".format(1))
    df = pd.DataFrame(find_articles(user, 1))
    i = 2
    while df.price.min() > cut_price:
        print("Page {}".format(i))
        df = pd.concat([df, pd.DataFrame(find_articles(user, i))], axis=0)
        i += 1
    dtime = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    df.to_csv('./users/{}_{}.csv'.format(user, dtime), index=False)
    return df

def users_diff():
    ls = os.listdir('./users')
    users = set([i.split('_')[0] for i in ls])
    df = pd.DataFrame()
    for u in users:
        tmp = user_diff(u)
        tmp['seller'] = u
        df = pd.concat([df, tmp], axis=0)
    df['url'] = df['url'].apply(lambda x: x[29:])
    df = df.drop(['count_x','count_y'], axis=1)
    return df

def user_diff(user):
    ls = os.listdir('./users')
    ls = [i for i in ls if i.split('_')[0] == user]
    if len(ls) < 2:
        return ''
    ls.sort(reverse=True)
    df1 = pd.read_csv('./users/{}'.format(ls[0]))
    df2 = pd.read_csv('./users/{}'.format(ls[1]))
    return df_diff(df1, df2)

def df_diff(df1, df2):
    df = pd.merge(df1, df2, on=['url','condition','language','first_ed','comments'], how='outer')
    sold = df[df.price_y.isnull()]
    sold['change'] = 'NEW'
    new = df[df.price_x.isnull()]
    new['change'] = 'SOLD'
    increase = df[df.price_y < df.price_x]
    increase['change'] = 'INCREASE'
    decrease = df[df.price_y > df.price_x]
    decrease['change'] = 'DESCREASE'
    
    df = pd.concat([increase, decrease, new, sold], axis=0)
    return df
    

################################################################################

if __name__ == "__main__":
    usrs = ['EttoreMTG','Gengar88','LPPCollecting','muskiooo']
    cut = 10.0 
    for u in usrs:
        print(u)
        search_user(u, cut)