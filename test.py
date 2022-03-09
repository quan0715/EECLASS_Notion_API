from PyNotion import *
import pandas as pd
from PyNotion.NotionClient import Notion

AUTH = "secret_8JtNxNiUCCWPRhFqzl1e2juzxoz96dyjYWubDLbNchy"
notion = Notion(AUTH)
d = notion.fetch_databases("記帳表")
df = pd.DataFrame(d.results)
with open("data.csv",'w') as c:
    df.to_csv(c)

print("hi")

