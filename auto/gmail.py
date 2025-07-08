from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import pathlib
import csv
import os
import warnings
from time import sleep
import logging
import pyautogui
import random
from selenium.webdriver.common.action_chains import ActionChains

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.openai import Gpt

warnings.simplefilter('ignore')

def setup_logging():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    return logger

logger = setup_logging()

def setup_driver():
    global driver
    ScriptDir = pathlib.Path().absolute()
    options = uc.ChromeOptions()
    options.add_argument('--profile-directory=Default')
    options.add_argument(f'--user-data-dir={ScriptDir}\\assets\\chromedata')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-background-timer-throttling')
    options.add_argument('--disable-renderer-backgrounding')
    options.add_argument('--page-load-strategy=eager')
    options.add_argument('--user-agent=Mozilla/5.0 ...')

    try:
        driver = uc.Chrome(
            options=options,
            driver_executable_path=os.path.join(ScriptDir, 'assets', 'chromedriver.exe')
        )
        driver.maximize_window()
        driver.set_page_load_timeout(30)
        driver.implicitly_wait(10)
        logger.info("✅ Driver setup successful")
        return True
    except Exception as e:
        logger.error(f"❌ Driver setup failed: {e}")
        return False

def safe_get(url, retries=3):
    for attempt in range(retries):
        try:
            driver.get(url)
            return True
        except Exception as e:
            logger.warning(f"⚠️ Attempt {attempt+1} failed to load {url}: {e}")
            sleep(random.uniform(3, 10))
    return False

xpaths = {
    "username": (By.XPATH, '//*[@id="identifierId"]'),
    "next_btn": (By.XPATH, '//*[@id="identifierNext"]'),
    "password": (By.XPATH, '//*[@id="password"]'),
    "signin_btn": (By.XPATH, '//*[@id="passwordNext"]'),
    "compose_btn": (By.XPATH, '//*[@id=":l0"]/div/div'),
    "to_btn": (By.XPATH, '//*[@id=":qs"]/div/div[3]/div/div/div/div/div'),
    "subject_btn": (By.ID, '//*[@id=":or"]'),
    "body_btn": (By.ID, '//*[@id=":nb"]'),
    "compose_max_btn": (By.XPATH, '//*[@id=":1m7"]'),
    "attach_btn": (By.XPATH, '//*[@id=":sr"]'),
    "send_btn": (By.XPATH, '//*[@id=":p2"]'),
    "sechedule_btn1": (By.XPATH, '//*[@id=":pv"]/div'),
    "schedule_btn2": (By.XPATH, '//*[@id=":pv"]'),
    "date-time_btn": (By.XPATH, '/html/body/div[43]/div[2]/div/div/div[2]/div/div[2]/div[4]'),
    "date_btn": (By.XPATH, '//*[@id="c12"]'),  # 17 Jul 2025
    "time_btn": (By.XPATH, '//*[@id="c13"]'),  # 17:53
    "schedule_send_btn": (By.XPATH, '/html/body/div[43]/div[2]/div/div[2]/div[2]/button/span[5]'),
}

def set_up(username: str, password: str):
    try:
        safe_get("https://mail.google.com/")
        WebDriverWait(driver, 30).until(EC.presence_of_element_located(xpaths['username']))
        driver.find_element(*xpaths['username']).send_keys(str(username))
        sleep(1)
        driver.find_element(*xpaths['next_btn']).click()
        sleep(1)
        WebDriverWait(driver, 30).until(EC.presence_of_element_located(xpaths['password']))
        driver.find_element(*xpaths['password']).send_keys(str(password))
        sleep(1)
        driver.find_element(*xpaths['signin_btn']).click()
        sleep(10)
        logger.info("✅ Setup Completed Successfully")
    except Exception as e:
        logger.warning(f"⚠️ Setup failed: {e}")

def cause_error(error):
    return logger.error(f"❌ Error in {error}")

def compose_mail(to: str, subject: str, body: str, attach: str = None, schedule: str = None):
    global driver
    try:
        LOGGED = safe_get("https://mail.google.com/")
        sleep(5)
        if LOGGED:
            try:
                driver.find_element(*xpaths['compose_btn']).click()
                #sleep(100000)
                #try:
                    #WebDriverWait(driver, 30).until(EC.presence_of_element_located(*xpaths['to_btn']))
                    #driver.find_element(*xpaths['compose_max_btn']).click()
                    #sleep(2)
                try:
                    driver.find_element(*xpaths["to_btn"]).send_keys(str(to))
                    sleep(2)
                    try:
                        driver.find_element(*xpaths["subject_btn"]).send_keys(str(subject))
                        sleep(2)
                        try:
                            driver.find_element(*xpaths['body_btn']).send_keys(str(body))
                            sleep(2)
                            if attach:
                                driver.find_element(*xpaths['attach_btn']).click()
                                sleep(10)
                                driver.find_element(*xpaths['send_btn']).click()
                                sleep(2)
                                logger.info("✅ Mail sent successfully")
                                
                            else:
                                driver.find_element(*xpaths['send_btn']).click()
                                sleep(2)
                                logger.info("✅ Mail sent successfully")
                                #logger.error("❌ Could not send mail")
                        except Exception:
                            cause_error('body_btn')

                    except Exception:
                            cause_error('subject_btn')

                except Exception:
                    cause_error('to_btn')
       
                #except Exception:
                #    cause_error('compose_max_btn')

            except Exception:
                cause_error('compose_btn')
            
    except Exception as e:
        logger.error(f"❌ Failed to open Gmail: {e}")
            
            


if __name__ == '__main__':
    if setup_driver():
        compose_mail(to='chanduj2525@gmail.com', subject='Test', body="This is a test message from Automation")
    else:
        logger.error("❌ Could not continue without a driver.")
