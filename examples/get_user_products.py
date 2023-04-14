import cmscraper.scrape as cms
from utils import get_timestamp

import os
import pandas as pd
import json


if __name__ == "__main__":
    brand = "Pokemon"
    user = "EttoreMTG"

    # prepare forder for dumping data
    path = f"./dump/{get_timestamp()}-user-{user}"
    os.makedirs(path, exist_ok=True)

    # find all the articles sold by the user
    # the details about the options can be found in cmscraper.utils
    options = {"idLanguage": 7, "minPrice": 15}
    articles = cms.find_user(brand, user, "Singles", options)

    # save options and articles
    with open(f"{path}/options.json", "w") as fp:
        json.dump(options, fp)
    df = pd.DataFrame(articles)
    df.to_csv(f"{path}/articles.csv", index=False)
