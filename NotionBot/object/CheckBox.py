from enum import Enum
from .NotionObject import *


class CheckBox:
    class Type(str, Enum):
        checkbox = "checkbox"

    class Filter(str, Enum):
        checkbox = "checkbox"

    class CheckboxFilter(str, Enum):
        # checkbox
        equals = "equals"
        does_not_equal = "does_not_equal"

    def __init__(self, status: bool = True):
        self.status = status

    def make(self):
        return self.status


class CheckboxProperty(PropertyBase):
    def __init__(self):
        super().__init__(CheckBox.Type.checkbox)


class CheckboxValue(CheckboxProperty):
    def __init__(self, key, value):
        super().__init__()
        self.value = value
        if isinstance(self.value, bool):
            self.value = CheckBox(self.value)

        self.template = {key: {self.type: self.value.make()}}