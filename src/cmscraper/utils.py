import time
import datetime
import requests

def get_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def tprint(*kargs, **kwargs):
    print(datetime.datetime.now(), *kargs, **kwargs)


def request(method, url, **kwargs):
    tprint(f"{method.upper()}: {url}")
    return requests.request(method, url, **kwargs)


def sleep(t, reason=""):
    reason = f"waitinig for {reason}" if reason else ""
    tprint(f"Sleeping for {t} [s] {reason}")
    time.sleep(t)


def heuristic_str2url(string, replace=""):
    not_admissible_char = r".:/?*%|<>\"!$&@#;,'{}[]()#^$&="
    sane = string.replace(" ", "-")
    for c in not_admissible_char:
        sane = sane.replace(c, replace)
    sane = sane.replace("--", "-")
    return sane


def apply_dict_safe(x, table):
    try:
        return table[x]
    except KeyError:
        print(f"WARNING: key '{x}' not found in {table}")
        return x


CONDITION_DICT = [
    {"long": "Mint", "short": "MT", "id": 1},
    {"long": "Near Mint", "short": "NM", "id": 2},
    {"long": "Excellent", "short": "EX", "id": 3},
    {"long": "Good", "short": "GD", "id": 4},
    {"long": "Light Played", "short": "LP", "id": 5},
    {"long": "Played", "short": "PL", "id": 6},
    {"long": "Poor", "short": "PO", "id": 7},
]

LANGUAGE_DICT = [
    {"long": "English", "short": "EN", "id": 1},
    {"long": "French", "short": "FR", "id": 2},
    {"long": "German", "short": "DE", "id": 3},
    {"long": "Spanish", "short": "ES", "id": 4},
    {"long": "Italian", "short": "IT", "id": 5},
    {"long": "S-Chinese", "short": "S-CN", "id": 6},
    {"long": "Japanese", "short": "JP", "id": 7},
    {"long": "Portuguese", "short": "PT", "id": 8},
    {"long": "Russian", "short": "RU", "id": 9},
    {"long": "Korean", "short": "KR", "id": 10},
    {"long": "T-Chinese", "short": "T-CN", "id": 11},
    {"long": "Dutch", "short": "NE", "id": 12},
    {"long": "Polish", "short": "PL", "id": 13},
    {"long": "Czech", "short": "CZ", "id": 14},
    {"long": "Hungarian", "short": "HU", "id": 15},
]

LOCATION_DICT = [
    {"long": "Austria", "short": "AT", "id": 1},
    {"long": "Belgium", "short": "BE", "id": 2},
    {"long": "Bulgary", "short": "BG", "id": 3},
    {"long": "Canada", "short": "CA", "id": 33},
    {"long": "Croatia", "short": "HR", "id": 35},
    {"long": "Cyprus", "short": "CY", "id": 5},
    {"long": "Czech Republic", "short": "CZ", "id": 6},
    {"long": "Denmark", "short": "DK", "id": 8},
    {"long": "Estonia", "short": "EE", "id": 9},
    {"long": "Finland", "short": "FI", "id": 11},
    {"long": "France", "short": "FR", "id": 12},
    {"long": "Germany", "short": "DE", "id": 7},
    {"long": "Greece", "short": "GR", "id": 14},
    {"long": "Hungary", "short": "HU", "id": 15},
    {"long": "Iceland", "short": "IS", "id": 37},
    {"long": "Ireland", "short": "IR", "id": 16},
    {"long": "Italy", "short": "IT", "id": 17},
    {"long": "Japan", "short": "JP", "id": 36},
    {"long": "Latvia", "short": "LV", "id": 21},
    {"long": "Liechtenstein", "short": "LI", "id": 18},
    {"long": "Lithuania", "short": "LT", "id": 19},
    {"long": "Luxembourg", "short": "LU", "id": 20},
    {"long": "Malta", "short": "MT", "id": 22},
    {"long": "Netherlands", "short": "NL", "id": 23},
    {"long": "Norway", "short": "NO", "id": 24},
    {"long": "Poland", "short": "PL", "id": 25},
    {"long": "Portugal", "short": "PR", "id": 26},
    {"long": "Romania", "short": "RO", "id": 27},
    {"long": "Singapore", "short": "SG", "id": 29},
    {"long": "Slovakia", "short": "SK", "id": 31},
    {"long": "Slovenia", "short": "SI", "id": 30},
    {"long": "Spain", "short": "ES", "id": 10},
    {"long": "Sweden", "short": "SE", "id": 28},
    {"long": "Switzerland", "short": "CH", "id": 4},
    {"long": "United Kingdom", "short": "UK", "id": 13},
]

YN = [
    {"long": "Yes", "id": "Y"},
    {"long": "No", "id": "N"},
]

USER_OFFERS_SINGLE_OPTIONS = [
    "idLanguage",
    "idExpansion",
    "condition",
    "minPrice",
    "maxPrice",
    "isSigned",
    "isFirstEd",
    "isAltered",
]

PRODUCTS_SINGLE_OPTIONS = [
    "sellerCountry",
    "idLanguage",
    "condition",
    "isSigned",
    "isFirstEd",
    "isAltered",
]
