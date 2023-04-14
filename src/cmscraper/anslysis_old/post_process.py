# -*- coding: utf-8 -*-
"""
Created on Sun Oct 30 08:46:54 2022

@author: Matteo
"""
import pandas as pd
import re
from collections import Counter
import utils


def clean_text(s):
    s = s.lower()
    return [
        x
        for x in re.sub(r"[-.,!?:;=+*$%<>^|&/@'_#()\[\]\"\\0-9£~§“”⁕€]", " ", s).split(
            " "
        )
        if x
    ]


def post_process(df):
    df["comments"] = df["comments"].fillna("")
    df["reverse_comment"] = df["comments"].apply(lambda s: s.find("reverse") != -1)
    volatile_re = "|".join(
        x for y in utils.GRADING_MODIFIER_TOKENS for x in [f"^{y}", f" {y}"]
    )
    df["volatile_grading"] = df["comments"].apply(
        lambda s: bool(re.search(volatile_re, s))
    )
    print(
        "Reverse:",
        df["reverse_comment"].sum(),
        "| Volatile grading:",
        df["volatile_grading"].sum(),
    )
    return df


df = pd.read_csv(
    "log/20221029articles.221029base-ex.language=1,5&minCondition=4&isSigned=N&isAltered=N.csv"
)
df = post_process(df)
gb = df[~df.volatile_grading].groupby(
    ["card", "reverse_comment", "first_ed", "condition", "language"]
)
price_df = gb.agg({"price": ["describe",], "count": ["sum"],})
# df["clean_comments"] = df["comments"].apply(clean_text)
# cc = [x for y in list(df["clean_comments"]) for x in y]
# cc2 = pd.DataFrame.from_dict(Counter(cc), orient='index').reset_index()
