from typing import List

from flask_accepts import responds
from flask_restx import Namespace, Resource

from .model import Edge
from .schema import EdgeSchema
from .service import EdgeService
from .. import SessionLocal

api = Namespace("Edge", description="Single namespace, single entity")  # noqa


@api.route("/<string:graph_id>/<string:vertex>")
@api.param("graph_id", "Graph Id")
@api.param("vertex", "The vertex to query")
class GetEdges(Resource):

    @responds(schema=EdgeSchema(many=True))
    def get(self, graph_id: int, vertex: str) -> List[Edge]:
        with SessionLocal() as db:
            edges = EdgeService.get_edges(vertex, graph_id, db)
            return edges

