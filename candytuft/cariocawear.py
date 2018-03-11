import re
import ujson
import logging

from uuid import uuid4

from selenium.webdriver import Remote

from candytuft.produсt import *

CARIOCAWEAR_STORE = Store(id=UUID("fd1e0b6f-9f35-4261-8bf7-4204bc7cff6a"), name="CA-RIO­CA Sunga Co.", url="https://cariocawear.com")

logger = logging.getLogger("candytuft.cariocawear")


def _new_family(store: Store, url: str, json: Dict[str, Any]) -> Family:
	return Family(id=uuid4(), foreign_id=str(json["id"]), store_id=store.id, name=json["title"], url=url)


def _new_product(family: Family, currency: str, json: Dict[str, Any]) -> Product:
	price = Price(value=json["price"] / 100.0, currency=currency)
	product = Product(id=uuid4(), foreign_id=str(json["id"]), family_id=family.id, available=json["available"], price=price, cut=json["option1"],
		size=json["option2"])
	return product


def _new_product_image(family: Family, product: Product, json: Dict[str, Any]) -> Image:
	return Image(id=uuid4(), foreign_id=str(json["id"]), family_id=family.id, product_id=product.id, url=json["src"])


def _load_family_urls(driver: Remote, url: str):
	page_url_pattern = url + "?page={}"

	result = []
	page_number = 1
	page_count = 1

	while page_number <= page_count:
		page_url = page_url_pattern.format(page_number)

		driver.get(page_url)

		div_element = driver.find_element_by_css_selector("div.breadcrumb-collection div.breadcrumb_text")
		page_count = int(re.match(".*Page \d+ of (?P<page_count>\d+)$", div_element.get_property("innerText"), re.IGNORECASE).group("page_count"))

		a_elements = driver.find_elements_by_css_selector("div.product-list div.product-wrap a.product-info__caption")
		for a_element in a_elements:
			result.append(a_element.get_attribute("href"))

		logger.debug("Loaded %d products family URLs from '%s'", len(a_elements), page_url)

		page_number += 1

	return result


def _load_family(driver: Remote, store: Store, url: str) -> Bundle:
	builder = Bundle.builder()

	driver.get(url)

	currency = driver.execute_script("return Currency.currentCurrency;")

	meta = driver.execute_script("return window.ShopifyAnalytics.meta;")
	element = driver.find_element_by_id("product-form-{}".format(meta["page"]["resourceId"]))

	family_json = ujson.loads(element.get_attribute("data-product"))

	family = _new_family(store, url, family_json)
	builder.family(family)

	for product_json in family_json["variants"]:
		product = _new_product(family, currency, product_json)
		builder.product(product)

		image_json = product_json["featured_image"]
		if image_json:
			builder.image(_new_product_image(family, product, image_json))

	bundle = builder.build()

	logger.debug("Loaded product family '%s' with %d products and %d images from '%s'", bundle.family.name, len(bundle.products), len(bundle.images),
		bundle.family.url)

	return bundle


def load_families(driver: Remote) -> List[Bundle]:
	family_urls = _load_family_urls(driver, CARIOCAWEAR_STORE.url + "/collections/swimwear-sunga")
	return [_load_family(driver, CARIOCAWEAR_STORE, family_url) for family_url in family_urls]

