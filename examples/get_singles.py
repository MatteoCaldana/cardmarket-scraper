import cmscraper.scrape as cms
from utils import get_timestamp

import os
import pandas as pd


WIZARDS_EXPANSIONS = [
    "Base-Set",
    "Jungle",
    "Fossil",
    "Team-Rocket",
    "Neo-Genesis",
    "Neo-Discovery",
    "Neo-Revelation",
    "Neo-Destiny",
    "Gym-Challenge",
    "Gym-Heroes",
    "Aquapolis",
    "Expedition-Base-Set",
    "Skyridge",
    "Legendary-Collection",
]

if __name__ == "__main__":
    # prepare forder for dumping data
    path = f"./dump/{get_timestamp()}-singles"
    os.makedirs(path, exist_ok=True)

    brand = "Pokemon"
    # find all the expansions of the brand
    expansions = cms.find_expansions(brand)
    # interested only in the "EX" expansion
    expansions = [exp for exp in expansions if exp[1][:2] == "EX"]

    # save the list expansions
    # you can recover it from the singles url but is nice
    # to see them all together 
    df_ex = pd.DataFrame(expansions, columns=["id", "name"])
    df_ex.to_csv(f"{path}/expansions.csv", index=False)

    # for each expansion find all the singles
    singles = cms.find_singles(expansions, brand)
    # save the list
    df_sn = pd.DataFrame(singles, columns=["url"])
    df_sn.to_csv(f"{path}/singles.csv", index=False)
