import psutil

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
