from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import os


class EEChromeDriver:
    driver = None

    @staticmethod
    def create_driver():
        chrome_options = Options()
        # chrome_options.add_argument("--headless")
        chrome_options.page_load_strategy = "eager"
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://ncueeclass.ncu.edu.tw/")
        time.sleep(3)
        login_button = driver.find_element(By.CLASS_NAME, "nav.navbar-nav.navbar-right").find_element(By.TAG_NAME, "span")
        login_button.click()
        time.sleep(2)
        login_form = driver.find_element(By.ID, "login_form")
        login_form.find_element(By.NAME, "account").send_keys(os.getenv("ACCOUNT"))
        login_form.find_element(By.NAME, "password").send_keys(os.getenv("PASSWORD"))
        time.sleep(2)
        try:
            login_button = login_form.find_element(By.TAG_NAME, "button")
            login_button.click()
        except:
            pass
        time.sleep(3)
        login_button = driver.find_element(By.CLASS_NAME, "btn.btn-default.keepLoginBtn")
        login_button.click()
        time.sleep(3)
        EEChromeDriver.driver = driver

    @staticmethod
    def get_driver() -> webdriver.Chrome:
        if EEChromeDriver.driver is None:
            EEChromeDriver.create_driver()
        return EEChromeDriver.driver

    @staticmethod
    def close_driver() -> None:
        if EEChromeDriver.driver is not None:
            EEChromeDriver.driver.close()
            EEChromeDriver.driver = None
