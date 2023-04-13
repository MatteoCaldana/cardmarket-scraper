import requests
import re
import bs4
import time

################################################################################
# SINGLES FIND ALL CARDS
################################################################################

BASE_URL = "https://www.cardmarket.com/en"
BACKOFF = 2.0


def set_default_backoff(backoff):
    global BACKOFF
    BACKOFF = backoff


def find_singles(expansions, brand="Pokemon", backoff=BACKOFF):
    base_url = f"{BASE_URL}/{brand}/Products/Singles/{{}}?site={{}}"

    singles_list = []
    for expansion in expansions:
        expansion = _expansion_name_to_url(expansion)
        url = base_url.format(expansion, "1")
        page = requests.get(url).content.decode("utf-8")
        n_pages = _parse_tot_num_pages(page)

        for i in range(1, n_pages + 1):
            print(f"Expansion: {expansion}, pages:{i}/{n_pages}")
            new_singles_list = _find_all_singles_in_page(base_url.format(expansion, i))
            time.sleep(backoff)
            singles_list += new_singles_list
    return singles_list


def find_expansions(brand="Pokemon"):
    page = requests.get(f"{BASE_URL}/{brand}/Products/Singles").content.decode("utf-8")
    soup = bs4.BeautifulSoup(page, features="lxml")
    sets = soup.find("select", {"name": "idExpansion"}).find_all("option")
    sets = [i.text for i in sets]
    return sets[1:]  # the first option is "All"


def _parse_tot_num_pages(page):
    n_pages_re = re.search(r"Page ([0-9]+) of ([0-9]+)", page)
    if n_pages_re:
        n_pages = n_pages_re.group(2)
        return int(n_pages)
    n_singles = int(re.search(r"([0-9]+) Risultati", page).group(1))
    return n_singles // 20 + 1


def _find_all_singles_in_page(url):
    page = requests.get(url).content.decode("utf-8")
    soup = bs4.BeautifulSoup(page, features="lxml")
    cards = soup.find("div", {"class": "table-body"}).find_all(
        "div", {"class": "row no-gutters"}
    )[1::2]

    singles_list = []
    for card in cards:
        singles_list.append(_extract_card(card))
    return singles_list


def _extract_card(bs4_card):
    return bs4_card.find("a")["href"]


def _expansion_name_to_url(name):
    return name.replace(" ", "-").replace("'", "")


if __name__ == "__main__":
    brand = "Magic"
    expansions = find_expansions(brand)
    singles = find_singles([expansions[0]], brand)
