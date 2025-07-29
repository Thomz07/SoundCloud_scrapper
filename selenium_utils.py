import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from config import HEADLESS


def create_chrome_opts():
    opts = webdriver.ChromeOptions()
    if HEADLESS:
        opts.add_argument("--headless=new")
        opts.add_argument("--window-size=1920,1080")
    opts.add_experimental_option("excludeSwitches", ["enable-logging"])
    opts.add_argument("--log-level=3")
    return opts


def create_driver():
    return webdriver.Chrome(
        service=Service(log_path=os.devnull),
        options=create_chrome_opts()
    )


def scroll_to_bottom(driver):
    last_h = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_h = driver.execute_script("return document.body.scrollHeight")
        if new_h == last_h:
            break
        last_h = new_h


def wait_for_mp3_download(folder, timeout=300):
    end = time.time() + timeout
    while time.time() < end:
        files = [f for f in os.listdir(folder) if f.endswith((".mp3", ".crdownload"))]
        if not files:
            time.sleep(1)
            continue
        files.sort(key=lambda x: os.path.getmtime(os.path.join(folder, x)))
        latest = files[-1]
        path = os.path.join(folder, latest)
        if latest.endswith(".crdownload"):
            time.sleep(1)
            continue
        size1 = os.path.getsize(path)
        time.sleep(2)
        if size1 == os.path.getsize(path):
            return path
    return None
