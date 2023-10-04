from enum import Enum
from .NotionObject import *


class UrlProperty(PropertyBase):
    def __init__(self):
        super().__init__("url")


class UrlValue(UrlProperty):
    def __init__(self, url):
        UrlProperty.__init__(self)
        self.url = url
        self.template = {self.type: self.url}


class Link(UrlProperty):
    def __init__(self, url: str=None):
        super().__init__()
        self.url = url
        self.template = {"type": self.type, self.type: url}
