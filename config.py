from PyNotion.NotionClient import Notion
from PyNotion.block import *
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
        "PASSWORD": table['PASSWORD'],
        "CONFIG_BLOCK_ID": table['CONFIG_BLOCK_ID']
    }

def get_config_block(block_id):
    load_dotenv()
    NOTION_AUTH = os.getenv("NOTION_AUTH")
    notion_bot = Notion(NOTION_AUTH)
    config_block = Block(bot=notion_bot, block_id=block_id)
    print(config_block.retrieve())
    code_block = CodeBlock()
    #print(code_block.make())
    config_block.update(code_block.make())

if __name__ == "__main__":
    c = get_config()
    get_config_block(c['CONFIG_BLOCK_ID'])