import os
import time
import pandas as pd
import shutil
import sys

from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

from cookies_util import load_cookies, save_cookies

from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class MaiMaiScraper:
    def __init__(self, filter_page="https://maimai.cn/ent/talents/discover/search_v2/", profile_url=None, excel_file=None, url_column='Link', profiles=None):        
        chrome_options = webdriver.ChromeOptions()
        #chrome_options.add_argument('--proxy-server=https://127.0.0.1:11304')
        #self.download_dir = r"C:\\AnyHelper\\MaiMai_auto\\output"  # Specify your desired download directory
        #prefs = {"download.default_directory": self.download_dir}
        #chrome_options.add_experimental_option("prefs", prefs)

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        self.login_url = "https://maimai.cn/platform/login"
        self.filter_page = filter_page
        self.profile_url = profile_url
        self.excel_file = excel_file
        self.url_column = url_column
        self.cookies = []
        self.wait_10s = WebDriverWait(self.driver, 10, 0.5)
        self.wait_180s = WebDriverWait(self.driver, 180, 0.5)
        self.filter_count = 0
        self.connect_count = 0
        self.profiles = profiles

        self.candidate_df = pd.DataFrame(columns=[
            "Name", "URL", "Description", "Industry", "Location", "IP Location",
            "Position 1", "Company 1", "Duration 1", "Job Details 1", "Job Keywords 1",
            "Position 2", "Company 2", "Duration 2", "Job Details 2", "Job Keywords 2",
            "Position 3", "Company 3", "Duration 3", "Job Details 3", "Job Keywords 3",
            "University 1", "University Time 1", "Major 1", "Degree 1",
            "University 2", "University Time 2", "Major 2", "Degree 2"
        ])

    def upload_link(self):
        self.driver.get(self.filter_page)
        #self.wait_10s.until(expected_conditions.presence_of_element_located(
        #    (By.XPATH, '//div[@data-x-deferred-did-intersect]')
        #))*/
        print(f"Link uploaded: {self.filter_page}")
        time.sleep(5)  # wait for the page to load

    def login_ez(self):
        self.driver.get(self.login_url)

        if os.path.exists('cookies.pkl'):
            cookies = load_cookies()
            self.driver.delete_all_cookies()
            for cookie in cookies:
                self.driver.add_cookie(cookie)
            self.driver.refresh()
        else:
            self.wait_180s.until(EC.url_contains("https://maimai.cn/feed_list"))
            self.cookies = self.driver.get_cookies()
            save_cookies(self.cookies)

        print("登录成功 - login success")

    def login(self):
        self.driver.get(self.login_url)
        print("Cookie support will be added later \n")
        self.wait_180s.until(EC.url_contains("https://maimai.cn/feed_list"))

    def quit(self):
        self.driver.quit()

    def scroll_and_load(self, max_people=100):
        #scrollable_div = self.driver.find_element(By.XPATH, '//div[@data-x--search-results-container]')
        current_count = 0
        while True:
            # scroll down 1000 pixels
            self.driver.execute_script('window.scrollBy(0, 1000)')
            time.sleep(2)  # Wait for the new items to load

            # Count the number of loaded items
            new_count = len(self.driver.find_elements(By.XPATH, '//*[@id="react_app"]/div/div/div[2]/div/div[1]/div[2]/div/div/div[1]/ul/div'))
            if new_count == current_count:
                # If no new items loaded, exit the loop
                break
            current_count = new_count

            # If the number of loaded items exceeds the maximum, exit the loop
            if current_count >= max_people:
                break

        print(f"Loaded {current_count} people.")
    
    def extract_info(self):
        info = {
            "Name": "",
            "URL": self.driver.current_url,
            "Description": "",
            "Industry": "",
            "Location": "",
            "IP Location": "",
            "Position 1": "",
            "Company 1": "",
            "Duration 1": "",
            "Job Details 1": "",
            "Job Keywords 1": "",
            "Position 2": "",
            "Company 2": "",
            "Duration 2": "",
            "Job Details 2": "",
            "Job Keywords 2": "",
            "Position 3": "",
            "Company 3": "",
            "Duration 3": "",
            "Job Details 3": "",
            "Job Keywords 3": "",
            "University 1": "",
            "University Time 1": "",
            "Major 1": "",
            "Degree 1": "",
            "University 2": "",
            "University Time 2": "",
            "Major 2": "",
            "Degree 2": ""
        }

        try:
            name_element = self.driver.find_element(By.XPATH, "//h1[@class='maimai-personal-card-name']")
            info["Name"] = name_element.text.strip()
        except NoSuchElementException:
            print("Name not found")

        try:
            description_element = self.driver.find_element(By.XPATH, "//div[@class='maimai-personal-card-desc']")
            info["Description"] = description_element.text.strip()
        except NoSuchElementException:
            print("Description not found")

        try:
            industry_element = self.driver.find_element(By.XPATH, "//span[contains(text(),'所在行业：')]/following-sibling::span")
            info["Industry"] = industry_element.text.strip()
        except NoSuchElementException:
            print("Industry not found")

        try:
            location_element = self.driver.find_element(By.XPATH, "//span[contains(text(),'所在地区：')]/following-sibling::span")
            info["Location"] = location_element.text.strip()
        except NoSuchElementException:
            print("Location not found")

        try:
            ip_location_element = self.driver.find_element(By.XPATH, "//span[contains(text(),'IP地址所在地：')]/following-sibling::span")
            info["IP Location"] = ip_location_element.text.strip()
        except NoSuchElementException:
            print("IP Location not found")

        return info
    
    def click_and_extract(self):
        candidates = self.driver.find_elements(By.XPATH, '//*[@id="react_app"]/div/div/div[2]/div/div[1]/div[2]/div/div/div/ul')
        for candidate in candidates:
            # Click on the candidate's profile link
            try:
                candidate.click()
                time.sleep(2)  # Wait for the profile to load
            except NoSuchElementException:
                print("Profile link not found")
                continue  # Move to the next candidate if profile link not found

            # Extract the information from the profile page
            try:
                candidate_info = self.extract_info()
                self.candidate_df = self.candidate_df.append(candidate_info, ignore_index=True)
            except Exception as e:
                print(f"Failed to extract information: {e}")

            # Go back to the search results page
            self.driver.execute_script("window.history.go(-1)")
            time.sleep(2)  # Wait for the page to load

        # Export DataFrame to Excel file
        output_file_path = "C:/AnyHelper/MaiMai_auto/output/candidates_info.xlsx"
        self.candidate_df.to_excel(output_file_path, index=False)
        print(f"Exported candidate information to {output_file_path}")

    def run(self):
        self.driver.maximize_window()
    
        self.login_ez()
        time.sleep(1)
        self.wait_180s.until(EC.url_contains("https://maimai.cn/"))
        self.upload_link()

        time.sleep(1)

        self.scroll_and_load()
        time.sleep(1)
        self.click_and_extract()
        time.sleep(10)

        
    
        

if __name__ == "__main__":
    # Specify the necessary parameters
    filter_page = "https://maimai.cn/web/search_center?type=contact&query=%E4%B8%8A%E6%B5%B7%E5%88%9D%E4%BA%BA&highlight=true"
    profile_url = None
    excel_file = None
    url_column = 'Link'
    profiles = None

    # Create an instance of MaiMaiScraper
    scraper = MaiMaiScraper(filter_page=filter_page, profile_url=profile_url, excel_file=excel_file, url_column=url_column, profiles=profiles)

    # Run the scraper
    scraper.run()