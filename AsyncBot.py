from PyNotion.Object import *
from PyNotion.NotionClient import Notion
import requests
from bs4 import BeautifulSoup
import re
import threading
import os
import json
import aiohttp
import asyncio
from aiohttp import web
from fake_user_agent import user_agent
import re

class Bot:
    URL = "https://ncueeclass.ncu.edu.tw"
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
        self.course_list = []

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
        url = Bot.URL + "/index/login"
        resp = await self.session.get(Bot.URL)
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

    # def connect_notion_database(self, auth, database_name):
    #     try:
    #         # print("正在和Notion做連線")
    #         self.notion = Notion(auth)
    #         self.database = self.notion.fetch_databases(database_name)
    #         self.issue_id = self.database.query_database_dataframe()['ID']  # 已經update的事件ID
    #         # print(f"成功連線到 {database_name} Notion資料庫")
    #
    #     except:
    #         print("資訊有誤請重新嘗試")

    async def retrieve_all_course(self, refresh: bool=False, check: bool=False):
        self.course_list = await Course.retrieve_all(self, refresh, check)
        return self.course_list

    async def retrieve_all_bulletins(self):
        pass


    def get_latest_events(self):
        print("爬取最新事件......")
        url = "/dashboard/latestEvent"
        results = []
        parmas = {
            "category": "all",
            "page": "1",
            "pageSize": "20",
        }
        r = self.session.get(Bot.URL + url, headers=self.headers, params=parmas)
        print(r)
        soup = BeautifulSoup(r.text, 'lxml')
        s = soup.select('#recentEventTable > tbody > tr ')
        for row in s:
            r = row.findAll('td')
            if len(r) == 3:
                results.append({
                    '標題': r[0].text,
                    '連結': "https://ncueeclass.ncu.edu.tw" + r[0].div.a['href'],
                    '課程': r[1].text,
                    '課程連結': r[1].div.a['href'],
                    '日期': r[2].text,
                    '類型': '作業' if r[0].div.a['href'].find("homework") != -1 else '問卷',
                    'ID': r[0].div.a['href'].split('/')[-1]
                })
        print("最近事件爬取完畢")
        return results

    def get_homework_content(self, homework):
        r = self.session.get(homework['連結'], headers=self.headers)
        soup = BeautifulSoup(r.text, 'lxml')
        dl = soup.select("dl")
        title = dl[0].findAll('dt')
        content = dl[0].findAll('dd')
        results = {t.text : "" for t in title}
        results['附件'] = []
        results['連結'] = []
        for t, c in zip(title, content):
            if t.text == '附件':
                for li in c.findAll('li'):
                    results[t.text].append({"名稱": li.text, "連結": "https://ncueeclass.ncu.edu.tw" + li.find('a')['href']})
            else:
                for l in c.findAll('a'):
                    results['連結'].append({"名稱": l.text, "連結": l['href']})
                results[t.text] = c.text
        homework['內容'] = results
        homework['日期'] = {'start': results['開放繳交'], 'end': results['繳交期限']}
        return homework

    def update_events(self):
        def post(homework):
            self.post(self.get_homework_content(homework))

        def update(homework, index):
            self.update(self.get_homework_content(homework), index)

        r = self.get_latest_events()
        threadings = []
        for h in r:
            if h['類型'] == '作業':
                if h['ID'] not in self.issue_id:
                    print(f'新增事件:{h["標題"]}')
                    t = threading.Thread(target=post, args=(h,))
                    t.start()
                    threadings.append(t)
                else:
                    print(f'更新事件:{h["標題"]}')
                    t = threading.Thread(target=update, args=(h, h['ID']))
                    t.start()
                    threadings.append(t)
        for t in threadings:
            t.join()

    def update_bulletin(self):
        print("開始更新最新公告")
        self.all_bulletins = self.get_latest_bulletins()
        self.issue_id = self.database.query_database_dataframe()['ID']
        threadings = []

        for target in self.all_bulletins:
            if target['index'] not in self.issue_id:
                print(f'更新事件:{target["title"]}')
                t = threading.Thread(target=lambda b: self.post(self.get_bulletin_content(b)), args=(target,))
                t.start()
                threadings.append(t)
        for t in threadings:
            t.join()
        print("最新公告更新完成")


class Course:
    def __init__(self,bot, name: str, index: str):
        self.bot = bot
        self.name = name
        self.index = index
        self.url = "https://ncueeclass.ncu.edu.tw/course/" + index
        self.bulletin_url = "https://ncueeclass.ncu.edu.tw/course/bulletin/" + index
        self.bulletin_page_url = [self.bulletin_url]
        self.bulletins = []

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
            result = soup.select("#currentTerm > div > ul > li > div > div > div> div > div.fs-label > a")
            courses = [dict(name=r.text.strip(), index=r['href'].split('/')[-1]) for r in result]
            with open("course_info.json", 'w') as f:
                print(json.dumps(courses), file=f)

        courses_list = []
        for course in courses:
            courses_list.append(Course(bot,course['name'], course['index']))

        if check:
            for c in courses_list:
                print(c)

        return courses_list

    async def get_bulletin_page(self):
        async with self.bot.session.get(self.bulletin_url, headers=self.bot.headers) as resp:
            # print(self)
            soup = BeautifulSoup(await resp.text(), 'lxml')
            pagination = soup.select("#xbox-inline > div.module.mod_bulletin.mod_bulletin-list > div.fs-pagination.clearfix > div > div > nav > ul > li > a")
            pagination = [p['href'] for p in pagination]
            pagination = list(set(pagination))
            if pagination:
                for p in pagination:
                    self.bulletin_page_url.append(self.bulletin_url+p)

    async def get_all_bulletin(self):
        for url in self.bulletin_page_url:
            async with self.bot.session.get(url,headers=self.bot.headers) as resp:
                soup = BeautifulSoup(await resp.text(), 'lxml')
                bulletins_list = soup.select(
                    '#bulletinMgrTable > tbody > tr > td > div > div.fs-singleLineText.afterText > div.text-overflow > a'
                )
                for bulletins in bulletins_list:
                    link = bulletins['data-url']
                    title = bulletins.find('span').text
                    self.bulletins.append(Bulletin(bot=self.bot, link=link, title=title))


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
                        link.append({'名稱': l.text, '連結': l['href']})
                    except:
                        pass

            content = '\n'.join([c.text for c in content])
            attach = soup.select('div.text > a')
            attach = [{'名稱': a.text, '連結': "https://ncueeclass.ncu.edu.tw" + a['href'], '檔案大小': a.span.text} for a in
                      attach]
            result = {
                '類型': '公告',
                '連結': self.url,
                '標題': self.title,
                '日期': {'start': f"{Bot.YEAR}-{detail[1].strip('公告日期 ')}"},
                'ID': self.index,
                '課程': detail[2].strip(' '),
                '發佈人': detail[3].strip(' by '),
                '內容': {'公告內容': content, '附件': attach, '連結': link},
                '人氣': detail[0].split(' ')[1],
            }
            print(f"{self.title} Finish")
            self.details = result
            return result



