from typing import Optional
from uuid import UUID

class Family:
	def __init__(self, id: UUID, foreign_id: str, name: str, image: Optional[Image], url: str, **kwargs):
		self.id = id
		self.foreign_id = foreign_id
		self.name = name
		self.image = image
		self.url = url
		for name, value in kwargs.items():
			setattr(self, name, value)

class Product:
	def __init__(self, id: UUID, foreign_id: str, family_id: UUID, **kwargs):
		self.id = id
		self.foreign_id = foreign_id
		self.family_id = family_id
		for name, value in kwargs.items():
			setattr(self, name, value)

class Image:
	def __init__(self, id: UUID, foreign_id: Optional[str], url: str):
		self.id = id
		self.foreign_id = foreign_id
		self.url = url

class Price:
	def __init__(self, id: UUID, product_id: UUID, value: float, currency: str):
		self.id = id
		self.product_id = product_id
		self.value = value
		self.currency = currency
