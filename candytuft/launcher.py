import logging

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

from flask import Flask

from candytuft.cariocawear import load_families as load_cariocawear_families
from candytuft.webapi import register_routes as register_web_api_routes
from candytuft.config import store_repository

logging.basicConfig()
logging.getLogger("candytuft").setLevel(logging.DEBUG)

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--blink-settings=imagesEnabled=false")
options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

driver = Chrome(executable_path="/Users/akolmakov/chromedriver", chrome_options=options)


try:
	from candytuft.produсt import Family, Product, Image
	from candytuft.persistence import FilePersistence
	from candytuft.repository import FamilyRepository, ProductRepository, ImageRepository, persistent
	family_repository = persistent(type=FamilyRepository, persistence=FilePersistence[Family](file_path="/tmp/family.json", to_dict=lambda f: f.to_dict(), from_dict=Family.from_dict))()
	product_repository = persistent(type=ProductRepository, persistence=FilePersistence[Product](file_path="/tmp/product.json", to_dict=lambda p: p.to_dict(), from_dict=Product.from_dict))()
	image_repository = persistent(type=ImageRepository, persistence=FilePersistence[Image](file_path="/tmp/image.json", to_dict=lambda i: i.to_dict(), from_dict=Image.from_dict))()

	flask = Flask("candytuft")
	register_web_api_routes(flask, store_repository, family_repository, product_repository, image_repository)
	flask.run(port=8080)

	bundles = load_cariocawear_families(driver)
	for bundle in bundles:
		family_repository.put(bundle.family)
		product_repository.put_all(bundle.products)
		image_repository.put_all(bundle.images)

	family_repository.flush()
	product_repository.flush()
	image_repository.flush()


finally:
	driver.quit()

