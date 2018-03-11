import ujson

from uuid import UUID
from typing import Any, List
from flask import Flask, Response, request

from candytuft.produсt import Store
from candytuft.cariocawear import STORE as CARIOCAWEAR_STORE
from candytuft.repository import FamilyRepository, ProductRepository, ImageRepository

def _json_response(content: Any):
	return Response(response=ujson.dumps(content, ensure_ascii=False), status=200, mimetype="application/json")

def _not_found_response():
	return Response(status=404)

class WebApi:
	def __init__(self, stores: List[Store], family_repository: FamilyRepository, product_repository: ProductRepository,
			image_repository: ImageRepository):
		self._store_by_short_name = {s.short_name: s for s in stores}
		self._family_repository = family_repository
		self._product_repository = product_repository
		self._image_repository = image_repository

	def get_families(self):
		short_name = request.args.get("short_name")
		if not short_name:
			return _json_response([f.to_dict() for f in self._family_repository.get_all()])

		store = self._store_by_short_name.get(short_name, None)
		if not store:
			return _not_found_response()

		return _json_response([f.to_dict() for f in self._family_repository.find_by_store_id(store.id)])

	def get_products_by_family_id(self, family_id: UUID):
		return _json_response([f.to_dict() for f in self._product_repository.find_by_family_id(family_id)])

	def get_images_by_family_id(self, family_id: UUID):
		return _json_response([f.to_dict() for f in self._image_repository.find_by_family_id(family_id)])

	def get_images_by_product_id(self, product_id: UUID):
		return _json_response([f.to_dict() for f in self._image_repository.find_by_product_id(product_id)])


def register_routes(flask: Flask, family_repository: FamilyRepository, product_repository: ProductRepository, image_repository: ImageRepository):
	web_api = WebApi([CARIOCAWEAR_STORE], family_repository, product_repository, image_repository)

	flask.add_url_rule("/families", "families", web_api.get_families)
	flask.add_url_rule("/families/<uuid:family_id>/products", "families-products", web_api.get_products_by_family_id)
	flask.add_url_rule("/families/<uuid:family_id>/images", "families-images", web_api.get_images_by_family_id)
	flask.add_url_rule("/products/<uuid:product_id>/images", "products-images", web_api.get_images_by_product_id)
