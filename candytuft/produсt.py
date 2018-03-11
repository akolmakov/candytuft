from typing import Optional, Dict, List, Any, Tuple
from uuid import UUID

class Store:
	def __init__(self, id: UUID, name: str, url: str):
		self.id = id
		self.name = name
		self.url = url


class Family:
	def __init__(self, id: UUID, foreign_id: str, store_id: UUID, name: str, url: str):
		self.id = id
		self.foreign_id = foreign_id
		self.store_id = store_id
		self.name = name
		self.url = url

	def __str__(self) -> str:
		return "id={}, foreign_id={}, store_id={}, name='{}', url='{}'".format(self.id, self.foreign_id, self.store_id, self.name,
			self.url)

class Price:
	def __init__(self, value: float, currency: str):
		self.value = value
		self.currency = currency

	@staticmethod
	def from_dict(dict: Dict[str, Any]):
		return Price(value=dict["value"], currency=dict["currency"])

	def to_dict(self) -> Dict[str, Any]:
		return {"value": self.value, "currency": self.currency}

	def __str__(self) -> str:
		return "value={}, currency={}".format(self.value, self.currency)

class Product:
	def __init__(self, id: UUID, foreign_id: str, family_id: UUID, available: bool, price: Price, **kwargs):
		self.id = id
		self.foreign_id = foreign_id
		self.family_id = family_id
		self.available = available
		self.price = price

		self.options: Dict[str, str] = dict()
		for name, value in kwargs.items():
			if type(value) != str:
				raise ValueError("'{}' must be of str type".format(name))
			self.options[name] = value

	@staticmethod
	def from_dict(dict: Dict[str, Any]):
		return Product(id=UUID(dict["id"]), foreign_id=dict["foreign_id"], family_id=UUID(dict["family_id"]), available=dict["available"],
			price=Price.from_dict(dict["price"]), **dict["options"])

	def to_dict(self) -> Dict[str, Any]:
		return {"id": str(self.id), "foreign_id": self.foreign_id, "family_id": str(self.family_id), "available": self.available, "price": self.price.to_dict(),
			"options": self.options}

	def __str__(self) -> str:
		options = ", ".join(["{}={}".format(key, "'{}'".format(value) if type(value) == str else value) for (key, value) in sorted(self.options.items())])
		return "id={}, foreign_id={}, family_id={}, available={}, price=[{}], options=[{}]".format(self.id, self.foreign_id, self.family_id, self.available,
			self.price, options)

class Image:
	def __init__(self, id: UUID, foreign_id: Optional[str], family_id: UUID, product_id: Optional[UUID], url: str):
		self.id = id
		self.foreign_id = foreign_id
		self.family_id = family_id
		self.product_id = product_id
		self.url = url

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
