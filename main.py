import json
import time
from psutil import Process

import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

from helper import normalize_time_string, init_options

import logging

class BookingBot:
    def __init__(self, config_path="config.json"):
        self.load_config(config_path)

        chromedriver_autoinstaller.install()

        self.options = init_options()
        self.driver = webdriver.Chrome(options=self.options)
        self.wait = WebDriverWait(self.driver, 10)

        # track chrome process to kill safely
        self.driver_pid = self.driver.service.process.pid
        self.parent = Process(self.driver_pid)
        self.child_before = self.parent.children(recursive=True)

    def wait_for_page_stable(self, timeout=5):
        """
        Wait until the page stops loading dynamic content (Vue/JS rendering).
        """
        last_html = ""
        for _ in range(timeout * 2):
            html = self.driver.page_source
            if html == last_html:
                return
            last_html = html
            time.sleep(0.5)
    
    def wait_for_element(self, by, value, timeout=10):
        for _ in range(timeout):
            try:
                return self.wait.until(EC.presence_of_element_located((by, value)))
            except:
                time.sleep(1)

    def wait_and_click(self, by, value, timeout=10):
        for _ in range(timeout):
            try:
                el = self.wait.until(EC.element_to_be_clickable((by, value)))
                self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
                el.click()
                return el
            except Exception:
                time.sleep(0.5)

    # Load config
    def load_config(self, path):
        with open(path) as f:
            cfg = json.load(f)
        
        self.LIB_NAME = cfg["library"]
        self.LIB_ID = cfg["libraries"][self.LIB_NAME]

        self.SERVICE_NAME = cfg["service"]
        self.SERVICE_ID = cfg["services"][self.SERVICE_NAME]

        self.DURATION_HOURS = cfg["duration_hours"]
        self.DURATION_ID = cfg["durations"][str(self.DURATION_HOURS)]

        self.PREFERRED_TIME = cfg["preferred_time"]

        self.USER_CF = cfg["user_info"]["codice_fiscale"]
        self.USER_EMAIL = cfg["user_info"]["email"]
        self.USER_NAME = cfg["user_info"]["name"]
    
    def click_xpath(self, xpath, scroll=True):
        el = self.wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
        if scroll:
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});", el
            )
        el.click()
        return el

    def click_css(self, css, scroll=True):
        el = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, css)))
        if scroll:
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});", el
            )
        el.click()
        return el

    def open_site(self):
        self.driver.get("https://prenotabiblio.sba.unimi.it/portalePlanning/biblio")
        time.sleep(4)

    def start_new_booking(self):
        xpath = "//h5[contains(normalize-space(.), 'New booking')]/ancestor::a"
        self.wait_and_click(By.XPATH, xpath)
        self.wait_for_page_stable()
        logging.info(f"Clicked New Booking")

    def select_library(self):
        # open dropdown
        self.wait_and_click(By.CSS_SELECTOR, "input[placeholder='Choose the appointment location']")
        self.wait_for_page_stable()

        library_xpath = f"//div[@class='option' and @value='{self.LIB_ID}']"
        self.wait_and_click(By.XPATH, library_xpath)
        self.wait_for_page_stable()

        logging.info(f"Selected library: {self.LIB_NAME}")


    def select_service(self):
        self.wait_and_click(By.CSS_SELECTOR, "input[placeholder='Choose a service for which you want to request an appointment']")
        self.wait_for_page_stable()

        service_xpath = f"//div[@class='option' and @value='{self.SERVICE_ID}']"
        self.wait_and_click(By.XPATH, service_xpath)
        self.wait_for_page_stable()

        logging.info(f"Selected SERVICE: { self.SERVICE_NAME}")


    def select_duration(self):
        duration_el = self.wait_for_element(By.ID, "durata")
        Select(duration_el).select_by_value(self.DURATION_ID)
        self.wait_for_page_stable()
        logging.info(f"Selected duration: {self.DURATION_HOURS}")


    def click_next(self):
        self.wait_and_click(By.CSS_SELECTOR, "button[data-cypress='continua']")
        self.wait_for_page_stable()

    def click_final_next(self):
        xpath = "//a[contains(text(), 'Next') and contains(@class, 'btn-primary')]"
        self.wait_and_click(By.XPATH, xpath)
        self.wait_for_page_stable()
        logging.info("Clicked FINAL NEXT button")

    def select_first_available_day(self):
        # find element first
        day_el = self.wait.until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.day:not(.unselectable)"))
        )
        day_text = day_el.text.strip()
        # now click using JS to avoid stale after click
        self.driver.execute_script("arguments[0].click();", day_el)
        self.wait_for_page_stable()

        logging.info(f"Selected first available day: {day_text}")

    def select_time_slot(self):
        time_xpath = (
            "//div[contains(@class,'chip') and contains(@class,'disponibile')]"
            f"[.//span[contains(normalize-space(), '{self.PREFERRED_TIME}')]]"
        )
        self.wait_and_click(By.XPATH, time_xpath)
        self.wait_for_page_stable()
        logging.info(f"Selected time slot: {self.PREFERRED_TIME}")


    def fill_user_info(self):
        self.wait_for_element(By.NAME, "codice_fiscale").send_keys(self.USER_CF)
        self.wait_for_element(By.NAME, "cognome_nome").send_keys(self.USER_NAME)
        self.wait_for_element(By.NAME, "email").send_keys(self.USER_EMAIL)
        self.wait_for_page_stable()

        logging.info(f"User info filled")

    def click_confirm(self):
        xpath = "//button[normalize-space(text())='Confirm']"
        self.wait_and_click(By.XPATH, xpath)
        self.wait_for_page_stable()
        logging.info("Clicked Confirm button")

    
    def run(self):
        try:
            self.open_site()
            self.start_new_booking()
            self.select_library()
            self.select_service()
            self.select_duration()
            self.click_next()
            self.select_first_available_day()
            self.select_time_slot()
            self.fill_user_info()
            self.click_final_next()
            self.click_confirm()

            print("\nBooking bot finished successfully!\n")

        except Exception as e:
            #self.driver.save_screenshot("error.png")
            #print("ERROR — Screenshot saved as error.png")
            raise e

        finally:
            self.driver.quit()
            time.sleep(1)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    bot = BookingBot("config.json")
    bot.run()



