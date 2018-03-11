
from typing import Optional, Dict, List, Any
from datetime import datetime, timezone
from uuid import UUID

def _now_utc() -> int:
	return int(datetime.now(timezone.utc).timestamp() * 1000)


class Store:
	def __init__(self, id: UUID, short_name: str, name: str, currency: str, url: str):
		self.id = id
		self.short_name = short_name
		self.name = name
		self.currency = currency
		self.url = url


class Family:
	def __init__(self, id: UUID, foreign_id: str, store_id: UUID, name: str, url: str, timestamp: Optional[int]):
		self.id = id
		self.foreign_id = foreign_id
		self.store_id = store_id
		self.name = name
		self.url = url
		self.timestamp = timestamp if timestamp else _now_utc()

	@staticmethod
	def from_dict(dict: Dict[str, Any]) -> "Family":
		return Family(id=UUID(dict["id"]), foreign_id=dict["foreign_id"], store_id=UUID(dict["store_id"]), name=dict["name"], url=dict["url"],
			timestamp=dict["timestamp"])

	def to_dict(self) -> Dict[str, Any]:
		return {"id": str(self.id), "foreign_id": self.foreign_id, "store_id": str(self.store_id), "name": self.name, "url": self.url,
			"timestamp": self.timestamp}

	def __str__(self) -> str:
		return "id={}, foreign_id={}, store_id={}, name='{}', url='{}', timestamp={}".format(self.id, self.foreign_id, self.store_id, self.name, self.url,
			self.timestamp)

class Product:
	def __init__(self, id: UUID, foreign_id: str, family_id: UUID, available: bool, price: float, timestamp: Optional[int], **kwargs):
		self.id = id
		self.foreign_id = foreign_id
		self.family_id = family_id
		self.available = available
		self.price = price
		self.timestamp = timestamp if timestamp else _now_utc()

		self.options: Dict[str, str] = dict()
		for name, value in kwargs.items():
			if type(value) != str:
				raise ValueError("'{}' must be of str type".format(name))
			self.options[name] = value

	@staticmethod
	def from_dict(dict: Dict[str, Any]) -> "Product":
		return Product(id=UUID(dict["id"]), foreign_id=dict["foreign_id"], family_id=UUID(dict["family_id"]), available=dict["available"],
			price=dict["price"], timestamp=dict["timestamp"], **dict["options"])

	def to_dict(self) -> Dict[str, Any]:
		return {"id": str(self.id), "foreign_id": self.foreign_id, "family_id": str(self.family_id), "available": self.available, "price": self.price,
			"timestamp": self.timestamp, "options": self.options}

	def __str__(self) -> str:
		options = ", ".join(["{}={}".format(key, "'{}'".format(value) if type(value) == str else value) for (key, value) in sorted(self.options.items())])
		return "id={}, foreign_id={}, family_id={}, available={}, price=[{}], timestamp={}, options=[{}]".format(self.id, self.foreign_id, self.family_id,
			self.available, self.price, self.timestamp, options)

class Image:
	def __init__(self, id: UUID, foreign_id: Optional[str], family_id: UUID, product_id: Optional[UUID], url: str, timestamp: Optional[int]):
		self.id = id
		self.foreign_id = foreign_id
		self.family_id = family_id
		self.product_id = product_id
		self.url = url
		self.timestamp = timestamp if timestamp else _now_utc()

	@staticmethod
	def from_dict(dict: Dict[str, Any]) -> "Image":
		return Image(id=UUID(dict["id"]), foreign_id=dict["foreign_id"], family_id=UUID(dict["family_id"]), product_id=UUID(dict["product_id"]),
			url=dict["url"], timestamp=dict["timestamp"])

	def to_dict(self) -> Dict[str, Any]:
		return {"id": str(self.id), "foreign_id": self.foreign_id, "family_id": str(self.family_id), "product_id": str(self.product_id), "url": self.url,
			"timestamp": self.timestamp}


class BundleBuilder:
	def __init__(self):
		self._family = None
		self._products = []
		self._images = []

	def family(self, family: Family) -> "BundleBuilder":
		self._family = family
		return self

	def product(self, product: Product) -> "BundleBuilder":
		self._products.append(product)
		return self

	def image(self, image: Image) -> "BundleBuilder":
		self._images.append(image)
		return self

	def build(self) -> "Bundle":
		return Bundle(family=self._family, products=self._products, images=self._images)

class Bundle:
	def __init__(self, family: Family, products: List[Product], images: List[Image]):
		self.family = family
		self.products = products
		self.images = images

	@staticmethod
	def builder() -> BundleBuilder:
		return BundleBuilder()
