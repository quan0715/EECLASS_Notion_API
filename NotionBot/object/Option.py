from .Color import *
from .NotionObject import *
from enum import Enum


class Option:
    class Type(str, Enum):
        select = "select"
        multi_select = "multi_select"

    class Filter(str, Enum):
        equals = "equals"
        does_not_equal = "does_not_equal"
        is_empty = "is_empty"
        is_not_empty = "is_not_empty"

    def __init__(self, name, color=Colors.Option.default):
        self.name = name
        self.color = color
        # can't update color in value currently
        self.template = {"name": self.name, "color": self.color}

    def make(self):
        return self.template

    def value(self):
        del self.template['color']


class SelectProperty(PropertyBase):
    def __init__(self, *option_list: Option):
        super().__init__(Option.Type.select)
        self.template[self.type] = {"options": [option.make() for option in option_list]}


class MultiSelectProperty(PropertyBase):
    def __init__(self, *option_list):
        super().__init__(Option.Type.multi_select)
        self.template[self.type] = {"options": [option.make() for option in option_list]}


class SelectValue(SelectProperty):
    def __init__(self, value: Union[Option, str]):
        super().__init__()
        self.value = value
        if isinstance(self.value, str):
            self.value = Option(self.value)

        self.value.value()
        self.template = {"select": self.value.make()}


class MultiSelectValue(MultiSelectProperty):
    def __init__(self, key, value: list):
        super().__init__()
        self.value = value
        self.option_list = []
        for p in self.value:
            if isinstance(p, str):
                o = Option(p)
                o.value()
                self.option_list.append(o.make())

            elif isinstance(p, Option):
                p.value()
                self.option_list.append(p.make())
        self.template = {key: {self.type: self.option_list}}