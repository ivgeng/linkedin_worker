import json
import time
import logging
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException,ElementClickInterceptedException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

#config_data.json file path
config_file_path = "D:\Python projects\Environments\linkedin_worker\config_data.json"

#read config_data.json and store values
with open(config_file_path,'r') as config_data:
    contents = json.loads(config_data.read())
    url = contents['Login_Data']['URL']
    username = contents['Login_Data']['Username']
    password = contents['Login_Data']['Password']
    work_experience = list(contents['Work_Experience_Data'].values())
    jobinput = list(contents['Job_Search_Input'].values())
    recipients = contents['Message_Info']['Desired_Contacts']
    message = contents['Message_Info']['Message']

#Logger configuration - application.log
log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=log_fmt,filename='application.log')

#xpath_lists
xpath_workexp = ["//*[text()='View Profile']","//li-icon[@aria-label='Add new experience']","//*[text()='Add position']"]
xpath_edit_workexp = ["//*[@placeholder='Ex: Retail Sales Manager']","//*[@placeholder='Ex: Microsoft']","//select[@name='month']",
"//select[@name='year']","//*[@placeholder='Ex: Retail']"]
xpath_open_job_section = ["//*[text()='Skip']","//*[text()='Jobs']"]
xpath_input_jobsearch = ["//input[@aria-label='Search by title, skill, or company']","//input[@aria-label='City, state, or zip code']"]

#Initialization of the Service() class
logging.info("Starting WebDriver")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.maximize_window()

#Open the browser
driver.get(url)

#Check if username or password are correct/ Try to sign in
try:
    #Get username and send key
    driver.find_element(By.NAME,value="session_key").send_keys(username)
    #Get password and send key
    driver.find_element(By.NAME,value="session_password").send_keys(password)
    #Sign in
    driver.find_element(By.XPATH,"//*[@id='main-content']/section[1]/div/div/form/button").click()
    logging.info("Signing in...")
    #Try to open 'Me' button
    driver.implicitly_wait(5)
    driver.find_element(By.XPATH,"//*[text()='Me']").click()
except (NoSuchElementException, ElementClickInterceptedException,TimeoutException, Exception) as e:
    e = ("Sign in failed!")
    logging.error(e)
else:
    logging.info("Sign in successful!")
    logging.info("Trying to open 'Edit work experience' modal window..")
    time.sleep(0.5)


try:
    #Try to open "Edit work experience" modal window
    for xpath in xpath_workexp:
        driver.find_element(By.XPATH,xpath).click()
        driver.implicitly_wait(3)
except (NoSuchElementException, ElementClickInterceptedException,TimeoutException, Exception) as e:
    e = ("Couldn't open 'Edit work experience' modal window")
    logging.error(e)
else:
    logging.info("'Edit work experience' modal window opened successfully!")
    logging.info("Trying to edit work experience...")

#Clear industry field
driver.find_element(By.XPATH,"//*[@placeholder='Ex: Retail']").clear()

try:
    #Input work experience data
    for xpath,work_exp in zip(xpath_edit_workexp, work_experience):
        Edit = driver.find_element(By.XPATH,xpath)
        Edit.send_keys(work_exp)
        time.sleep(0.5)
        Edit.send_keys(Keys.ENTER)
        time.sleep(0.5)
    #Save changes
    driver.find_element(By.XPATH,"//*[text()='Save']").click()
except (NoSuchElementException, ElementClickInterceptedException,TimeoutException, Exception) as e:

    e = ("Editing work experience failed!")
    logging.error(e)
else:
    logging.info("Work experience saved successfully!")

try:
#Open job section
    logging.info("Trying to open 'Jobs' section...")

    for open_job_section in xpath_open_job_section:
        driver.find_element(By.XPATH,open_job_section).click()
        driver.implicitly_wait(3)
except (NoSuchElementException, ElementClickInterceptedException,TimeoutException, Exception) as e:
    e = ("Couldn't open 'Jobs' section")
    logging.error(e)
else:
    logging.info("'Jobs' section opened successfully")
    logging.info("Trying to input job search values...")

try:
#Input job search values
    for xpath_job_search,job_input in zip(xpath_input_jobsearch,jobinput):
        driver.find_element(By.XPATH,xpath_job_search).click()
        driver.implicitly_wait(1)
        driver.find_element(By.XPATH,xpath_job_search).send_keys(job_input)

    driver.find_element(By.XPATH,"//input[@aria-label='Search by title, skill, or company']").click()
    driver.find_element(By.XPATH,"//input[@aria-label='Search by title, skill, or company']").send_keys(Keys.ENTER)
    driver.find_element(By.XPATH,"//input[@aria-label='Search by title, skill, or company']").send_keys(Keys.SPACE)
except (NoSuchElementException, ElementClickInterceptedException,TimeoutException, Exception) as e:
    e = ("Couldn't input job search values!")
    logging.error(e)
else:
    logging.info("Job search input was successful!")
    logging.info("Trying to scrape available jobs...")
    
try:
    #Set Job alert on
    time.sleep(2)
    driver.find_element(By.XPATH,"//span[text()='Set alert']").click()
    time.sleep(0.5)
    #Jobs scrape
    jobs_lists = driver.find_element(By.CLASS_NAME,'jobs-search-results__list')
    jobs = jobs_lists.find_elements(By.CLASS_NAME,"jobs-search-results__list-item")

    list = []
    for i in jobs:
        list.append(i.text.split("\n"))
        time.sleep(0.5)

    new_list = []
    for i in list:
        mydict = {}
        mydict["job"] = i[0]
        mydict["company"] = i[1]
        mydict["location"] = i[2]
        new_list.append(mydict)    
    #Save new list in a .json file
    with open("scrape_results.json", "w") as outfile:
         json.dump(new_list, outfile)  
    time.sleep(1)           
except (NoSuchElementException, ElementClickInterceptedException,TimeoutException, Exception) as e:
    e = ("Couldn't scrape available jobs")
    logging.error(e)
else:
    logging.info("Jobs scrape was successful!")

try:
    #Send message to contacts

    driver.find_element(By.XPATH,'//*[@href="#global-nav-icon--mercado__messaging"]').click()
   # driver.find_element(By.XPATH,'//*[@aria-label="Compose a new message"]').click() 
    for i in recipients:
        time.sleep(0.5)
        driver.find_element(By.XPATH,'//*[@aria-label="Compose a new message"]').click() 
        driver.find_element(By.XPATH,'//*[@placeholder="Type a name or multiple names"]').send_keys(i) 
        time.sleep(1)
        driver.find_element(By.XPATH,'//*[@placeholder="Type a name or multiple names"]').send_keys(Keys.ENTER)
        #driver.find_element(By.XPATH,'//*[@aria-label="Write a message…"]').click()
        time.sleep(0.5)
        driver.find_element(By.XPATH,'//*[@aria-label="Write a message…"]').send_keys(message)
        time.sleep(0.5)
        driver.find_element(By.XPATH,'//button[text()="Send"]').send_keys(Keys.ENTER)
        #driver.implicitly_wait(5)
        #driver.find_element(By.XPATH,'//button[@class="msg-form__send-button artdeco-button artdeco-button--1"]').send_keys(Keys.ENTER)
        time.sleep(1)
except (NoSuchElementException, ElementClickInterceptedException,TimeoutException, Exception) as e:
    e = ("Couldn't send a message")
    logging.error(e)

else:
    logging.info("Messages were sent successfully!")
  
#Stop the browser from closing
while True:
    time.sleep(1)