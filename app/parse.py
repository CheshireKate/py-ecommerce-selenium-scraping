import csv

import selenium
from bs4 import Tag
from selenium import webdriver


from dataclasses import dataclass, fields, astuple
from urllib.parse import urljoin

from selenium.webdriver.common.by import By

BASE_URL = "https://webscraper.io/"
HOME_URL = urljoin(BASE_URL, "test-sites/e-commerce/more/")

_driver = selenium.webdriver.Safari | None

def get_driver() -> selenium.webdriver:
    return _driver

def set_driver(driver_to_set) -> None:
    global _driver
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
    absolute_url = urljoin(BASE_URL, product_soup.select(".title a href").get())
    driver = get_driver()
    driver.get(absolute_url)
    swatches = driver.find_element(By.CLASS_NAME, ".swatches")
    buttons = swatches.find_element(By.CLASS_NAME, ".button")
    btn = driver.find_element(By.CLASS_NAME, ".btn").value
    price = driver.find_element(By.CLASS_NAME, ".price")
    additional_info = {}

    for button in buttons:
        if not button.get_property("disabled"):
            additional_info[btn] = int(price.replace("$", ""))
            button.click()

    return additional_info


def parse_a_product(product_soup: Tag) -> Product:
    absolute_url = urljoin(BASE_URL, product_soup.select(".card thumbnail").get())
    driver = get_driver()
    driver.get(absolute_url)
    additional_info = parse_additional_info(product_soup)
    return Product(
        title = driver.find_element(By.CLASS_NAME, ".title")("title"),
        description = driver.find_element(By.CLASS_NAME, ".price"),
        price = float(driver.find_element(By.CLASS_NAME, ".price").replace("$", "")),
        rating = driver.find_element(By.CLASS_NAME, ".rating")("p data-rating"),
        num_of_reviews = driver.find_element(By.CLASS_NAME, ".review-count"),
        additional_info = additional_info,
    )


def to_csv(products: [Product], driver: webdriver) -> None:
    absolute_url = urljoin(BASE_URL, driver.find_element(By.CLASS_NAME, ".nav-link").get())
    with open (f"{absolute_url}.cvs", "w") as f:
        writer = csv.writer(f)
        writer.writerow(PRODUCT_FIELDS)
        writer.writerows(astuple(product) for product in products)



def get_all_products() -> None:
    driver = get_driver()
    products = []
    more = driver.find_element(By.NAME, ".ecomerce-items-scroll-more")
    while more:
        parse_a_product()
        more.click()
    to_csv(products, driver)



if __name__ == "__main__":
    get_all_products()
