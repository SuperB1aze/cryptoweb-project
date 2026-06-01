from fastapi import Query

from infrastructure.db.enums import SortOrder


class PaginationParams:
    def __init__(
        self,
        limit: int = Query(default=20, ge=1, le=50, description="Number of objects to return per page"),
        offset: int = Query(default=0, ge=0, description="Number of objects to skip before collecting the result"),
    ):
        self.limit = limit
        self.offset = offset

class SortingParams:
    def __init__(
        self,
        sort_by: SortOrder = Query(default=SortOrder.newest, description="Sorting order"),
    ):
        self.sort_by = sort_by