from PyNotion.NotionClient import Notion
from PyNotion.object import *
from dotenv import load_dotenv
import os


def get_config():
    load_dotenv()
    NOTION_AUTH = os.getenv("NOTION_AUTH")
    notion_bot = Notion(NOTION_AUTH)
    db = notion_bot.fetch_databases("CONFIG")
    db_table = db.query_database_dataframe()
    table = {
         k: v for k, v in zip(db_table['KEY'], db_table['VALUE'])
    }
    return {
        "DATABASE_NAME": table['DATABASE_NAME'],
        "ACCOUNT": table['STUDENT_ID'],
        "PASSWORD": table['PASSWORD']
    }


if __name__ == "__main__":
    c = get_config()
    print(c)