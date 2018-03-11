from typing import TypeVar, Generic, Callable, Dict, List, Optional
from uuid import UUID
from threading import RLock
from io import open

import ujson

from candytuft.produсt import Family, Product, Image

T = TypeVar("T")


class FilePersistence(Generic[T]):
	def __init__(self, file_path: str, to_dict: Callable[[T], Dict], from_dict: Callable[[Dict], T]):
		self._file_path = file_path
		self._to_dict = to_dict
		self._from_dict = from_dict

	def load(self) -> List[T]:
		try:
			with open(self._file_path, mode="r", encoding="utf-8") as file:
				return [self._from_dict(t) for t in ujson.load(file)]
		except FileNotFoundError:
			return []

	def save(self, ts: List[UUID]):
		json = [self._to_dict(t) for t in ts]
		with open(self._file_path, mode="w", encoding="utf-8") as file:
			file.write(ujson.dumps(json, ensure_ascii=False))


class Repository(Generic[T]):
	def __init__(self, persistence: FilePersistence, resolve_id: Callable[[T], UUID]):
		self._persistence = persistence
		self._resolve_id = resolve_id
		self._lock = RLock()
		self._t_by_id: Dict[UUID, T] = {}

		for t in self._persistence.load():
			self._put(t)

	def put(self, t: T):
		self._lock.acquire()
		try:
			self._put(t)
		finally:
			self._lock.release()

	def put_all(self, ts: List[T]):
		self._lock.acquire()
		try:
			for t in ts:
				self._put(t)
		finally:
			self._lock.release()

	def _put(self, t: T):
		self._t_by_id[self._resolve_id(t)] = t

	def find_by_id(self, id: UUID) -> Optional[T]:
		self._lock.acquire()
		try:
			return self._t_by_id.get(id)
		finally:
			self._lock.release()

	def get_all(self) -> List[T]:
		self._lock.acquire()
		try:
			return list(self._t_by_id.values())
		finally:
			self._lock.release()

	def flush(self):
		self._lock.acquire()
		try:
			return self._persistence.save(list(self._t_by_id.values()))
		finally:
			self._lock.release()

class FamilyRepository(Repository[Family]):
	def __init__(self, file_path: str):
		self._families_by_store_id: Dict[UUID, List[Family]] = {}

		persistence = FilePersistence[Family](file_path=file_path, to_dict=lambda f: f.to_dict(), from_dict=Family.from_dict)
		super().__init__(persistence, lambda t: t.id)

	def _put(self, family: Family):
		super()._put(family)
		self._families_by_store_id.setdefault(family.store_id, []).append(family)

	def find_by_store_id(self, store_id: UUID) -> List[Family]:
		return self._families_by_store_id.get(store_id, [])


class ProductRepository(Repository[Product]):
	def __init__(self, file_path: str):
		self._products_by_family_id: Dict[UUID, List[Product]] = {}

		persistence = FilePersistence[Product](file_path=file_path, to_dict=lambda p: p.to_dict(), from_dict=Product.from_dict)
		super().__init__(persistence, lambda t: t.id)

	def _put(self, product: Product):
		super()._put(product)
		self._products_by_family_id.setdefault(product.family_id, []).append(product)

	def find_by_family_id(self, family_id: UUID) -> List[Product]:
		return self._products_by_family_id.get(family_id, [])


class ImageRepository(Repository[Image]):
	def __init__(self, file_path: str):
		self._images_by_family_id: Dict[UUID, List[Image]] = {}
		self._images_by_product_id: Dict[UUID, List[Image]] = {}

		persistence = FilePersistence[Image](file_path=file_path, to_dict=lambda i: i.to_dict(), from_dict=Image.from_dict)
		super().__init__(persistence, lambda t: t.id)

	def _put(self, image: Image):
		super()._put(image)

		self._images_by_family_id.setdefault(image.family_id, []).append(image)
		if image.product_id:
			self._images_by_product_id.setdefault(image.product_id, []).append(image)

	def find_by_family_id(self, family_id: UUID) -> List[Image]:
		return self._images_by_family_id.get(family_id, [])

	def find_by_product_id(self, product_id: UUID) -> List[Image]:
		return self._images_by_product_id.get(product_id, [])
