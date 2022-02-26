from PyNotion.block import *
from PyNotion.object import BlockObject
from PyNotion.NotionClient import Notion
import requests
from bs4 import BeautifulSoup
import re

YEAR = 2022
url = "https://ncueeclass.ncu.edu.tw"
headers = {
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Accept-Encoding": "gzip, deflate, br",
    #"Connection": "keep-alive",
    "Content-Length": "142",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Cookie": "noteFontSize=100; noteExpand=0; defaultPlayer=html5; _ga_8E1C17R08X=GS1.1.1638244341.1.1.1638244589.0; _ga=GA1.3.802723757.1638244342; player.volume=1; PHPSESSID=4cufub5ft05u6ige0b1bjukq46; accesstoken=978662802; timezone=%2B0800; locale=zh-tw",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36 Edg/97.0.1072.62",
}



def login(session):
    p = {
        "_fmSubmit": "yes",
        "formId": "login_form",
        "account": "109502563",
        "password": "H125920690",
    }
    url = "https://ncueeclass.ncu.edu.tw/index/login"
    result = session.get(url)
    Soup = BeautifulSoup(result.text, 'lxml')
    soup = Soup.select("#csrf-t > div > input[type=hidden]")
    p['csrf-t'] = soup[0]['value']
    result = s.post(url, data=p, headers=headers)
    print(result)


def get_all_courses(session):
    url = "https://ncueeclass.ncu.edu.tw"
    dashboard_url = "https://ncueeclass.ncu.edu.tw/dashboard"
    r = session.get(dashboard_url, headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')
    selects = soup.select('#xbox2-inline > div.module.app-dashboard.app-dashboard-show > div > div.fs-block-body > div > ul > li > div > div > div > div > div.fs-label > a')
    results = [{
        'title': i.text.strip('\n').strip(' ').strip('\n'),
        'link': url + i['href'],
        'id': i['href'].strip('/course/')
    } for i in selects]
    return results


def get_bulletins(session, target):
    url = f"https://ncueeclass.ncu.edu.tw/course/bulletin/{target['id']}"
    result_list = []
    for page_index in range(1, 3):
        parmas = {
            "category": "all",
            "page": f"{page_index}",
            "pageSize": "20",
        }
        r = session.get(url, headers=headers, params=parmas)
        soup = BeautifulSoup(r.text, 'lxml')
        soup = soup.select(
            '#bulletinMgrTable > tbody > tr > td > div > div.fs-singleLineText.afterText > div.text-overflow > a')
        pattern = r"id=[0-9]+"
        for j in soup:
            result_list.append({
                'course': target['title'],
                "title": j['data-modal-title'],
                'link': j['data-url'],
                'index': re.search(pattern, j['data-url']).group().strip('id=')
            })

    return result_list


def make_template(content):
    template = []
    def check_length(word):
        if len(word) > 2000:
            for t in [word[c:c + 1999] for c in range(0, len(word), 1999)]:
                template.append(BlockObject("paragraph", traces=dict(content=t)).template)
        else:
            template.append(BlockObject("paragraph", traces=dict(content=word)).template, )

    for k, v in content.items():
        if k != '附件':
            template.append(BlockObject("heading_3", traces=dict(content=k)).template, )
            check_length(v)
        else:
            template.append(BlockObject("heading_3", traces=dict(content=k)).template, )
            for a in v:
                template.append(
                    BlockObject("paragraph", traces=dict(content=f"{a['名稱']}", link=a['連結'])).template, )
    return template


def post(content, database):
    keys = database.properties.keys()
    p = {}
    for k in keys:
        try:
            p[k] = content[k]
        except:
            print(f"property {k} dose not defined")
    new_post = notion.create_new_page(database=database, data=p)
    print(new_post)
    #print(p.json())
    if new_post:
        new_post.update_page({
            "icon": {"type": "emoji","emoji": "🐶"},
        })
        new_post.append_block(children_array=make_template(content['內容']))


def get_latest_events(session):
    url = "https://ncueeclass.ncu.edu.tw/dashboard/latestEvent"
    result_list = []
    for page_index in range(1, 3):
        parmas = {
            "category": "all",
            "page": f"{page_index}",
            "pageSize": "20",
        }
        r = session.get(url, headers=headers, params=parmas)
        soup = BeautifulSoup(r.text, 'lxml')
        s = soup.select('#recentEventTable > tbody > tr ')
        pattern = r"id=[0-9]+"
        # print(s)
        result_list.extend(s)
    results = []
    for row in result_list:
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
    return results


def get_latest_bulletins(session):
    url = "https://ncueeclass.ncu.edu.tw/dashboard/latestBulletin"
    result_list = []
    for page_index in range(1, 3):
        parmas = {
            "category": "all",
            "page": f"{page_index}",
            "pageSize": "20",
        }
        r = session.get(url, headers=headers, params=parmas)
        soup = BeautifulSoup(r.text, 'lxml')
        s = soup.select(
            '#bulletinMgrTable > tbody > tr > td > div > div.fs-singleLineText.afterText > div.text-overflow > a')
        pattern = r"id=[0-9]+"
        title = soup.select('#bulletinMgrTable > tbody > tr > td.text-center.col-char7 > div > a > span')
        for j, t in zip(s, title):
            result_list.append({
                'course': t.text,
                "title": j['data-modal-title'],
                'link': j['data-url'],
                'index': re.search(pattern, j['data-url']).group().strip('id=')
            })
    return result_list


def get_bulletin_content(session, target):
    url = "https://ncueeclass.ncu.edu.tw" + target['link'] + "&fs_no_foot_js = 1"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')
    title = soup.select('div.modal-iframe-ext2')[0].text
    title = title.split(',')
    content = soup.select('div.fs-text-break-word')
    content = '\n'.join([c.text for c in content])
    attach = soup.select('div.text > a')
    attach = [{'名稱': a.text, '連結': "https://ncueeclass.ncu.edu.tw" + a['href'], '檔案大小': a.span.text} for a in attach]
    result = {
        '類型': '公告',
        '連結': url,
        '標題': target['title'],
        '日期': {'start': f"{YEAR}-{title[1].strip('公告日期 ')}"},
        'ID': target['index'],
        '課程': title[2].strip(' '),
        '發佈人': title[3].strip(' by '),
        '內容': {'公告內容': content, '附件': attach},
        '人氣': title[0].split(' ')[1],
    }
    return result


def get_homework_content(session, homework):
    r = session.get(homework['連結'], headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')
    dl = soup.select("dl")
    title = dl[0].findAll('dt')
    content = dl[0].findAll('dd')
    results = {}
    for t, c in zip(title, content):
        if t.text == '附件':
            results[t.text] = []
            for ul in c.findAll('ul'):
                results[t.text].append(
                    {"名稱": ul.text, "連結": "https://ncueeclass.ncu.edu.tw" + ul.find('a')['href']})
        else:
            results[t.text] = c.text
    homework['內容'] = results
    homework['日期'] = {'start': results['開放繳交'], 'end': results['繳交期限']}
    return homework


def update_bulletins(session):
    latest_bulletins = get_latest_bulletins(session=session)
    # print(latest_bulletins)
    import threading
    threadings = []

    def all_issue(b):
        r = get_bulletin_content(s, b)
        if r['ID'] not in issue_id:
            print(f'更新事件:{r["標題"]}')
            post(r, database)

    for b in latest_bulletins:
        threadings.append(threading.Thread(target=all_issue, args=(b,)))
        threadings[-1].start()
    for t in threadings:
        t.join()


def update_events(session):
    def all_events(h):
        result = get_homework_content(session=s, homework=h)
        post(result, database)

    r = get_latest_events(s)
    import threading
    threadings = []
    for h in r:
        if h['類型'] == '作業' and h['ID'] not in issue_id:
            print(f'更新事件:{ h["標題"]}')
            threadings.append(threading.Thread(target=all_events, args=(h,)))
            threadings[-1].start()

    for t in threadings:
        t.join()


def get_questionnaire_contents(session, questionnaire):
    pass


AUTH = "secret_8JtNxNiUCCWPRhFqzl1e2juzxoz96dyjYWubDLbNchy"
notion = Notion(AUTH)
database = notion.fetch_databases("EECLASS")
issue_id = [r['properties']['ID']['rich_text'][0]['plain_text'] for r in database.results]  # print(issue_id)
# print(issue_id)
s = requests.Session()
login(s)
import threading
b = threading.Thread(target=update_bulletins, args=(s,))
e = threading.Thread(target=update_events, args=(s,))
b.start()
e.start()
b.join()
e.join()
