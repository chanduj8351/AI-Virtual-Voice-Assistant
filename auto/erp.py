import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from time import sleep
from tabulate import tabulate
import pyautogui


class Erp:
    def __init__(self, speed=0.5, click_speed=0.3):
        cookie_file = "erp"
        erp = f"user-data-dir=C:/Users/Chand/AppData/Local/Google/Chrome/User Data/Default/{cookie_file}"
        chrome_path = os.getcwd() + "\\assets\\chromedriver.exe"
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument(erp)
        self.chrome_options.add_argument("--disable-gpu")
        # self.chrome_options.add_argument("--headless=new")
        self.service = Service(chrome_path)
        self.driver = None
        self.speed = speed
        self.click_speed = click_speed


    def login(self):
        try:
            self.driver = webdriver.Chrome(service=self.service, options=self.chrome_options)
            self.driver.get("https://erp.lbrce.ac.in/")
            self.driver.maximize_window()

            # Fetch username & password from environment variables
            user_id = os.getenv("ERP_USERNAME", "23765A5605")  # Default if not set
            password_val = os.getenv("ERP_PASSWORD", "23ASELE08")

            user = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="txtusername"]')))
            user.send_keys(user_id)
            sleep(0.3)

            password = self.driver.find_element(By.XPATH, '//*[@id="txtpassword"]')
            password.send_keys(password_val)
            sleep(0.3)
            password.send_keys(Keys.ENTER)
            print("ERP Web launched.\n\nLogged In ✔")
            #sleep(100000)
        except Exception as e:
            print('❌ Error in ERP Web login:  \nException: ', e)

               

    def attendance(self, username = "23765A5605", password = "23ASELE08"):
        self.login()

        # Navigate to attendance page
        discipline_btn = WebDriverWait(self.driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="dvMenu_Main"]/ul/li[1]/a/span[1]'))
        )
        x = discipline_btn.click()
        print("return", x)

        

        attendance_btn = WebDriverWait(self.driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="ContentPlaceHolder1_btnAtt"]'))
        )
        attendance_btn.click()

        # Attendance percentage
        attendance_data = WebDriverWait(self.driver, 15).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="ContentPlaceHolder1_lblAttPercent"]')))
        percent = attendance_data.text
        print(f"\n🔹 Attendance Percentage: {percent} 🔹\n\n")

        # Attendance details
        attendance_details = WebDriverWait(self.driver, 15).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="ContentPlaceHolder1_Panel1"]')))
        details_text = attendance_details.text.split("\n")[1:]  # Skipping header

        # Extract table data
        data = []
        for line in details_text:
            parts = line.split()
            if len(parts) >= 5:
                subject = " ".join(parts[:-3])  # Merge subject name (excluding last 3 numbers)
                classes_held = parts[-3]
                classes_present = parts[-2]
                attendance_percent = parts[-1]
                data.append([subject, classes_held, classes_present, attendance_percent])

        print(tabulate(data, headers=["Subject", "Classes Held", "Classes Present", "Attendance %"], tablefmt="grid"))
        sleep(2)

        # Monthly Attendance
        try:
            monthly_details = WebDriverWait(self.driver, 15).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="ContentPlaceHolder1_PanelAtt"]/div/div/div[3]/div/div[2]/div/div[2]/div')))
            month_data = monthly_details.text.split("\n")

            # Remove unexpected headers if present
            if "Month Total Class(s) Present Class(s) Percentage %" in month_data[0]:
                month_data = month_data[1:]

            # Fix monthly attendance formatting
            monthly_table = []
            for i in range(0, len(month_data), 4):  # Ensure proper column grouping
                if i + 3 < len(month_data):
                    monthly_table.append([month_data[i], month_data[i + 1], month_data[i + 2], month_data[i + 3]])

            print("\n🔹 Monthly Attendance 🔹\n")
            print(tabulate(monthly_table, headers=["Month", "Total Classes", "Present Classes", "Percentage %"], tablefmt="grid"))
            sleep(1)

            # graph = WebDriverWait(self.driver, 15).until(
            #     EC.visibility_of_element_located((By.XPATH, '//*[@id="ContentPlaceHolder1_Chart2"]')))
            # attendance_graph = graph.screenshot_as_png
            # with open(os.getcwd()+"\\temp\\img\\attendance_graph.png", "wb") as file:
            #     file.write(percent)
            #     print("Attendance graph saved as attendance_graph.png")
            # sleep(1)

        except Exception as e:
            print("Error fetching Monthly Attendance:", e)

        finally:
            return f"🔹 Attendance Percentage: {percent} 🔹"


    def fee_details(self):
        try:
            self.driver = webdriver.Chrome(service=self.service, options=self.chrome_options)
            self.driver.get("https://erp.lbrce.ac.in/")
            self.driver.maximize_window()

            # Fetch username & password from environment variables
            user_id = os.getenv("ERP_USERNAME", "23765A5605")  # Default if not set
            password_val = os.getenv("ERP_PASSWORD", "23ASELE08")

            user = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="txtusername"]'))
            )
            user.send_keys(user_id)
            sleep(0.3)

            password = self.driver.find_element(By.XPATH, '//*[@id="txtpassword"]')
            password.send_keys(password_val)
            sleep(0.3)
            password.send_keys(Keys.ENTER)
        except Exception as e:
            print('Exception: ', e)

        print("\nERP Web launched. Please scan the QR code if required.\n")
        sleep(1)

        try:
            # Navigate to fee payment page
            fee_btn = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="ContentPlaceHolder1_pnlFC"]'))
            )

            fee_text = fee_btn.text.split("\n")  # Split text into lines
            fee_raw_data = []
            
            # Process fee data
            for row in fee_text[1:]:  # Skip the first row (header)
                parts = row.split()
                if len(parts) >= 6:  # Ensure the row has enough elements
                    fee_name = " ".join(parts[:2])  # Join first two words as Fee Name
                    fee_type = parts[2]             # Third word is Fee Type
                    amount = parts[-3]              # Third-last is Amount
                    paid = parts[-2]                # Second-last is Paid
                    due = parts[-1]                 # Last is Due
                    fee_raw_data.append([fee_name, fee_type, amount, paid, due])

            #print("fee_raw_data: ", fee_raw_data)  # Debugging output

            # Print formatted table
            headers = ["Fee Name", "Fee Type", "Amount", "Paid", "Due"]
            print(tabulate(fee_raw_data, headers=headers, tablefmt="grid"))

        except Exception as e:
            print("Error fetching Fee Details:", e)

        finally:
            return fee_text


    def marks(self):
        try:
            self.driver = webdriver.Chrome(service=self.service, options=self.chrome_options)
            self.driver.get("https://erp.lbrce.ac.in/")
            self.driver.maximize_window()

            # Fetch username & password from environment variables
            user_id = os.getenv("ERP_USERNAME", "23765A5605")  # Default if not set
            password_val = os.getenv("ERP_PASSWORD", "23ASELE08")

            user = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="txtusername"]'))
            )
            user.send_keys(user_id)
            sleep(0.3)

            password = self.driver.find_element(By.XPATH, '//*[@id="txtpassword"]')
            password.send_keys(password_val)
            sleep(0.3)
            password.send_keys(Keys.ENTER)
        except Exception as e:
            print('Exception: ', e)

        print("\nERP Web launched. Please scan the QR code if required.\n")
        sleep(1)

        try:
            # Navigate to marks page
            discipline_btn = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="dvMenu_Main"]/ul/li[1]/a/span[1]'))
            )
            discipline_btn.click()

            marks_btn = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="ContentPlaceHolder1_btnIM"]'))
            )
            marks_btn.click()
            sleep(1)

            marks_details = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="ContentPlaceHolder1_gvJT1"]'))
            )
            
            # Process marks text
            marks_text = marks_details.text.split("\n")  # Split into lines
            headers = marks_text[0].split()  # First row as headers
            marks_data = []

            for row in marks_text[1:]:  # Skip header row
                parts = row.split()
                
                # Handle multi-word subject names
                subject_code = parts[0]  # First element is always the subject code
                marks_start_index = -1

                # Identify the position where numeric marks start
                for i in range(1, len(parts)):
                    if parts[i].replace('.', '', 1).isdigit():  # Detect first numeric value
                        marks_start_index = i
                        break
                
                if marks_start_index == -1:
                    continue  # Skip if no valid marks found
                
                subject_name = " ".join(parts[1:marks_start_index])  # Join words for subject name
                marks_values = parts[marks_start_index:]  # Extract numeric values
                
                # Ensure the extracted row matches the header column count
                while len(marks_values) < len(headers) - 2:  # Adjust for SubjectCode and SubjectName
                    marks_values.append("0")  # Fill missing values with 0
                
                marks_data.append([subject_code, subject_name] + marks_values)

            print("\nFormatted Marks Table:\n")
            print(tabulate(marks_data, headers=headers, tablefmt="grid"))

        except Exception as e:
            print("Error fetching marks details:", e)




    def fee_payment(self, amount: int):
        try:
            self.driver = webdriver.Chrome(service=self.service, options=self.chrome_options)
            self.driver.get("https://erp.lbrce.ac.in/")
            self.driver.maximize_window()

            # Fetch username & password from environment variables
            user_id = os.getenv("ERP_USERNAME", "23765A5605")  # Default if not set
            password_val = os.getenv("ERP_PASSWORD", "23ASELE08")

            user = WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="txtusername"]'))
            )
            user.send_keys(user_id)
            sleep(0.3)

            password = self.driver.find_element(By.XPATH, '//*[@id="txtpassword"]')
            password.send_keys(password_val)
            sleep(0.3)
            password.send_keys(Keys.ENTER)
        except Exception as e:
            print('Exception: ', e)

        print("\nERP Web launched. Please scan the QR code if required.\n")
        sleep(1)

        try:

            mail_id = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="ContentPlaceHolder1_txtmailid"]'))
            )
            mail_id.send_keys('chanduj8351@gmail.com')
            sleep(1)


            # Navigate to fee payment page
            fee_amount_btn = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="ContentPlaceHolder1_gvFeeChallana_txtPayAmount_1"]'))
            )
            fee_amount_btn.send_keys(amount)
            sleep(1)

            accept_btn = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="ContentPlaceHolder1_chkterms"]'))
            )
            accept_btn.click()
            sleep(1)


            pay_btn = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="ContentPlaceHolder1_btnsave"]'))
            )
            pay_btn.click()
            sleep(10)
            try:
                position = pyautogui.locateOnScreen('C:\\Users\\chand\\Desktop\\Siri16\\auto\\assets\\upi.png', confidence=0.7)
                pyautogui.moveTo(position[0:2], duration=self.speed)
                pyautogui.moveRel(100, 40, duration=self.speed)
                pyautogui.click(interval=self.click_speed)
                sleep(1)
                position = pyautogui.locateOnScreen('auto\\assets\\qrcode.png', confidence=0.7)
                pyautogui.moveTo(position[0:2], duration=self.speed)
                pyautogui.moveRel(20, 20, duration=self.speed)
                pyautogui.click(interval=self.click_speed)
                sleep(1)
                position = pyautogui.locateOnScreen('auto\\assets\\proceednow.png', confidence=0.7)
                pyautogui.moveTo(position[0:2], duration=self.speed)
                pyautogui.moveRel(20, 20, duration=self.speed)
                pyautogui.click(interval=self.click_speed)
                sleep(15)
                QR_CODE = pyautogui.screenshot('qrcode.png')
                QR_CODE.save()
                print("QR code saved as qrcode.png")
                print('done')   

            except Exception as e:
                print("Error locating UPI image:", e)
            

        except Exception as e:
            print("Error processing Fee Payment:", e)
            

        

if __name__ == "__main__":
    print(Erp().attendance())