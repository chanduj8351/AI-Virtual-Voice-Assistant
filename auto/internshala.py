from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys
import json
import os
import pyautogui

class Freelance:
    def __init__(self):
        cookie_file = "internshala"
        freelancer_profile_path = f"user-data-dir=C:/Users/Chand/AppData/Local/Google/Chrome/User Data/Default/{cookie_file}"
        chrome_path = os.getcwd() + "\\assets\\chromedriver.exe"
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument(freelancer_profile_path)
        self.chrome_options.add_argument("--disable-gpu")
        #self.chrome_options.add_argument("--headless=new")
        self.service = Service(chrome_path)
        self.driver = None

    def login(self):
        print('starting service')
        self.driver = webdriver.Chrome(service=self.service, options=self.chrome_options)
        print('loading chrome')
        self.driver.get("https://internshala.com/student/dashboard")
        print("Internshala Web launched. Please scan the QR code if required.")
        sleep(1000000)

Freelance().login()