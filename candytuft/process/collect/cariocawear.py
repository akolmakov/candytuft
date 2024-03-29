import re
import ujson
import logging

from uuid import UUID, uuid4
from typing import Dict, List, Any

from selenium.webdriver import Remote

from candytuft.product import Family, Product, Image, Bundle
from candytuft.config import CARIOCA_VENDOR
from candytuft.config import CARIOCAWEAR_STORE


logger = logging.getLogger("candytuft.process.collect.cariocawear")

def _new_family(url: str, json: Dict[str, Any]) -> Family:
	return Family(id=uuid4(), foreign_id=str(json["id"]), store_id=CARIOCAWEAR_STORE.id, vendor_id=CARIOCA_VENDOR.id, name=json["title"], url=url,
		timestamp=None)


def _resolve_tags(products: List[Product]):
	tags = set()
	tags.add("swimwear")

	for product in products:
		tags.add(product.options["cut"].lower())

	return tags


def _new_product(family_id: UUID, json: Dict[str, Any]) -> Product:
	options = {"sku": json["sku"]}
	if not json.get("option3"):
		options["cut"] = json["option1"]
		options["fit"] = json["option2"]
	else:
		options["color"] = json["option1"]
		options["cut"] = json["option2"]
		options["fit"] = json["option3"]
	product = Product(id=uuid4(), foreign_id=str(json["id"]), family_id=family_id, available=json["available"], price=json["price"] / 100.0, timestamp=None,
		**options)
	return product


def _new_product_image(family_id: UUID, product_id: UUID, json: Dict[str, Any]) -> Image:
	return Image(id=uuid4(), foreign_id=str(json["id"]), family_id=family_id, product_id=product_id, url=json["src"], timestamp=None)


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


def _load_family(driver: Remote, url: str) -> Bundle:
	builder = Bundle.builder()

	driver.get(url)

	# todo: compare with store currency
	currency = driver.execute_script("return Currency.currentCurrency;")

	meta = driver.execute_script("return window.ShopifyAnalytics.meta;")
	element = driver.find_element_by_id("product-form-{}".format(meta["page"]["resourceId"]))

	family_json = ujson.loads(element.get_attribute("data-product"))
	family = _new_family(url, family_json)
	builder.family(family)

	for product_json in family_json["variants"]:
		product = _new_product(family.id, product_json)
		builder.product(product)

		image_json = product_json["featured_image"]
		if image_json:
			builder.image(_new_product_image(family.id, product.id, image_json))

	bundle = builder.build()

	logger.debug("Loaded product family '%s' with %d products and %d images from '%s'", bundle.family.name, len(bundle.products), len(bundle.images),
		bundle.family.url)

	return bundle


def load_families(driver: Remote) -> List[Bundle]:
	family_urls = _load_family_urls(driver, CARIOCAWEAR_STORE.url + "/collections/swimwear-sunga")
	return [_load_family(driver, family_url) for family_url in family_urls]

