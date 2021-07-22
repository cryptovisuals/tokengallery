from mypy_extensions import TypedDict


class VertexMetadataInterface(TypedDict, total=False):
    id: int
    eth: str
    type: str
    value: str
    description: str