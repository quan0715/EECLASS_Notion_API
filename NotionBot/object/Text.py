from typing import Union
from .Color import Colors
from enum import Enum
from .NotionObject import *


class Annotations(NotionObject):
    class Type(str, Enum):
        bold = "bold"
        italic = "italic"
        strikethrough = "strikethrough"
        underline = "underline"
        code = "code"
        color = "color"

    def __init__(self, color=Colors.Text.default, **kwargs):
        super().__init__()
        self.template = kwargs
        self.template['color'] = color


class Text(NotionObject):
    """
    This is Notion Text object class, the element of the rich_text array
    """
    class Type(str, Enum):
        title = "title"
        rich_text = "rich_text"

    class Filter(str, Enum):
        # "title", "rich_text", "url", "email", and "phone_number"
        # Only return pages where the page property value matches the provided value exactly.
        equals = "equals"
        # Only return pages where the page property value does not match the provided value exactly.
        does_not_equal = "does_not_equal"
        # Only return pages where the page property value contains the provided value.
        contains = "contains"
        # Only return pages where the page property value does not contain the provided value.
        does_not_contain = "does_not_contain"
        # Only return pages where the page property value starts with the provided value.
        starts_with = "starts_with"
        # Only return pages where the page property value ends with the provided value.
        ends_with = "ends_with"
        # Only return pages where the page property value is empty.
        is_empty = "is_empty"
        # Only return pages where the page property value is present.
        is_not_empty = "is_not_empty"

    def __init__(self,
                 content="This is text",
                 annotations: Union[Annotations, dict] = None,
                 link: str = None):
        super().__init__()
        self.content = content
        self.link = link
        self.annotations = Annotations(**annotations) if isinstance(annotations, dict) else annotations
        self.template = dict(text={'content': self.content, "link": None})
        # if self.link:
        #     self.link_object = Link(self.link)
        #     self.template['text']['link'] = self.link_object.template
        if isinstance(self.annotations, Annotations):
            self.template.update(dict(annotations=self.annotations.make()))

    # def update_link(self, url):
    #     self.link = url
    #     self.link_object.update(self.link)
    #     self.template[0]['text']["link"] = self.link_object.make()
class Texts(NotionObject):
    def __init__(self, *contents: Union[str, Text]):
        super().__init__()
        self.template = [
            c.make() if isinstance(c, Text) else Text(c).make() for c in contents
        ]


class TextProperty(PropertyBase):
    def __init__(self):
        PropertyBase.__init__(self, prop_type="rich_text")


class TitleProperty(PropertyBase):
    def __init__(self):
        PropertyBase.__init__(self, prop_type="title")


class TitleValue(TitleProperty):
    def __init__(self, *contents):
        super(TitleProperty).__init__()
        self.template = TextValue(*contents).make()
        self.template = {"title": self.template['rich_text']}


class TextValue(TextProperty):
    def __init__(self, *values: Union[str, Text]):
        super().__init__()
        self.template = {'rich_text': []}
        self.values = values
        for v in values:
            if isinstance(v, str):
                v = Text(v)
            self.template['rich_text'].append(v.make())