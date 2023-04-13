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
    path = f"./dump/{get_timestamp()}-singles"
    os.makedirs(path, exist_ok=True)

    brand = "Pokemon"
    expansions = cms.find_expansions(brand)
    expansions = [exp for exp in expansions if exp[:2] == "EX"]

    df_ex = pd.DataFrame(expansions, columns=["url"])
    df_ex.to_csv(f"{path}/expansions.csv", index=False)

    singles = cms.find_singles(expansions, brand)

    df_sn = pd.DataFrame(singles, columns=["url"])
    df_sn.to_csv(f"{path}/singles.csv", index=False)
