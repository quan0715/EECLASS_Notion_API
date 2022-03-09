
from PyNotion.NotionClient import Notion
import pandas as pd

AUTH = "secret_8JtNxNiUCCWPRhFqzl1e2juzxoz96dyjYWubDLbNchy"
notion = Notion(AUTH)
database = notion.fetch_databases("EECLASS")

d = database.query_database()
df = pd.DataFrame(d)
print(df.head())