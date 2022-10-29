from PyNotion.Object import *
from PyNotion.NotionClient import Notion
from bs4 import BeautifulSoup
import re
import os
import json
import aiohttp
import asyncio
from aiohttp import web
from fake_user_agent import user_agent
import re


class Bot:
    BASE_URL = "https://ncueeclass.ncu.edu.tw"
    YEAR = 2022
    ua = user_agent()
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "User-Agent": user_agent("chrome")
    }

    def __init__(self, session, account, password):
        self.session = session
        self.account = account
        self.password = password
        self.courses_list: list[Course] = []
        self.bulletins_list: list[Bulletin] = []
        self.homeworks_list: list[Homework] = []
        self.bulletins_detail_list: list[dict] = []
        self.homeworks_detail_list: list[dict] = []

    async def login(self):
        data = {
            "_fmSubmit": "yes",
            "formVer": "3.0",
            "formId": "login_form",
            "next": "/",
            "act": "keep",
            "account": f"{self.account}",
            "password": f"{self.password}",
        }
        url = Bot.BASE_URL + "/index/login"
        resp = await self.session.get(Bot.BASE_URL)
        # get csrf-t code
        # print("get csrf-t code")
        soup = BeautifulSoup(await resp.text(), 'lxml')
        code = soup.select("#csrf-t > div > input[type=hidden]")
        data['csrf-t'] = code[0]['value']
        # print(data['csrf-t'])
        # print("login ......")
        result = await self.session.post(url, data=data)
        result = await result.text()
        result = json.loads(result)
        # print(result)
        if result['ret']['status'] == 'true':
            print(f"login successfully\nwelcome {self.account}")
            # url = "https://ncueeclass.ncu.edu.tw/dashboard"
            # resp = await self.session.get(url)
            # soup = BeautifulSoup(await resp.text(), 'lxml')
            # print(soup)
            return True
        else:
            print("wrong password or username")
            return False

    async def pipline(self):
        await self.retrieve_all_course(check=True, refresh=True)
        await self.retrieve_all_homeworks()
        await self.retrieve_all_homeworks_details()
        await self.retrieve_all_bulletins()
        await self.retrieve_all_bulletins_details()
        # print(self.bulletins_list)
        # print(self.homeworks_list)
        # print(self.homeworks_detail_list)
        # print(self.bulletins_detail_list)

    async def retrieve_all_course(self, refresh: bool = False, check: bool = False):
        self.courses_list = await Course.retrieve_all(self, refresh, check)
        return self.courses_list

    async def retrieve_all_bulletins(self):
        # tasks = [r.get_bulletin_page() for r in self.courses_list]
        # await asyncio.gather(*tasks)
        tasks = [r.get_all_bulletin_page() for r in self.courses_list]
        course_bulletins_list = await asyncio.gather(*tasks)
        self.bulletins_list = []
        for cb in course_bulletins_list:
            self.bulletins_list.extend(cb)

        return self.bulletins_list

    async def retrieve_all_homeworks(self):
        tasks = [r.get_all_homework_page() for r in self.courses_list]
        course_homework_list = await asyncio.gather(*tasks)
        self.homeworks_list = []
        for ch in course_homework_list:
            self.homeworks_list.extend(ch)
        return self.homeworks_list

    async def retrieve_all_bulletins_details(self):
        tasks = [bu.retrieve() for bu in self.bulletins_list if isinstance(bu, Bulletin)]
        self.bulletins_detail_list = await asyncio.gather(*tasks)
        return self.bulletins_detail_list

    async def retrieve_all_homeworks_details(self):
        tasks = [hw.retrieve() for hw in self.homeworks_list if isinstance(hw, Homework)]
        self.homeworks_detail_list = await asyncio.gather(*tasks)
        return self.homeworks_detail_list


class Course:
    BASE_URL = Bot.BASE_URL + '/course/'

    def __init__(self, bot, name: str, index: str):
        self.bot = bot
        self.name = name
        self.index = index
        self.url = Course.BASE_URL + index
        self.bulletin_page_url = Course.BASE_URL + "bulletin/" + index
        self.bulletins_url_list = [self.bulletin_page_url]
        self.bulletins: list[Bulletin] = []
        self.homework_list_url = Course.BASE_URL + "homeworkList/" + index
        self.homeworks_url = []
        self.homeworks = []

    def __repr__(self):
        return f"{self.name}\n {self.url}\n"

    @classmethod
    async def retrieve_all(cls, bot, refresh=False, check=False):
        if os.path.isfile("course_info.json") and not refresh:
            with open("course_info.json", 'r') as f:
                courses = json.load(f)
        else:
            url = "https://ncueeclass.ncu.edu.tw/dashboard"
            resp = await bot.session.get(url, headers=Bot.headers)
            soup = BeautifulSoup(await resp.text(), 'lxml')
            result = soup.select("div > ul > li > div > div > div> div > div.fs-label > a")
            courses = [dict(name=r.text.strip(), index=r['href'].split('/')[-1]) for r in result]
            with open("course_info.json", 'w') as f:
                print(json.dumps(courses), file=f)

        courses_list = []
        for course in courses:
            courses_list.append(Course(bot, course['name'], course['index']))

        if check:
            for c in courses_list:
                print(c)

        return courses_list

    async def get_all_bulletin_page(self) -> list:
        async with self.bot.session.get(self.bulletin_page_url, headers=self.bot.headers) as resp:
            soup = BeautifulSoup(await resp.text(), 'lxml')
            b_list = soup.select(
                "#bulletinMgrTable > tbody > tr > td > div > div.fs-singleLineText.afterText > div.text-overflow > a"
            )
            # pagination = list(set(pagination))
            # if pagination:
            #     for p in pagination:
            # self.bulletins.append(self.bulletin_page_url + p)
            self.bulletins = [Bulletin(bot=self.bot, link=p['data-url'],title=p['data-modal-title']) for p in b_list]
            return self.bulletins

    # async def get_all_bulletin_page(self):
    #     task = [Bulletin.get_bulletin_page(url=url, bot=self.bot) for url in self.bulletins_url_list]
    #     self.bulletins = await asyncio.gather(*task)
    #     return self.bulletins

    async def get_all_homework_page(self):
        """ homework 暫且不會有選頁面的問題"""
        async with self.bot.session.get(self.homework_list_url, headers=self.bot.headers) as resp:
            # print(self)
            soup = BeautifulSoup(await resp.text(), 'lxml')
            soup_select = soup.select("#homeworkListTable > tbody > tr > td > div > div > div.text-overflow > a")
            homework_link_list = [p['href'] for p in soup_select]
            for homework in soup_select:
                url = homework['href']
                title = homework.find('span').text
                self.homeworks.append(
                    Homework(
                        bot=self.bot,
                        title=title,
                        link=url,
                        course=self
                    )
                )

            return self.homeworks


class Bulletin:
    BaseURL = "https://ncueeclass.ncu.edu.tw"
    exp = r"id=([0-9]+)&"

    def __init__(self, bot, link, title):
        self.bot = bot
        self.link = link
        self.title = title
        self.index = re.search(pattern=self.exp, string=self.link).group(1)
        self.url = self.BaseURL + link
        self.details = {}

    def __repr__(self):
        return f"{self.title}"

    async def retrieve(self):
        async with self.bot.session.get(self.url, headers=self.bot.headers) as resp:
            soup = BeautifulSoup(await resp.text(), 'lxml')
            detail = soup.select('div.modal-iframe-ext2')[0].text
            detail = detail.split(',')
            content = soup.select('div.fs-text-break-word')
            link = []
            for c in content:
                for l in c.findAll('a'):
                    try:
                        if not l['href'].startswith('https://'):
                                l['href'] = "https://ncueeclass.ncu.edu.tw" + l['href']
                        else:
                            link.append({'名稱': l.text, '連結': l['href']})
                    except:
                        pass

            content = '\n'.join([c.text for c in content])
            attach = soup.select('div.text > a')
            attach = [{'名稱': a.text, '連結': "https://ncueeclass.ncu.edu.tw" + a['href'], '檔案大小': a.span.text} for a in
                      attach]
            result = {
                'type': '公告',
                'url': self.url,
                'title': self.title,
                'date': {'start': f"{Bot.YEAR}-{detail[1].strip('公告日期 ')}"},
                'ID': self.index,
                'course': detail[2].strip(' '),
                '發佈人': detail[3].strip(' by '),
                'content': {'公告內容': content, '附件': attach, '連結': link},
                '人氣': detail[0].split(' ')[1],
            }
            print(f"{self.title} Finish")
            self.details = result
            return result

    # @classmethod
    # async def get_bulletin_page(cls, url, bot) -> __class__:
    #     async with bot.session.get(url, headers=bot.headers) as resp:
    #         soup = BeautifulSoup(await resp.text(), 'lxml')
    #         bulletins_list = soup.select(
    #             '#bulletinMgrTable > tbody > tr > td > div > div.fs-singleLineText.afterText > div.text-overflow > a'
    #         )
    #         for bulletins in bulletins_list:
    #             link = bulletins['data-url']
    #             title = bulletins.find('span').text
    #
    #             self.bulletins.append(Bulletin(bot=self.bot, link=link, title=title))
    #     return self.bulletins

class Homework:
    BaseURL = "https://ncueeclass.ncu.edu.tw/course/homework/"

    def __init__(self, bot, title, link, course):
        self.bot = bot
        self.title = title
        self.index = link.split('/')[-1]
        self.course = course
        self.url = self.BaseURL + self.index
        self.details = {}

    def __repr__(self):
        return f"{self.course.name} : {self.title}"

    async def retrieve(self) -> dict:
        async with self.bot.session.get(self.url, headers=self.bot.headers) as resp:
            soup = BeautifulSoup(await resp.text(), 'lxml')
            dl = soup.select("dl")
            title = dl[0].findAll('dt')
            content = dl[0].findAll('dd')
            results = {t.text: "" for t in title}
            results['attach'] = []
            results['link'] = []
            for t, c in zip(title, content):
                if t.text == '附件':
                    for li in c.findAll('li'):
                        results['attach'].append(
                            {"title": li.text.strip(), "link": Bot.BASE_URL + li.find('a')['href']}
                        )
                    continue

                for link in c.findAll('a'):
                    results['link'].append({"title": link.text.strip(), "link": link['href']})
                results[t.text] = c.text

            self.details = dict(
                title=self.title,
                url=self.url,
                course=self.course.name,
                course_link=self.course.url,
                date=dict(start=results['開放繳交'], end=results['繳交期限']),
                content=results,
                type='homework',
                ID=self.index,
            )
            return self.details


async def main():
    async with aiohttp.ClientSession() as session:
        # bot part
        bot = Bot(session, "109502563", "H125920690")
        await bot.login()
        await bot.pipline()
        # await bot.retrieve_all_course(check=True, refresh=True)
        # homeworks = await bot.retrieve_all_homeworks()
        # await bot.retrieve_all_homeworks_details()
        #hw = homeworks[1]
        # print(hw, type(hw), type(hw[0]))
        # await bot.retrieve_all_homeworks_details()
        # print(hw[0])
        # print(await hw[0].retrieve())
if __name__ == '__main__':
    asyncio.run(main())
