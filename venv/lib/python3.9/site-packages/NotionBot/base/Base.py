from ..object import *
import asyncio
import requests
from enum import Enum


class Base:
    """
    The Base class for Database Page and Block
    """
    class Type(Enum):
        database = "database"
        page = "page"
        block = "block"

    BlockAPI = "https://api.notion.com/v1/blocks/"
    DatabaseAPI = "https://api.notion.com/v1/databases/"
    PageAPI = 'https://api.notion.com/v1/pages/'

    def __init__(self, bot, object_id, object):
        self.bot = bot
        self.object = object
        self.object_id = object_id
        self.object_api = (Base.PageAPI if object == "page" else Base.DatabaseAPI) + self.object_id
        self.parent_type = self.object + "_id"
        self.created_time, self.last_edited_time = None, None
        self.created_by, self.last_edited_by = None, None,
        self.properties_list = []

    def __repr__(self):
        return f"------------------------------------------------------\n" \
               f"Object : {self.object}\n" \
               f"id : {self.object_id}\n" \
               f"parent_type : {self.parent_type}\n" \
               f"object_api : {self.object_id}\n" \
               "------------------------------------------------------" \


    def retrieve(self):
        result = requests.get(self.object_api, headers=self.bot.headers)
        result = result.json()
        self.created_time = result['created_time']
        self.last_edited_time = result['last_edited_time']
        self.created_by = result['created_by']
        self.last_edited_by = result['last_edited_by']
        self.properties_list = result['properties']
        return result

    def print_properties(self):
        self.retrieve()
        r = [f"\t{v['name'] : <10} --- {v['type']: ^10} --- {v['id']: >10}" for v in self.properties_list.values()]
        return "\n".join(r)

    # def update(self, url, data):
    #     # data = data if isinstance(data, str) else json.dumps(data)
    #     r = requests.patch(url, headers=self.bot.headers, json=data)
    #     if r.status_code != 200:
    #         print(r.json()['message'])
    #     return r.json()

    def delete_object(self):
        url = self.__class__.BlockAPI + self.object_id
        r = requests.delete(url, headers=self.bot.headers)
        return r.json()

    async def async_delete_object(self, session):
        url = self.__class__.BlockAPI + self.object_id
        async with session.delete(url, headers=self.bot.headers) as resp:
            return await resp.json()

    def retrieve_children(self):
        url = Base.BlockAPI + self.object_id + "/children"
        r = requests.get(url, headers=self.bot.headers)
        return r.json()

    def append_children(self, children: Children):
        url = Base.BlockAPI + self.object_id + "/children"
        r = requests.patch(url, headers=self.bot.patch_headers, json=children.make())
        if r.status_code != 200:
            return r.json()['message']
        else:
            return r.json()['results']

    async def async_append_children(self, children: Children, session):
        url = Base.BlockAPI + self.object_id + "/children"
        async with session.patch(url, headers=self.bot.patch_headers, json=children.make()) as resp:
            await asyncio.sleep(0.3)
            print()
            print(await resp.text())
            if resp.status == 200:
                return await resp.json()
            return await resp.json()['message']

    # @classmethod
    # def properties_data(cls, json_data):
    #     result = {}
    #     for key, value in json_data.items():
    #         prop_type = value['type']
    #         try:
    #             if prop_type in ['title', 'rich_text']:
    #                 result[key] = value[prop_type][0]['plain_text']
    #             elif prop_type in ['number', 'url']:
    #                 result[key] = value[prop_type]
    #             elif prop_type == 'select':
    #                 result[key] = value[prop_type]['name']
    #             elif prop_type == 'date':
    #                 text = value[prop_type]['start']
    #                 if value[prop_type]['end']:
    #                     text += f" ~ {value[prop_type]['end']}"
    #                 # if value[prop_type]['start']
    #                 result[key] = text
    #             elif prop_type == 'people':
    #                 result[key] = ""
    #                 # print(value[prop_type])
    #                 for n in value[prop_type]:
    #                     result[key] += f"{n['name']} "
    #             else:
    #                 result[key] = "None"
    #         except:
    #             result[key] = "None"
    #     return result
