from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotVisibleException, ElementNotSelectableException

import os
import re
import bs4
import base64
import json
import string
import random
import pandas as pd

from utils import tprint, sleep, heuristic_str2url, request

################################################################################
# GLOBALS
################################################################################

BASE_URL = "https://www.cardmarket.com/en"
BACKOFF = 3.0


def set_default_backoff(backoff):
    global BACKOFF
    BACKOFF = backoff


################################################################################
# FIND SINGLES
################################################################################


def find_singles(expansions, brand="Pokemon", backoff=BACKOFF, save_tmp=False):
    base_url = f"{BASE_URL}/{brand}/Products/Singles/{{}}?site={{}}"

    singles_list = []
    saved_list = []
    for expansion in expansions:
        expansion_url = heuristic_str2url(expansion["name"])
        url = base_url.format(expansion_url, "1")
        page = request("get", url).content.decode("utf-8")
        n_pages = _parse_tot_num_pages(page)

        for i in range(1, n_pages + 1):
            tprint(f"Expansion: {expansion['name']}, pages:{i}/{n_pages}")
            if i > 1:
                url = base_url.format(expansion_url, i)
                page = request("get", url).content.decode("utf-8")
            new_singles_list = _find_all_singles_in_page(page)
            singles_list += new_singles_list
            sleep(backoff)

        if save_tmp:
            filename = f".{expansion_url}.tmp.csv"
            saved_list.append(filename)
            df = pd.DataFrame(new_singles_list)
            df.to_csv(filename, index=False)
            
    for file in saved_list:
        os.remove(file)
            
    return singles_list


def _parse_tot_num_pages(page):
    n_pages_re = re.search(r"Page ([0-9]+) of ([0-9]+)", page)
    if n_pages_re:
        n_pages = n_pages_re.group(2)
        return int(n_pages)
    n_singles = int(re.search(r"([0-9]+) Hits", page).group(1))
    return n_singles // 20 + 1


def _find_all_singles_in_page(page):
    soup = bs4.BeautifulSoup(page, features="lxml")
    cards = soup.find("div", {"class": "table-body"}).find_all(
        "div", {"class": "row no-gutters"}
    )[::2]

    singles_list = []
    for card in cards:
        singles_list.append(_extract_card(card))
    return singles_list


def _extract_card(bs4_card):
    spans = bs4_card.find_all("span")
    price = bs4_card.find_all("div", {"class": "col-price"})
    avail = bs4_card.find_all("div", {"class": "col-availability"})
    number = bs4_card.find("div", {"class": "col-md-2"}).text
    return {
        "url": bs4_card.find_all("a")[1]["href"],
        "number": number,
        "rarity": spans[3]["data-original-title"],
        "available": avail[0].text,
        "min_price": price[0].text,
        "available_rev": avail[1].text,
        "min_price_rev": price[1].text,
    }


################################################################################
# FIND EXPANSIONS
################################################################################


def find_expansions(brand="Pokemon"):
    page = request("get", f"{BASE_URL}/{brand}/Products/Singles").content.decode(
        "utf-8"
    )
    soup = bs4.BeautifulSoup(page, features="lxml")
    sets = soup.find("select", {"name": "idExpansion"}).find_all("option")
    sets = [{"id": i["value"], "name": i.text} for i in sets]
    return sets[1:]  # the first option is "All"


################################################################################
# FIND USER
################################################################################


def _find_user_articles_in_page(page):
    soup = bs4.BeautifulSoup(page, features="lxml")
    page_articles = soup.find_all("div", {"class": "row no-gutters article-row"})

    articles = []
    for art in page_articles:
        url = art.find("a")["href"]
        attr_cols = art.find("div", {"class": "product-attributes col"}).find_all(
            "span"
        )
        condition = attr_cols[2].text
        language = attr_cols[3]["data-original-title"]

        first_ed_tag = "Prima edizione"
        safe_attr_cols = []
        for span in attr_cols:
            try:
                safe_attr_cols.append(span["data-original-title"])
            except Exception as e:
                pass
        first_ed = any([_ == first_ed_tag for _ in safe_attr_cols])

        try:
            comments = art.find("div", {"class": "product-comments"}).text
        except Exception as e:
            comments = ""

        price = art.find(
            "span",
            {"class": "font-weight-bold color-primary small text-right text-nowrap"},
        ).text

        count = art.find("span", {"class": "item-count"}).text

        article = {
            "url": url,
            "condition": condition,
            "language": language,
            "price": float(price.split(" ")[0].replace(".", "").replace(",", ".")),
            "first_ed": first_ed,
            "comments": comments,
            "count": count,
        }
        articles.append(article)

    return articles


def find_user(brand, user, offer="Singles", options={}, backoff=BACKOFF):
    # TODO: check options are ok according to table in utils
    options = {**options, "site": "{}"}
    options_str = "&".join([f"{k}={options[k]}" for k in options])
    url = f"{BASE_URL}/{brand}/Users/{user}/Offers/{offer}?{options_str}"

    r = request("get", url.format(1))
    sleep(backoff)
    page = r.content.decode("utf-8")
    n_pages = _parse_tot_num_pages(page)
    if n_pages >= 15:
        tprint(
            "WARNING: Too many results, only showing partial results, please filter with options."
        )

    articles = _find_user_articles_in_page(page)
    for i in range(2, n_pages + 1):
        r = request("get", url.format(i))
        sleep(backoff)
        page = r.content.decode("utf-8")
        articles += _find_user_articles_in_page(page)

    return articles


################################################################################
# FIND ARTICLES
################################################################################


def _find_articles_in_page(page):
    if isinstance(page, str):
        soup = bs4.BeautifulSoup(page, features="lxml")
    else:
        soup = page

    articles = soup.find_all("div", {"class": "row no-gutters article-row"})
    tprint(f"Found {len(articles)} articles")

    parsed_articles = []
    for raw_art in articles:
        location_html_elem = raw_art.find(
            "span", {"class": "icon d-flex has-content-centered mr-1"}
        )
        location = (
            location_html_elem["data-original-title"]
            if "data-original-title" in location_html_elem.attrs
            else location_html_elem["title"]
        ).split(" ")[-1]
        #
        seller_el = raw_art.find("span", {"class": "seller-name"})
        sell_count = seller_el.find("span", {"class": "sell-count"})
        sell_count = sell_count["title"].split("\xa0")[0]
        seller = seller_el.find("a")["href"].split("/")[-1]
        #
        condition = raw_art.find("a", {"class": "article-condition"}).text
        #
        attributes = raw_art.find("div", {"class": "product-attributes col"})
        language = attributes.find_all("span")[1]["data-original-title"]
        reverse_holo = int(str(attributes).find("Reverse Holo") != -1)
        #
        first_ed = int(str(raw_art).find("Prima edizione") != -1)
        #
        comments = raw_art.find("div", {"class": "product-comments"})
        comments = comments.text if comments else ""
        #
        price = raw_art.find("div", {"class": "price-container"}).text
        price = float(price.split(" ")[0].replace(".", "").replace(",", "."))
        #
        count = raw_art.find("span", {"class": "item-count"}).text
        #
        parsed_articles.append(
            {
                "location": location,
                "seller": seller,
                "sell_count": sell_count,
                "condition": condition,
                "reverse_holo": reverse_holo,
                "language": language,
                "price": price,
                "first_ed": first_ed,
                "comments": comments,
                "count": count,
            }
        )

    return parsed_articles


GET_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,"
    "application/xml;q=0.9,image/avif,"
    "image/webp,image/apng,*/*;q=0.8,"
    "application/signed-exchange;v=b3;q=0.9",
    "Accept-Language": "it-IT,it;q=0.9",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/106.0.0.0 Safari/537.36",
    # "sec-ch-ua": '"Chromium";v="106", '
    # '"Google Chrome";v="106", '
    # '"Not;A=Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    # "sec-ch-ua-platform": '"Windows"',
}

POST_HEADERS = {
    "Accept": "*/*",
    "Accept-Language": "it-IT,it;q=0.9",
    "Connection": "keep-alive",
    "Content-Type": "multipart/form-data; boundary=----WebKitFormBoundary{}",
    "Origin": "https://www.cardmarket.com",
    "Referer": "https://www.cardmarket.com{}",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/106.0.0.0 Safari/537.36",
    # "sec-ch-ua": '"Chromium";v="106", '
    # '"Google Chrome";v="106", '
    # '"Not;A=Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    # "sec-ch-ua-platform": '"Windows"',
}


def id_generator(size=16, chars=string.ascii_letters + string.digits):
    return "".join(random.choice(chars) for _ in range(size))


def get_articles_requests(
    brand, product, product_name, options={}, proxies=None, backoff=BACKOFF
):
    # TODO: check options are ok according to table in utils
    options_str = "&".join([f"{k}={options[k]}" for k in options])
    options_str = f"?{options_str}" if options_str else ""
    url = f"{BASE_URL}/{brand}/Products/{product}/{product_name}{options_str}"

    get_response = request("get", url, headers=GET_HEADERS, proxies=proxies)
    get_content = get_response.content.decode("utf-8")

    soup = bs4.BeautifulSoup(get_content, features="lxml")
    all_rows = _find_articles_in_page(soup.find("div", {"class": "table-body"}))
    try:
        load_more_button = soup.find("button", {"id": "loadMoreButton"})["onclick"]
    except:
        load_more_button = False

    if not load_more_button:
        tprint("Load more button is not present")
        return all_rows

    m = re.match(
        r"jcp\(\'([A-Z0-9%]+)\'"
        r"\+Base64\.encode\(\'\' \+"
        r" JSON.stringify\(\{.*\'filterSettings\':\'(.*)\',"
        r"\'idProduct\':\'([0-9]+)\'\}\).*",
        load_more_button,
    )

    payload_id = m.groups()[0]
    filter_settings = m.groups()[1]
    article_id = m.groups()[2]
    # tprint(f"Load more button has following attributes: "
    #        f"payload_id={payload_id}, filter_settings={filter_settings}, "
    #        f"article_id={article_id}")

    cookies = {
        "PHPSESSID": get_response.cookies.get("PHPSESSID"),
    }
    # tprint(f"Cookies: {cookies}")
    boundary_id = id_generator()

    new_page = "0"
    while new_page != "-1":
        tprint("At page:", new_page)
        payload = {
            "page": f"{new_page}",
            "filterSettings": filter_settings.replace("\\\\", "\\"),
            "idProduct": article_id,
        }
        payload64 = base64.b64encode(
            json.dumps(payload).replace(" ", "").encode("utf-8")
        ).decode("utf-8")

        data = (
            f"------WebKitFormBoundary{boundary_id}\r\n"
            + 'Content-Disposition: form-data; name="args"\r\n\r\n'
            + f"{payload_id}{payload64}\r\n"
            + f"------WebKitFormBoundary{boundary_id}--\r\n"
        )

        headers = POST_HEADERS.copy()
        headers["Content-Type"] = headers["Content-Type"].format(boundary_id)
        headers["Referer"] = headers["Referer"].format(product_name)

        # tprint(f"Headers: {headers}")
        # tprint(f"Data: {data}")

        sleep(backoff, "POST backoff")
        post_response = request(
            "post",
            f"{BASE_URL}/{brand}/AjaxAction",
            cookies=cookies,
            headers=headers,
            data=data,
            proxies=proxies,
        )
        post_content = post_response.content.decode("utf-8")

        post_soup = bs4.BeautifulSoup(post_content, features="lxml")
        rows_b64 = post_soup.find("rows").text
        new_page = post_soup.find("newpage").text

        rows_raw = base64.b64decode(rows_b64).decode("utf-8")
        all_rows += _find_articles_in_page(rows_raw)

    return all_rows


def get_driver(proxy=None):
    options = Options()
    options.add_argument("--headless")
    service = Service(ChromeDriverManager().install())
    if proxy is not None:
        tprint("Setting up proxy")
        prox = Proxy()
        prox.proxy_type = ProxyType.MANUAL
        prox.http_proxy = proxy
        prox.https_proxy = proxy

        capabilities = webdriver.DesiredCapabilities.CHROME
        prox.add_to_capabilities(capabilities)
    else:
        capabilities = None
    return webdriver.Chrome(
        service=service, options=options, desired_capabilities=capabilities
    )


def _get_html_table(driver, backoff=BACKOFF):
    def find_load_more_button():
        try:
            return driver.find_element(By.ID, "loadMoreButton")
        except NoSuchElementException:
            tprint("Cannot find 'loadMoreButton'")
            return None

    # while loading the button may not be clickable, so we try many times
    def click_button(button, ntry=5):
        for _ in range(ntry):
            try:
                button.click()
                return
            except (
                ElementNotVisibleException,
                ElementNotSelectableException,
            ):
                tprint("Button not ready")
                sleep(backoff, "button to be ready")
        tprint("WARNING: Reached maximum retries for button click")

    def unroll_page():
        loadMoreButton = find_load_more_button()
        nclicks = 0
        # the loading button is never removed if present at the start
        # it is just hidden, so we check that some text is displayed
        while (loadMoreButton is not None) and loadMoreButton.text:
            click_button(loadMoreButton)
            nclicks += 1
            tprint(f"Unroll number {nclicks}")
            sleep(backoff, "more elements request")
            loadMoreButton = find_load_more_button()

    tprint("Unrolling page:", driver.current_url)
    unroll_page()
    tprint("Getting articles table")
    return driver.find_element(By.ID, "table").get_attribute("innerHTML")


def get_articles_selenium(
    driver, brand, product, product_name, options={}, backoff=BACKOFF
):
    # TODO: check options are ok according to table in utils
    options_str = "&".join([f"{k}={options[k]}" for k in options])
    options_str = f"?{options_str}" if options_str else ""
    url = f"{BASE_URL}/{brand}/Products/{product}/{product_name}{options_str}"
    driver.get(url)
    return _find_articles_in_page(_get_html_table(driver, backoff))

################################################################################
################################################################################

if __name__ == "__main__":
    # brand = "Pokemon"
    # expansions = find_expansions(brand)
    # singles = find_singles(expansions, brand)

    # a = find_user(
    #     "Pokemon", "GeCaFeProject", "Singles", {"idLanguage": 7, "minPrice": 15}
    # )
    options = {"language": "1,5", "minCondition": 5, "isSigned": "N", "isAltered": "N"}
    options = {"minCondition": 3, "isSigned": "N", "isAltered": "N"}

    products = [
        "Leaders-Stadium/Mistys-Tears-LST",
        "Challenge-from-the-Darkness/Sabrinas-Gengar-CFTD",
        "Challenge-from-the-Darkness/Kogas-Ninja-Trick-CFTD",
        "Rocket-Gang/Grimer",
        "Challenge-from-the-Darkness/Sabrinas-Gaze-CFTD"
    ]
    articles = []
    for product in products:
        tmp = get_articles_requests(
            "Pokemon", "Singles", product, options=options
        )
        articles += [{"product": product, **a} for a in tmp]
        sleep(BACKOFF)
        #pd.DataFrame(a).to_csv(f".{product.replace('/','.')}.tmp.csv", index=False)
