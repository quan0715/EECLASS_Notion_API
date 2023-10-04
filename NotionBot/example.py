from NotionClient import Notion


def main():
    notion = Notion(auth="secret_8JtNxNiUCCWPRhFqzl1e2juzxoz96dyjYWubDLbNchy")
    # get notion user (for private)
    r = notion.get_user()
    # print(r)
    page_id = notion.search("Weakly Plan")['results'][0]['id']
    print(page_id)
    print(notion.search("XXX"))


if __name__ == "__main__":
    main()
