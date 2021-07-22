from flask import request
from flask_accepts import responds, accepts
from flask_restx import Namespace, Resource

from .model import Vertex
from .schema import VertexSchemaPos
from .service import VertexService
from .. import SessionLocal

api = Namespace("Vertex", description="Single namespace, single entity")  # noqa


@api.route("/closest/<string:graph_id>/<float(signed=True):x>/<float(signed=True):y>")
@api.param("graph_id", "Graph Id")
@api.param("y", "Y coordinate")
@api.param("x", "X coordinate")
class GetClosestVertexWithMetadata(Resource):

    @responds(schema=VertexSchemaPos)
    def get(self, graph_id: int, x: float, y: float) -> Vertex:
        with SessionLocal() as db:
            closest_vertex = VertexService.get_closest(graph_id, x, y, db)
            metadata = VertexService.attach_metadata(closest_vertex, db)
            return metadata[0]


@api.route("/type/<string:type>")
@api.param("type", "type")
class GetVerticesByType(Resource):
    @api.doc(params={'graphId': {'description': 'If you provide a graph id your query will be scoped to that graph only',
                                 'type': 'int'}})
    @responds(schema=VertexSchemaPos(many=True))
    def get(self, type: str) -> Vertex:
        with SessionLocal() as db:
            graph_id = request.args.get('graphId')
            vertices = VertexService.get_by_type(graph_id, type, db)
            vertices = VertexService.attach_metadata(vertices, db)
            return vertices


@api.route("/label/<string:label>")
@api.param("label", "label")
class GetVerticesByLabel(Resource):
    @api.doc(params={'graphId': {'description':  'If you provide a graph id your query will be scoped to that graph only',
                                 'type': 'int'}})
    @responds(schema=VertexSchemaPos(many=True))
    def get(self, label: str) -> Vertex:
        with SessionLocal() as db:
            graph_id = request.args.get('graphId')
            vertices = VertexService.get_by_label(graph_id, label, db)
            vertices = VertexService.attach_metadata(vertices, db)
            # if graph_id is not None:
            #     vertices = VertexService.attach_position(vertices, graph_id, db)
            return vertices