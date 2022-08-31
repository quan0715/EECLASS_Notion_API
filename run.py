from bot import Bot
import threading
from PyNotion import *
from PyNotion.NotionClient import Notion
import os
from dotenv import load_dotenv
load_dotenv()

NOTION_AUTH = os.getenv("NOTION_AUTH")
ACCOUNT = os.getenv("ACCOUNT")
PASSWORD = os.getenv("PASSWORD")
DATABASE_NAME = os.getenv("DATABASE_NAME")

# notion_bot = Notion(NOTION_AUTH)
# eeclass_db = notion_bot.fetch_databases(DATABASE_NAME)
eeclass_bot = Bot()
eeclass_bot.login(ACCOUNT, PASSWORD)
courses = eeclass_bot.retrieve_all_course(refresh=True, check=True)
# courses[7].get_bulletin()

#print(eeclass_bot.get_latest_bulletins())
#eeclass_bot.set_emoji("💩")  #可以自行修改


# t1 = threading.Thread(target=lambda: b.update_bulletin())  # 更新最新公告上去
# t2 = threading.Thread(target=lambda: b.update_events())  # 更新最新事件上去
# t1.start()
# t2.start()
# t1.join()
# t2.join()
