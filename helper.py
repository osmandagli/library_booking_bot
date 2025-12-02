from selenium.webdriver.chrome.options import Options
import functools
import logging
import traceback

def logged_step(func):
    """Decorator to log each step with detailed error info."""
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        step_name = func.__name__
        logging.info(f"START: {step_name}")

        try:
            result = func(self, *args, **kwargs)
            logging.info(f"FINISH: {step_name}")
            return result

        except Exception as e:
            logging.error(f"ERROR in {step_name}: {e}")
            traceback.print_exc()

            # try to screenshot
            try:
                self.driver.save_screenshot(f"error_{step_name}.png")
                logging.error(f"Screenshot saved: error_{step_name}.png")
            except:
                logging.error("Could not save screenshot")

            raise e

    return wrapper


def init_options() -> Options:
    options = Options()

    options.add_argument("--headless=new")              # NEW headless mode
    options.add_argument("--no-sandbox")                # required on servers
    options.add_argument("--disable-dev-shm-usage")     # prevents crashes
    options.add_argument("--disable-gpu")               # safe
    options.add_argument("--remote-allow-origins=*")    # recent Selenium fix

    return options
