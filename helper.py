import psutil
from selenium.webdriver.chrome.options import Options

def kill_browser(parent: psutil.Process, child_before: list[psutil.Process]) -> None:
    """
    Kill only the Brave browser instance started by Selenium,
    without affecting other Brave windows.
    """

    # Kill child processes (Brave)
    for child in child_before:
        try:
            print("Killing: ", child.pid, child.name())
            child.terminate()
            child.wait(timeout=1)
        except psutil.NoSuchProcess:
            pass
        except psutil.TimeoutExpired:
            child.kill()

    # Kill ChromeDriver parent process
    if parent.is_running():
        try:
            print("Killing parent ChromeDriver process: ", parent.pid)
            parent.terminate()
            parent.wait(timeout=1)
        except psutil.NoSuchProcess:
            pass
        except psutil.TimeoutExpired:
            parent.kill()
    
    print("Browser closed cleanly")

def highlight(driver, el):
    driver.execute_script("arguments[0].style.border='3px solid red'", el)

def normalize_time_string(t: str):
    return t.replace(" ", "")

def init_options() -> Options:
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

    return options
