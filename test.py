import threading
from PyNotion.NotionClient import Notion
NOTION_AUTH = "secret_8JtNxNiUCCWPRhFqzl1e2juzxoz96dyjYWubDLbNchy"
#ACCOUNT = "109502563"
#PASSWORD = "H125920690"
DATABASE_NAME = "EECLASS"
test = Notion(auth=NOTION_AUTH)
db = test.fetch_databases(DATABASE_NAME)
#print(db.results[0].retrieve_page())
# pl = db.query_database_dataframe(query={
#     "filter": {
#         "property": "課程",
#         "select": {"equals": "程式語言 Principles of Programming Languages"}
#     }
# })
import pandas as pd
#print(pl)
print(pd.DataFrame(db.query_database_dataframe()))


#print(len(db.results['ID']))
#print(index)
#print(sorted(index),len(index))
#b = Bot()
#b.set_emoji("💩") #可以自行修改
#b.login(ACCOUNT, PASSWORD)  # 登入EECLASS
#b.connect_notion_database(NOTION_AUTH, DATABASE_NAME)  # 連線Notion資料庫
#t1 = threading.Thread(target= lambda : b.update_bulletin()) # 更新最新公告上去
#t2 = threading.Thread(target= lambda : b.update_events()) # 更新最新事件上去
#t1.start()
#t2.start()
#t1.join()

