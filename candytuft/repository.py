from threading import RLock
from typing import Type, TypeVar, Generic, Dict, List, Optional, Callable
from uuid import UUID

from candytuft.product import Store, Family, Product, Image
from candytuft.persistence import FilePersistence

T = TypeVar("T")

class Repository(Generic[T]):
	def __init__(self, resolve_id: Callable[[T], UUID]):
		self._resolve_id = resolve_id
		self._rlock = RLock()
		self._t_by_id: Dict[UUID, T] = {}

	def put(self, t: T):
		self._lock()
		try:
			self._put(t)
		finally:
			self._unlock()

	def put_all(self, ts: List[T]):
		self._lock()
		try:
			for t in ts:
				self._put(t)
		finally:
			self._unlock()

	def find_by_id(self, id: UUID) -> Optional[T]:
		self._lock()
		try:
			return self._t_by_id.get(id)
		finally:
			self._unlock()

	@property
	def all(self) -> List[T]:
		self._lock()
		try:
			return self._all
		finally:
			self._unlock()

	def _lock(self):
		self._rlock.acquire()

	def _unlock(self):
		self._rlock.release()

	def _put(self, t: T):
		self._t_by_id[self._resolve_id(t)] = t

	@property
	def _all(self):
		return list(self._t_by_id.values())


def persistent(type: Type[Repository], persistence: FilePersistence):
	class _Persistable(type):
		def __init__(self, *args, **kwargs):
			super().__init__(*args, **kwargs)
			for t in persistence.load():
				self._put(t)

		def flush(self):
			self._lock()
			try:
				return persistence.save(list(self._all))
			finally:
				self._unlock()

	return _Persistable


class StoreRepository(Repository[Store]):
	def __init__(self):
		self._stores_by_short_name: Dict[str, Store] = {}
		super().__init__(lambda s: s.id)

	def _put(self, store: Store):
		super()._put(store)
		self._stores_by_short_name[store.short_name] = store

	def find_by_short_name(self, short_name) -> Optional[Store]:
		return self._stores_by_short_name.get(short_name)


class FamilyRepository(Repository[Family]):
	def __init__(self):
		super().__init__(lambda t: t.id)
		self._families_by_store_id: Dict[UUID, List[Family]] = {}

	def _put(self, family: Family):
		super()._put(family)
		self._families_by_store_id.setdefault(family.store_id, []).append(family)

	def find_by_store_id(self, store_id: UUID) -> List[Family]:
		return self._families_by_store_id.get(store_id, [])


class ProductRepository(Repository[Product]):
	def __init__(self):
		super().__init__(lambda t: t.id)
		self._products_by_family_id: Dict[UUID, List[Product]] = {}

	def _put(self, product: Product):
		super()._put(product)
		self._products_by_family_id.setdefault(product.family_id, []).append(product)

	def find_by_family_id(self, family_id: UUID) -> List[Product]:
		return self._products_by_family_id.get(family_id, [])


class ImageRepository(Repository[Image]):
	def __init__(self):
		super().__init__(lambda t: t.id)
		self._images_by_family_id: Dict[UUID, List[Image]] = {}
		self._images_by_product_id: Dict[UUID, List[Image]] = {}

	def _put(self, image: Image):
		super()._put(image)

		self._images_by_family_id.setdefault(image.family_id, []).append(image)
		if image.product_id:
			self._images_by_product_id.setdefault(image.product_id, []).append(image)

	def find_by_family_id(self, family_id: UUID) -> List[Image]:
		return self._images_by_family_id.get(family_id, [])

	def find_by_product_id(self, product_id: UUID) -> List[Image]:
		return self._images_by_product_id.get(product_id, [])
