import ujson

from uuid import uuid4

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

from candytuft.produсt import *

CARIOCAWEAR_STORE = Store(id=UUID("fd1e0b6f-9f35-4261-8bf7-4204bc7cff6a"), name="CA-RIO­CA Sunga Co.", url="https://cariocawear.com")

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

driver = Chrome(executable_path="/Users/akolmakov/chromedriver", chrome_options=options)


def _new_family(store: Store, json: Dict[str, Any]) -> Family:
	return Family(id=uuid4(), foreign_id=str(json["id"]), store_id=store.id, name=json["title"], url=url)


def _new_product(family: Family, json: Dict[str, Any]) -> Product:
	price = Price(value=json["price"] / 100.0, currency=currency)
	product = Product(id=uuid4(), foreign_id=str(json["id"]), family_id=family.id, available=json["available"], price=price, cut=json["option1"],
		size=json["option2"])
	return product


def _new_product_image(family: Family, product: Product, json: Dict[str, Any]) -> Image:
	return Image(id=uuid4(), foreign_id=str(json["id"]), family_id=family.id, product_id=product.id, url=json["src"])


try:
	url = "https://cariocawear.com/collections/sale/products/verde-green"
	store = CARIOCAWEAR_STORE

	driver.get(url)

	resourceId = driver.execute_script("return window.ShopifyAnalytics.meta;")["page"]["resourceId"]
	currency = driver.execute_script("return Currency.currentCurrency;")

	form = driver.find_element_by_id("product-form-{}".format(resourceId))
	json = ujson.loads(form.get_attribute("data-product"))

	family = _new_family(store, json)

	for variant_json in json["variants"]:
		product = _new_product(family, variant_json)
		image = _new_product_image(family, product, variant_json["featured_image"])


finally:
	driver.quit()

# read page.resourceId from meta


