from typing import List

from flask import request
from flask_accepts import responds, accepts
from flask_restx import Namespace, Resource

from . import VertexMetadataSchema
from .model import VertexMetadata
from .service import VertexMetadataService
from .. import SessionLocal

api = Namespace("VertexMetadata", description="Global metadata related to eth addresses")

@api.route("/vertex/<string:eth>")
@api.param("eth", "Ethereum address")
class MetadataEthResource(Resource):

    @responds(schema=VertexMetadataSchema(many=True))
    def get(self, eth: str) -> List[VertexMetadata]:
        with SessionLocal() as db:
            by_eth = VertexMetadataService.get_by_eth(eth, db)
            return by_eth

@api.route("/create")
class MetadataResource(Resource):

    @accepts(schema=VertexMetadataSchema, api=api)
    @responds(schema=VertexMetadataSchema)
    def post(self) -> VertexMetadata:
        with SessionLocal() as db:
            by_eth = VertexMetadataService.create(request.parsed_obj, db)
            return by_eth