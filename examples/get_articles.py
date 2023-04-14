import cmscraper.scrape as cms
from utils import get_timestamp

import os
import pandas as pd
import json


if __name__ == "__main__":
    # prepare forder for dumping data
    path = f"./dump/{get_timestamp()}-articles"
    os.makedirs(path, exist_ok=True)

    # find all the articles under a certain product
    # the details about the options can be found in cmscraper.utils
    brand = "Pokemon"
    procuct = "Neo-Genesis/Focus-Band-N186"
    options = {"language": "1,5", "minCondition": 5, "isSigned": "N"}
    articles = cms.get_articles_requests(
        brand, "Singles", procuct, options=options
    )

    # save options and articles
    with open(f"{path}/options.json", "w") as fp:
        json.dump(options, fp)
    df = pd.DataFrame(articles)
    df.to_csv(f"{path}/articles.csv", index=False)