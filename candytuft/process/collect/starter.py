from selenium.webdriver import Remote
from candytuft.repository import FamilyRepository, ProductRepository, ImageRepository
from candytuft.process.task import TaskQueue
from candytuft.process.collect.task import new_cariocawear_task

class Starter:
	def __init__(self, driver: Remote, queue: TaskQueue, family_repository: FamilyRepository, product_repository: ProductRepository, image_repository: ImageRepository, ) -> None:
		self._driver = driver
		self._queue = queue
		self._family_repository = family_repository
		self._product_repository = product_repository
		self._image_repository = image_repository

	def start(self):
		task = new_cariocawear_task(driver=self._driver, family_repository=self._family_repository, product_repository=self._product_repository,
			image_repository=self._image_repository)
		self._queue.add(task)
