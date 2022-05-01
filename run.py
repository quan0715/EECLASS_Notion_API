from bot import Bot
import threading

NOTION_AUTH = "Notion_integration_token"
ACCOUNT = "EECLASS的帳號"
PASSWORD = "EECLASS的密碼"
DATABASE_NAME = "Database名稱"

b = Bot()
b.set_emoji("💩") #可以自行修改
b.login(ACCOUNT, PASSWORD)  # 登入
b.connect_notion_database(NOTION_AUTH, DATABASE_NAME)  # 連線Notion資料庫

t1 = threading.Thread(target= lambda : b.update_bulletin())
t2 = threading.Thread(target= lambda : b.update_events())
t1.start()
t2.start()
t1.join()
t2.join()
