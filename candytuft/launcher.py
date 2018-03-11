import logging

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

from flask import Flask

from candytuft.cariocawear import load_families as load_cariocawear_families
from candytuft.webapi import register_routes as register_web_api_routes

logging.basicConfig()
logging.getLogger("candytuft").setLevel(logging.DEBUG)

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--blink-settings=imagesEnabled=false")
options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

driver = Chrome(executable_path="/Users/akolmakov/chromedriver", chrome_options=options)


try:
	from candytuft.repository import FamilyRepository, ProductRepository, ImageRepository
	family_repository = FamilyRepository("/tmp/family.json")
	product_repository = ProductRepository("/tmp/product.json")
	image_repository = ImageRepository("/tmp/image.json")

	flask = Flask("candytuft")
	register_web_api_routes(flask, family_repository, product_repository, image_repository)
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

