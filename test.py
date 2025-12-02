import logging
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

logging.basicConfig(level=logging.INFO)

try:
    chromedriver_autoinstaller.install()
    logging.info("ChromeDriver installed")

    opts = Options()
    logging.info("Creating WebDriver")
    driver = webdriver.Chrome(options=opts)
    logging.info("WebDriver created")

    driver.get("https://google.com")
    logging.info("Loaded URL: %s", driver.current_url)

    input("Press Enter to exit...")

except Exception as e:
    logging.exception("Driver failed: %s", e)
