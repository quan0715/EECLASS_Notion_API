import json
import os

from bs4 import BeautifulSoup

from eeclass_bot.EEBulletin import EEBulletin
from eeclass_bot.EEConfig import EEConfig
from eeclass_bot.EEHomework import EEHomework
from eeclass_bot.EEMaterial import EEMaterial
from eeclass_bot.models.BlockMaterial import BlockMaterial


class EECourse:
    def __init__(self, bot, name: str, index: str):
        self.bot = bot
        self.name = name
        self.index = index
        self.url = EEConfig.get_index_url(EEConfig.COURSE_URL, index)
        self.bulletin_page_url = EEConfig.get_index_url(EEConfig.BULLETIN_URL, index)
        self.bulletins_url_list = [self.bulletin_page_url]
        self.bulletins: list[EEBulletin] = []
        self.homework_list_url = EEConfig.get_index_url(EEConfig.HOMEWORK_LIST, index)
        self.homeworks_url = []
        self.homeworks = []
        self.material_url = EEConfig.get_index_url(EEConfig.COURSE_URL, index)
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
            resp = await bot.session.get(url, headers=EEConfig.HEADERS)
            soup = BeautifulSoup(await resp.text(), 'lxml')
            result = soup.select("div > ul > li > div > div > div> div > div.fs-label > a")
            courses = [dict(name=r.text.strip(), index=r['href'].split('/')[-1]) for r in result]
            with open("course_info.json", 'w') as f:
                print(json.dumps(courses), file=f)

        courses_list = []
        for course in courses:
            courses_list.append(EECourse(bot, course['name'], course['index']))

        if check:
            for c in courses_list:
                print(c)

        return courses_list

    async def get_all_bulletin_page(self) -> list:
        async with self.bot.session.get(self.bulletin_page_url, headers=EEConfig.HEADERS) as resp:
            soup = BeautifulSoup(await resp.text(), 'lxml')
            b_list = soup.select(
                "#bulletinMgrTable > tbody > tr > td > div > div.fs-singleLineText.afterText > div.text-overflow > a"
            )
            # pagination = list(set(pagination))
            # if pagination:
            #     for p in pagination:
            # self.bulletins.append(self.bulletin_page_url + p)
            self.bulletins = [EEBulletin(bot=self.bot, link=p['data-url'], title=p['data-modal-title']) for p in b_list]
            return self.bulletins

    # async def get_all_bulletin_page(self):
    #     task = [Bulletin.get_bulletin_page(url=url, bot=self.bot) for url in self.bulletins_url_list]
    #     self.bulletins = await asyncio.gather(*task)
    #     return self.bulletins

    async def get_all_homework_page(self):
        """ homework 暫且不會有選頁面的問題"""
        async with self.bot.session.get(self.homework_list_url, headers=EEConfig.HEADERS) as resp:
            # print(self)
            soup = BeautifulSoup(await resp.text(), 'lxml')
            soup_select = soup.select("#homeworkListTable > tbody > tr > td > div > div > div.text-overflow > a")
            for homework in soup_select:
                url: str = homework['href']
                title: str = homework['title']
                self.homeworks.append(
                    EEHomework(
                        bot=self.bot,
                        title=title,
                        link=url,
                        course=self
                    )
                )
            return self.homeworks

    async def get_all_material_page(self):
        async with self.bot.session.get(self.material_url, headers=EEConfig.HEADERS) as resp:
            soup = BeautifulSoup(await resp.text(), 'lxml')
            material_block = soup.select(".fs-block-body > div > ol.xtree-list > li")
            for block in material_block:
                block_material_list = []
                block_title = block.select_one("div.header.hover.hover > div > span > div.text > div").text
                material_in_block = block.select("div.body > ol.xtree-list > li")
                for material in material_in_block:
                    if " ".join(material['class']) == "xtree-node type- clearfix":
                        type = EEConfig.CLASS_NAME_TO_MATERIAL_TYPE[' '.join(material.select_one(
                            "div.header.hover.hover > div.center-part > span.xtree-node-label > div.icon.pull-left > "
                            "span")['class'])]
                        link = material.select(
                            "div.header.hover.hover > div.center-part > span.xtree-node-label > div.text > div.node-title > div.fs-singleLineText > div")[
                            1].select_one('a')['href']
                        title = material.select(
                            "div.header.hover.hover > div.center-part > span.xtree-node-label > div.text > div.node-title > div.fs-singleLineText > div")[
                            1].select_one('a > span.text').text
                        brief_condition = material.select_one(
                            "div.header.hover.hover > div.center-part > div.hidden-xs.pull-right")
                        deadline = brief_condition.select("div.ext-col.fs-text-nowrap.col-time.text-center")[0].text
                        complete_condition = brief_condition.select_one(
                            "div.ext-col.fs-text-nowrap.col-char7.text-center").text
                        read_time = brief_condition.select_one(
                            "div.ext-col.fs-text-nowrap.col-char4.text-center > span").text if brief_condition.select_one(
                            "div.ext-col.fs-text-nowrap.col-char4.text-center > span") != None else brief_condition.select_one(
                            "div.ext-col.fs-text-nowrap.col-char4.text-center").text
                        complete_check = True if brief_condition.select("div.ext-col.fs-text-nowrap.col-time.text-center")[1].select_one("span.font-icon.fs-text-success.item-pass.fa.fa-check-circle") != None else False
                        block_material_list.append(
                            EEMaterial(
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
                self.materials.append(
                    BlockMaterial(
                        block_title=block_title,
                        materials=block_material_list
                    )
                )
            return self.materials
