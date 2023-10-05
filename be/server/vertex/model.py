from typing import List

from geoalchemy2 import Geometry
from psycopg2._psycopg import AsIs
from sqlalchemy import (
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.sql import text

from be.server import configs

from .. import (
    Base,
    engine,
)
from ..utils import (
    to_pd_frame,
    wkt_to_x_y_list,
)


class Vertex(Base):

    __tablename__ = "tg_vertex"

    graph_id = Column(
        Integer(), 
        ForeignKey('tg_graphs.id'), 
        primary_key=True,
    )
    vertex = Column(
        String(), 
        primary_key=True,
    )
    size = Column(Float(precision=8))
    pos = Column(Geometry('Point', 3857))

    @staticmethod
    def get(vertices: List[str], graph_id: int, db: object):

        query = text(
            """
            SELECT graph_id, vertex, size, ST_AsText(ST_PointFromWKB(pos)) AS pos 
            FROM :table_name 
            WHERE vertex IN :vertices
            """ 
        )

        substitution = {
            'table_name': AsIs(configs.VERTEX_TABLE_NAME(graph_id)),
            'vertices': tuple(vertices)
        }

        with engine.connect() as conn:

            raw_result = conn.execute(query, substitution)

            fetchall = to_pd_frame(raw_result)

            return Vertex._map_to_model(fetchall)

    @staticmethod
    def _map_to_model(fetchall):
        collect = []
        for (i, e) in fetchall.iterrows():
            pos_as_list = wkt_to_x_y_list(e['pos'])
            vertex = Vertex(graph_id=e['graph_id'], vertex=e['vertex'], size=e['size'], pos=pos_as_list)
            collect.append(vertex)
        return collect
