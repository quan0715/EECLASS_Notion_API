from fake_user_agent import user_agent


class EEConfig:
    YEAR = 2023
    BASE_URL = "https://ncueeclass.ncu.edu.tw/"
    COURSE_URL = f"{BASE_URL}course/"
    HOMEWORK_URL = f"{BASE_URL}course/homework/"
    HOMEWORK_LIST = f"{BASE_URL}course/homeworkList/"
    BULLETIN_URL = f"{BASE_URL}course/bulletin/"
    MATERIAL_URL = f"{BASE_URL}course/material/"
    LOGIN_URL = f"{BASE_URL}index/login/"

    HEADERS = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "User-Agent": user_agent("chrome")
    }

    CLASS_NAME_TO_MATERIAL_TYPE = {
        "font-icon fs-fw far fa-file-alt": "text",
        "font-icon fs-fw far fa-file-video": "video",
        "font-icon fs-fw far fa-clipboard": "homework",
        "font-icon fs-fw far fa-file-pdf": "pdf",
        "font-icon fs-fw far fa-file-powerpoint": "ppt"
    }

    @classmethod
    def get_index_url(cls, url:str, index:str):
        return url.strip('/') + '/' + index.strip('/')
