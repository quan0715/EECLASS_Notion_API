import asyncio
import json
from typing import List

from bs4 import BeautifulSoup

from eeclass_bot.EEChromeDriver import EEChromeDriver
from eeclass_bot.EEConfig import EEConfig
from eeclass_bot.EECourse import EECourse
from eeclass_bot.EEHomework import EEHomework
from eeclass_bot.EEBulletin import EEBulletin
from eeclass_bot.EEMaterial import EEMaterial


class EEAsyncBot:
    def __init__(self, session, account, password):
        self.session = session
        self.account = account
        self.password = password
        self.courses_list: List[EECourse] = []
        self.bulletins_list: List[EEBulletin] = []
        self.homeworks_list: List[EEHomework] = []
        self.material_list: List[EEMaterial] = []
        self.bulletins_detail_list: list = []
        self.homeworks_detail_list: list = []
        self.materials_detail_list: list = []

    def _generate_login_data(self, account: str, password: str, csrf_t_code: str):
        return {
            "_fmSubmit": "yes",
            "formVer": "3.0",
            "formId": "login_form",
            "next": "/",
            "act": "keep",
            "account": account,
            "password": password,
            'csrf-t': csrf_t_code
        }

    async def find_csrf_t_code(self):
        resp = await self.session.get(EEConfig.BASE_URL, headers=EEConfig.HEADERS)
        soup = BeautifulSoup(await resp.text(), 'lxml')
        code = soup.select("#csrf-t > div > input[type=hidden]")
        # TODO: check if code is empty
        return code[0]['value']

    async def login(self):
        code = await self.find_csrf_t_code()
        print("login ......")
        login_data = self._generate_login_data(account=self.account, password=self.password, csrf_t_code=code)
        r = await self.session.post(EEConfig.LOGIN_URL, data=login_data)
        result = await r.text()
        result = json.loads(result)
        if result['ret']['status'] == 'true':
            print(f"login successfully\nwelcome {self.account}")
            return True
        else:
            print("wrong password or username")
            return False

    async def pipline(self):
        await self.retrieve_all_course(check=False, refresh=False)
        # await self.retrieve_all_bulletins()
        # await self.retrieve_all_bulletins_details()
        await self.retrieve_all_homeworks()
        await self.retrieve_all_homeworks_details()
        # await self.retrieve_all_material()
        # await self.retrieve_all_materials_details()
        EEChromeDriver.close_driver()

    async def retrieve_all_course(self, refresh: bool = False, check: bool = False):
        self.courses_list = await EECourse.retrieve_all(self, refresh, check)
        return self.courses_list

    async def retrieve_all_bulletins(self):
        tasks = [r.get_all_bulletin_page() for r in self.courses_list]
        course_bulletins_list = await asyncio.gather(*tasks)
        self.bulletins_list = []
        for cb in course_bulletins_list:
            self.bulletins_list.extend(cb)
        return self.bulletins_list

    async def retrieve_all_homeworks(self):
        tasks = [r.get_all_homework_page() for r in self.courses_list]
        course_homework_list = await asyncio.gather(*tasks)
        self.homeworks_list = []
        for ch in course_homework_list:
            self.homeworks_list.extend(ch)
        return self.homeworks_list

    async def retrieve_all_material(self):
        tasks = [r.get_all_material_page() for r in self.courses_list]
        course_material_list = await asyncio.gather(*tasks)
        self.material_list = []
        for course in course_material_list:
            for block in course:
                self.material_list.extend(block.materials)
        return self.material_list
    
    async def retrieve_all_bulletins_details(self):
        tasks = [bu.retrieve() for bu in self.bulletins_list if isinstance(bu, EEBulletin)]
        self.bulletins_detail_list = await asyncio.gather(*tasks)
        return self.bulletins_detail_list

    async def retrieve_all_homeworks_details(self):
        tasks = [hw.retrieve() for hw in self.homeworks_list if isinstance(hw, EEHomework)]
        self.homeworks_detail_list = await asyncio.gather(*tasks)
        return self.homeworks_detail_list
    
    async def retrieve_all_materials_details(self):
        tasks = [m.retrieve() for m in self.material_list if isinstance(m, EEMaterial) and m.type != "homework"]
        self.materials_detail_list = await asyncio.gather(*tasks)
        return self.materials_detail_list
