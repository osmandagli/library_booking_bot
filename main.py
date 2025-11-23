import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from helper import kill_browser, highlight
from psutil import Process
import time
import json

chromedriver_autoinstaller.install()  # installs correct version

options = Options()
options.binary_location = "/usr/bin/brave-browser"

options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-extensions")
options.add_argument("--single-process")
options.add_argument("--enable-javascript")
options.add_argument("--js-flags=--expose-gc")
options.add_argument("--disable-gpu")
options.add_argument("--remote-allow-origins=*")
options.add_argument("--disable-web-security")
options.add_argument("--allow-running-insecure-content")
options.add_argument("--enable-features=NetworkService,NetworkServiceInProcess")
options.add_argument("--user-data-dir=/tmp/brave_profile_selenium")


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
# open dropdown
input_box = wait.until(
    EC.element_to_be_clickable(
        (By.CSS_SELECTOR, "input[placeholder='Choose the appointment location']")
    )
)
driver.execute_script("arguments[0].scrollIntoView({block:'center'});", input_box)
input_box.click()
time.sleep(1)

# get all visible options
location_options = driver.find_elements(By.CSS_SELECTOR, "div.options div.option")

locations = []
for opt in location_options:
    name = opt.text.strip()
    value = opt.get_attribute("value")
    locations.append({"name": name, "value": value})

print("FOUND LOCATIONS:")
for loc in locations:
    print(f"{loc['value']} → {loc['name']}")

bicf = wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, "//div[@class='option' and @value='25']")
    )
)
driver.execute_script("arguments[0].scrollIntoView({block:'center'});", bicf)
time.sleep(0.2)
bicf.click()

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

floor = wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, "//div[@class='option' and @value='50']")
    )
)
driver.execute_script("arguments[0].scrollIntoView({block:'center'});", floor)
time.sleep(0.2)
floor.click()
time.sleep(3)

duration_select = wait.until(
    EC.presence_of_element_located((By.CSS_SELECTOR, "select#durata"))
)

sel = Select(duration_select)
sel.select_by_value("7200")  # 2 hours
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

slot_19 = wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, "//div[@aria-label='11:00click to book']")
    )
)

driver.execute_script("arguments[0].scrollIntoView({block:'center'});", slot_19)
slot_19.click()
print("Clicked 11:00 slot")
time.sleep(2)

cf_input = wait.until(
    EC.element_to_be_clickable((By.NAME, "codice_fiscale"))
)

cf_input.clear()
cf_input.send_keys("CVLYMN98R66Z243C")

print("Typed codice fiscale")

cn_input = wait.until(
    EC.element_to_be_clickable((By.NAME, "cognome_nome"))
)

cn_input.clear()
cn_input.send_keys("CAVILDAK YASEMIN")

email_input = wait.until(
    EC.element_to_be_clickable((By.NAME, "email"))
)

email_input.clear()
email_input.send_keys("yasemin.cavildak@studenti.unimi.it")
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

