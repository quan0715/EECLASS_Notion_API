from typing import Dict

import aiohttp
# from AsyncBot import *
from NotionBot import *
from NotionBot.base.Database import *
from NotionBot.object import *
from NotionBot.object.BlockObject import *

import os
from dotenv import load_dotenv

from eeclass_bot.EEAsyncBot import EEAsyncBot


def builtin_in_notion_template(db: Database, target):
    return BaseObject(
        parent=Parent(db),
        properties=Properties(
            Title=TitleValue(target['title']),
            Course=SelectValue(target['course']),
            ID=TextValue(target['ID']),
            Announce_Date=DateValue(NotionDate(**target['date'])),
            link=UrlValue(target['url']),
            label=SelectValue("公告")
        ),
        children=Children(
            CallOutBlock(f"發佈人 {target['發佈人']}  人氣 {target['人氣']}", color=Colors.Background.green),
            QuoteBlock(f"內容"),
            ParagraphBlock(target['content']["公告內容"]),
            ParagraphBlock(" "),
            QuoteBlock(f"連結"),
            *[ParagraphBlock(TextBlock(content=links['名稱'], link=links['連結'])) for links in
              target['content']['連結']],
            ParagraphBlock(" "),
            QuoteBlock(f"附件"),
            *[ParagraphBlock(TextBlock(content=links['名稱'], link=links['連結'])) for links in
              target['content']['附件']],
        ),
        icon=Emoji("🐶"),
    )


def homework_in_notion_template(db: Database, target):
    cover_file_url = "https://images.pexels.com/photos/13010695/pexels-photo-13010695.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1"
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

    return BaseObject(
        parent=Parent(db),
        properties=Properties(
            Title=TitleValue(target['title']),
            Course=SelectValue(target['course']),
            ID=TextValue(target['ID']),
            Deadline=DateValue(NotionDate(**target['date'])),
            link=UrlValue(target['url']),
            label=SelectValue("作業")
        ),
        children=Children(*children_list),
        icon=Emoji("🐶"),
        cover=FileValue(cover_file_url)
    )

def material_in_notion_template(db: Database, target):
    complete_emoji = "✅" if target['已完成'] else "❎"
    return BaseObject(
        parent = Parent(db),
        properties = Properties(
            Title = TitleValue(target['title']),
            Course = SelectValue(target['course']),
            ID = TextValue(target['ID']),
            # Deadline = DateValue(NotionDate(**target['deadline'])),
            link = UrlValue(target['url']),
            label = SelectValue("教材")
        ),
        children = Children(
            # CallOutBlock(f"發佈人 {target['發佈者']}  觀看數 {target['觀看數']}  教材類型 {target['subtype']}", color=Colors.Background.green),
            CallOutBlock(f"教材類型 {target['subtype']}", color=Colors.Background.green),
            CallOutBlock(f"完成條件: {target['完成條件']}  進度: {target['完成度']}  已完成: " + complete_emoji, color=Colors.Background.red),

        )
    )

async def fetch_all_eeclass_data(account, password):
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        bot = EEAsyncBot(session, account, password)
        await bot.login()
        await bot.retrieve_all_course(check=True, refresh=True)
        await bot.retrieve_all_bulletins()
        all_bulletins_detail = await bot.retrieve_all_bulletins_details()
        await bot.retrieve_all_homeworks()
        all_homework_detail = await bot.retrieve_all_homeworks_details()
        await bot.retrieve_all_material()
        all_material_detail = await bot.retrieve_all_materials_details()
        return all_bulletins_detail, all_homework_detail, all_material_detail


# def get_config():
#     load_dotenv()
#     auth = os.getenv("NOTION_AUTH")
#     notion_bot = Notion(auth)
#     db: Database = notion_bot.search("CONFIG")
#     db_table = db.query_database_dataframe()
#     table = {
#          k: v for k, v in zip(db_table['KEY'], db_table['VALUE'])
#     }
#     return {
#         "DATABASE_NAME": table['DATABASE_NAME'],
#         "ACCOUNT": table['STUDENT_ID'],
#         "PASSWORD": table['PASSWORD'],
#     }

def get_id_col(db_col: List[Dict]) -> List[str]:
    return [p['properties']['ID']['rich_text'][0]['plain_text'] for p in db_col]


async def update_all_homework_info_to_notion_db(homeworks: List[Dict], db: Database):
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        object_index = get_id_col(db.query())
        tasks = []
        for r in homeworks:
            if r['ID'] not in object_index:
                print(f"upload homework : {r['title']} to homework database")
                tasks.append(db.async_post(homework_in_notion_template(db, r), session))
        await asyncio.gather(*tasks)


async def update_all_bulletin_info_to_notion_db(bulletins: List[Dict], db: Database):
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        object_index = get_id_col(db.query())
        tasks = []
        for r in bulletins:
            if r['ID'] not in object_index:
                print(f"upload bulletin : {r['title']} to bulletin database")
                tasks.append(db.async_post(builtin_in_notion_template(db, r), session))
        await asyncio.gather(*tasks)

async def update_all_material_info_to_notion_db(materials: List[Dict], db: Database):
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        object_index = get_id_col(db.query())
        tasks = []
        for r in materials:
            if r != None and r['ID'] not in object_index:
                print(f"upload material : {r['title']} to material database")
                tasks.append(db.async_post(material_in_notion_template(db, r), session))
        await asyncio.gather(*tasks)

async def run():
    load_dotenv()
    # auth = os.getenv("NOTION_AUTH")
    account = os.getenv("ACCOUNT")
    password = os.getenv("PASSWORD")
    #notion_bot = Notion(auth)
    #homework_db: Database = notion_bot.get_database("1a23c1f9c75d427f925b83a9f220f9af")
    # bulletin_db: Database = notion_bot.get_database("1a23c1f9c75d427f925b83a9f220f9af")
    # material_db: Database = notion_bot.get_database("1a23c1f9c75d427f925b83a9f220f9af")

    bulletins, homeworks, materials = await fetch_all_eeclass_data(account, password)
    print(len(materials))

    # await update_all_bulletin_info_to_notion_db(bulletins, bulletin_db)
    # await update_all_homework_info_to_notion_db(homeworks, homework_db)
    # await update_all_material_info_to_notion_db(materials, material_db)


if __name__ == '__main__':
    asyncio.run(run())
