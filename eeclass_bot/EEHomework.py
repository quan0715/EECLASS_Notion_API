from NotionBot.object import NotionDate
from bs4 import BeautifulSoup
import re

from eeclass_bot.EEConfig import EEConfig
from eeclass_bot.models.Homework import Homework


class EEHomework:
    def __init__(self, bot, title, link, course):
        self.bot = bot
        self.title = title
        self.index = link.split('/')[-1]
        self.course = course
        self.url = EEConfig.get_index_url(EEConfig.HOMEWORK_URL, self.index)
        self.details = None

    def __repr__(self):
        return f"{self.course.name} : {self.title}"

    async def retrieve(self) -> Homework:
        async with self.bot.session.get(self.url, headers=EEConfig.HEADERS) as resp:
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
                            {"title": li.text.strip(), "link": EEConfig.BASE_URL + li.find('a')['href']}
                        )
                    continue

                for link in c.findAll('a'):
                    try:
                        results['link'].append({"title": link.text.strip(), "link": link['href']})
                    except KeyError:
                        continue
                results[t.text] = c.text

            homework_type = results['類型']
            try:
                description_content = results['說明']
            except:
                description_content = ""
            exp = r"(\d+)人"
            submission_status = soup.select_one("div.text-center.fs-margin-default > a > span").text
            submission_number = re.search(pattern=exp, string=results['已繳交']).group(1)

            self.details = Homework(
                title=self.title,
                url=self.url,
                course=self.course.name,
                course_link=self.course.url,
                deadline=NotionDate(
                    start=results['開放繳交'],
                    end=results['繳交期限']
                ),
                content=results,
                id=self.index,
                homework_type=homework_type,
                description_content=description_content,
                submission_status=submission_status,
                submission_number=int(submission_number)
            )
            print(f"EECLASS BOT (fetch) : {self.title}")
            return self.details
