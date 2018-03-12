from uuid import UUID

from flask import Blueprint, request, abort

from candytuft.repository import StoreRepository, FamilyRepository, ProductRepository, ImageRepository
from candytuft.webapi import json_response as json


class _StoreApi:
	def __init__(self, store_repository: StoreRepository):
		self._store_repository = store_repository

	def get_all(self):
		return json([s.to_dict() for s in self._store_repository.all])

class _FamilyApi:
	def __init__(self, store_repository: StoreRepository, family_repository: FamilyRepository):
		self._store_repository = store_repository
		self._family_repository = family_repository

	def get_all(self):
		short_name = request.args.get("short_name")
		if not short_name:
			return json([f.to_dict() for f in self._family_repository.all])

		store = self._store_repository.find_by_short_name(short_name)
		if not store:
			abort(404)

		return json([f.to_dict() for f in self._family_repository.find_by_store_id(store.id)])

	def get_by_store_id(self, store_id: UUID):
		return json([f.to_dict() for f in self._family_repository.find_by_store_id(store_id)])

class _ProductApi:
	def __init__(self, product_repository: ProductRepository):
		self._product_repository = product_repository

	def get_family_id(self, family_id: UUID):
		return json([f.to_dict() for f in self._product_repository.find_by_family_id(family_id)])

class _ImageApi:
	def __init__(self, image_repository: ImageRepository):
		self._image_repository = image_repository

	def get_family_id(self, family_id: UUID):
		return json([f.to_dict() for f in self._image_repository.find_by_family_id(family_id)])

	def get_product_id(self, product_id: UUID):
		return json([f.to_dict() for f in self._image_repository.find_by_product_id(product_id)])


def get_web_api(store_repository: StoreRepository, family_repository: FamilyRepository, product_repository: ProductRepository,
		image_repository: ImageRepository) -> Blueprint:
	store_api = _StoreApi(store_repository)
	family_api = _FamilyApi(store_repository, family_repository)
	product_api = _ProductApi(product_repository)
	image_api = _ImageApi(image_repository)

	blueprint = Blueprint("product", __name__)

	blueprint.add_url_rule("/stores", "store-get_all", store_api.get_all)
	blueprint.add_url_rule("/stores/<uuid:store_id>/families", "family-get_by_store_id", family_api.get_by_store_id)
	blueprint.add_url_rule("/families", "family-get_all", family_api.get_all)
	blueprint.add_url_rule("/families/<uuid:family_id>/products", "product-get_family_id", product_api.get_family_id)
	blueprint.add_url_rule("/families/<uuid:family_id>/images", "image-get_family_id", image_api.get_family_id)
	blueprint.add_url_rule("/products/<uuid:product_id>/images", "image-get_product_id", image_api.get_product_id)

	return blueprint
