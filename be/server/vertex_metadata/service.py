from typing import List

import numpy as np
from psycopg2._psycopg import AsIs
from sqlalchemy.sql import text

from be.server import configs

from .. import engine
from ..utils import to_pd_frame
from .interface import VertexMetadataInterface
from .model import VertexMetadata
import pandas as pd


class VertexMetadataService:

    @staticmethod
    def get_all_by_graph(graph_id: int, db) -> List[VertexMetadata]:
        # TODO merge the account type and metadata table for vertices
        account_types = VertexMetadataService.merge_graph_vertices_with_account_type(graph_id, db)
        vertex_metadatas = VertexMetadataService.merge_graph_vertices_with_metadata(graph_id, db)
        return account_types.merge(vertex_metadatas, on='vertex', how='outer')[['vertex', 'type_x', 'label', 'icon']]

    @staticmethod
    def get_by_vertex(vertex: str, db) -> List[VertexMetadata]:
        query = select(VertexMetadata).filter(VertexMetadata.vertex == vertex)
        result = db.execute(query)
        return [e[0] for e in result.fetchall()]

    @staticmethod
    def get_by_label(label: str, db) -> List[VertexMetadata]:
        query = select(VertexMetadata).filter(VertexMetadata.label == label)
        result = db.execute(query)
        return [e[0] for e in result.fetchall()]
    
    @staticmethod
    def get_by_type(type: str, db) -> List[VertexMetadata]:
        query = select(VertexMetadata).filter(VertexMetadata.type == type)
        result = db.execute(query)
        return [e[0] for e in result.fetchall()]

    @staticmethod
    def create(metadata_to_insert: VertexMetadataInterface, db: object):

        new_metadata = VertexMetadata(
            vertex=metadata_to_insert['vertex'],
            type=metadata_to_insert['type'],
            label=metadata_to_insert['label'],
            account_type=metadata_to_insert.get('account_type'),
            description=metadata_to_insert['description'])

        # db.add(new_metadata)
        new_metadata.add(db)
        db.commit()
        return new_metadata

    @staticmethod
    def delete(vertex, typee, value, db):
        return VertexMetadata.delete(vertex, typee, value, db)

    @staticmethod
    def merge_graph_vertices_with_account_type(graph_id: int, db):
        table_name = configs.VERTEX_TABLE_NAME(graph_id)
        query = text(
            """
            SELECT tg_account_type.vertex, tg_account_type.type FROM :table_name
            INNER JOIN tg_account_type
            ON (tg_account_type.vertex = :table_name.vertex);
            """
        )        
        with engine.connect() as conn:
        
            execute = conn.execute(query, {'table_name': AsIs(table_name)})
            result = to_pd_frame(execute)
            result['type'] = result['type'].astype(np.int64)
            return result


    @staticmethod
    def merge_graph_vertices_with_metadata(graph_id, db):
        table_name = configs.VERTEX_TABLE_NAME(graph_id)
        query = text(
            """
            SELECT * FROM :table_name
            INNER JOIN tg_vertex_metadata
            ON (tg_vertex_metadata.vertex = :table_name.vertex);
            """
        )
        
        with engine.connect() as conn:
            execute = conn.execute(
                query, 
                {'table_name': AsIs(table_name)}
            )
            result = to_pd_frame(execute)
            if(len(list(result)) == 0): # if the result contains no columns (and no rows), manually add them
                result["vertex"] = None
                result["type"] = None
                result["label"] = None
                result["icon"] = None
            result = result.loc[:, ~result.columns.duplicated()]
            return result
