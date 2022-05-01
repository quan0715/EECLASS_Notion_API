from bot import Bot
import threading

NOTION_AUTH = "secret_8JtNxNiUCCWPRhFqzl1e2juzxoz96dyjYWubDLbNchy"
ACCOUNT = "EECLASS的帳號"
PASSWORD = "EECLASS的密碼"
DATABASE_NAME = "TEST"

b = Bot()
b.set_emoji("💩") #可以自行修改
b.login(ACCOUNT, PASSWORD)  # 登入EECLASS
b.connect_notion_database(NOTION_AUTH, DATABASE_NAME)  # 連線Notion資料庫

t1 = threading.Thread(target= lambda : b.update_bulletin()) # 更新最新公告上去
t2 = threading.Thread(target= lambda : b.update_events()) # 更新最新事件上去
t1.start()
t2.start()
t1.join()
t2.join()
