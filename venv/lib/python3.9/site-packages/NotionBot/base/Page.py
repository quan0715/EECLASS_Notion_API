from typing import Union
from ..object import *
from .Base import Base
import asyncio
import requests


class Page(Base):

    def __init__(self, bot, page_id):
        super().__init__(bot, page_id, 'page')
        self.page_property_api = self.object_api + "/properties/"
        self.update_children_api = f"https://api.notion.com/v1/blocks/{self.object_id}/children"

    def retrieve_property_item(self, property_id):
        r = requests.get(url=self.page_property_api + property_id, headers=self.bot.headers)
        if r.status_code == 200:
            return r.json()
        return r.json()['message']

    def update(self, **kwargs):
        page_object = BaseObject(**kwargs)
        r = requests.patch(self.object_api, headers=self.bot.headers, json=page_object.make())
        if r.status_code == 200:
            return r.json()
        return r.json()['message']

    def delete(self):
        return self.update(archived=True)

    def restore(self):
        return self.update(archived=False)

    def create_new_page(self,properties: Properties = Properties(), **kwargs):
        page_object = BaseObject(
            parent=Parent(self),
            properties=properties,
            **kwargs,
        )
        r = requests.post(Page.PageAPI, headers=self.bot.headers, json=page_object.make())
        if r.status_code == 200:
            return Page(self.bot, r.json()['id'])
        else:
            print(r.json()['message'])
            return r.json()['message']

