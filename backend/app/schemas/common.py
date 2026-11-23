from pydantic import BaseModel, ConfigDict


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PageMeta(BaseModel):
    total: int
    limit: int
    offset: int


class PaginatedResponse[T](BaseModel):
    items: list[T]
    pagination: PageMeta


def validate_pagination(limit: int = 20, offset: int = 0) -> tuple[int, int]:
    return min(max(limit, 1), 100), max(offset, 0)
