import time, os, logging
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# --- Logging setup ---
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
download_dir = os.getcwd()  

# --- Date setup ---
date_range = (datetime.now() - timedelta(days=1)).strftime("%d%m%y-%d%m%y")

# --- Credentials ---
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

# --- Chrome configuration ---
chrome_options = Options()
chrome_options.add_argument("--headless=new") 
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")
prefs = {
    "download.default_directory": download_dir,
    "download.prompt_for_download": False,
    "directory_upgrade": True,
    "safebrowsing.enabled": False,
    "safebrowsing.disable_download_protection": True,
}
chrome_options.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(options=chrome_options)

try:
    logging.info("Navigating to target URL and logging in")
    driver.get(os.getenv("WEBSITE"))

    WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[2]/div/div[2]/div/form/div/div[1]/div/input"))).send_keys(username)
    WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[2]/div/div[2]/div/form/div/div[2]/div/input"))).send_keys(password)
    WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[2]/div/div[2]/div/form/div/div[3]/button"))).click()
    time.sleep(8)

    WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/aside/div/div[4]/div/div/nav/ul/li[9]/a"))).click()
    time.sleep(8)

    data = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.ID, "orders_date_range")))
    data.clear()
    data.send_keys(date_range)
    data.send_keys(Keys.ENTER)
    time.sleep(8)
    
    WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[1]/div[2]/div/div/div[1]/div[2]/div[1]/div/div/div/div/div/div/h1/div[1]/button"))).click()
    time.sleep(20)
    
    WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/aside/div/div[4]/div/div/nav/ul/li[11]/a"))).click()
    
    WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, "//td[text()='Marketing Drogaria']/following-sibling::td[3]/a"))).click()
    
    files = os.listdir(download_dir)
    downloaded_files = [f for f in files if f.endswith('.csv')]
    if downloaded_files:
        # sort files by modifi time
        downloaded_files.sort(key=lambda x: os.path.getmtime(os.path.join(download_dir, x)))
        most_recent_file = downloaded_files[-1]  # get the most recent file
        downloaded_file_path = os.path.join(download_dir, most_recent_file)

        # log the final file path and size
        file_size = os.path.getsize(downloaded_file_path)
        logging.info(f"Download completed successfully. File path: {downloaded_file_path}, Size: {file_size} bytes")
    else:
        logging.error("Download failed. No files found.")

except Exception as e:
    logging.error(f"Error: {e}")

finally:
    time.sleep(15)
    driver.quit()
    logging.info("Browser closed.")
