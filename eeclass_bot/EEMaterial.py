import re

from NotionBot.object import NotionDate
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from eeclass_bot.EEChromeDriver import EEChromeDriver

from eeclass_bot.EEConfig import EEConfig

from eeclass_bot.models.Material import Material
from eeclass_bot.models.MaterialContent import MaterialContent


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
            soup = BeautifulSoup( await resp.text(), 'lxml')
            detail_str = soup.select_one("div.ext2.fs-hint")
            content, attachments, link = "", [], []
            update_time, views, announcer, video_view, video_url = "", "", "", "", ""
            if self.type == "video":
                '''影片類型'''
                detail_list = soup.select_one("div.module.mod_media.mod_media-detail").findAll("dd")
                update_time = detail_list[1].text
                views = detail_list[2].text
                announcer = detail_list[4].text

                driver = EEChromeDriver.get_driver()
                driver.get(self.url)
                video_view = driver.find_element(By.ID, "mediaBox").find_elements(By.TAG_NAME, "img")[1].get_attribute("src")
                video_url = driver.find_element(By.ID, "mediaBox").find_element(By.TAG_NAME, "video").get_attribute("src")
                # print(video_url, video_view)

            elif self.type in ["text", "pdf", "ppt"]:
                detail_str = detail_str.text
                exp = r"(\d+) 觀看數"
                views = re.search(pattern=exp, string=detail_str).group(1)
                exp = r"更新時間 (.+),"
                update_time = re.search(pattern=exp, string=detail_str).group(1)
                exp = r"by (.+)"
                announcer = re.search(pattern=exp, string=detail_str).group(1)

                link = []
                content_block = soup.select_one("div#xbox-inline")
                content = content_block.select_one("div.module.mod_mediaDoc.mod_mediaDoc-show")
                if content is not None:
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

            self.details = Material(
                title=self.title,
                id=self.url.split('/')[-1],
                url=self.url,
                course=self.course.name,
                material_type=self.type,
                views=views,
                update_time=update_time,
                deadline=NotionDate(
                    end=self.deadline if self.deadline != '-' else None
                ),
                announcer=announcer,
                complete_condition=self.complete_condition,
                read_time=self.read_time,
                complete_check=self.complete_check,
                content=MaterialContent(
                    content=content,
                    attachments=attachments,
                    link=link
                ),
                video_view=video_view,
                video_url=video_url
            )
            return self.details
