from enum import Enum
from .NotionObject import *


class FileValue(NotionObject):
    class Type(str, Enum):
        file = "file"
        external = "external"

    def __init__(self, url, file_type=Type.external):
        super().__init__()
        self.url = url
        self.file_type = file_type
        self.template = dict(type=self.file_type)
        self.template[self.file_type] = (dict(url=self.url))
