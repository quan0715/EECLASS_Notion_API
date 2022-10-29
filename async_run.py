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


def builtin_in_notion_template(db, target):
    return db.new_page(
        prop_value=PropertyValue(
            TitleValue(key="標題", value=target['title']),
            SelectValue("課程", target['course']),
            SelectValue("類型", target['type']),
            TextValue("ID", target['ID']),
            DateValue("日期", Date(**target['date'])),
            UrlValue("連結", Url(url=target['url'])),
        ),
        children=Children(
            CalloutBlock(f"發佈人 {target['發佈人']}  人氣 {target['人氣']}", color=Colors.Background.green),
            QuoteBlock(f"內容"),
            ParagraphBlock(target['content']["公告內容"]),
            ParagraphBlock(" "),
            QuoteBlock(f"連結"),
            *[ParagraphBlock(TextBlock(content=l['名稱'], link=l['連結'])) for l in target['content']['連結']],
            ParagraphBlock(" "),
            QuoteBlock(f"附件"),
            *[ParagraphBlock(TextBlock(content=l['名稱'], link=l['連結'])) for l in target['content']['附件']],
        ),
        icon=Emoji("🐶"),
    )


def homework_in_notion_template(db, target):
    children_list = []
    for key, value in target['content'].items():
        children_list.append(QuoteBlock(TextBlock(key.capitalize()), color=Colors.Text.red))
        if key == 'attach' or key == 'link':
            children_list.extend([
                BulletedBlock(TextBlock(content=a['title'], link=a['link'])) for a in value
            ])
        else:
            result = TextBlock.check_length_and_split(value)
            text = [TextBlock(r) for r in result] if result else [TextBlock(value)]
            children_list.append(ParagraphBlock(*text)),

        children_list.append(DividerBlock()),

    return db.new_page(
        prop_value=PropertyValue(
            TitleValue(key="標題", value=target['title']),
            SelectValue("課程", target['course']),
            SelectValue("類型", target['type']),
            TextValue("ID", target['ID']),
            DateValue("日期", Date(**target['date'])),
            UrlValue("連結", Url(url=target['url']))
        ),
        children=Children(*children_list),
        icon=Emoji("🐶"),
        cover=File(
            "https://images.pexels.com/photos/13010695/pexels-photo-13010695.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1"),
    )


async def run():
    async with aiohttp.ClientSession() as session:
        # bot part
        bot = Bot(session, ACCOUNT, PASSWORD)
        await bot.login()
        await bot.retrieve_all_course(check=True, refresh=True)
        await bot.retrieve_all_bulletins()
        await bot.retrieve_all_bulletins_details()
        await bot.retrieve_all_homeworks()
        await bot.retrieve_all_homeworks_details()
        # await bot.pipline()
        #
        # c = Course(bot, "編譯器 Compiler", "15581")
        # print(await c.get_all_bulletin_page())
        # await c.get_all_bulletin()
        # tasks = [r.retrieve() for r in c.bulletins]
        # result = await asyncio.gather(*tasks)
        # print(result)
        # for r in result:
        #     resp = await r.retrieve()
    #     courses = await eeclass_bot.retrieve_all_course(refresh=True, check=True)
    #     tasks = [r.get_bulletin_page() for r in courses]
    #     await asyncio.gather(*tasks)
    #     tasks = [r.get_all_bulletin() for r in courses]
    #     await asyncio.gather(*tasks)
    #     builtins_list = []
    #     for course in courses:
    #         for bulletin in course.bulletins:
    #             builtins_list.append(await bulletin.retrieve())
    #             # await db.async_post(new_page(target=target), session=session)
    # print(builtins_list)
    # db.post(new_page(target=builtins_list[0]))
    async with aiohttp.ClientSession() as session:
        # notion part
        df = db.query_database_dataframe()
        index = df['ID']
        # print(index)
        # await db.async_clear(session)
        tasks = []
        for r in bot.homeworks_detail_list:
            if r['ID'] not in index:
                tasks.append(db.async_post(homework_in_notion_template(db, r), session))
        await asyncio.gather(*tasks)
        tasks = []
        for r in bot.bulletins_detail_list:
            if r['ID'] not in index:
                tasks.append(db.async_post(builtin_in_notion_template(db, r), session))
        await asyncio.gather(*tasks)
        # tasks = [db.async_post(builtin_in_notion_template(db, r), session) for r in bot.bulletins_detail_list]
        # await asyncio.gather(*tasks)
        # tasks = [db.async_post(homework_in_notion_template(db, r), session) for r in bot.homeworks_detail_list]
        # tasks.extend([db.async_post(builtin_in_notion_template(db, r), session) for r in bot.bulletins_detail_list])


if __name__ == '__main__':
    asyncio.run(run())
