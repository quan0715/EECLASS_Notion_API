from AsyncBot import *
from PyNotion.NotionClient import Notion
from PyNotion.block import *
import os
from dotenv import load_dotenv


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


def get_config():
    load_dotenv()
    auth = os.getenv("NOTION_AUTH")
    notion_bot = Notion(auth)
    db = notion_bot.fetch_databases("CONFIG")
    db_table = db.query_database_dataframe()
    table = {
         k: v for k, v in zip(db_table['KEY'], db_table['VALUE'])
    }
    return {
        "DATABASE_NAME": table['DATABASE_NAME'],
        "ACCOUNT": table['STUDENT_ID'],
        "PASSWORD": table['PASSWORD'],
    }

async def update_to_notion_db(target, db):
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        # notion part
        # await db.async_clear(session)
        df = db.query_database_dataframe()
        index = df['ID']
        homeworks = target['homeworks']
        bulletins = target['bulletins']
        tasks = []
        for r in homeworks:
            if r['ID'] not in index:
                tasks.append(db.async_post(homework_in_notion_template(db, r), session))
        await asyncio.gather(*tasks)
        tasks = []
        for r in bulletins:
            if r['ID'] not in index:
                tasks.append(db.async_post(builtin_in_notion_template(db, r), session))
        await asyncio.gather(*tasks)


async def run():
    load_dotenv()
    auth = os.getenv("NOTION_AUTH")
    config_file = get_config()
    account = config_file['ACCOUNT']
    password = config_file['PASSWORD']
    db_name = config_file['DATABASE_NAME']
    notion_bot = Notion(auth)
    db = notion_bot.fetch_databases(db_name)
    r = await fetch_all_eeclass_data(account, password)
    target = {'bulletins': r[0], 'homeworks': r[1]}
    await update_to_notion_db(target, db)

if __name__ == '__main__':
    asyncio.run(run())

