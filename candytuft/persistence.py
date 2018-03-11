import ujson
from io import open
from typing import TypeVar, Generic, Callable, Dict, List
from uuid import UUID

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