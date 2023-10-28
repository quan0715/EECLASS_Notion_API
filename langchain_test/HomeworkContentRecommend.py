from langchain.tools import BaseTool
from NotionBot import *
from NotionBot.base.Database import *
from eeclass_bot.EEAsyncBot import EEAsyncBot

from typing import Optional, Type
from pydantic import BaseModel, Field
import datetime
import os
from fuzzywuzzy import fuzz
import aiohttp
from datetime import datetime, timezone, timedelta, date
from dotenv import load_dotenv

class HomeworkTitleInput(BaseModel):
    """Input for homework title"""
    course_title: str = Field(
        ...,
        description=f"It's a college course that the user takes in this semester. If user doesn't offer this, please return empty string."
    )
    homework_title_input: str = Field(
        ...,
        description="It's a homework title that is assigned in a college course."
    )

class HomeworkContent(BaseTool):
    name = "Homework_Content_Recommendation_system"
    description = f"User will give only homework name or course name with homework name. Please make some detail recommendation to each homework content. Or give some useful idea on each content. Or what it is about. You can summarize it. By the way, current time is {date.today()}"

    @staticmethod
    async def get_most_possible_course(course_title: str):
        load_dotenv()
        account = os.getenv("ACCOUNT")
        password = os.getenv("PASSWORD")
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False),
                                     cookie_jar=aiohttp.CookieJar(unsafe=True, quote_cookie=True)) as session:
            bot = EEAsyncBot(session, account, password)
            await bot.login()
            course_list = await bot.retrieve_all_course(check=True, refresh=True)
            course_list = [course.name for course in course_list]
        possibility = {}
        for course in course_list:
            possibility[course] = fuzz.partial_ratio(course, course_title)
        sorted_possibility = dict(sorted(possibility.items(), key=lambda x:x[1], reverse=True))
        return list(sorted_possibility.keys())[0]

    @staticmethod
    def get_homework_content(course_name: str="", homework_title_input: str="") -> List[dict] | str:
        if homework_title_input == "":
            return "抓不到課程名稱"
        load_dotenv()
        auth = os.getenv("NOTION_AUTH")
        notion_bot = Notion(auth)
        homework_db: Database = notion_bot.get_database(os.getenv("HOMEWORK_DB"))
        now = datetime.strptime(datetime.now(tz=timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M")
        similar_homework = []
        for h in homework_db.query():
            homework_title = h['properties']['Title']['title'][0]['plain_text']
            page = homework_db.bot.get_page(h['id'])
            Attach_title_url = []
            course=h['properties']['Course']['select']['name']
            for p in page.retrieve_children()['results']:
                    if 'object' in p and p['object'] == 'block':
                        if 'bulleted_list_item' in p:
                            Attach_title_url.append(dict(
                                title=p['bulleted_list_item']['rich_text'][0]['plain_text'],
                                url=p['bulleted_list_item']['rich_text'][0]['href']
                            ))
            print(homework_title, homework_title_input)
            print(course, course_name)
            if (course == course_name and fuzz.partial_ratio(homework_title, homework_title_input) > 0.5) or fuzz.partial_ratio(course_name, course) > 0.6:
                similar_homework.append(dict(
                    Content=h['properties']['Content']['rich_text'][0]['text'],
                    Deadline=h['properties']['Deadline']['date'],
                    Course=course,
                    Status=h['properties']['Status']['select']['name'],
                    Link=h['properties']['Link']['url'],
                    Submission=h['properties']['Submission']['number'],
                    Homework_Type=h['properties']['Homework_Type']['select']['name'],
                    Attach_title_url=Attach_title_url
                ))
            else:
                similar_homework = "比對後找不到類似名稱．請再輸入更詳細的名稱"
        return similar_homework

    def _run(self, course_title: str, homework_title_input: str):
        pass
        

    async def _arun(self, course_title: str, homework_title_input: str):
        course_title = await self.get_most_possible_course(course_title)
        result = self.get_homework_content(course_title, homework_title_input)
        return result
    
    args_schema: Optional[Type[BaseModel]] = HomeworkTitleInput
