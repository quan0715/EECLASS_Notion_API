import requests
from bs4 import BeautifulSoup
import re


class Bot:
    URL = "https://ncueeclass.ncu.edu.tw"
    YEAR = 2022
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Content-Length": "142",
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Cookie": "noteFontSize=100; noteExpand=0; defaultPlayer=html5; _ga_8E1C17R08X=GS1.1.1638244341.1.1.1638244589.0; _ga=GA1.3.802723757.1638244342; player.volume=1; PHPSESSID=4cufub5ft05u6ige0b1bjukq46; accesstoken=978662802; timezone=%2B0800; locale=zh-tw",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 Edg/97.0.1072.62",
    }

    def __init__(self):
        self.session = requests.Session()
        self.account = ""
        self.password = ""

    def login(self, account, password):
        self.account = account
        self.password = password
        data = {
            "_fmSubmit": "yes",
            "formId": "login_form",
            "account": f"{self.account}",
            "password": f"{self.password}"
        }
        url = Bot.URL + "/index/login"
        ## get csrf-t code
        result = self.session.get(url)
        Soup = BeautifulSoup(result.text, 'lxml')
        code = Soup.select("#csrf-t > div > input[type=hidden]")
        data['csrf-t'] = code[0]['value']
        result = self.session.post(url, data=data, headers=Bot.headers)
        if result.json()['ret']['status'] == 'true':
            print("帳號登入成功")
            return True
        else:
            print("登入資訊有誤")
            return False

    def get_latest_bulletins(self):
        print("正在抓取最近公告......")
        url = Bot.URL + "/dashboard/latestBulletin"
        result_list = []
        page_index = 1
        while True:
            print(f"page {page_index}")
            parameter = {
                "category": "all",
                "page": f"{page_index}",
                "pageSize": "20",
            }
            r = self.session.get(url, headers=Bot.headers, params=parameter)
            soup = BeautifulSoup(r.text, 'lxml')
            s = soup.select('#bulletinMgrTable > tbody > tr > td > div > div.fs-singleLineText.afterText > div.text-overflow > a')
            pattern = r"id=[0-9]+"
            title = soup.select('#bulletinMgrTable > tbody > tr > td.text-center.col-char7 > div > a > span')
            for j, t in zip(s, title):
                result_list.append({
                    'course': t.text,
                    "title": j['data-modal-title'],
                    'link': j['data-url'],
                    'index': re.search(pattern, j['data-url']).group().strip('id=')
                })
            if len(title) <= 20:
                break
            page_index += 1

        print("最近公告爬取完畢......")
        return result_list

    def get_bulletin_content(self, target):
        url = Bot.URL + target['link'] + "&fs_no_foot_js = 1"
        r = self.session.get(url, headers=Bot.headers)
        soup = BeautifulSoup(r.text, 'lxml')
        title = soup.select('div.modal-iframe-ext2')[0].text
        title = title.split(',')
        content = soup.select('div.fs-text-break-word')
        content = '\n'.join([c.text for c in content])
        attach = soup.select('div.text > a')
        attach = [{
            '名稱': a.text, '連結': "https://ncueeclass.ncu.edu.tw" + a['href'], '檔案大小': a.span.text
             } for a in attach
        ]
        result = {
            '類型': '公告',
            '連結': url,
            '標題': target['title'],
            '日期': {'start': f"{Bot.YEAR}-{title[1].strip('公告日期 ')}"},
            'ID': target['index'],
            '課程': title[2].strip(' '),
            '發佈人': title[3].strip(' by '),
            '內容': {'公告內容': content, '附件': attach},
            '人氣': title[0].split(' ')[1],
        }
        return result
