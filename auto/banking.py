import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import pyautogui
from time import sleep
import google.generativeai as ai
from PIL import Image
import PIL.Image

key = os.environ["GEMINI_API_KEY"]
ai.configure(api_key=key)

prompt = "Observe the picture and return the captcha code. No need to add anything. Just return the captcha code."

class Banking:
    def __init__(self, speed=0.5, click_speed=0.3):
        cookie_file = "banking"
        banking_profile_path = f"user-data-dir=C:/Users/Chand/AppData/Local/Google/Chrome/User Data/Default/{cookie_file}"
        chrome_path = "C:\\Users\\chand\\Desktop\\Siri16\\auto\\assets\\chromedriver.exe"
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument(banking_profile_path)
        self.chrome_options.add_argument("--disable-gpu")
        #self.chrome_options.add_argument("--headless=new")
        self.service = Service(chrome_path)
        self.driver = None
        self.speed = speed
        self.click_speed = click_speed

    @staticmethod
    def cam_vision(image_path: str = "C:\\Users\\chand\\Desktop\\Siri16\\auto\\assets\\captcha.png", prompt=prompt, model_name="gemini-1.5-flash-002"):
        try:
                model = ai.GenerativeModel(model_name)
                response = model.generate_content([prompt, PIL.Image.open(image_path)])
                return response.text
        
        except Exception as e:
            print("\033[91m" + f"Error occurred: {e}\033[0m")
            return ""
        finally:
            pass
             
    def login(self):
        try:
            self.driver = webdriver.Chrome(service=self.service, options=self.chrome_options)
            self.driver.get("https://retail.onlinesbi.sbi/retail/login.htm")
            self.driver.maximize_window()
            sleep(3)
            position = pyautogui.locateOnScreen('auto/assets/login.png', confidence=0.7)
            pyautogui.moveTo(position[0:2], duration=self.speed)
            pyautogui.moveRel(100, 40, duration=self.speed)
            pyautogui.click(interval=self.click_speed)
            sleep(1)
            pyautogui.screenshot("auto/assets/captcha.png")
            user_name = "Chanduj8351"
            pyautogui.write(user_name)
            sleep(0.2)
            pyautogui.press('\n')
            sleep(0.2)
            pyautogui.press('\n')
            sleep(0.2)
            password = "Chandu@8351"
            pyautogui.write(password)
            sleep(0.1)
            pyautogui.press('\n')
            sleep(0.1)
            pyautogui.press('\n')
            print('Processing...')
            sleep(3)
            captcha = self.cam_vision()
            pyautogui.write(captcha)
            sleep(0.1)
            pyautogui.press('\n')
            sleep(0.2)
            pyautogui.press('\n')
            print('Logged in successfully.')
        except Exception as e:
            print(f'Exception during login: {e}')
    
        sleep(1000000)

if __name__ == '__main__':
    Banking().login()
