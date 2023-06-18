from .NotionObject import *


class Properties(NotionObject):
    def __init__(self, **kwargs):
        super().__init__()

        for k, v in kwargs.items():
            if isinstance(v, NotionObject):
                self.template.update({k: v.make()})
            else:
                self.template.update({k: v})


class CreatedByProperty(PropertyBase):
    def __init__(self):
        super().__init__("created_by")


class CreatedTimeProperty(PropertyBase):
    def __init__(self):
        super().__init__("created_time")


class LastEditedTimeProperty(PropertyBase):
    def __init__(self):
        super().__init__("last_edited_time")


class LastEditedByProperty(PropertyBase):
    def __init__(self):
        super().__init__("last_edited_by")

