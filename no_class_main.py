import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from helper import normalize_time_string, init_options
from psutil import Process
import time
import json

chromedriver_autoinstaller.install()  # installs correct version

options = init_options()

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 10)

driver_pid = driver.service.process.pid
parent = Process(driver_pid)
child_before = parent.children(recursive=True)

driver.get("https://prenotabiblio.sba.unimi.it/portalePlanning/biblio")
time.sleep(5)

el = wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, "//h5[contains(normalize-space(.), 'New booking')]/ancestor::a")
    )
)

# Highlight so we SEE it's the right one
driver.execute_script("arguments[0].style.border='3px solid red'", el)
time.sleep(1)

# Scroll & click
driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", el)
time.sleep(0.5)
el.click()

print("Clicked!")
time.sleep(5)

# Click the custom select input to open the dropdown
input_box = wait.until(
    EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "input[placeholder='Choose the appointment location']")
    )
)
driver.execute_script("arguments[0].scrollIntoView({block:'center'});", input_box)
input_box.click()
time.sleep(1)

with open("config.json") as f:
    cfg = json.load(f)

LIB_NAME = cfg["library"]
LIB_ID = cfg["libraries"][LIB_NAME]

library_xpath = f"//div[@class='option' and @value='{LIB_ID}']"
library_element = wait.until(EC.element_to_be_clickable((By.XPATH, library_xpath)))
library_element.click()

print("Clicked Biblioteca BICF!")
time.sleep(2)

# Click the custom select input to open the dropdown
input_box_2 = wait.until(
    EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "input[placeholder='Choose a service for which you want to request an appointment']")
    )
)

driver.execute_script("arguments[0].scrollIntoView({block:'center'});", input_box_2)
input_box_2.click()
time.sleep(1)

SERVICE_NAME = cfg["service"]
SERVICE_ID = cfg["services"][SERVICE_NAME]

service_xpath = f"//div[@class='option' and @value='{SERVICE_ID}']"
service_element = wait.until(EC.element_to_be_clickable((By.XPATH, service_xpath)))
service_element.click()

DURATION_HOURS = cfg["duration_hours"]
DURATION_ID = cfg["durations"][str(DURATION_HOURS)]

duration_select = wait.until(EC.presence_of_element_located((By.ID, "durata")))
from selenium.webdriver.support.ui import Select

Select(duration_select).select_by_value(DURATION_ID)
print("Selected 2 hours")
time.sleep(3)

next_btn = wait.until(
    EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "button[data-cypress='continua']")
    )
)

driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", next_btn)
time.sleep(0.3)
next_btn.click()

print("Clicked NEXT button!")
time.sleep(3)

first_clickable = wait.until(
    EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "div.day:not(.unselectable)")
    )
)

driver.execute_script("arguments[0].scrollIntoView({block:'center'});", first_clickable)
time.sleep(0.2)
day_text = first_clickable.text.strip()
first_clickable.click()

print("Clicked first available day:", day_text)
time.sleep(3)

PREFERRED_TIME = cfg["preferred_time"]
pattern = normalize_time_string(PREFERRED_TIME)

time_xpath = (
    "//div[contains(@class,'chip') and contains(@class,'disponibile')]"
    f"[.//span[contains(normalize-space(), '{PREFERRED_TIME}')]]"
)

print("Looking for slot:", PREFERRED_TIME)

time_slot = wait.until(EC.element_to_be_clickable((By.XPATH, time_xpath)))

driver.execute_script("arguments[0].scrollIntoView({block:'center'});", time_slot)
time.sleep(0.2)
time_slot.click()

print("Selected time slot:", PREFERRED_TIME)
time.sleep(2)

USER_CF = cfg["user_info"]["codice_fiscale"]
USER_EMAIL = cfg["user_info"]["email"]
USER_NAME = cfg["user_info"]["name"]

cf_input = wait.until(
    EC.element_to_be_clickable((By.NAME, "codice_fiscale"))
)

cf_input.clear()
cf_input.send_keys(USER_CF)

print("Typed codice fiscale")

cn_input = wait.until(
    EC.element_to_be_clickable((By.NAME, "cognome_nome"))
)

cn_input.clear()
cn_input.send_keys(USER_NAME)

email_input = wait.until(
    EC.element_to_be_clickable((By.NAME, "email"))
)

email_input.clear()
email_input.send_keys(USER_EMAIL)
time.sleep(3)

#confirm_btn = wait.until(
#    EC.element_to_be_clickable(
#        (By.XPATH, "//button[normalize-space()='Confirm']")
#    )
#)
#
#driver.execute_script("arguments[0].scrollIntoView({block:'center'});", confirm_btn)
#time.sleep(0.2)
#confirm_btn.click()
#
#print("Clicked Confirm")
#time.sleep(2)


driver.quit()
time.sleep(1)

