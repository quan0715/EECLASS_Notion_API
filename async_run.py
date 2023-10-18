import os
from typing import Dict

import aiohttp
from NotionBot import *
from NotionBot.base.Database import *
from NotionBot.object.BlockObject import *
from dotenv import load_dotenv

from eeclass_bot.EEAsyncBot import EEAsyncBot
from eeclass_bot.EEChromeDriver import EEChromeDriver
from eeclass_bot.models.Bulletin import Bulletin
from eeclass_bot.models.Homework import Homework
from eeclass_bot.models.Material import Material

def handle_date(target: dict):
    from datetime import datetime, timezone, timedelta
    now = datetime.strptime(datetime.now(tz=timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M")
    date_format = '%Y-%m-%d %H:%M'
    try:
        target.deadline.start = datetime.strptime(target.deadline.start, date_format)
    except:
        target.deadline.start += " 00:00"
        target.deadline.start = datetime.strptime(target.deadline.start, date_format)
    try:
        target.deadline.end = datetime.strptime(target.deadline.end, date_format)
    except:
        target.deadline.end += " 23:59"
        target.deadline.end = datetime.strptime(target.deadline.end, date_format)
    if target.submission_status == "檢視 / 修改我的作業":
        submission_status = "已完成"
    elif target.submission_status == "交作業" and target.deadline.start < now < target.deadline.end or now < target.date.start:
        submission_status = "未完成"
    else:
        submission_status = "缺交"
    target.deadline.start = target.deadline.start.strftime("%Y-%m-%d %H:%M")
    target.deadline.end = target.deadline.end.strftime("%Y-%m-%d %H:%M")
    return target.deadline.start, target.deadline.end, submission_status

def bulletin_in_notion_template(db: Database, target: Bulletin):
    return BaseObject(
        parent=Parent(db),
        properties=Properties(
            Title=TitleValue(target.title),
            Course=SelectValue(target.course),
            ID=TextValue(target.id),
            Announced_Date=DateValue(NotionDate(start=target.announced_date.start)),
            Content=TextValue(target.content.content),
            Link=UrlValue(target.url)
        ),
        children=Children(
            CallOutBlock(f"發佈人 {target.announcer}  人氣 {target.popularity}", color=Colors.Background.green),
            QuoteBlock(f"內容"),
            ParagraphBlock(target.content.content),
            ParagraphBlock(" "),
            QuoteBlock(f"連結"),
            *[ParagraphBlock(TextBlock(content=links['名稱'], link=links['連結'])) for links in
              target.content.link],
            ParagraphBlock(" "),
            QuoteBlock(f"附件"),
            *[ParagraphBlock(TextBlock(content=links['名稱'], link=links['連結'])) for links in
              target.content.attach],
        ),
        icon=Emoji("🐶"),
    )


def homework_in_notion_template(db: Database, target: Homework):
    cover_file_url = "https://images.pexels.com/photos/13010695/pexels-photo-13010695.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1"
    target.deadline.start, target.deadline.end, submission_status = handle_date(target)    
    children_list = []
    for key, value in target.content.items():
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
            Title=TitleValue(target.title),
            Status=SelectValue(submission_status),
            Course=SelectValue(target.course),
            ID=TextValue(target.id),
            Deadline=DateValue(target.deadline),
            Link=UrlValue(target.url),
            Homework_Type=SelectValue(target.homework_type),
            Content=TextValue(target.description_content),
            Submission=NumberValue(target.submission_number)
        ),
        children=Children(*children_list),
        icon=Emoji("🐶"),
        cover=FileValue(cover_file_url)
    )


def material_in_notion_template(db: Database, target: Material):
    complete_emoji = "✅" if target.complete_check else "❎"
    study_status = "已完成" if target.complete_check else "未完成"
    material_type = "影片" if target.material_type == "video" else "文字"
    return BaseObject(
        parent=Parent(db),
        properties=Properties(
            Title=TitleValue(target.title),
            Course=SelectValue(target.course),
            ID=TextValue(target.id),
            Material_Type=SelectValue(material_type),
            Content=TextValue(target.content.content),
            Study_Status=SelectValue(study_status),
            Goal=TextValue(target.complete_condition),
            Read_Time=TextValue(target.read_time),
            Announcer=TextValue(target.announcer),
            Views=NumberValue(int(target.views)),
            Link=UrlValue(target.url)
        ),
        children=Children(
            CallOutBlock(f"發佈人 {target.announcer}  觀看數 {target.views}  教材類型 {target.material_type}",
                         color=Colors.Background.green),
            CallOutBlock(f"完成條件: {target.complete_condition}  進度: {target.read_time}  已完成: " + complete_emoji,
                         color=Colors.Background.red),
            QuoteBlock(f"內容"),
            ParagraphBlock(TextBlock(content=target.video_url, link=target.video_url)),
            ImageBlock(target.video_view),
            ParagraphBlock(target.content.content),
            ParagraphBlock(" "),
            QuoteBlock(f"連結"),
            *[ParagraphBlock(TextBlock(content=links['名稱'], link=links['連結'])) for links in
              target.content.link],
            ParagraphBlock(" "),
            QuoteBlock(f"附件"),
            *[ParagraphBlock(TextBlock(content=links['名稱'], link=links['連結'])) for links in
              target.content.attachments],
        ),
    ) if target.video_view != "" else \
        BaseObject(
            parent=Parent(db),
            properties=Properties(
                Title=TitleValue(target.title),
                Course=SelectValue(target.course),
                ID=TextValue(target.id),
                Material_Type=SelectValue(material_type),
                Content=TextValue(target.content.content),
                Study_Status=SelectValue(study_status),
                Goal=TextValue(target.complete_condition),
                Read_Time=TextValue(target.read_time),
                Announcer=TextValue(target.announcer),
                Views=NumberValue(int(target.views)),
                Link=UrlValue(target.url)
            ),
            children=Children(
                CallOutBlock(f"發佈人 {target.announcer}  觀看數 {target.views}  教材類型 {target.material_type}",
                             color=Colors.Background.green),
                CallOutBlock(
                    f"完成條件: {target.complete_condition}  進度: {target.read_time}  已完成: " + complete_emoji,
                    color=Colors.Background.red),
                QuoteBlock(f"內容"),
                ParagraphBlock(target.content.content),
                ParagraphBlock(" "),
                QuoteBlock(f"連結"),
                *[ParagraphBlock(TextBlock(content=links['名稱'], link=links['連結'])) for links in
                  target.content.link],
                ParagraphBlock(" "),
                QuoteBlock(f"附件"),
                *[ParagraphBlock(TextBlock(content=links['名稱'], link=links['連結'])) for links in
                  target.content.attachments],
            ),
        )


async def fetch_all_eeclass_data(account, password):
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False),
                                     cookie_jar=aiohttp.CookieJar(unsafe=True, quote_cookie=True)) as session:
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

def get_all_ids(db_pages: list[Dict]) -> list[str]:
    ids = []
    for page in db_pages:
        try:
            ids.append(page['properties']['ID']['rich_text'][0]['plain_text'])
        except IndexError:
            pass
    return ids


async def update_all_homework_info_to_notion_db(homeworks: list[Homework], db: Database):
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        object_index = get_all_ids(db.query())
        newly_upload, newly_update = [], []
        tasks = []
        for r in homeworks:
            if object_index is not None:
                if r.id not in object_index:
                    newly_upload.append(f"upload homework : {r.title} to homework database")
                    tasks.append(db.async_post(homework_in_notion_template(db, r), session))
                else:
                    newly_update.append(f"update homework : {r.title} to homework database")
                    page = db.bot.get_page(db.query(
                        query=Query(
                            filters=PropertyFilter(
                                prop="ID",
                                filter_type=Text.Type.rich_text,
                                condition=Text.Filter.equals,
                                target=r.id
                            )
                        )
                    )[0]['id'])
                    page.update(
                        parent=Parent(db),
                        properties=Properties(
                            Deadline=DateValue(NotionDate(
                                start=r.deadline.start,
                                end=r.deadline.end
                            )),
                            Content=TextValue(r.description_content),
                            Submission=NumberValue(int(r.submission_number))
                        )
                    )
        await asyncio.gather(*tasks)
        return newly_upload, newly_update


async def update_all_bulletin_info_to_notion_db(bulletins: List[Bulletin], db: Database):
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        object_index = get_all_ids(db.query())
        newly_upload = []
        tasks = []
        for r in bulletins:
            if object_index is not None and r.id not in object_index:
                newly_upload.append(f"upload bulletin : {r.title} to bulletin database")
                tasks.append(db.async_post(bulletin_in_notion_template(db, r), session))
        await asyncio.gather(*tasks)
        return newly_upload


async def update_all_material_info_to_notion_db(materials: List[Material], db: Database):
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        object_index = get_all_ids(db.query())
        newly_upload = []
        tasks = []
        for r in materials:
            if object_index is not None and r.id not in object_index:
                newly_upload.append(f"upload material : {r.title} to material database")
                tasks.append(db.async_post(material_in_notion_template(db, r), session))
        await asyncio.gather(*tasks)
        return newly_upload


async def run():
    load_dotenv()
    auth = os.getenv("NOTION_AUTH")
    account = os.getenv("ACCOUNT")
    password = os.getenv("PASSWORD")
    notion_bot = Notion(auth)
    bulletin_db: Database = notion_bot.get_database(os.getenv("BULLETIN_DB"))
    homework_db: Database = notion_bot.get_database(os.getenv("HOMEWORK_DB"))
    material_db: Database = notion_bot.get_database(os.getenv("MATERIAL_DB"))
    bulletins, homeworks, materials = await fetch_all_eeclass_data(account, password)

    await update_all_bulletin_info_to_notion_db(bulletins, bulletin_db)
    await update_all_homework_info_to_notion_db(homeworks, homework_db)
    await update_all_material_info_to_notion_db(materials, material_db)
    EEChromeDriver.close_driver()


if __name__ == '__main__':
    asyncio.run(run())
