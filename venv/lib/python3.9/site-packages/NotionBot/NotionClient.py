import requests
# from bs4 import BeautifulSoup
import os
from .base import *
from .object import *


class Notion:
    """
    Client side of notion server, provide simple get method to retrieve block, page and database by their object index\n
    you can also create new page or new database from client side
    """
    user_api = "https://api.notion.com/v1/users/me"
    api = f'https://api.notion.com/v1'
    notion_version = "2022-06-28"
    search_database_api = 'https://api.notion.com/v1/databases'

    def __init__(self, auth: str):
        """
        :param auth: your notion integration internal token
        """
        self.auth = auth
        self.headers = {
            "Authorization": f"Bearer {self.auth}",
            "Notion-Version": Notion.notion_version,
            "Accept": "application/json",
        }
        # self.bot = self.bot_user()

    def get_user(self):
        api = "https://api.notion.com/v1/users/me"
        r = requests.get(api, headers=self.headers)
        if r.status_code == 200:
            print(f"Connect to integration {r.json()['name']}")
            return r.json()
        else:
            print(r.json()['message'])
            return r.json()['message']

    def search(self, target: str = None):
        """
        :param target:  the name of target database or page
        :return: if success it will return json file which represent the list of search result,\n otherwise it will print error message and return it
        """
        payload = {
            'query': f'{target}',
            'page_size': 100
        }
        search_api = 'https://api.notion.com/v1/search'
        r = requests.post(search_api, headers=self.headers, json=payload)
        if r.status_code == 200:
            return r.json()
        else:
            print(r.json()['message'])
            return r.json()['message']

    def get_block(self, block_id) -> Block:
        api = f"https://api.notion.com/v1/blocks/{block_id}"
        r = requests.get(api, headers=self.headers)
        if r.status_code == 200:
            return Block(self, block_id)
        else:
            print(r.json()['message'])
            return r.json()['message']

    def get_page(self, page_id) -> Page:
        api = f"https://api.notion.com/v1/pages/{page_id}"
        r = requests.get(api, headers=self.headers)
        if r.status_code == 200:
            # print(f"Connect to integration {r.json()['name']}")
            return Page(self, page_id)
        else:
            print(r.json()['message'])
            return r.json()['message']

    def get_database(self, database_id):
        database_api = f'https://api.notion.com/v1/databases/{database_id}'
        r = requests.get(database_api, headers=self.headers)
        if r.status_code == 200:
            return Database(self, r.json()['id'])
        else:
            print(r.json()['message'])
            return r.json()['message']

    def create_new_page(self,
                        parent: Union[Page, Database, Parent],
                        properties: Union[Properties, dict] = Properties(),
                        **kwargs):
        """
        properties*	object Schema of properties. using Properties object to implement
        parent	object	Information about the database's parent.
        icon: File Object (only type of "external" is supported currently) or Emoji object. using File object or Emoji object
        cover: File object (only type of "external" is supported currently). using File object
        archived: boolean. The archived status of the database.
        """
        page_object = BaseObject(
            parent=Parent(parent) if not isinstance(parent, Parent) else parent,
            properties=properties,
            **kwargs
        )
        r = requests.post(Database.PageAPI, headers=self.headers, json=page_object.make())
        if r.status_code == 200:
            return Page(self, r.json()['id'])
        else:
            print(r.json()['message'])
            return r.json()['message']

    def create_new_database(self,
                            parent: Union[Page, Parent],
                            properties: Union[Properties, dict] = Properties(),
                            **kwargs):
        """
            parent	object	Information about the database's parent.
            properties*	object Schema of properties. using Properties object to implement
            title: array of rich text objects. using Texts object to implement
            description: array of rich text . using Texts object to implement
            icon: File Object or Emoji object. using File object or Emoji object
            cover: File object (only type of "external" is supported currently). using File object
            archived: boolean. The archived status of the database.
            is_inline: boolean. Has the value true if the database appears in the page as an inline block.
        """
        database_object = BaseObject(
            parent=Parent(parent) if not isinstance(parent, Parent) else parent,
            properties=properties,
            **kwargs
        )
        r = requests.post(Database.DatabaseAPI, headers=self.headers, json=database_object.make())
        if r.status_code == 200:
            return Database(self, r.json()['id'])
        else:
            return r.json()


if __name__ == '__main__':
    notion_bot = Notion(auth="secret_8JtNxNiUCCWPRhFqzl1e2juzxoz96dyjYWubDLbNchy")
    test_page = notion_bot.get_page('3be396829d3149b2818a4957ff878bf9')
    db = notion_bot.get_database('ad29cd8f20584c1d98d33bf9e70c5377')
    r = db.query()
    print(r)
    # db = notion_bot.create_new_database(
    #     parent=test_page,
    #     title="Hello",
    #     properties=Properties(
    #         name=TitleProperty(),
    #         test=TextProperty(),
    #     )
    # )
    # print(db.print_properties())
    # # p = Properties(title=TitleValue('Hello'))
    # # print(p.make())
    # test = notion_bot.create_new_page(
    #     parent=test_page,
    #     properties=Properties(
    #         title=TitleValue('Hello')
    #     ),
    #     icon=Emoji('🐒')
    # )
    # test.restore()
    # print(test_page.retrieve())
    # print(test_page.retrieve_property_item())
    # notion_bot.create_new_page(parent=test_page, properties=Properties())

    #
    # @classmethod
    # def retrieve_from(cls, target: Union[Page, Database, Block]):
    #     return target.retrieve()
    #
    # @staticmethod
    # def create_new_page(parent: Union[Page, Database], content: PageObject):
    #     if isinstance(parent, Database):
    #         return parent.post(parent.new_page(content))
    #
    #     elif isinstance(parent, Page):
    #         return parent.create_page(content)
    #
    # def fetch_databases(self, title: str):
    #     payload = {
    #         'query': f'{title}',
    #         'filter': {'value': 'database', 'property': 'object'},
    #         'page_size': 100
    #     }
    #     response = requests.request("POST", self.search_api, json=payload, headers=self.patch_headers)
    #     if response.json()['results']:
    #         text = response.json()['results'][0]
    #         database_id = text['id']
    #         print(f"fetching database {title} successfully")
    #         return Database(bot=self, database_id=database_id)
    #
    #     else:
    #         print(f"Can't find database {title}, check if it exist in your notion page")
    #
    # def fetch_page(self, title):
    #     payload = {
    #         'query': f'{title}',
    #         'filter': {'value': 'page', 'property': 'object'},
    #         'page_size': 100
    #     }
    #     response = requests.post(self.search_api, json=payload, headers=self.patch_headers)
    #     # print(response.json())
    #     if response.status_code == 200:
    #         # print(response.text)
    #         text = response.json()['results'][0]
    #         page_id = text['id']
    #         # print(page_id)
    #         print(f"fetch {title} page successfully")
    #         return Page(page_id=page_id, bot=self)
    #     else:
    #         print(f"Can't find page {title}")
    #
    #     return None
    #
    # def append_block(self, target_page: Page, children_array):
    #     target_page.append_children(children_array)
    #
    # def update_page(self, target, data):
    #     if isinstance(target.parent, Database):
    #         data = target.parent.new_page(data)
    #     target.update(data)
    #
    # def create_new_database(self, parent: Page, title=None, properties=None, icon=None, cover=None, is_inline=False):
    #     r = parent.create_database(title=title, properties=properties, icon=icon, cover=cover, is_inline=is_inline)
    #     if r.status_code == 200:
    #         print(f"create_new_database successfully id {r.json()['id']} ")
    #         return Database(self, r.json()['id'])
    #     else:
    #         print(r.json()['message'])
