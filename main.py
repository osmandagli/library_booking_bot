import json
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

from helper import init_options, logged_step

import logging
import argparse

class BookingBot:
    def __init__(self, config_path="config.json"):
        try:
            self.load_config(config_path)

            self.options = init_options()

            self.driver = webdriver.Chrome(options=self.options)   # <-- crashing here

            self.wait = WebDriverWait(self.driver, 10)

            self.driver_pid = self.driver.service.process.pid

        except Exception as e:
            logging.exception("FATAL ERROR in __init__: %s", e)
            raise


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

    @logged_step
    def start_new_booking(self):
        xpath = "//h5[contains(normalize-space(.), 'New booking')]/ancestor::a"
        self.wait_and_click(By.XPATH, xpath)
        self.wait_for_page_stable()
        logging.info(f"Clicked New Booking")

    @logged_step
    def select_library(self):
        # open dropdown
        self.wait_and_click(By.CSS_SELECTOR, "input[placeholder='Choose the appointment location']")
        self.wait_for_page_stable()

        library_xpath = f"//div[@class='option' and @value='{self.LIB_ID}']"
        self.wait_and_click(By.XPATH, library_xpath)
        self.wait_for_page_stable()

        logging.info(f"Selected library: {self.LIB_NAME}")

    @logged_step
    def select_service(self):
        self.wait_and_click(By.CSS_SELECTOR, "input[placeholder='Choose a service for which you want to request an appointment']")
        self.wait_for_page_stable()

        service_xpath = f"//div[@class='option' and @value='{self.SERVICE_ID}']"
        self.wait_and_click(By.XPATH, service_xpath)
        self.wait_for_page_stable()

        logging.info(f"Selected SERVICE: { self.SERVICE_NAME}")

    @logged_step
    def select_duration(self):
        duration_el = self.wait_for_element(By.ID, "durata")
        Select(duration_el).select_by_value(self.DURATION_ID)
        self.wait_for_page_stable()
        logging.info(f"Selected duration: {self.DURATION_HOURS}")

    @logged_step
    def click_next(self):
        self.wait_and_click(By.CSS_SELECTOR, "button[data-cypress='continua']")
        self.wait_for_page_stable()

    @logged_step
    def click_final_next(self):
        xpath = "//a[contains(text(), 'Next') and contains(@class, 'btn-primary')]"
        self.wait_and_click(By.XPATH, xpath)
        self.wait_for_page_stable()
        logging.info("Clicked FINAL NEXT button")

    @logged_step
    def select_first_available_day(self):
        # Wait for calendar to render
        self.wait_for_page_stable()

        # Try multiple selectors (sometimes the HTML changes)
        selectors = [
            "div.day:not(.unselectable)",
            ".day.disponibile",
            "div.day-wrapper div.day:not(.unselectable)"
        ]

        day_el = None

        for css in selectors:
            try:
                day_el = self.wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, css))
                )
                break
            except:
                continue

        if not day_el:
            # Save HTML for debugging
            with open("calendar_debug.html", "w") as f:
                f.write(self.driver.page_source)

        logging.error("❌ No available day found. HTML saved to calendar_debug.html")
        raise Exception("No available day found.")

        # Click using JS
        day_text = day_el.text.strip()
        self.driver.execute_script("arguments[0].click();", day_el)
        self.wait_for_page_stable()

        logging.info(f"Selected first available day: {day_text}")

    @logged_step
    def select_time_slot(self):
        time_xpath = (
            "//div[contains(@class,'chip') and contains(@class,'disponibile')]"
            f"[.//span[contains(normalize-space(), '{self.PREFERRED_TIME}')]]"
        )
        self.wait_and_click(By.XPATH, time_xpath)
        self.wait_for_page_stable()
        logging.info(f"Selected time slot: {self.PREFERRED_TIME}")

    @logged_step
    def fill_user_info(self):
        self.wait_for_element(By.NAME, "codice_fiscale").send_keys(self.USER_CF)
        self.wait_for_element(By.NAME, "cognome_nome").send_keys(self.USER_NAME)
        self.wait_for_element(By.NAME, "email").send_keys(self.USER_EMAIL)
        self.wait_for_page_stable()

        logging.info(f"User info filled")

    @logged_step
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
            time.sleep(1)

            print("\nBooking bot finished successfully!\n")

        except Exception as e:
            logging.ERROR("Fuck")
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
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.json")
    args = parser.parse_args()

    bot = BookingBot(args.config)
    bot.run()



