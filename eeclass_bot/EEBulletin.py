import re

from NotionBot.object import NotionDate
from bs4 import BeautifulSoup

from eeclass_bot.EEConfig import EEConfig
from eeclass_bot.models.Bulletin import Bulletin
from eeclass_bot.models.BulletinContent import BulletinContent


class EEBulletin:
    exp = r"id=([0-9]+)&"

    def __init__(self, bot, link, title):
        self.bot = bot
        self.link = link
        self.title = title
        self.index = re.search(pattern=self.exp, string=self.link).group(1)
        self.url = EEConfig.get_index_url(EEConfig.BASE_URL, link)
        self.details = None

    def __repr__(self):
        return f"{self.title}"

    async def retrieve(self) -> Bulletin:
        async with self.bot.session.get(self.url, headers=EEConfig.HEADERS) as resp:
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
            result = Bulletin(
                url=self.url,
                title=self.title,
                announced_date=NotionDate(
                    start=f"{date}"
                ),
                id=self.index,
                course=detail[2].strip(' '),
                announcer=detail[3].strip(' by '),
                content=BulletinContent(
                    content=content,
                    attach=attach,
                    link=link,
                ),
                popularity=detail[0].split(' ')[1],
            )
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