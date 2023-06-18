from enum import Enum
from typing import List
from .NotionObject import *
from typing import Union

class PropertyFilter(NotionObject):
    def __init__(self, prop: str, filter_type: str, condition: str, target):
        super().__init__()
        self.property = prop
        self.filter_type = filter_type
        self.condition = condition
        self.target = target
        self.template = {"property": self.property, self.filter_type: {self.condition: self.target}}


class ConditionFilters(NotionObject):
    class Operator(str, Enum):
        And = "and"
        Or = "or"

    def __init__(self, operator: Operator, filter_list: List[Union[PropertyFilter, 'ConditionFilters']]):
        super().__init__()
        self.operator = operator
        self.filter_list = filter_list
        self.template = {self.operator: [f.template for f in self.filter_list]}


class SearchSort(NotionObject):
    class Direction(str, Enum):
        ascending = "ascending"
        descending = "descending"

    class Timestamp(str, Enum):
        created_time = "created_time"
        last_edited_time = "last_edited_time"

    def __init__(self,
                 direction: Direction = Direction.ascending,
                 timestamp: Timestamp = Timestamp.created_time):
        super().__init__()
        self.direction = direction
        self.timestamp = timestamp
        self.template = dict(sort=dict(direction=self.direction,timestamp=self.timestamp))


class SortObject(NotionObject):
    class Direction(str, Enum):
        asc = "ascending"
        dec = "descending"

    class Timestamp(str, Enum):
        created_time = "created_time"
        last_edited_time = "last_edited_time"

    def __init__(self, prop: str, direction="ascending"):
        super().__init__()
        self.property = prop
        self.direction = direction
        self.template = {
            "property": self.property,
            "direction": self.direction,
        }


class Query(NotionObject):
    def __init__(self,
                 filters: Union[PropertyFilter, ConditionFilters] = None,
                 sorts: List[SortObject] = None,
                 start_cursor: str = None,
                 page_size: int = 100):
        super().__init__()
        self.filters = filters
        self.sorts = sorts
        self.start_cursor = start_cursor
        self.page_size = page_size
        self.template = self.make()

    def make(self) -> dict:
        template = {}
        if self.filters:
            template["filter"] = self.filters.template
        if self.sorts:
            template["sorts"] = [s.make() for s in self.sorts]
        if self.start_cursor:
            template["start_cursor"] = self.start_cursor
        if self.page_size:
            template["page_size"] = self.page_size
        return template
