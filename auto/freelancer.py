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
from bs4 import BeautifulSoup

class Freelance:
    def __init__(self):
        cookie_file = "freelancer"
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
        self.driver.get("https://www.freelancer.in/dashboard")
        print("Freelancer Web launched. Please scan the QR code if required.")
        sleep(1000000)


    def available_bids(self):
        print('starting service')
        self.driver = webdriver.Chrome(service=self.service, options=self.chrome_options)
        print('loading chrome')
        self.driver.get("https://www.freelancer.in/dashboard")
        print("Freelancer Web launched. Please scan the QR code if required.")
        sleep(2)
        print("Available Bids")

        try:
            bid_btn = self.driver.find_element(By.XPATH, '/html/body/app-root/app-logged-in-shell/div/div[1]/div/app-navigation/app-navigation-primary/div/fl-container/div[5]/fl-highlight/div')
            bid_btn.click()
            sleep(2)
            print('bid button clicked')
            sleep(1)

            # Get page source and parse it
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        
            # Find all project items
            projects = soup.find_all("app-project-item")

            # Extract and print information
            for project in projects:
                try:
                    # Project Title
                    title_tag = project.find("div", class_="NativeElement", attrs={"data-weight": "bold"})
                    title = title_tag.get_text(strip=True) if title_tag else "N/A"

                    # Skills
                    skills_tag = project.find("div", class_="Jobs")
                    skills = skills_tag.get_text(strip=True) if skills_tag else "N/A"

                    # Budget
                    budget_tag = project.find("fl-budget")
                    budget = budget_tag.get_text(strip=True) if budget_tag else "N/A"

                    # Link
                    link_tag = project.find("a", class_="ButtonElement")
                    link = "https://www.freelancer.com" + link_tag["href"] if link_tag and link_tag.get("href") else "N/A"

                    # Display
                    print(f"Title: {title}")
                    print(f"Skills: {skills}")
                    print(f"Budget: {budget}")
                    print(f"Link: {link}")
                    print("-" * 40)

                except Exception as e:
                    print("Error extracting project:", e)
                    print("-" * 40)

                    
        except:
            return "Bid Button not found"
        











# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.chrome.options import Options

# # Setup
# options = Options()
# options.add_argument("--headless")  # Run in headless mode
# driver = webdriver.Chrome(service=Service(), options=options)

# # Load the Freelancer project feed page (update to your actual URL)
# driver.get("https://www.freelancer.in/dashboard")  # Replace with your page

# # Find all project elements
# projects = driver.find_elements(By.TAG_NAME, "app-project-item")

# for project in projects:
#     try:
#         # Project title
#         title = project.find_element(By.CSS_SELECTOR, "div[role='paragraph'][data-weight='bold']").text

#         # Project categories
#         categories = project.find_element(By.CSS_SELECTOR, ".Jobs div[role='paragraph']").text

#         # Budget
#         budget = project.find_element(By.CSS_SELECTOR, "fl-budget").text

#         # Time posted
#         time_posted = project.find_element(By.CSS_SELECTOR, "fl-relative-time span").text

#         # Project link
#         link_element = project.find_element(By.CSS_SELECTOR, "a.ButtonElement")
#         project_url = link_element.get_attribute("href")

#         # Print details
#         print("Title:", title)
#         print("Categories:", categories)
#         print("Budget:", budget)
#         print("Time Posted:", time_posted)
#         print("Project URL:", project_url)
#         print("-" * 40)

#     except Exception as e:
#         print("Error reading project:", e)

# # Cleanup
# driver.quit()
