import ujson

from uuid import UUID
from typing import Any
from flask import Flask, Response, request

from candytuft.repository import StoreRepository, FamilyRepository, ProductRepository, ImageRepository

def _json_response(content: Any):
	return Response(response=ujson.dumps(content, ensure_ascii=False), status=200, mimetype="application/json")

def _not_found_response():
	return Response(status=404)

class WebApi:
	def __init__(self, store_repository: StoreRepository, family_repository: FamilyRepository, product_repository: ProductRepository,
			image_repository: ImageRepository):
		self._store_repository = store_repository
		self._family_repository = family_repository
		self._product_repository = product_repository
		self._image_repository = image_repository

	def get_stores(self):
		return _json_response([s.to_dict() for s in self._store_repository.all])

	def get_families_by_store_id(self, store_id: UUID):
		return _json_response([f.to_dict() for f in self._family_repository.find_by_store_id(store_id)])

	def get_families(self):
		short_name = request.args.get("short_name")
		if not short_name:
			return _json_response([f.to_dict() for f in self._family_repository.all])

		store = self._store_repository.find_by_short_name(short_name)
		if not store:
			return _not_found_response()

		return _json_response([f.to_dict() for f in self._family_repository.find_by_store_id(store.id)])

	def get_products_by_family_id(self, family_id: UUID):
		return _json_response([f.to_dict() for f in self._product_repository.find_by_family_id(family_id)])

	def get_images_by_family_id(self, family_id: UUID):
		return _json_response([f.to_dict() for f in self._image_repository.find_by_family_id(family_id)])

	def get_images_by_product_id(self, product_id: UUID):
		return _json_response([f.to_dict() for f in self._image_repository.find_by_product_id(product_id)])


def register_routes(flask: Flask, store_repository: StoreRepository, family_repository: FamilyRepository, product_repository: ProductRepository,
		image_repository: ImageRepository):
	web_api = WebApi(store_repository, family_repository, product_repository, image_repository)

	flask.add_url_rule("/stores", "stores", web_api.get_stores)
	flask.add_url_rule("/stores/<uuid:store_id>/families", "stores-families", web_api.get_families_by_store_id)
	flask.add_url_rule("/families", "families", web_api.get_families)
	flask.add_url_rule("/families/<uuid:family_id>/products", "families-products", web_api.get_products_by_family_id)
	flask.add_url_rule("/families/<uuid:family_id>/images", "families-images", web_api.get_images_by_family_id)
	flask.add_url_rule("/products/<uuid:product_id>/images", "products-images", web_api.get_images_by_product_id)
