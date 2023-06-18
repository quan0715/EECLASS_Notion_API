from enum import Enum
from .NotionObject import *


class Number:
    class Type(str, Enum):
        number = "number"

    class Filter(str, Enum):
        # "number"
        # Only return pages where the page property value matches the provided value exactly.
        equals = "equals"
        # Only return pages where the page property value does not match the provided value exactly.
        does_not_equal = "does_not_equal"
        # Only return pages where the page property value is greater than the provided value.
        greater_than = "greater_than"
        # Only return pages where the page property value is less than the provided value.
        less_than = "less_than"
        # Only return pages where the page property value is greater than or equal to the provided value.
        greater_than_or_equal_to = "greater_than_or_equal_to"
        # Only return pages where the page property value is less than or equal to the provided value.
        less_than_or_equal_to = "less_than_or_equal_to"
        # Only return pages where the page property value is empty.
        is_empty = "is_empty"
        # Only return pages where the page property value is present.
        is_not_empty = "is_not_empty"

    class Format(str, Enum):
        number = "number"
        number_with_commas = "number_with_commas"
        percent = "percent"
        dollar = "dollar"
        canadian_dollar = "canadian_dollar"
        euro = "euro"
        pound = "pound"
        yen = "yen"
        ruble = "ruble"
        rupee = "rupee"
        won = "won"
        yuan = "yuan"
        real = "real"
        lira = "lira"
        rupiah = "rupiah"
        franc = "franc"
        hong_kong_dollar = "hong_kong_dollar"
        new_zealand_dollar = "new_zealand_dollar"
        krona = "krona"
        norwegian_krone = "norwegian_krone"
        mexican_peso = "mexican_peso"
        rand = "rand"
        new_taiwan_dollar = "new_taiwan_dollar"
        danish_krone = "danish_krone"
        zloty = "zloty"
        baht = "baht"
        forint = "forint"
        koruna = "koruna"
        shekel = "shekel"
        chilean_peso = "chilean_peso"
        philippine_peso = "philippine_peso"
        dirham = "dirham"
        colombian_peso = "colombian_peso"
        riyal = "riyal"
        ringgit = "ringgit"
        leu = "leu"
        argentine_peso = "argentine_peso"
        uruguayan_peso = "uruguayan_peso"

    def __init__(self, number):
        self.number = number
        #self.template = dict(number=self.number)

    def make(self):
        return self.number


class NumberProperty(PropertyBase):
    def __init__(self, _format=Number.Format.number):
        PropertyBase.__init__(self, Number.Type.number)
        self.format = _format
        self.template[self.type] = {"format": _format}


class NumberValue(NumberProperty):
    def __init__(self, value):
        super().__init__()
        self.value = value
        if isinstance(self.value, int) or isinstance(self.value, float):
            self.value = Number(self.value)

        self.template = {self.type: self.value.make()}