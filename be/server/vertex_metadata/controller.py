import json
from typing import List

from flask import Response, request
from flask_accepts import responds, accepts
from flask_restx import Namespace, Resource

from . import VertexMetadataSchema
from .model import VertexMetadata
from .service import VertexMetadataService
from .. import SessionLocal
from ...configuration import CONFIGURATIONS

api = Namespace("VertexMetadata", description="Global metadata related to eth addresses")

@api.route("/<int:graph_id>")
@api.param("graph_id")
class MetadataVerticesGraphResource(Resource):

    @responds(schema=VertexMetadataSchema(many=True))
    def get(self, graph_id: int) -> List[VertexMetadata]:

        def stream(t: List):
            for row in t:
                yield json.dumps(row) + "\n"

        with SessionLocal() as db:
            df_vertex_metadata = VertexMetadataService.get_all_by_graph(graph_id, db)
            json_string = df_vertex_metadata.to_json(orient="records")
            json_obj = json.loads(json_string)

            return Response(stream(json_obj))

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
        if CONFIGURATIONS['is_labelling_enabled'] != 'true':
            print("\tLabelling is disabled in config, this endpoint is not active")
            return {}
        with SessionLocal() as db:
            by_eth = VertexMetadataService.create(request.parsed_obj, db)
            return by_eth


@api.route("/<string:eth>/<string:typee>/<string:value>")
class MetadataResource(Resource):

    @responds(schema=VertexMetadataSchema)
    def delete(self, eth: str, typee: str, value: str) -> VertexMetadata:
        if CONFIGURATIONS['is_labelling_enabled'] != 'true':
            print("\tLabelling is disabled in config, this endpoint is not active")
            return {}
        with SessionLocal() as db:
            VertexMetadataService.delete(eth, typee, value, db)
            return {}
