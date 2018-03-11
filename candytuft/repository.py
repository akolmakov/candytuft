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

	def load(self) -> Dict[UUID, T]:
		try:
			with open(self._file_path, mode="r", encoding="utf-8") as file:
				json = ujson.load(file)
				return {UUID(id): self._from_dict(t) for id, t in json.items()}
		except FileNotFoundError:
			return {}

	def save(self, t_by_id: Dict[UUID, T]):
		json = {str(id): self._to_dict(t) for id, t in t_by_id.items()}
		with open(self._file_path, mode="w", encoding="utf-8") as file:
			file.write(ujson.dumps(json, ensure_ascii=False))


class Repository(Generic[T]):
	def __init__(self, persistence: FilePersistence, resolve_id: Callable[[T], UUID]):
		self._persistence = persistence
		self._resolve_id = resolve_id
		self._lock = RLock()
		self._t_by_id: Dict[UUID, T] = self._persistence.load()

	def put(self, t: T):
		self._lock.acquire()
		try:
			self._t_by_id[self._resolve_id(t)] = t
		finally:
			self._lock.release()

	def put_all(self, ts: List[T]):
		self._lock.acquire()
		try:
			for t in ts:
				self._t_by_id[self._resolve_id(t)] = t
		finally:
			self._lock.release()

	def find_by_id(self, id: UUID) -> Optional[T]:
		self._lock.acquire()
		try:
			return self._t_by_id.get(id)
		finally:
			self._lock.release()

	def flush(self):
		self._lock.acquire()
		try:
			return self._persistence.save(self._t_by_id)
		finally:
			self._lock.release()

class ProductRepository(Repository[Product]):
	def __init__(self, file_path: str):
		persistence = FilePersistence[Product](file_path=file_path, to_dict=lambda p: p.to_dict(), from_dict=Product.from_dict)
		super().__init__(persistence, lambda t: t.id)
