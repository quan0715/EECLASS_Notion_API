from PyNotion.Object import *
from PyNotion.NotionClient import Notion
import requests
from bs4 import BeautifulSoup
import re
import threading


## EECLASS and Notion update Bot
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
        self.all_bulletins = []
        self.notion = None
        self.database = None
        self.issue_id = []
        self.emoji = ""

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
            print("歡迎 109502563 同學登入")
            return True
        else:
            print("登入資訊有誤")
            return False

    def connect_notion_database(self, auth, database_name):
        try:
            # print("正在和Notion做連線")
            self.notion = Notion(auth)
            self.database = self.notion.fetch_databases(database_name)
            self.issue_id = self.database.query_database_dataframe()['ID']  # 已經update的事件ID
            # print(f"成功連線到 {database_name} Notion資料庫")

        except:
            print("資訊有誤請重新嘗試")

    def get_page_url(self, url):
        r = self.session.get(Bot.URL + url, headers=Bot.headers)
        soup = BeautifulSoup(r.text, 'lxml')
        s = soup.select('div > nav > ul > li')
        page_list = [p.text for p in s if p.text != "<" and p.text != ">"]
        # print(page_list)
        # print("總爬取頁數",len(page_list))
        return page_list

    def get_latest_bulletins(self):
        print("正在抓取最新公告......")
        url = "/dashboard/latestBulletin"
        page_list = self.get_page_url(url)
        result_list = []
        def scrapy_page(page_index):
            parameter = {
                "category": "all",
                "condition":"",
                "page": page_index,
                "pageSize": "20",
            }
            r = self.session.get(Bot.URL + url, headers=Bot.headers, params=parameter)
            soup = BeautifulSoup(r.text, 'lxml')
            s = soup.select('#bulletinMgrTable > tbody > tr > td > div > div.fs-singleLineText.afterText > div.text-overflow > a')
            pattern = r"id=[0-9]+"
            title = soup.select('#bulletinMgrTable > tbody > tr > td.text-center.col-char7 > div > a > span')
            for j, t in zip(s, title):
                #print("獲取 : ", j['data-modal-title'], t.text, "頁數", page_index)
                result_list.append({
                    'course': t.text,
                    "title": j['data-modal-title'],
                    'link': j['data-url'],
                    'index': re.search(pattern, j['data-url']).group().strip('id=')
                })

        threadings = []
        for p in page_list:
            #scrapy_page(p)
            t = threading.Thread(target=scrapy_page, args=(p,))
            t.start()
            threadings.append(t)
        for t in threadings:
            t.join()

        print("最新公告爬取完畢......")
        return result_list

    def get_bulletin_content(self, target):
        url = Bot.URL + target['link'] + "&fs_no_foot_js = 1"
        r = self.session.get(url, headers=Bot.headers)
        soup = BeautifulSoup(r.text, 'lxml')
        title = soup.select('div.modal-iframe-ext2')[0].text
        title = title.split(',')
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
        attach = [{ '名稱': a.text, '連結': "https://ncueeclass.ncu.edu.tw" + a['href'], '檔案大小': a.span.text} for a in attach ]
        result = {
            '類型': '公告',
            '連結': url,
            '標題': target['title'],
            '日期': {'start': f"{Bot.YEAR}-{title[1].strip('公告日期 ')}"},
            'ID': target['index'],
            '課程': title[2].strip(' '),
            '發佈人': title[3].strip(' by '),
            '內容': {'公告內容': content, '附件': attach,'連結':link},
            '人氣': title[0].split(' ')[1],
        }
        return result

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

    @classmethod
    def make_template(cls, content):
        children_list = []
        for k, v in content.items():
            children_list.append(Blocks.Heading(3, Blocks.Text(content=k)))
            if k != '附件' and k != '連結':
                words = [v[s:s + 1999] for s in range(0, len(v), 1999)]
                text_list = [Blocks.Text(content=w) for w in words]
                children_list.append(Blocks.Paragraph(*text_list))
            else:
                children_list.extend([Blocks.Paragraph(Blocks.Text(f"{a['名稱']}", a['連結'])) for a in v])

        return ChildrenObject(*children_list)

    def post(self, content):
        keys = self.database.properties.keys()
        p = {k : content[k] for k in keys if k in content.keys()}
        new_post = self.notion.create_new_page(database=self.database, data=p)
        if new_post:
            new_post.update_emoji(self.emoji)
            new_post.append_children(data=Bot.make_template(content['內容']))

    def update(self, content,index):
        page = self.database.query_database_page_list(
            query=Query(
                filters=PropertyFilter("ID",Text.Type.rich_text,Text.Filter.contains,index)
            )
        )[0]
        keys = self.database.properties.keys()
        data = {k: content[k] for k in keys if k in content.keys()}
        #print(data)
        page.update(self.database.post_template(data))
        page.update_emoji(self.emoji)
        page.append_children(data=self.make_template(content['內容']))


    def set_emoji(self, emoji):
        self.emoji = emoji
