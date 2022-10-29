import requests
import aiohttp
import asyncio
import PyNotion
from PyNotion.NotionClient import Notion
from PyNotion.object import *
from PyNotion.block import *

AUTH = "secret_6Dxn84zjANca6LHA6jXuY1gOlcqXzQttl3kGZKNPemh"
PAGE_TITLE = "PyNotion test"
notion = Notion(auth=AUTH)
page = notion.fetch_page(title=PAGE_TITLE)

child = Children(
    QuoteBlock(),
    ParagraphBlock(TextBlock("Test Annotations")),
    ParagraphBlock("Test Annotations", "Test Annotations1", "Test Annotationes2"),
    CalloutBlock(),
)
# p = dict(
#     title=TitleProperty.post(Text("HIHI")),
#     #text=TitleProperty.post(Text("HIHI")),
#     # number=123,
#     # select=SelectProperty(),
#     # multiselect=MultiSelectProperty(),
#     # checkbox=CheckboxProperty(),
#     # data=DateProperty(),
#     # url=UrlProperty(),
# )
db = notion.fetch_databases("Test1")
annotation = Annotations(bold=True, color=Colors.Text.green)
new_post = db.new_page(
    TitleValue(key="title", value=Text("你好")),
    # TitleValue(key="title", value=你好"),
    TextValue(key="text", value=Text("HIHI", annotations=annotation)),
    # TextValue(key="title", value=HIHI"),
    NumberValue(key="number", value=Number(99.9)),
    # NumberValue(key="number", value=99.8),
    SelectValue(key="select", value=Option("select")),
    # SelectValue(key="select", value="select"),
    MultiSelectValue(key="multiselect", value=[Option("1"), Option("2"), Option("3"), Option("4")]),
    # MultiSelectValue(key="multiselect", value=["1,2,3,4"]),
    CheckboxValue(key="checkbox", value=False),
    # CheckboxValue(key="checkbox", value=True)
    DateValue(key="data", value=Date(start=datetime(2022, 8, 16, 21, 30), end=datetime(2022, 8, 17, 21, 30))),
    # DateValue(key="data", value=Date(start="2022-08-16T21:00", end="2022-08-17T21:00")),
    UrlValue(key="url", value=Url("https://developers.notion.com/reference/database")),
    # UrlValue(key="url", value="https://developers.notion.com/reference/database"),
)
# db.post(new_post)


async def main():
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(100):
            # tasks.append(page.async_append_children(child, session))
            tasks.append(db.async_post(new_post, session))

        results = await asyncio.gather(*tasks)
        for r in results:
            print(r)


if __name__ == '__main__':
    asyncio.run(main())