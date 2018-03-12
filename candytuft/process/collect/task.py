from typing import Callable, List
from selenium.webdriver import Remote

from candytuft.repository import FamilyRepository, ProductRepository, ImageRepository
from candytuft.process.task import Task

class Task(Task):
	def __init__(self, name: str, driver: Remote, load_families: Callable[[Remote], List], family_repository: FamilyRepository, product_repository: ProductRepository,
			image_repository: ImageRepository) -> None:
		self._name = name
		self._driver = driver
		self._load_families = load_families
		self._family_repository = family_repository
		self._product_repository = product_repository
		self._image_repository = image_repository

	@property
	def name(self) -> str:
		return self._name

	def __call__(self, *args, **kwargs):
		bundles = self._load_families(self._driver)
		for bundle in bundles:
			self._family_repository.put(bundle.family)
			self._product_repository.put_all(bundle.products)
			self._image_repository.put_all(bundle.images)

		self._family_repository.flush()
		self._product_repository.flush()
		self._image_repository.flush()

def new_cariocawear_task(driver: Remote, family_repository: FamilyRepository, product_repository: ProductRepository, image_repository: ImageRepository) -> Task:
	from candytuft.process.collect.cariocawear import load_families
	return Task(name="collect.cariocawear", driver=driver, load_families=load_families, family_repository=family_repository,
		product_repository=product_repository, image_repository=image_repository)
