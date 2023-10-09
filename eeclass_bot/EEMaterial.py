import re

from bs4 import BeautifulSoup

from EEConfig import EEConfig


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

    def __repr__(self) -> str:
        return f"{self.title}: {self.url}"

    async def retrieve(self):
        async with self.bot.session.get(self.url, headers=EEConfig.HEADERS) as resp:
            soup = BeautifulSoup(await resp.text(), 'lxml')
            detail_str = soup.select_one("div.ext2.fs-hint")
            if detail_str == None:
                '''影片類型'''
                pass
            else:
                detail_str = detail_str.text
                exp = r"(\d+) 觀看數"
                views = re.search(pattern=exp, string=detail_str).group(1)
                exp = r"更新時間 (.+),"
                update_time = re.search(pattern=exp, string=detail_str).group(1)
                exp = r"by (.+)"
                uploader = re.search(pattern=exp, string=detail_str).group(1)

                online_links = soup.select("div.fs-block-body.list-margin > div > a")
                online_links = [link['href'] for link in online_links]
                attachments = soup.select("div.fs-list.fs-filelist > ul > li > div.text > a")
                attachments = [attachment['href'] for attachment in attachments]

            self.details = dict(
                title=self.title,
                ID=self.url.split('/')[-1],
                url=self.url,
                course=self.course.name,
                type='material',
                subtype=self.type,
                # 觀看數 = views,
                # 更新時間 = update_time,
                deadline={'end': f"{self.deadline}"},
                # 發佈者 = uploader,
                完成條件=self.complete_condition,
                完成度=self.read_time,
                已完成=self.complete_check
            )
            return self.details
            # video =  soup.select_one("div.fs-videoWrap") if soup.select_one("div.fs-videoWrap") != None else None
            # print(self.title, ":", video)

