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


def bulletin_in_notion_template(db: Database, target: Bulletin):
    return BaseObject(
        parent=Parent(db),
        properties=Properties(
            Title=TitleValue(target.title),
            Course=SelectValue(target.course),
            ID=TextValue(target.ID),
            Announce_Date=DateValue(NotionDate(start=target.date.start)),
            Content=TextValue(target.content.content),
            Link=UrlValue(target.url)
        ),
        children=Children(
            CallOutBlock(f"發佈人 {target.announcer}  人氣 {target.popular}", color=Colors.Background.green),
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
    from datetime import datetime, timezone, timedelta
    now = datetime.strptime(datetime.now(tz=timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M")
    cover_file_url = "https://images.pexels.com/photos/13010695/pexels-photo-13010695.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1"
    date_format = '%Y-%m-%d %H:%M'
    try:
        target.date['start'] = datetime.strptime(target.date['start'], date_format)
    except:
        target.date['start'] += " 00:00"
        target.date['start'] = datetime.strptime(target.date['start'], date_format)
    try:
        target.date['end'] = datetime.strptime(target.date['end'], date_format)
    except:
        target.date['end'] += " 23:59"
        target.date['end'] = datetime.strptime(target.date['end'], date_format)
    submission_status = ""
    if target.submission_status == "檢視 / 修改我的作業":
        submission_status = "已完成"
    elif target.submission_status == "交作業" and (now > target.date['start'] and now < target.date['end']) or (
            now < target.date['start']):
        submission_status = "未完成"
    else:
        submission_status = "缺交"

    target.date['start'] = target.date['start'].strftime("%Y-%m-%d %H:%M")
    target.date['end'] = target.date['end'].strftime("%Y-%m-%d %H:%M")

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
            ID=TextValue(target.ID),
            Deadline=DateValue(NotionDate(**target.date)),
            Link=UrlValue(target.url),
            Homework_Type=SelectValue(target.homework_type),
            Content=TextValue(target.description_content),
            Submission=NumberValue(target.already_submit_number)
        ),
        children=Children(*children_list),
        icon=Emoji("🐶"),
        cover=FileValue(cover_file_url)
    )


def material_in_notion_template(db: Database, target: Material):
    complete_emoji = "✅" if target.complete_check else "❎"
    study_status = "已完成" if target.complete_check else "未完成"
    material_type = "影片" if target.subtype == "video" else "文字"
    return BaseObject(
        parent=Parent(db),
        properties=Properties(
            Title=TitleValue(target.title),
            Course=SelectValue(target.course),
            ID=TextValue(target.ID),
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
            CallOutBlock(f"發佈人 {target.announcer}  觀看數 {target.views}  教材類型 {target.subtype}",
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
                ID=TextValue(target.ID),
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
                CallOutBlock(f"發佈人 {target.announcer}  觀看數 {target.views}  教材類型 {target.subtype}",
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

def get_id_col(db_col: List[Dict]) -> List[str]:
    cols = []
    for p in db_col:
        rich_text = p['properties']['ID']['rich_text']
        if len(rich_text) > 0:
            cols.append(rich_text[0]['plain_text'])
    return cols


def get_id_submission_pair(db_col: List[Dict]) -> Dict[str, str]:
    pair = {}
    for p in db_col:
        rich_text = p['properties']['ID']['rich_text']
        submission = p['properties']['Submission']
        try:
            pair[rich_text[0]['plain_text']] = submission['number']
        except:
            raise Exception("ID or Submission may be None")
    return pair


async def update_all_homework_info_to_notion_db(homeworks: List[Homework], db: Database):
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        object_index = get_id_col(db.query())
        id_submission_pair = get_id_submission_pair(db.query())
        newly_upload, newly_update = [], []
        tasks = []
        for r in homeworks:
            if object_index is not None and r.ID not in object_index:
                newly_upload.append(f"upload homework : {r.title} to homework database")
                tasks.append(db.async_post(homework_in_notion_template(db, r), session))
            elif object_index is not None and str(r.already_submit_number) != id_submission_pair[r.ID]:
                newly_update.append(f"update homework : {r.title} to homework database")
                page = db.query(
                    query=Query(
                        filters=PropertyFilter("ID", Text.Type.rich_text, Text.Filter.contains, r.ID)
                    )
                )[0]['id']
                page = db.bot.get_page(page)
                page.update(parent=Parent(db), properties=Properties(Submission=int(r.already_submit_number)))
        await asyncio.gather(*tasks)
        return newly_upload, newly_update


async def update_all_bulletin_info_to_notion_db(bulletins: List[Bulletin], db: Database):
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        object_index = get_id_col(db.query())
        newly_upload = []
        tasks = []
        for r in bulletins:
            if object_index is not None and r.ID not in object_index:
                newly_upload.append(f"upload bulletin : {r.title} to bulletin database")
                tasks.append(db.async_post(bulletin_in_notion_template(db, r), session))
        await asyncio.gather(*tasks)
        return newly_upload


async def update_all_material_info_to_notion_db(materials: List[Material], db: Database):
    async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
        object_index = get_id_col(db.query())
        newly_upload = []
        tasks = []
        for r in materials:
            if object_index is not None and r.ID not in object_index:
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
