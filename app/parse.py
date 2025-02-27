import csv

import selenium
from bs4 import Tag, BeautifulSoup
from selenium import webdriver


from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

from selenium.webdriver.common.by import By

BASE_URL = "https://webscraper.io/"
HOME_URL = urljoin(BASE_URL, "test-sites/e-commerce/more/")

driver: webdriver = None

PAGES = {
    "home": "https://webscraper.io/test-sites/e-commerce/more",
    "computers": "https://webscraper.io/test-sites/e-commerce/more/computers",
    "laptops": "https://webscraper.io/test-sites/e-commerce/more/computers/laptops",
    "tablets": "https://webscraper.io/test-sites/e-commerce/more/computers/tablets",
    "phones": "https://webscraper.io/test-sites/e-commerce/more/phones",
    "touch": "https://webscraper.io/test-sites/e-commerce/more/phones/touch",
}

def get_driver() -> selenium.webdriver:
    return driver

def set_driver(driver_to_set) -> None:
    global driver
    _driver = driver_to_set

@dataclass
class Product:
    title: str
    description: str
    price: float
    rating: int
    num_of_reviews: int
    additional_info: dict

PRODUCT_FIELDS = [field.name for field in fields(Product)]

def parse_additional_info(product_soup: Tag) -> dict:
    absolute_url = urljoin(BASE_URL, product_soup.select_one("a")["href"])
    driver = get_driver()
    driver.get(absolute_url)
    swatches = driver.find_element(By.CLASS_NAME, "swatches")
    buttons = swatches.find_elements(By.CLASS_NAME, "button")
    btn = driver.find_element(By.CLASS_NAME, "btn").text
    price = driver.find_element(By.CLASS_NAME, "price").text
    additional_info = {}

    for button in buttons:
        if not button.get_property("disabled"):
            additional_info[btn] = int(price.replace("$", ""))
            button.click()

    return additional_info


def parse_a_product(product_soup: Tag) -> Product:
    absolute_url = urljoin(BASE_URL, product_soup.select_one(".card.thumbnail a")["href"])
    driver = get_driver()
    driver.get(absolute_url)
    additional_info = parse_additional_info(product_soup)
    return Product(
        title = driver.find_element(By.CLASS_NAME, "title").text,
        description = driver.find_element(By.CLASS_NAME, "description").text,
        price = float(driver.find_element(By.CLASS_NAME, "price").replace("$", "")),
        rating = driver.find_element(By.CLASS_NAME, "rating"),
        num_of_reviews = driver.find_element(By.CLASS_NAME, "review-count").text,
        additional_info = additional_info,
    )

def parse_page(page_url: str) -> list[Product]:
    driver = get_driver()
    products = []
    more = driver.find_element(By.CLASS_NAME, "ecomerce-items-scroll-more")
    driver.get(page_url)

    while True:
        try:
            more.click()
        except:
            break

    soup = BeautifulSoup(driver.page_source, "html.parser")
    product_elements = soup.select(".thumbnail")

    products = [parse_a_product(product) for product in product_elements]
    return products



def to_csv(products: [Product], driver: webdriver) -> None:
    absolute_url = driver.current_url.split("/")[-1]
    with open (f"{absolute_url}.csv", "w") as f:
        writer = csv.writer(f)
        writer.writerow(PRODUCT_FIELDS)
        writer.writerows(astuple(product) for product in products)



def get_all_products() -> None:
    products = []
    for page in PAGES:
        products += parse_page(page)

    to_csv(products, driver)



if __name__ == "__main__":
    get_all_products()
