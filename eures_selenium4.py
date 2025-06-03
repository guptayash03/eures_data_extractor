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
options.headless = True  # it's more scalable to work in headless mode
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
    job_titles = element.find_elements(By.TAG_NAME, 'h1')
    if job_titles:
        job_titles = job_titles[0].text
    else:
        job_titles = None

    occupations = element.find_elements(
        By.XPATH, './/jv-se-requirement-expandable//span[contains(@class, "ecl-accordion__toggle-title")]')
    occupation = ", ".join([span.text for span in occupations])

    creation_dt = element.find_elements(
        By.CSS_SELECTOR, "span[id*='jv-lastModificationDate']")
    if creation_dt:
        creation_dt = creation_dt[0].text
    else:
        creation_dt = None

    employer = element.find_elements(
        By.CSS_SELECTOR, "h2[class*='ecl-u-type-heading-2 ecl-u-mt-s']")
    if employer:
        employer = employer[0].text
    else:
        employer = None

    job_sector = element.find_elements(
        By.CSS_SELECTOR, "span[id*='jv-employer-sector-codes-result']")
    if job_sector:
        job_sector = job_sector[0].text
    else:
        job_sector = None

    job_type = element.find_elements(
        By.CSS_SELECTOR, "span[id*='jv-position-schedule-result']")
    if job_type:
        job_type = job_type[0].text
    else:
        job_type = None

    contract_type = element.find_elements(
        By.CSS_SELECTOR, "span[id*='jv-position-type-code-result']")
    if contract_type:
        contract_type = contract_type[0].text
    else:
        contract_type = None

    location = element.find_elements(
        By.CSS_SELECTOR, "span[class*='jv-address-country']")
    if location:
        location = location[0].text
    else:
        location = None

    city = element.find_elements(
        By.CSS_SELECTOR, "span[class*='jv-address-city-name']")
    if city:
        city = city[0].text
    else:
        city = None

    languages = element.find_elements(
        By.XPATH, './/jv-se-requirement-language//span[contains(@class, "ecl-accordion__toggle-title")]')
    language = ", ".join([span.text for span in languages])

    skills = element.find_elements(
        By.XPATH, './/div[contains(@id, "jv-details-job-requirements-skills-section")]//dd')
    skill = ", ".join([span.text for span in skills])

    educations = element.find_elements(
        By.XPATH, './/div[contains(@id, "jv-details-job-requirements-education-level-section")]//dd')
    education = ", ".join([span.text for span in educations])

    legal_ID = element.find_elements(
        By.CSS_SELECTOR, "dd[id*='jv-details-employer-legal-id']")
    if legal_ID:
        legal_ID = legal_ID[0].text
    else:
        legal_ID = None

    how_to_apply = element.find_elements(
        By.CSS_SELECTOR, "span[id*='jv-details-application-instruction-0']")
    if how_to_apply:
        how_to_apply = how_to_apply[0].text
    else:
        how_to_apply = None

    phone = element.find_elements(
        By.CSS_SELECTOR, "li[id*='jv-details-telNumber-0-0']")
    if phone:
        phone = phone[0].text
    else:
        phone = None

    contact = element.find_elements(
        By.CSS_SELECTOR, "li[id*='jv-details-displayName-0']")
    if contact:
        contact = contact[0].text
    else:
        contact = None

    email = element.find_elements(
        By.XPATH, './/li[contains(@id, "jv-details-emails-0-0")]//a')
    email = ", ".join([span.text for span in email])

    description_elements = element.find_elements(By.XPATH, './/p//p')
    description = ", ".join([span.text for span in description_elements])

    # job_link_element = element.find_elements(By.XPATH, './/h3//a')
    # job_link = job_link_element[0].get_attribute('href')

    return {
        "Job Title": job_titles,
        "Occupation": occupation,  # Assuming occupation is the first dd element
        "Employer": employer,
        "Creation date": creation_dt,
        "Country": location,
        "City": city,
        "Contract Type": contract_type,
        "Job Type": job_type,
        "Job Sector": job_sector,
        "Language": language,
        "Skills": skill,
        "Education": education,
        "Legal ID": legal_ID,
        "How to Apply": how_to_apply,
        "Contact": contact,
        "Email": email,
        "Phone": phone,
        # "Job link" : job_link,
        "Job Description": description,

    }


def flatten2(myList):
    flatList = []
    for item in myList:
        if isinstance(item, list):
            flatList.extend(flatten2(item))
        else:
            flatList.append(item)
    return flatList


num_api_calls = 1
urlString = 'https://europa.eu/eures/portal/jv-se/search?page={0}&resultsPerPage=10&orderBy=BEST_MATCH&locationCodes=nl&lang=en'
# jobsnew=[]
extracted_data = []
start_time = time.time()  # Start the timer here

for page in range(1, num_api_calls+1):
    print("Page Number:", page)
    driver.get(urlString.format(page))
#    driver.get('https://ec.europa.eu/eures/portal/jv-se/search?page={0}&resultsPerPage=50&orderBy=BEST_MATCH&locationCodes=de&keywordsEverywhere=data%20engineer&positionScheduleCodes=fulltime&lang=en'.format(page))
    time.sleep(10)

    # content = driver.find_element(By.CSS_SELECTOR, "div[class*='ecl-u-pv-l ecl-u-border-bottom ecl-u-border-color-primary-20 ng-star-inserted']")
    # # print("**************")
    # # print(content.text)
    job_link_element = driver.find_elements(By.XPATH, './/h3//a')
    jobs = [link.get_attribute('href') for link in job_link_element]
    # jobssnew=jobs
    # if len(jobsnew)==0:
    #     jobsnew = jobs
    # else:
    #     jobsnew.extend(jobs)
    if len(jobs) == 0:
        print("No jobs found on page", page)
        continue
    print("Found", len(jobs), "jobs on page", page)

    for job in jobs:
        driver.get(job)
        time.sleep(10)
        job_data = driver.find_element(By.TAG_NAME, 'main')
        extracted_data.append(extract_data(job_data))

# Calculate and print the total execution time
execution_time = time.time() - start_time
print("Total execution time:", execution_time, "seconds")

if extracted_data:
    df = pd.DataFrame(extracted_data)
    df.to_csv("result.csv", index=False)
