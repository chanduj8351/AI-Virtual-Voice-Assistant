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

class WhatsApp:
    def __init__(self):
        cookie_file = "whatsapp"
        whatsapp_profile_path = f"user-data-dir=C:/Users/Chand/AppData/Local/Google/Chrome/User Data/Default/{cookie_file}"
        chrome_path = os.getcwd() + "\\assets\\chromedriver.exe"
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument(whatsapp_profile_path)
        self.chrome_options.add_argument("--disable-gpu")
        #self.chrome_options.add_argument("--headless=new")
        self.service = Service(chrome_path)
        self.driver = None

    def login(self):
        print('starting service')
        self.driver = webdriver.Chrome(service=self.service, options=self.chrome_options)
        print('loading chrome')
        self.driver.get("https://web.whatsapp.com/")
        print("WhatsApp Web launched. Please scan the QR code if required.")
        sleep(1000000)
        return True


    def send_message(self, contact, message=None, file_path=None):
        self.driver = webdriver.Chrome(service=self.service, options=self.chrome_options)
        self.driver.get("https://web.whatsapp.com/")
        self.driver.maximize_window()

        try:
            # Wait for search box
            print('waiting for search box')
            search_box = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div[3]/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/p')))
            
            WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[1]/div/div/div[3]/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/p')))

            sleep(2) 
            search_box.click()
            search_box.clear()
            sleep(1.5)  
            search_box.send_keys(contact)
            sleep(2)
            search_box.send_keys(Keys.ENTER)
            sleep(1)

            if message:
                # Send text message
                #message_box = self.driver.find_element(By.XPATH, '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div[1]/div[2]/div[1]/p')
                message_box =  WebDriverWait(self.driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div/div[3]/div[1]/p'))
                )
                sleep(0.33)
                message_box.send_keys(message)
                sleep(1)
                message_box.send_keys(Keys.ENTER)
                sleep(1.5)

            if file_path and os.path.exists(file_path):
                # Click on attachment button 📎
                attach_btn = WebDriverWait(self.driver, 30).until(
                    EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span/div/div[1]/div/button/span'))
                )
                attach_btn.click()
                sleep(2)

                # Determine file type (image/video or document)
                file_extension = os.path.splitext(file_path)[-1].lower()

                if file_extension in ['.png', '.jpg', '.jpeg', '.gif', '.mp4', '.mov', '.avi', '.py']:
                    file_input = self.driver.find_element(By.XPATH, '//*[@id="app"]/div/span[5]/div/ul/div/div/div[2]/li/div/span')
                    file_input.click()
                    sleep(1)
                    pyautogui.write(file_path)
                    sleep(1) 
                    pyautogui.hotkey('enter')
                    send_btn = WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((By.XPATH, '//*[@id="app"]/div/div[3]/div/div[2]/div[2]/span/div/div/div/div[2]/div/div[2]/div[2]/div/div/span')))
                    #sleep(8)
                    #send_btn = self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div[3]/div/div[2]/div[2]/span/div/div/div/div[2]/div/div[2]/div[2]/div/div/span')
                    sleep(1)
                    send_btn.click()
                    WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div[3]/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/p')))
                    sleep(10)
                    print('Sent file: %s' % file_path)

                else:  # Document upload
                    file_input = self.driver.find_element(By.XPATH, '//*[@id="app"]/div/span[5]/div/ul/div/div/div[1]/li/div/span')
                    file_input.click()
                    sleep(1)
                    pyautogui.write(file_path)
                    sleep(1) 
                    pyautogui.hotkey('enter')
                    sleep(2)
                    send_btn = self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div[3]/div/div[2]/div[2]/span/div/div/div/div[2]/div/div[2]/div[2]/div/div/span')
                    send_btn.click()
                    sleep(1)
                    # pyautogui.hotkey('enter')
                    sleep(3)
                    print('Sent file: %s' % file_path)
                    return True

        except WebDriverException as e:
            print(f"Error occurred while sending message: {e}")

        finally:
            self.driver.quit()

    

    def get_unread_messages(self):
        self.driver = webdriver.Chrome(service=self.service, options=self.chrome_options)
        self.driver.get("https://web.whatsapp.com/")
        #self.driver.maximize_window()

        unread_data = []  
        try:
            print('main starting')
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div[3]/div/div[3]/div/div[1]/div/div[2]/div/div/div[1]/p')))
            print("WhatsApp Web loaded.")

            sleep(1)

            # Access the unread chats
            print('start')
            unread_chats_button = self.driver.find_element(
                By.XPATH, '//*[@id="unread-filter"]/div/div' #//*[@id="unread-filter"]/div/div
            )
            unread_chats_button.click()
            sleep(10)
            print('end')

            # Find all unread chats
            unread_chats = self.driver.find_elements(By.XPATH, '//div[@role="gridcell"]//span[@title]')
            unread_messages_count = self.driver.find_elements(By.XPATH, '//div[@class="_ahlk"]//span[@aria-label]')
            unread_messages = self.driver.find_elements(By.XPATH, '//div[@class="_ak8k"]//span[@title]')
            time_stamp = self.driver.find_elements(By.XPATH, '//div[@role="gridcell"][@aria-colindex="2"]//div[@class="_ak8i"]')

            min_length = min(len(unread_chats), len(unread_messages_count), len(unread_messages), len(time_stamp))

            for i in range(min_length):
                chat_name = unread_chats[i].get_attribute("title")
                message_count = unread_messages_count[i].get_attribute("aria-label")
                message_text = unread_messages[i].text
                message_time = time_stamp[i].text

                unread_data.append({
                    "chat_name": chat_name,
                    "message_count": message_count,
                    "message_text": message_text,
                    "message_time": message_time
                })

        except WebDriverException as e:
            print(f"Error occurred: {e}")
        finally:
            self.driver.quit()

        print(json.dumps(unread_data, indent=4, ensure_ascii=False))
        return unread_data
    

    def get_all_unread_messages(self):
        self.driver = webdriver.Chrome(service=self.service, options=self.chrome_options)
        self.driver.get("https://web.whatsapp.com/")
        #self.driver.maximize_window()

        unread_data = [] 
        try:
            WebDriverWait(self.driver, 30).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="side"]/div[1]/div/div[2]/div'))
            )
            print("WhatsApp Web loaded.")

            sleep(1.5)

            unread_chats_button = self.driver.find_element(
                By.XPATH, '//*[@id="side"]/div[2]/button[2]/div/div'
            )
            unread_chats_button.click()
            sleep(1.5)

            unread_chats = self.driver.find_elements(By.XPATH, '//div[@role="gridcell"]//span[@title]')
            unread_messages_count = self.driver.find_elements(By.XPATH, '//div[@class="_ahlk"]//span[@aria-label]')
            unread_messages = self.driver.find_elements(By.XPATH, '//div[@class="_ak8k"]//span[@title]')
            time_stamp = self.driver.find_elements(By.XPATH, '//div[@role="gridcell"][@aria-colindex="2"]//div[@class="_ak8i"]')

            min_length = min(len(unread_chats), len(unread_messages_count), len(unread_messages), len(time_stamp))

            for i in range(min_length):
                chat_name = unread_chats[i].get_attribute("title")
                message_count = unread_messages_count[i].get_attribute("aria-label")
                message_text = unread_messages[i].text
                message_time = time_stamp[i].text

                unread_data.append({
                    "chat_name": chat_name,
                    "message_count": message_count,
                    "message_text": message_text,
                    "message_time": message_time
                })

            for chat in unread_chats:
                chat.click() 
                sleep(2)  
                
                unread_messages_elements = self.driver.find_elements(By.XPATH, '//div[contains(@class, "message-in")]')
                all_unread_messages = [msg.text for msg in unread_messages_elements]

                unread_data.append({
                    "chat_name": chat_name,
                    "message_count": message_count,
                    "all_unread_messages": all_unread_messages, 
                    "message_time": message_time
                })


        except WebDriverException as e:
            print(f"Error occurred: {e}")
        finally:
            self.driver.quit()

        print(json.dumps(unread_data, indent=4, ensure_ascii=False))
        return unread_data
    

    def status(self):
        self.driver = webdriver.Chrome(service=self.service, options=self.chrome_options)
        self.driver.get("https://web.whatsapp.com/")
        self.driver.maximize_window()

        try:
            WebDriverWait(self.driver, 15).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="side"]/div[1]/div/div[2]/div'))
            )
            sleep(1)

            status_btn = self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div[3]/div/header/div/div/div/div/span/div/div[1]/div[2]/button')
            status_btn.click()
            sleep(1) 

            contact_elements = self.driver.find_elements(By.XPATH, '//span[@class="x1iyjqo2 x6ikm8r x10wlt62 x1n2onr6 xlyipyv xuxw1ft _ao3e"]')
            
            contacts = [contact.text for contact in contact_elements]  
            print("Contacts found:")
            for contact in contacts:
                print(f"- {contact}")
                return contact

        except WebDriverException as e:
            print(f"Error occurred: {e}")
        finally:
            self.driver.quit()


if __name__ == "__main__":
    whatsapp = WhatsApp()
    #whatsapp.send_message(contact='chandu', file_path='C:\\Users\\chand\\Desktop\\Siri17\\siri.py')
 
    whatsapp.status()
    

    #whatsapp.login()
























    # def send_message(self, contact, message=None, file_path=None):
    #     self.driver = webdriver.Chrome(service=self.service, options=self.chrome_options)
    #     self.driver.get("https://web.whatsapp.com/")
    #     self.driver.maximize_window()

    #     try:
    #         # Wait for the search box to be visible
    #         search_box = WebDriverWait(self.driver, 30).until(
    #             EC.visibility_of_element_located((By.XPATH, '//*[@id="side"]/div[1]/div/div[2]/div'))
    #         )
            
    #         # Search for the contact
    #         search_box.clear()
    #         search_box.send_keys(contact)
    #         sleep(1)
    #         search_box.send_keys(Keys.ENTER)
    #         sleep(1)

    #         # If a file path is provided, send the file
    #         if file_path:
    #             # Click the attachment button
    #             attachment_button = WebDriverWait(self.driver, 10).until(
    #                 EC.element_to_be_clickable((By.XPATH, '//*[@id="main"]/footer/div[1]/div/span/div/div[1]/div/button'))
    #             )
    #             attachment_button.click()
    #             sleep(1)


    #             file_input = self.driver.find_element(By.XPATH, '//*[@id="app"]/div/span[5]/div/ul/div/div/div[2]/li/div/span')
    #             file_input.click()
    #             sleep(1)
    #             pyautogui.write(file_path)
    #             sleep(1) 
    #             pyautogui.hotkey('enter')
    #             sleep(2)
    #             send_btn = self.driver.find_element(By.XPATH, '//*[@id="app"]/div/div[3]/div/div[2]/div[2]/span/div/div/div/div[2]/div/div[2]/div[2]/div/div/span')
    #             send_btn.click()
    #             sleep(1)
    #             # pyautogui.hotkey('enter')
    #             sleep(5)
    #             print('Sent file: %s' % file_path)



    #         # If a message is provided, send the message
    #         if message:
    #             message_box = self.driver.find_element(By.XPATH, '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div[1]/div[2]/div[1]/p')
    #             message_box.send_keys(message)
    #             sleep(1)
    #             message_box.send_keys(Keys.ENTER)
    #             sleep(0.3)
    #             message_box.send_keys(Keys.ENTER)
    #             sleep(1.2)

    #     except WebDriverException as e:
    #         print(f"Error occurred while sending message or file: {e}")

    #     finally:
    #         self.driver.quit()

