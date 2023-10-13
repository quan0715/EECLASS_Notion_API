from AsyncBot import *
from async_run import *
from asyncio import futures
import pytest
from unittest import mock
from NotionBot.base import Database
from unittest.mock import AsyncMock
# from asynctest import CoroutineMock

# @pytest.mark.asyncio_cooperative
# async def test_login():
#     '''登入測試'''
#     load_dotenv()
#     account = [os.getenv("ACCOUNT"), os.getenv("ACCOUNT")]
#     password = [os.getenv("PASSWORD"), os.getenv("PASSWORD")+"a"]
#     async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False), cookie_jar=aiohttp.CookieJar(unsafe=True, quote_cookie=True)) as session:
#         bot = Bot(session, account[0], password[0])
#         assert await bot.login() == True
#     async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False), cookie_jar=aiohttp.CookieJar(unsafe=True, quote_cookie=True)) as session:
#         bot = Bot(session, account[1], password[1])
#         assert await bot.login() == False

# @pytest.mark.asyncio_cooperative
# async def test_course_retrieve_all():
#     '''檢查是否產生課程json'''
#     account = os.getenv("ACCOUNT")
#     password = os.getenv("PASSWORD")
#     async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False), cookie_jar=aiohttp.CookieJar(unsafe=True, quote_cookie=True)) as session:
#         bot = Bot(session, account, password)
#         await bot.retrieve_all_course(refresh=True, check=True)
#     assert os.path.isfile("course_info.json") == True

# @pytest.mark.asyncio_cooperative
# @mock.patch.object(Bot, "retrieve_all_materials_details", return_value = [])
# async def test_fetch_all_eeclass_data(mock_material):
#     '''eeclass爬蟲全測試'''
#     account = os.getenv("ACCOUNT")
#     password = os.getenv("PASSWORD")
#     all_bulletins_detail, all_homework_detail, all_material_detail = await fetch_all_eeclass_data(account, password)
#     assert isinstance(all_bulletins_detail, list) == True
#     assert isinstance(all_homework_detail, list) == True
#     assert isinstance(all_material_detail, list) == True

# def test_get_database():
#     '''檢查Notion資料庫連接'''
#     load_dotenv()
#     auth = os.getenv("NOTION_AUTH")
#     database_id = os.getenv("DATABASE")
#     notion_bot = Notion(auth)
#     assert isinstance(notion_bot.get_database(database_id), Database) == True
#     assert isinstance(notion_bot.get_database(database_id+'a'), Database) == False
#     notion_bot = Notion(auth+'a')
#     assert isinstance(notion_bot.get_database(database_id), Database) == False

@pytest.mark.asyncio
@mock.patch("NotionBot.base.Database.async_post")
@mock.patch("NotionBot.base.Database")
@mock.patch("async_run.get_id_col", return_value=["87232"])
async def test_update_all_bulletin_info_to_notion_db(mock_get_id_col, mock_db, mock_post):
    bulletins = [{'type': '公告', 'url': 'https://ncueeclass.ncu.edu.tw/bulletin/content/?id=87232&pageId=course.21793&_lock=id%2CpageId&ajaxAuth=388728611f3bd1cb5bc5418a8eea316b', 'title': '分組囉', 'date': {'start': '2023-10-02'}, 'ID': '87232', 'course': '電腦攻擊與防禦 The Attack and Defense of Computers', '發佈人': '羅傳郡', 'content': {'公告內容': '各位有修課的同學們大家好：\n\n這堂課預計會做兩次小project,都是三人為一組,可以自行找組員加入,可以在eeclass中的組員選單中加入你們分好的隊伍中\n\n感謝你們,\n羅傳郡', '附件': [], '連結': []}, '人氣': '370'}, {'type': '公告', 'url': 'https://ncueeclass.ncu.edu.tw/bulletin/content/?id=87855&pageId=course.23712&_lock=id%2CpageId&ajaxAuth=3ef9c6f86c9051ac570814c6fac9feb8', 'title': 'Week4 lab3 補交相關事項', 'date': {'start': '2023-10-09'}, 'ID': '87855', 'course': '軟體工程實務 Software engineering practices', '發佈人': '沈廷勳', 'content': {'公告內容': '助教已經將各位的學習狀況以及建議看完了,首先謝謝各位同學耐心的提供看法,這些建議我也整理完並告訴老師了,老師可能會依據這些建議想一下如何重新安排lab3的課程。\n\n關於補交的部分,請同學於10/15 23:59前上傳,成績將會乘上75%(如果全對,該題即為75分),若未上傳者,將以0分計算。', '附件': [], '連結': []}, '人氣': '31'}]
    mock_db_instance = mock_db.return_value
    # mockresponse = CoroutineMock()
    # mockresponse.status = 200
    # mock_post.return_value = asyncio.Future()
    upload = await update_all_bulletin_info_to_notion_db(bulletins, mock_db_instance)
    assert upload == ['upload bulletin : Week4 lab3 補交相關事項 to bulletin database']

# @pytest.mark.asyncio
# @mock.patch("async_run.get_id_col", return_value=["32433"])
# @mock.patch("NotionBot.base.Database")
# async def test_update_all_homework_info_to_notion_db(mock_db, mock_get_id_col):
#     homeworks = [{'title': 'Homework 1: Debugging', 'url': 'https://ncueeclass.ncu.edu.tw/course/homework/32523', 'course': '軟體工程實務 Software engineering practices', 'course_link': 'https://ncueeclass.ncu.edu.tw/course/23712', 'date': {'start': '2023-09-11 00:00', 'end': '2023-09-18 00:00'}, 'content': {'類型': '個人作業', '開放繳交': '2023-09-11 00:00', '繳交期限': '2023-09-18 00:00', '已繳交': '122人', '允許遲交': '否', '成績比重': '0%', '評分方式': '直接打分數', '說明': '\n請繳交整個 eclipse 的專案檔\n檔名 : HW1_學號.zip\n以及一份 report，清楚的條列出你找到的 bug，並指出程式碼的錯誤處、原因和改正的程式碼\n檔名 : HW1_學號.pdf\n\xa0\n不開放遲交！！\n', '附件': '', 'attach': [{'title': '1.\n\ndebug AVL english.docx (18.5 KB)', 'link': 'https://ncueeclass.ncu.edu.tw/filedownload/1301909'}, {'title': '2.\n\ndebug AVL tree.docx (20.3 KB)', 'link': 'https://ncueeclass.ncu.edu.tw/filedownload/1301910'}, {'title': '3.\n\nAVLtree-incorrect.java (7.8 KB)', 'link': 'https://ncueeclass.ncu.edu.tw/filedownload/1301911'}], 'link': []}, 'type': 'homework', 'ID': '32523'}, {'title': 'Lab-1: system test (Jenkins)', 'url': 'https://ncueeclass.ncu.edu.tw/course/homework/32433', 'course': '軟體工程實務 Software engineering practices', 'course_link': 'https://ncueeclass.ncu.edu.tw/course/23712', 'date': {'start': '2023-09-18 00:00', 'end': '2023-09-19 23:30'}, 'content': {'類型': '個人作業', '開放繳交': '2023-09-18 00:00', '繳交期限': '2023-09-19 23:30', '已繳交': '121人', '允許遲交': '否', '成績比重': '4%', '評分方式': '直接打分數', '說明': '閱讀jenkins教學，並截圖指定的主控台輸出。', '附件': '', 'attach': [{'title': '1.\n\nLab 1-Jenkins-教學.pptx (1.7 MB)', 'link': 'https://ncueeclass.ncu.edu.tw/filedownload/1300112'}, {'title': '2.\n\nlab1_sample_output.png (41.3 KB)', 'link': 'https://ncueeclass.ncu.edu.tw/filedownload/1300113'}], 'link': []}, 'type': 'homework', 'ID': '32433'}]
#     mock_db_instance = mock_db.return_value
#     with mock.patch("async_run.builtin_in_notion_template", return_value=BaseObject()) as mock_template:
#         upload = await update_all_homework_info_to_notion_db(homeworks, mock_db_instance)
#         assert upload == ['upload homework : Homework 1: Debugging to homework database']
