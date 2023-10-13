from typing import List
from bs4 import BeautifulSoup
# import re
import os
import json
import aiohttp
import asyncio
# from aiohttp import web
from fake_user_agent import user_agent
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

exist_driver = None

def load_video():
    global exist_driver
    if exist_driver == None:
        chrome_option = Options()
        # chrome_option.add_argument("headless")
        chrome_option.page_load_strategy = "eager"
        driver = webdriver.Chrome(options=chrome_option)
        driver.get("https://ncueeclass.ncu.edu.tw/")
        login_button = driver.find_element(By.CLASS_NAME, "nav.navbar-nav.navbar-right").find_element(By.TAG_NAME, "span")
        login_button.click()
        login_form = driver.find_element(By.ID, "login_form")
        login_form.find_element(By.NAME, "account").send_keys("109502554")
        login_form.find_element(By.NAME, "password").send_keys("Timjack25!")
        login_button = login_form.find_element(By.TAG_NAME, "button")
        login_button.click()
        time.sleep(3)
        login_button = driver.find_element(By.CLASS_NAME, "btn.btn-default.keepLoginBtn")
        login_button.click()
        time.sleep(3)
        exist_driver = driver
    return exist_driver


from eeclass_bot.models.BlockMaterial import BlockMaterial


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
        self.courses_list: List[Course] = []
        self.bulletins_list: List[Bulletin] = []
        self.homeworks_list: List[Homework] = []
        self.bulletins_detail_list: List[dict] = []
        self.homeworks_detail_list: List[dict] = []

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
        await self.retrieve_all_material()
        await self.retrieve_all_materials_details()

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

    async def retrieve_all_material(self):
        tasks = [r.get_all_material_page() for r in self.courses_list]
        course_material_list = await asyncio.gather(*tasks)
        self.material_list = []
        for course in course_material_list:
            for block in course:
                print(block.materials)
                self.material_list.extend(block.materials)
        return self.material_list
    
    async def retrieve_all_bulletins_details(self):
        tasks = [bu.retrieve() for bu in self.bulletins_list if isinstance(bu, Bulletin)]
        self.bulletins_detail_list = await asyncio.gather(*tasks)
        return self.bulletins_detail_list

    async def retrieve_all_homeworks_details(self):
        tasks = [hw.retrieve() for hw in self.homeworks_list if isinstance(hw, Homework)]
        self.homeworks_detail_list = await asyncio.gather(*tasks)
        return self.homeworks_detail_list
    
    async def retrieve_all_materials_details(self):
        tasks = [m.retrieve() for m in self.material_list if isinstance(m, Material)]
        self.materials_detail_list = await asyncio.gather(*tasks)
        return self.materials_detail_list

class_name_to_material_type = {
    "font-icon fs-fw far fa-file-alt" : "text",
    "font-icon fs-fw far fa-file-video" : "video",
    "font-icon fs-fw far fa-clipboard" : "homework",
    "font-icon fs-fw far fa-file-pdf" : "pdf",
    "font-icon fs-fw far fa-file-powerpoint" : "ppt"
}

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
        self.material_url = Course.BASE_URL + index
        self.materials = []

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
            self.bulletins = [Bulletin(bot=self.bot, link=p['data-url'], title=p['data-modal-title']) for p in b_list]
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
            for homework in soup_select:
                url: str = homework['href']
                title: str = homework['title']
                self.homeworks.append(
                    Homework(
                        bot=self.bot,
                        title=title,
                        link=url,
                        course=self
                    )
                )
            return self.homeworks
        
    async def get_all_material_page(self):
        async with self.bot.session.get(self.material_url, headers=self.bot.headers) as resp:
            soup = BeautifulSoup(await resp.text(), 'lxml')
            material_block = soup.select(".fs-block-body > div > ol.xtree-list > li")
            for block in material_block:
                block_material_list = []
                block_title = block.select_one("div.header.hover.hover > div > span > div.text > div").text
                material_in_block = block.select("div.body > ol.xtree-list > li")
                for material in material_in_block:
                    if " ".join(material['class']) == "xtree-node type- clearfix":
                        type = class_name_to_material_type[' '.join(material.select_one("div.header.hover.hover > div.center-part > span.xtree-node-label > div.icon.pull-left > span")['class'])]
                        link = material.select("div.header.hover.hover > div.center-part > span.xtree-node-label > div.text > div.node-title > div.fs-singleLineText > div")[1].select_one('a')['href']
                        title = material.select("div.header.hover.hover > div.center-part > span.xtree-node-label > div.text > div.node-title > div.fs-singleLineText > div")[1].select_one('a > span.text').text
                        brief_condition = material.select_one("div.header.hover.hover > div.center-part > div.hidden-xs.pull-right")
                        deadline = brief_condition.select("div.ext-col.fs-text-nowrap.col-time.text-center")[0].text
                        complete_condition = brief_condition.select_one("div.ext-col.fs-text-nowrap.col-char7.text-center").text
                        read_time = brief_condition.select_one("div.ext-col.fs-text-nowrap.col-char4.text-center > span").text if brief_condition.select_one("div.ext-col.fs-text-nowrap.col-char4.text-center > span") != None else brief_condition.select_one("div.ext-col.fs-text-nowrap.col-char4.text-center").text
                        complete_check = True if brief_condition.select("div.ext-col.fs-text-nowrap.col-time.text-center")[1].select_one("span") != None else False
                        block_material_list.append(
                            Material(
                                bot=self.bot,
                                course=self,
                                type=type,
                                link=link,
                                title=title,
                                deadline=deadline,
                                complete_condition=complete_condition,
                                read_time=read_time,
                                complete_check=complete_check
                            )
                        )
                        print(type,link,title,deadline,complete_condition,read_time,complete_check)
                self.materials.append(
                    BlockMaterial(
                        block_title=block_title,
                        materials=block_material_list
                    )
                )
            return self.materials
            # for material in soup_select:
            #     url = material['href']
            #     title = material.select_one('span.text').text
            #     self.materials.append(
            #         Material(
            #             bot=self.bot,
            #             title=title,
            #             link=url,
            #             course=self
            #         )
            #     )
            # for r in self.materials:
            #     print(r)
            # return self.materials


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
            date = detail[1].strip('公告日期 ')
            if len(date.split('-')) == 2:
                date = "2023-" + date
                # TODO 動態抓取今年年份
            result = {
                'type': '公告',
                'url': self.url,
                'title': self.title,
                'date': {'start': f"{date}"},
                'ID': self.index,
                'course': detail[2].strip(' '),
                '發佈人': detail[3].strip(' by '),
                'content': {'公告內容': content, '附件': attach, '連結': link},
                '人氣': detail[0].split(' ')[1],
            }
            print(f"EECLASS BOT (fetch) : {self.title}")
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
                    try:
                        results['link'].append({"title": link.text.strip(), "link": link['href']})
                    except KeyError:
                        continue
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
            print(f"EECLASS BOT (fetch) : {self.title}")
            return self.details

class Material:
    BaseURL = "https://ncueeclass.ncu.edu.tw"

    def __init__(self, bot, title, link, course, type, deadline, complete_condition, read_time, complete_check) -> None:
        self.bot = bot
        self.url = self.BaseURL + link
        self.title = title
        self.course = course
        self.type = type
        self.deadline = deadline
        self.complete_condition = complete_condition
        self.read_time = read_time
        self.complete_check = complete_check

    def __repr__(self) -> str:
        return f"{self.title}: {self.url}"

    async def retrieve(self):

        async with self.bot.session.get(self.url, headers=self.bot.headers) as resp:
            soup = BeautifulSoup( await resp.text(), 'lxml')
            detail_str = soup.select_one("div.ext2.fs-hint")
            content, attachments, link = "", [], []
            update_time, views, uploader, video_view, video_url = "", "", "", "", ""
            if self.type == "video":
                '''影片類型'''
                detail_list = soup.select_one("div.module.mod_media.mod_media-detail").findAll("dd")
                update_time = detail_list[1].text
                views = detail_list[2].text
                uploader = detail_list[4].text

                driver = load_video()
                driver.get(self.url)
                video_view = driver.find_element(By.ID, "mediaBox").find_elements(By.TAG_NAME, "img")[1].get_attribute("src")
                video_url = driver.find_element(By.ID, "mediaBox").find_element(By.TAG_NAME, "video").get_attribute("src")
                print(video_url, video_view)
                
                
            elif self.type in ["text", "pdf", "ppt"]:
                detail_str = detail_str.text
                exp = r"(\d+) 觀看數"
                views = re.search(pattern=exp, string=detail_str).group(1)
                exp = r"更新時間 (.+),"
                update_time = re.search(pattern=exp, string=detail_str).group(1)
                exp = r"by (.+)"
                uploader = re.search(pattern=exp, string=detail_str).group(1)

                link = []
                content_block = soup.select_one("div#xbox-inline")
                content = content_block.select_one("div.module.mod_mediaDoc.mod_mediaDoc-show")
                if content != None:
                    for l in content.find_all("a"):
                        if not l['href'].startswith("https://"):
                            link.append({'名稱': "https://ncueeclass.ncu.edu.tw/" + l['href'], '連結': "https://ncueeclass.ncu.edu.tw/" + l['href']})
                        else:
                            link.append({'名稱': l.text, '連結': l['href']})
                else:
                    content = ""
                attachments = content_block.select_one("div.module.mod_media.mod_media-attachList").select("div.text > a")
                attachments = [{'名稱': a.text, '連結': "https://ncueeclass.ncu.edu.tw" + a['href'], '檔案大小': a.span.text} for a in attachments]

                content = '\n'.join([c.text.strip('\n').strip(' ') for c in content if c.text.strip('\n').strip(' ') != ""])
            else:
                pass
                
            self.details = dict(
                title = self.title,
                ID = self.url.split('/')[-1],
                url = self.url,
                course = self.course.name,
                type = 'material',
                subtype = self.type,
                觀看數 = views,
                更新時間 = update_time,
                deadline = {'end': f"{self.deadline}"},
                發佈者 = uploader,
                完成條件 = self.complete_condition,
                完成度 = self.read_time,
                已完成 = self.complete_check,
                content = {'教材內容': content, '附件': attachments, '連結': link},
                影片縮略圖 = video_view,
                影片網址 = video_url
            )
            return self.details




async def main():
    connector = aiohttp.TCPConnector(limit=50)
    timeout = aiohttp.ClientTimeout(total=600)
    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        bot = Bot(session=session,
                  account="你的帳號",
                  password="你的密碼")
        await bot.login()
        await bot.retrieve_all_course(check=True, refresh=True)
        await bot.pipline()

if __name__ == '__main__':
    asyncio.run(main())
