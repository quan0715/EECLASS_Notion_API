# EECLASS_Notion_API
### 創作動機與功能
自己本身是Notion的使用者，並會在Notion上打理生活的大小事，同時身為一位大學生，EECLASS (本校的課務系統) 也會通知我課程相關的瑣事（考試、作業、重要通知）

為了方便我自己整理，於是使用之前開發到一半的 [Notion_API](https://github.com/quan0715/PyNotion) 串連EECLASS系統，將EECLASS裏面的最新公告、以及最新事件(作業)，都一並存到Notion上面做紀錄 

### 下載後步驟
因為不方便公布自己的EECLASS帳號，下載後麻煩幫我打開，`run.py` 並且修改 `Notion_AUTH`,`ACCOUNT`,`PASSWORD`,`DATABASE_NAME`

```python3
NOTION_AUTH = "NOTION BOT 驗證碼"
ACCOUNT = "EECLASS的帳號"
PASSWORD = "EECLASS的密碼"
DATABASE_NAME = "Database的名稱"
```
### Notion串接
1. 申請 [Notion](https://www.notion.so/) 帳號（學生帳號可以免費升級） 
2. Create an integration（詳細請參考[此網站](https://developers.notion.com/docs/getting-started) ）
3. 將你的 integration 加入你的workspace，且將`Notion_AUTH` 裡的內容換成你自己的 token
4. 建立 DataBase 模板我自己的模板是[這個](https://plump-part-2d6.notion.site/e0353619b2774024a530e68b208b5820) 
   1. 標題、課程、類型、日期是必須要有的，其他的可以自由新增，方便做參考

### Python模組安裝
如果本身沒使用過爬蟲套件，可以用 pip 安裝

    pip install requests
    pip install beautifulsoup4