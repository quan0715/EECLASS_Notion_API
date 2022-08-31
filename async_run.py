import requests
import asyncio
import aiohttp
from AsyncBot import *
from PyNotion import *
from PyNotion.NotionClient import Notion
from PyNotion.object import *
from PyNotion.block import *
import os
from dotenv import load_dotenv

load_dotenv()
NOTION_AUTH = os.getenv("NOTION_AUTH")
ACCOUNT = os.getenv("ACCOUNT")
PASSWORD = os.getenv("PASSWORD")
DATABASE_NAME = os.getenv("DATABASE_NAME")
notion_bot = Notion(NOTION_AUTH)
db = notion_bot.fetch_databases(DATABASE_NAME)


def new_page(target):
    return db.new_page(
        TitleValue(key="標題", value=target['標題']),
        SelectValue("課程", target['課程']),
        SelectValue("類型", target['類型']),
        TextValue("ID", target['ID']),
        DataValue("日期", Data(**target['日期'])),
        children=Children(
            CalloutBlock(f"發佈人 {target['發佈人']}  人氣 {target['人氣']}"),
            QuoteBlock(f"內容"),
            ParagraphBlock(target['內容']["公告內容"]),
            ParagraphBlock(" "),
            QuoteBlock(f"連結"),
            *[ParagraphBlock(TextBlock(content=l['名稱'], link=l['連結'])) for l in target['內容']['連結']],
            ParagraphBlock(" "),
            QuoteBlock(f"附件"),
            *[ParagraphBlock(TextBlock(content=l['名稱'], link=l['連結'])) for l in target['內容']['附件']],
        )
    )


async def run():
    async with aiohttp.ClientSession() as session:
        eeclass_bot = Bot(session, ACCOUNT, PASSWORD)
        await eeclass_bot.login()
        courses = await eeclass_bot.retrieve_all_course(refresh=True)
        tasks = [r.get_bulletin_page() for r in courses]
        await asyncio.gather(*tasks)
        tasks = [r.get_all_bulletin() for r in courses]
        await asyncio.gather(*tasks)
        builtins_list = []
        for course in courses:
            for bulletin in course.bulletins:
                builtins_list.append(await bulletin.retrieve())
                # await db.async_post(new_page(target=target), session=session)
    print(builtins_list[0])
    # db.post(new_page(target=builtins_list[0]))
    async with aiohttp.ClientSession() as session:
        tasks = [db.async_post(new_page(target=t), session=session) for t in builtins_list]
        await asyncio.gather(*tasks)


# async def test1():
#     for i in range(3):
#         print(f"test 1 {i}")
#         await asyncio.sleep(1)
#
# async def test2():
#     for i in range(3):
#         print(f"test 2 {i}")
#         await asyncio.sleep(1)
#
#
# async def main():
#     await test1()
#     await test2()

if __name__ == '__main__':
    asyncio.run(run())
