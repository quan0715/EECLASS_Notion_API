from typing import Dict

from AsyncBot import *
from PyNotion.NotionClient import Notion
from PyNotion.base.Database import Database
from PyNotion.object import *
from PyNotion.object.BlockObject import *
import os
from dotenv import load_dotenv


def builtin_in_notion_template(db: Database, target):
    return BaseObject(
        parent=Parent(db),
        properties=Properties(
            Title=TitleValue(target['title']),
            Course=SelectValue(target['course']),
            ID=TextValue(target['ID']),
            Announce_Date=DateValue(NotionDate(**target['date'])),
            link=UrlValue(target['url']),
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
        ),
        children=Children(*children_list),
        icon=Emoji("🐶"),
        cover=FileValue(cover_file_url)
    )


async def fetch_all_eeclass_data(account, password):
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        bot = Bot(session, account, password)
        await bot.login()
        await bot.retrieve_all_course(check=True, refresh=True)
        await bot.retrieve_all_bulletins()
        all_bulletins_detail = await bot.retrieve_all_bulletins_details()
        await bot.retrieve_all_homeworks()
        all_homework_detail = await bot.retrieve_all_homeworks_details()
        return all_bulletins_detail, all_homework_detail


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


async def update_to_notion_db(target: Dict, hw_db: Database, bu_db: Database):
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        # notion part
        # await db.async_clear(session)
        hw_index, bu_index = get_id_col(hw_db.query()), get_id_col(bu_db.query())
        homeworks, bulletins = target['homeworks'], target['bulletins']
        tasks = []
        for r in homeworks:
            if r['ID'] not in []:
                tasks.append(hw_db.async_post(
                    homework_in_notion_template(hw_db, r), session))
        await asyncio.gather(*tasks)
        tasks = []
        for r in bulletins:
            if r['ID'] not in []:
                tasks.append(bu_db.async_post(
                    builtin_in_notion_template(bu_db, r), session))
        await asyncio.gather(*tasks)


async def run():
    load_dotenv()
    auth = os.getenv("NOTION_AUTH")
    # config_file = get_config()
    # account = config_file['ACCOUNT']
    # password = config_file['PASSWORD']
    account = "109502563"
    password = "H125920690"
    # db_name = config_file['DATABASE_NAME']
    notion_bot = Notion(auth)
    # print(notion_bot.get_user())
    # https://www.notion.so/de95ed40bcc4424fbcca5789197ea73a?v=1352eeec352d4a8b882ee9b6906e18e4&pvs=4
    hw_db: Database = notion_bot.get_database("de95ed40bcc4424fbcca5789197ea73a")
    bu_db: Database = notion_bot.get_database("292fb3447b5e47d1a82dbd3c6d561ced")
    # print(bu_db, '\n', hw_db)
    r = await fetch_all_eeclass_data(account, password)
    # print(r[0])
    # print(r[1])
    # target = {'bulletins': r[0], 'homeworks': r[1]}
    target = {'bulletins': r[0], 'homeworks': r[1]}
    await update_to_notion_db(target, hw_db, bu_db)
    # print(get_id_col(bu_db.query()))


if __name__ == '__main__':
    asyncio.run(run())
