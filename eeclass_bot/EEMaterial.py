import re

from bs4 import BeautifulSoup

from eeclass_bot.EEConfig import EEConfig
from eeclass_bot.models.Deadline import Deadline
from eeclass_bot.models.Material import Material


class EEMaterial:
    # BaseURL = "https://ncueeclass.ncu.edu.tw"

    def __init__(self, bot, title, link, course, type, deadline, complete_condition, read_time, complete_check) -> None:
        self.bot = bot
        self.url = EEConfig.get_index_url(EEConfig.BASE_URL, link)
        self.title = title
        self.course = course
        self.type = type
        self.deadline = deadline
        self.complete_condition = complete_condition
        self.read_time = read_time
        self.complete_check = complete_check
        self.details = None

    def __repr__(self) -> str:
        return f"{self.title}: {self.url}"

    async def retrieve(self) -> Material:
        async with self.bot.session.get(self.url, headers=EEConfig.HEADERS) as resp:
            soup = BeautifulSoup(await resp.text(), 'lxml')
            detail_str = soup.select_one("div.ext2.fs-hint")
            if detail_str is None:
                '''影片類型'''
                pass
            else:
                detail_str = detail_str.text
                exp = r"(\d+) 觀看數"
                views = re.search(pattern=exp, string=detail_str).group(1)
                exp = r"更新時間 (.+),"
                update_time = re.search(pattern=exp, string=detail_str).group(1)
                exp = r"by (.+)"
                announcer = re.search(pattern=exp, string=detail_str).group(1)

                online_links = soup.select("div.fs-block-body.list-margin > div > a")
                online_links = [link['href'] for link in online_links]
                attachments = soup.select("div.fs-list.fs-filelist > ul > li > div.text > a")
                attachments = [attachment['href'] for attachment in attachments]

            self.details = Material(
                title=self.title,
                ID=self.url.split('/')[-1],
                url=self.url,
                course=self.course.name,
                type='material',
                subtype=self.type,
                views=views,
                update_time=update_time,
                deadline=Deadline(
                    end=f"{self.deadline}"
                ),
                announcer=announcer,
                complete_condition=self.complete_condition,
                read_time=self.read_time,
                complete_check=self.complete_check
            )
            return self.details
            # video =  soup.select_one("div.fs-videoWrap") if soup.select_one("div.fs-videoWrap") != None else None
            # print(self.title, ":", video)

