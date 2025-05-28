import time 
import pandas as pd 
from selenium import webdriver 
from selenium.webdriver import Chrome 
from selenium.webdriver.chrome.service import Service 
from selenium.webdriver.common.by import By 
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import StaleElementReferenceException


# start by defining the options 
options = webdriver.ChromeOptions() 
options.headless = True # it's more scalable to work in headless mode 
# normally, selenium waits for all resources to download 
#  we don't need it as the page also populated with the running javascript code. 
options.page_load_strategy = 'none' 
#  this returns the path web driver downloaded 
chrome_path = ChromeDriverManager().install() 
chrome_service = Service(chrome_path) 
# # pass the defined options and service objects to initialize the web driver 
driver = Chrome(options=options, service=chrome_service) 
driver.implicitly_wait(5)

# driver = Chrome(service=Service('/usr/local/bin/chromedriver'))


def extract_data(element): 
    job_titles = element.find_elements(By.TAG_NAME, 'h3')
    if job_titles:
      job_titles = job_titles[0].text
    else:
      job_titles = None 

    occupation_elements = element.find_elements(By.XPATH, './/dd//span')
    occupation = ", ".join([span.text for span in occupation_elements])

    creation_dt = element.find_elements(By.CSS_SELECTOR, "li[id*='date']")
    if creation_dt:
      creation_dt_text = creation_dt[0].text
      creation_dt = creation_dt_text.replace("Publication date: ", "").strip()
    else:
      creation_dt = None  

    employer = element.find_elements(By.CSS_SELECTOR, "li[class*='ecl-content-block__primary-meta-item ng-star-inserted']")
    if employer:
      employer = employer[0].text
    else:
      employer = None 

    location = element.find_elements(By.CSS_SELECTOR, "span[class*='ng-star-inserted']")
    if location:
      location = location[0].text
    else:
      location = None  

    job_type = element.find_elements(By.CSS_SELECTOR, "span[id*='position-schedule-0']")
    if job_type:
      job_type = job_type[0].text
    else:
      job_type = None  
    
    description = element.find_elements(By.CSS_SELECTOR, "div[class*='ecl-content-block__description ng-star-inserted']")
    if description:
      description = description[0].text
    else:
      description = None

    job_link_element = element.find_elements(By.XPATH, './/h3//a')
    job_link = job_link_element[0].get_attribute('href')

    


    return {
      "Job Title" : job_titles,
      "Occupation" : occupation, # Assuming occupation is the first dd element
      "Creation date" : creation_dt, 
      "Employer" : employer,
      "Location" : location,
      "Job_Type" : job_type,
        # "Industry": 
      "Job link" : job_link,
      "Job Description" : description,

    } 


def flatten2 (myList):
	flatList = []
	for item in myList:
		if isinstance(item, list):
			flatList.extend(flatten2(item))
		else:
			flatList.append(item)
	return flatList


num_api_calls = 1

#jobsnew=[]
extracted_data=[]
start_time = time.time()  # Start the timer here

for page in range(1, num_api_calls+1):
    print("Page Number:", page)
    driver.get('https://europa.eu/eures/portal/jv-se/search?page={0}&resultsPerPage=50&orderBy=BEST_MATCH&locationCodes=nl&lang=en'.format(page))
#    driver.get('https://ec.europa.eu/eures/portal/jv-se/search?page={0}&resultsPerPage=50&orderBy=BEST_MATCH&locationCodes=de&keywordsEverywhere=data%20engineer&positionScheduleCodes=fulltime&lang=en'.format(page))
    time.sleep(20)

    # content = driver.find_element(By.CSS_SELECTOR, "div[class*='ecl-u-pv-l ecl-u-border-bottom ecl-u-border-color-primary-20 ng-star-inserted']")
    # # print("**************")
    # # print(content.text)
    jobs = driver.find_elements(By.TAG_NAME, 'search-page-jv-result-summary')
    #jobssnew=jobs
    # if len(jobsnew)==0:
    #     jobsnew = jobs    
    # else:
    #     jobsnew.extend(jobs) 
    if len(jobs) == 0:
        print("No jobs found on page", page)
        continue
    print("Found", len(jobs), "jobs on page", page)

    for job in jobs:
        
        extracted_data.append(extract_data(job))

# Calculate and print the total execution time
execution_time = time.time() - start_time
print("Total execution time:", execution_time, "seconds") 

if extracted_data:
    df = pd.DataFrame(extracted_data)
    df.to_csv("result2.csv", index=False)
