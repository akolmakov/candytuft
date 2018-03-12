import logging

from argparse import ArgumentParser

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

from flask import Flask

from candytuft.process.task import TaskQueue
from candytuft.process.collect.starter import Starter as CollectStarter
from candytuft.webapi.product import get_web_api as get_product_web_api
from candytuft.webapi.collect import get_web_api as get_collect_web_api
from candytuft.config import store_repository

logging.basicConfig()
logging.getLogger("candytuft").setLevel(logging.DEBUG)

logger = logging.getLogger("candytuft.launcher")


argument_parser = ArgumentParser()
argument_parser.add_argument("--chrome-path", nargs="?", required=True, dest="chrome_path")
argument_parser.add_argument("--chrome-driver-path", nargs="?", required=True, dest="chrome_driver_path")
arguments = argument_parser.parse_args()

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--disable-extensions")
options.add_argument("--no-sandbox")
options.add_argument("--blink-settings=imagesEnabled=false")
# "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
options.binary_location = arguments.chrome_path

# "/Users/akolmakov/chromedriver"
driver = Chrome(executable_path=arguments.chrome_driver_path, chrome_options=options)

def candytuft():
	logger.info("Launching Candytuft")
	try:
		from candytuft.product import Family, Product, Image
		from candytuft.persistence import FilePersistence
		from candytuft.repository import FamilyRepository, ProductRepository, ImageRepository, persistent
		family_repository = persistent(type=FamilyRepository, persistence=FilePersistence[Family](file_path="/tmp/family.json", to_dict=lambda f: f.to_dict(), from_dict=Family.from_dict))()
		product_repository = persistent(type=ProductRepository, persistence=FilePersistence[Product](file_path="/tmp/product.json", to_dict=lambda p: p.to_dict(), from_dict=Product.from_dict))()
		image_repository = persistent(type=ImageRepository, persistence=FilePersistence[Image](file_path="/tmp/image.json", to_dict=lambda i: i.to_dict(), from_dict=Image.from_dict))()

		collect_starter = CollectStarter(driver=driver, queue=TaskQueue(concurrency_level=1), family_repository=family_repository, product_repository=product_repository,
			image_repository=image_repository)

		flask = Flask("candytuft")
		product_web_api = get_product_web_api(store_repository, family_repository, product_repository, image_repository)
		collect_web_api = get_collect_web_api(starter=collect_starter)
		flask.register_blueprint(product_web_api, url_prefix="/api")
		flask.register_blueprint(collect_web_api, url_prefix="/api")

		logger.info("Web API listens on port 8080")
		flask.run(host="0.0.0.0", port=8080)

	finally:
		driver.quit()
