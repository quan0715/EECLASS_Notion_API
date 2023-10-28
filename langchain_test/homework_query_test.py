from NotionBot import *
from NotionBot.base.Database import *

import datetime
import os
from datetime import datetime, timezone, timedelta, date
from dotenv import load_dotenv

load_dotenv()
auth = os.getenv("NOTION_AUTH")
notion_bot = Notion(auth)
homework_db: Database = notion_bot.get_database(os.getenv("HOMEWORK_DB"))
now = datetime.strptime(datetime.now(tz=timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M"), "%Y-%m-%d %H:%M")
# for h in homework_db.query():
#     if object_index is not None:
#         page = homework_db.bot.get_page(homework_db.query(
#             query=Query(
#                 filters=PropertyFilter(
#                     prop="ID",
#                     filter_type=Text.Type.rich_text,
#                     condition=Text.Filter.equals,
#                     target=h['id']
#                 )
#             )
#         )[0]['id'])
#         print(page.retrieve_children())
for h in homework_db.query():
    homework_title = h['properties']
    print(h['id'])