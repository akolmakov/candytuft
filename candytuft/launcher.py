import logging

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options

from candytuft.cariocawear import load_families as load_cariocawear_families

logging.basicConfig()
logging.getLogger("candytuft").setLevel(logging.DEBUG)

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--blink-settings=imagesEnabled=false")
options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

driver = Chrome(executable_path="/Users/akolmakov/chromedriver", chrome_options=options)

try:
	from candytuft.repository import ProductRepository
	repository = ProductRepository("./product.json")

	bundles = load_cariocawear_families(driver)
	for bundle in bundles:
		repository.put_all(bundle.products)

	repository.flush()


finally:
	driver.quit()

