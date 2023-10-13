import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

from eeclass_bot.EEConfig import EEConfig
from eeclass_bot.models.Deadline import Deadline
from eeclass_bot.models.Material import Material

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
                announcer = re.search(pattern=exp, string=detail_str).group(1)

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
