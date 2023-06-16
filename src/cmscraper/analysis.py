import pandas as pd
import numpy as np

import utils


def q1(x):
    return np.quantile(x, 0.25)


def q3(x):
    return np.quantile(x, 0.75)


DESCRIBE = [
    q1,
    np.median,
    q3,
    np.mean,
    len
]


def single_price(df):
    return pd.pivot_table(
        df,
        values="price",
        index="product",
        columns=["condition", "language"],
        aggfunc=DESCRIBE
    ).sort_values(["language", "condition"], ascending=False, axis=1)


def describe(x):
    return pd.Series([f(x) for f in DESCRIBE])


if __name__ == "__main__":
    CONTITION_TABLE = {e["short"]: e["id"] for e in utils.CONDITION_DICT}

    df = pd.read_csv("2023-04-16_16-00-00.articles.csv")
    df["condition"] = df["condition"].apply(lambda x: CONTITION_TABLE[x])
    df["expansion"] = df["product"].apply(lambda x: x.split("/")[0])
    df = df[~df["expansion"].isin(["Base-Set-2"])]
    df = df[df["sell_count"] > 1000]

    s_df = single_price(df).reset_index()
    s_df["expansion"] = s_df["product"].apply(lambda x: x.split("/")[0])
    set_price = s_df.groupby("expansion").aggregate(
        lambda x: np.sum(x.to_numpy(), axis=0))

    s_df2 = df.groupby(["product", "language", "condition"])\
              .apply(lambda x: describe(x["price"]))
    s_df2 = s_df2.sort_values(["product", "condition"]).reset_index()
