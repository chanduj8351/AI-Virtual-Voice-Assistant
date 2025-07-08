import os
import sys
import pathlib
import logging
import warnings
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import undetected_chromedriver as uc
import random
import csv
import urllib3
from bs4 import BeautifulSoup
import re

# Setup paths
ScriptDir = pathlib.Path().absolute()
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
warnings.simplefilter('ignore')

# === Setup Logging ===
def setup_logging():
    logger = logging.getLogger("FreelancerBot")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    fh = logging.FileHandler('freelancer_bot.log', encoding='utf-8')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    return logger

logger = setup_logging()

# === XPaths ===
xpaths = {
    "login_btn": (By.XPATH, '/html/body/app-root/app-logged-out-shell/app-navigation-logged-out-home/div[2]/fl-container/div/fl-link[1]/a'),
    "user_name": (By.XPATH, '//*[@id="emailOrUsernameInput"]'),
    "password": (By.XPATH, '//*[@id="passwordInput"]'),
    "check_box": (By.CSS_SELECTOR, "label[for='RememberMeCheckbox']"),
    "login_now": (By.XPATH, '/html/body/app-root/app-logged-out-shell/div/app-login-page/div/div[1]/app-login/app-credentials-form/form/app-login-signup-button/fl-button/button'),
    "jobs_btn": (By.XPATH, '/html/body/app-root/app-logged-in-shell/div/div[1]/div/app-navigation/app-navigation-primary/div/fl-container/div[5]/fl-highlight/div/fl-callout/fl-callout-trigger/fl-callout/fl-callout-trigger/fl-button/button'),
    "available_jobs": (By.XPATH, '//*[@id="cdk-overlay-3"]/div/fl-callout-content/div/div[2]/app-updates/app-updates-list/div[2]/fl-scrollable-content')
}

path = os.path.join(ScriptDir, 'assets', 'chromedriver.exe')
print(path)

# === Setup Driver ===
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

# === Wait for element helper ===
def wait_and_find(driver, locator, timeout=10):
    try:
        return WebDriverWait(driver, timeout).until(EC.presence_of_element_located(locator))
    except TimeoutException:
        logger.warning(f"❌ Element not found: {locator}")
        return None

# driver = get_driver()



def safe_get(url, max_retries=3):
    """Safely navigate to URL with retry logic"""
    global driver
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Navigating to: {url} (Attempt {attempt + 1})")
            driver.get(url)
            sleep(random.uniform(2, 4))  # Random delay
            return True
            
        except (WebDriverException, urllib3.exceptions.ProtocolError, ConnectionResetError) as e:
            logger.warning(f"Navigation attempt {attempt + 1} failed: {str(e)}")
            
            if attempt < max_retries - 1:
                delay = random.uniform(3, 7)
                logger.info(f"Retrying in {delay:.1f} seconds...")
                sleep(delay)
                
                # Recreate driver if connection issues persist
                if attempt == max_retries - 2:
                    logger.info("Recreating driver for final attempt...")
                    driver.quit()
                    if not setup_driver():
                        return False
            else:
                logger.error(f"Failed to navigate to {url} after {max_retries} attempts")
                return False
                
    return False
# === Login Function ===
def login_setup(user_name: str, password: str):
    url = "https://www.freelancer.in/"
    global driver

    logger.info("🌐 Navigating to Freelancer login page...")
    try:
        driver.get(url)

        # Wait until the page is fully loaded
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        sleep(2)  # Allow JS content to settle

        # Debug screenshot
        driver.save_screenshot("debug_freelancer_home.png")

    except Exception as e:
        logger.error(f"❌ Failed to navigate to {url} - {e}")
        return "❌ Navigation failed"

    # Step 1: Click login link (using more stable CSS selector)
    try:
        login_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*='/login']"))
        )
        login_btn.click()
        logger.info("🔐 Clicked login button.")
    except Exception as e:
        logger.warning(f"❌ Login button not found or clickable: {e}")
        driver.save_screenshot("login_button_fail.png")
        return "❌ Login button not found"

    # Step 2: Enter credentials
    try:
        uname_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "emailOrUsernameInput"))
        )
        uname_input.send_keys(user_name)
        sleep(1)
        pwd_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "passwordInput"))
        )
        pwd_input.send_keys(password)
        sleep(1)
        logger.info("✅ Entered username and password.")
    except Exception as e:
        logger.error(f"❌ Username/Password field not found: {e}")
        return "❌ Input fields missing"

    # Step 3: Click 'Remember Me' checkbox
    try:
        checkbox = driver.find_element(By.CSS_SELECTOR, "label[for='RememberMeCheckbox']")
        checkbox.click()
        logger.info("✅ Checked 'Remember Me'")
    except Exception as e:
        logger.warning(f"⚠️ Could not click checkbox: {e}")

    # Step 4: Click login button
    try:
        login_click = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        )
        login_click.click()
        logger.info("🚀 Login initiated. Please solve CAPTCHA manually if prompted.")

        # Pause to solve CAPTCHA manually
        sleep_time = 40
        logger.info(f"⏳ Waiting {sleep_time}s for CAPTCHA...")
        sleep(sleep_time)

        # Try clicking login again
        try:
            login_click = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
            ).click()
            logger.info("🔁 Retried login after CAPTCHA.")
            #sleep(1000000000)
            
        except:
            logger.warning("❌ Couldn't retry login.")

        logger.info("✅ Login flow completed. Check if logged in successfully.")
        return "✅ Login flow finished (check for CAPTCHA)."
    

    except Exception as e:
        logger.error(f"❌ Final login button not found or failed: {e}")
        return "❌ Login button failed"

# login_setup(user_name="chanduj8351@gmail.com", password="chandu8351")

def is_budget_line(line):
    return bool(re.search(r'[\d,]+\s*[-–]\s*[\d,]+|€|\$|INR|USD|AUD', line))

def is_time_line(line):
    return bool(re.search(r'ago$', line.strip().lower()))

def login():
    url = "https://www.freelancer.in/"

    if not setup_driver():
        logger.error("❌ Driver setup failed.")
        return

    logger.info("🌐 Navigating to Freelancer login page...")
    try:
        safe_get(url)
        WebDriverWait(driver, 15).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        sleep(3)

        # Now locate the unread indicator
        try:
            x = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(xpaths["jobs_btn"])).click()
            sleep(2)
        except Exception as e:
            logger.error(f"❌ Failed to click on jobs button: {e}")
    
    except Exception as e:
        logger.error(f"❌ Navigation failed: {e}")
        

def parse_jobs():
    wait = WebDriverWait(driver, 20)
    updates_xpath = '//fl-callout-content//app-updates//app-updates-list//fl-scrollable-content'
    container = wait.until(EC.presence_of_element_located((By.XPATH, updates_xpath)))
    
    # Find all anchor tags inside the job updates
    anchor_elems = container.find_elements(By.XPATH, ".//a[contains(@href, '/projects/')]")

    jobs_data = []
    
    for a in anchor_elems:
        try:
            job_text = a.text.strip()
            href = a.get_attribute("href").strip()
            lines = [line.strip() for line in job_text.splitlines() if line.strip()]
            
            # Detect if it's a complete job card
            if len(lines) >= 4:
                title = lines[0]
                skills = lines[1]
                budget = lines[2]
                time_posted = lines[3]
                jobs_data.append([title, skills, budget, time_posted, href])
            else:
                print("⚠️ Incomplete job skipped:", lines)
        except Exception as e:
            print("⚠️ Error extracting job:", str(e))

    # Save to CSV
    with open("data/freelancer/jobs.csv", mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(["Job_Title", "Skills", "Budget", "Time_Posted", "Job_Link"])
        for job in jobs_data:
            writer.writerow(job)

    

    print("✅ Cleaned data saved to jobs.csv")



# Main workflow
def freelancer():
    login()
    logger.info('✅ Login Successful.')
    sleep(1)
    parse_jobs()

    # # with open('data/internshala/applied_jobs.txt', 'r', encoding='utf-8') as f:
    # #     jobs = f.readlines()
    # #     applied_jobs = [job.strip() for job in jobs]

    # with open('data/freelancer/jobs.csv', 'r', newline='', encoding='utf-8') as csvfile:
    #     reader = csv.reader(csvfile)
    #     next(reader)  # Skip header


    #     for row in reader:
    #         try:
    #             Job_Title, Skills,Budget,Time, Posted = row

    #             if Job_Title == 
        

    #         except (TimeoutException, NoSuchElementException) as e:
    #             print(f"❌ Failed to apply for {title}: {e}")
    #             continue
    #         except Exception as e:
    #             print(f"❌ Unexpected error: {e}")
    #             continue
    #         finally:
    #             driver.quit()
                
    # print("\n🎯 Finished applying to all eligible jobs.")

if __name__ == "__main__":
    freelancer() 





# def cover_letter_prompt():
#     # Generate cover letter based on job details
#     base_prompt = """
#     You are a highly skilled and professional Cover Letter Generator.

#     Your task is to write a compelling, tailored cover letter for a job application, focusing on why the applicant is a strong fit for the role.

#     You will be provided with specific job details, including the job title, responsibilities, and requirements.

#     Using this information, craft a well-structured cover letter that:
#     - Highlights the applicant's relevant skills, qualifications, and experience
#     - Aligns the applicant’s background with the job description
#     - Demonstrates enthusiasm and professionalism
#     - Concludes with a strong call to action

#     Applicant Details:
#         Name: J Chandu
#         Email: chanduj8351@gmail.com
#         Linkdin: https://www.linkedin.com/in/chandu-j-24558236b/


#     Wait for the job description before generating the cover letter.
#     """
#     return base_prompt

# def parse_jobs_to_csv(html, filename=os.getcwd() + '/data/internshala/jobs.csv'):  
#     soup = BeautifulSoup(html, 'html.parser')
#     internships = soup.find_all('div', class_='individual_internship')

#     with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
#         writer = csv.writer(csvfile)
#         writer.writerow(['Title', 'Company', 'Stipend', 'Experience', 'Posted Time', 'Job Link'])

#         for internship in internships:
#             # Initialize all fields with defaults
#             title = company = stipend = 'N/A'
#             experience = posted_time = job_link = 'N/A'

#             # Extract title and company
#             title_tag = internship.find('h3', class_='job-internship-name')
#             if title_tag:
#                 title = title_tag.text.strip()

#             company_tag = internship.find('p', class_='company-name')
#             if company_tag:
#                 company = company_tag.text.strip()

#             stipend_tag = internship.find('span', class_='desktop')
#             if stipend_tag:
#                 stipend = stipend_tag.text.strip()

       
#             experience = 'N/A'
#             for div in internship.find_all('div', class_='row-1-item'):
#                 if div.find('i', class_='ic-16-briefcase'):
#                     span = div.find('span')
#                     if span:
#                         experience = span.text.strip()
#                     break


#             # Posted Time
#             posted_div = internship.find('div', class_='status-success')
#             if posted_div and posted_div.find('i', class_='ic-16-reschedule'):
#                 span = posted_div.find('span')
#                 if span:
#                     posted_time = span.text.strip()

#             # Job Link
#             job_anchor = internship.find('a', class_='job-title-href')
#             if job_anchor and job_anchor.has_attr('href'):
#                 job_link = 'https://internshala.com' + job_anchor['href']

#             writer.writerow([
#                 title,
#                 company,
#                 stipend,
#                 experience,
#                 posted_time,
#                 job_link
#             ])

#     print(f"✅ Saved {len(internships)} jobs to {filename}")


# def fill_cover_letter(job_details: str) -> bool:
#     """Fill cover letter in application form"""
#     try:
#         logger.info("[WRITE] Filling cover letter...")
        
#         # Wait for cover letter editor
#         WebDriverWait(driver, 10).until(
#             EC.presence_of_element_located((By.CSS_SELECTOR, "#cover_letter_holder .ql-editor[contenteditable='true']"))
#         )
        
#         ql_editor = driver.find_element(By.CSS_SELECTOR, "#cover_letter_holder .ql-editor[contenteditable='true']")
        
#         # Clear and fill content
#         driver.execute_script("""
#             arguments[0].innerHTML = '';
#             arguments[0].focus();
#         """, ql_editor)

#         cv_text = Gpt(prompt= f"Job Details: \n {job_details}", system_prompt=cover_letter_prompt())
        
#         # Type the cover letter
#         ActionChains(driver).move_to_element(ql_editor).click().send_keys(cv_text).perform()
        
#         logger.info("[OK] Cover letter filled successfully")
#         return True
        
#     except Exception as e:
#         logger.error(f"[ERROR] Failed to fill cover letter: {e}")
#         return False


# def submit(job_link):
#     try:
#         submit_btn = WebDriverWait(driver, 60).until(
#             EC.element_to_be_clickable((By.ID, "submit"))
#         )
#         driver.execute_script("arguments[0].scrollIntoView(true);", submit_btn)
#         sleep(1)
#         submit_btn.click()
#         print("🚀 Application submitted successfully.")
#         with open('data/internshala/applied_jobs.txt', 'a') as f:
#             f.write(f"{job_link}\n")

#     except Exception as e:
#         print(f"❌ Submit failed: {e}")


# def fill_additional_questions():
#     try:
#         question_blocks = driver.find_elements(By.CLASS_NAME, "form-group")
#         for block in question_blocks:
#             try:
#                 # Get the question label
#                 label_elem = block.find_element(By.CLASS_NAME, "assessment_question").find_element(By.TAG_NAME, "label")
#                 question_text = label_elem.text.strip()
#                 print(f"🔍 Question: {question_text}")

#                 try:
#                     radio_yes = block.find_element(By.XPATH, './/input[@type="radio" and contains(@id, "Yes")]')
#                     driver.execute_script("arguments[0].click();", radio_yes)
#                     print("✅ Selected YES for radio-type question.\n")
#                     continue  

#                 except:
#                     pass

#                 textarea = block.find_element(By.TAG_NAME, "textarea")
#                 answer = Gpt(
#                     prompt=question_text,
#                     system_prompt=sys_prompt
#                 )
#                 textarea.clear()
#                 textarea.send_keys(answer)        
#                 print(f"✅ Filled answer: {answer}\n")

#             except Exception as e:
#                 # print(f"❌ Error processing question block")
#                 pass

#     except Exception as e:
#         print(f"❌ Error locating additional questions: {e}")



















































# # Setup paths
# ScriptDir = pathlib.Path().absolute()
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# warnings.simplefilter('ignore')

# # === Setup Logging ===
# def setup_logging():
#     logger = logging.getLogger("FreelancerBot")
#     logger.setLevel(logging.INFO)
#     logger.handlers.clear()

#     formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

#     fh = logging.FileHandler('freelancer_bot.log', encoding='utf-8')
#     fh.setFormatter(formatter)
#     logger.addHandler(fh)

#     ch = logging.StreamHandler()
#     ch.setFormatter(formatter)
#     logger.addHandler(ch)

#     return logger

# logger = setup_logging()

# # === XPaths ===
# xpaths = {
#     "login_btn": (By.XPATH, '/html/body/app-root/app-logged-out-shell/app-navigation-logged-out-home/div[2]/fl-container/div/fl-link[1]/a'),
#     "user_name": (By.XPATH, '//*[@id="emailOrUsernameInput"]'),
#     "password": (By.XPATH, '//*[@id="passwordInput"]'),
#     "check_box": (By.CSS_SELECTOR, "label[for='RememberMeCheckbox']"),
#     "login_now": (By.XPATH, '/html/body/app-root/app-logged-out-shell/div/app-login-page/div/div[1]/app-login/app-credentials-form/form/app-login-signup-button/fl-button/button'),
# }

# # === Setup Driver ===
# def get_driver():
#     options = uc.ChromeOptions()
#     options.add_argument('--profile-directory=Default')
#     options.add_argument(f'--user-data-dir={ScriptDir}\\assets\\chromedata')

#     driver = uc.Chrome(options=options, driver_executable_path=os.path.join(ScriptDir, 'assets', 'chromedriver.exe'))
#     driver.maximize_window()
#     return driver

# # === Wait for element helper ===
# def wait_and_find(driver, locator, timeout=10):
#     try:
#         return WebDriverWait(driver, timeout).until(EC.presence_of_element_located(locator))
#     except TimeoutException:
#         logger.warning(f"❌ Element not found: {locator}")
#         return None

# # === Login Function ===
# def login_freelancer(user_name: str, password: str):
#     url = "https://www.freelancer.in/"
#     driver = get_driver()

#     logger.info("🌐 Navigating to Freelancer login page...")
#     try:
#         driver.get(url)
#     except Exception as e:
#         logger.error(f"❌ Failed to navigate to {url} - {e}")
#         return "❌ Navigation failed"

#     # Step 1: Click login button
#     login_btn = wait_and_find(driver, xpaths["login_btn"])
#     if login_btn:
#         login_btn.click()
#         logger.info("🔐 Clicked login button.")
#     else:
#         return "❌ Login button not found"

#     # Step 2: Enter credentials
#     uname_input = wait_and_find(driver, xpaths["user_name"])
#     pwd_input = wait_and_find(driver, xpaths["password"])

#     if uname_input and pwd_input:
#         uname_input.send_keys(user_name)
#         pwd_input.send_keys(password)
#         logger.info("✅ Entered username and password.")
#     else:
#         return "❌ Input fields missing"

#     # Step 3: Click 'Remember Me' checkbox
#     checkbox = wait_and_find(driver, xpaths["check_box"])
#     if checkbox:
#         try:
#             checkbox.click()
#             logger.info("✅ Checked 'Remember Me'")
#         except:
#             logger.warning("⚠️ Couldn't click checkbox (maybe already selected)")
#     else:
#         logger.warning("⚠️ Checkbox not found")

#     # Step 4: Click login button
#     login_click = wait_and_find(driver, xpaths["login_now"])
#     if login_click:
#         login_click.click()
#         logger.info("🚀 Login initiated. Please solve CAPTCHA manually if prompted.")

#         # Wait for CAPTCHA manual solve
#         sleep_time = 40
#         logger.info(f"⏳ Waiting {sleep_time}s for CAPTCHA...")
#         sleep(sleep_time)

#         # Try clicking login again
#         login_click = wait_and_find(driver, xpaths["login_now"])
#         if login_click:
#             login_click.click()
#             logger.info("🔁 Retried login after CAPTCHA.")
#         else:
#             logger.warning("❌ Couldn't retry login.")

#         logger.info("✅ Login flow completed. Manual CAPTCHA may still block automation.")
#         return "✅ Login flow finished (check for CAPTCHA)."
#     else:
#         return "❌ Final login button not found"

# # === Main ===
# if __name__ == "__main__":
#     result = login_freelancer(user_name="chanduj8351@gmail.com", password="chandu8351")
#     print(result)
