import ujson
from typing import Any

from flask import Response


def json_response(content: Any):
	return Response(response=ujson.dumps(content, ensure_ascii=False), status=200, mimetype="application/json")

def ok_response():
	return Response(status=200)

