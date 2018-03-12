from flask import Blueprint

from candytuft.webapi import ok_response as ok
from candytuft.process.collect.starter import Starter as CollectStarter

class _CollectApi:
	def __init__(self, starter: CollectStarter):
		self._starter = starter

	def start(self):
		self._starter.start()
		return ok()

def get_web_api(starter: CollectStarter) -> Blueprint:
	blueprint = Blueprint("collect", __name__)

	collect_api = _CollectApi(starter=starter)

	blueprint.add_url_rule("/collect/start", "collect-start", collect_api.start)

	return blueprint
