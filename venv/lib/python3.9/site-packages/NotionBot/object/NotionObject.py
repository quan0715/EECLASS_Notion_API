from enum import Enum
from typing import Union


class NotionObject:
    def __init__(self):
        self.template = {}

    def make(self):
        return self.template


class PropertyObject(NotionObject):
    def __init__(self, properties_dict: dict) -> None:
        super().__init__()
        for name, value_type_object in properties_dict.items():
            self.template[name] = value_type_object.make()


class PropertyName(NotionObject):
    def __init__(self, name: str) -> None:
        super().__init__()
        self.template = dict(name=name)


class PropertyBase(NotionObject):
    def __init__(self, prop_type: str):
        NotionObject.__init__(self)
        self.type = prop_type
        self.template.update({self.type: dict()})

    def post(self, data):
        return {self.type: data.make()}


class BaseObject(NotionObject):
    def __init__(self, **kwargs):
        super().__init__()
        for key, value in kwargs.items():
            if isinstance(value, NotionObject):
                self.template[key] = value.make()
            else:
                self.template[key] = value


class Parent(NotionObject):
    class Type(str, Enum):
        database = "database_id"
        page = "page_id"
        workspace = "workspace"

    def __init__(self, parent_object: Union['Database', 'Page']):
        super().__init__()
        self.parent_type = parent_object.parent_type
        self.parent_id = parent_object.object_id
        self.template = {self.parent_type: self.parent_id}

    def __repr__(self):
        return f"Parent type : {self.parent_type}\n object_id : {self.parent_id}"


class Children(NotionObject):
    def __init__(self, *children):
        super().__init__()
        self.template = [c.make() for c in children]

