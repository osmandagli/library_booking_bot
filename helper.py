from selenium.webdriver.chrome.options import Options

def init_options() -> Options:
    options = Options()
    #options.binary_location = "/usr/bin/brave-browser"

    #options.add_argument("--headless=new")
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
