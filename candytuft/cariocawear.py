import ujson

from uuid import uuid4

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

from candytuft.produсt import Image, Price, Family, Product

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

driver = Chrome(executable_path="/Users/akolmakov/chromedriver", chrome_options=options)

try:
	url = "https://cariocawear.com/collections/sale/products/verde-green"
	driver.get(url)

	resourceId = driver.execute_script("return window.ShopifyAnalytics.meta;")["page"]["resourceId"]
	currency = driver.execute_script("return Currency.currentCurrency;")

	form = driver.find_element_by_id("product-form-{}".format(resourceId))
	json = ujson.loads(form.get_attribute("data-product"))

	family = Family(id=uuid4(), foreign_id=str(json["id"]), name=json["title"], image=None, url=url)

	for variant_json in json["variants"]:
		image_json = json["featured_image"]
		image = Image(id=uuid4(), foreign_id=str(image_json["id"]), url=image_json["src"])

		product = Product(id=uuid4(), foreign_id=str(variant_json["id"]), family_id=family.id, image=image, cut=variant_json["option1"], size=variant_json["option2"])
		price = Price(id=uuid4(), product_id=product.id, value=variant_json["price"] / 100.0, currency=currency)
finally:
	driver.quit()

# read page.resourceId from meta


