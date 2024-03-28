import os
import time
import pandas as pd
from tkinter import messagebox
from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

from util.cookies_util import *

from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

class MaiMaiScraper:
    def __init__(self, url_page = None, 
                 tag = "MaiMai", 
                 max_candidates = 100, 
                 cookies_path = None, 
                 excel_path = None,
                 filter_instance = False,
                 filter_folder = None,
                 filter_session = None):        
        chrome_options = webdriver.ChromeOptions()
        #chrome_options.add_argument("--headless")
        #chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

        self.login_url = "https://maimai.cn/platform/login"
        self.filter_page = "https://maimai.cn/ent/talents/discover/search_v2"
        self.url_page = url_page
        self.excel_keywords = []
        self.keywords_url = []
        self.tag = tag
        self.excel_path = excel_path
        self.filter_instance = filter_instance
        self.filter_folder = filter_folder
        self.filter_session = filter_session
        self.cookies_path = cookies_path
        self.max_candidates = max_candidates
        self.cookies = []
        self.wait_10s = WebDriverWait(self.driver, 10, 0.5)
        self.wait_180s = WebDriverWait(self.driver, 180, 0.5)

        self.candidate_df = pd.DataFrame(columns=[
            "Name", "URL", "Description", "Industry", "Location", "IP Location",
            "Position 1", "Company 1", "Duration 1", "Job Details 1", "Job Keywords 1",
            "Position 2", "Company 2", "Duration 2", "Job Details 2", "Job Keywords 2",
            "Position 3", "Company 3", "Duration 3", "Job Details 3", "Job Keywords 3",
            "University 1", "University Time 1", "Major 1", "Degree 1",
            "University 2", "University Time 2", "Major 2", "Degree 2"
        ])

    def upload_link(self, link):
        self.driver.get(link)
        print(f"Link uploaded: {link}")
        time.sleep(4)  # wait for the page to load

    def login_ez(self):

        if(self.filter_instance == False):
            self.driver.get(self.login_url)
        else:
            self.driver.get(self.filter_page)

        if self.cookies_path:
            cookies = load_cookies_path(self.cookies_path)
            print(f"Loaded cookies from {self.cookies_path}")
            self.driver.delete_all_cookies()
            for cookie in cookies:
                self.driver.add_cookie(cookie)
            

        elif os.path.exists('cookies.pkl'):
            cookies = load_cookies()
            self.driver.delete_all_cookies()
            for cookie in cookies:
                self.driver.add_cookie(cookie)

            time.sleep(3)

            if(self.filter_instance == False):
                self.driver.get("https://maimai.cn/feed_list")
                
                time.sleep(3)
                
                if self.login_url in self.driver.current_url:
                    print("Cookies are expired. Please log in manually or stop the program and upload new cookies.")
                    self.wait_180s.until(EC.url_contains("https://maimai.cn/feed_list"))
                    self.cookies = self.driver.get_cookies()
                    save_cookies(self.cookies)

            else:
                self.driver.get(self.filter_page)
                time.sleep(4)
                
                if self.login_url in self.driver.current_url:
                    print("Cookies are expired. Stop the program and upload new cookies or log in manually.")
                    time.sleep(3)
                    self.quit()

        else:
            print("Please log in manually.")

            if(self.filter_instance == False):
                self.wait_180s.until(EC.url_contains("https://maimai.cn/feed_list"))
                self.cookies = self.driver.get_cookies()
                save_cookies(self.cookies)
                print("Cookies saved.")

            else:
                self.wait_180s.until(EC.url_contains("https://maimai.cn/feed_list"))
                self.driver.get(self.filter_page)
                self.cookies = self.driver.get_cookies()
                save_cookies(self.cookies)
                print("Cookies saved.")
            

            
            

        print("登录成功 - login success")
            

    def extract_keywords_from_excel(self, excel_path):
        try:
            # Read the Excel file
            df = pd.read_excel(excel_path)

            # Extract keywords from the first column 
            keywords = df.iloc[:, 0].tolist()

            # Append the extracted keywords to self.excel_keywords
            self.excel_keywords.extend(keywords)

        except Exception as e:
            print(f"Error reading Excel file: {e}")

    def convert_keywords_to_urls(self,excel_keywords):
        keyword_urls = []
        for keyword in excel_keywords:
            # Replace spaces with '%20'
            keyword_url = keyword.replace(" ", "%20")
            # Create the URL format
            keyword_url = f"https://maimai.cn/web/search_center?type=contact&query={keyword_url}&highlight=true"
            # Append to the keyword_urls array
            keyword_urls.append(keyword_url)
        return keyword_urls

    def quit(self):
        self.driver.quit()

    def scroll_and_load(self):
        #scrollable_div = self.driver.find_element(By.XPATH, '//div[@data-x--search-results-container]')
        current_count = 0
        while True:
            # scroll down 1000 pixels
            self.driver.execute_script('window.scrollBy(0, 1000)')
            time.sleep(3)  # Wait for the new items to load

            # Count the number of loaded items
            new_count = len(self.driver.find_elements(By.XPATH, "//ul[contains(@class, 'list-group')]//div[starts-with(@id, 'contactcard')]"))
            if new_count == current_count:
                # If no new items loaded, exit the loop
                break
            current_count = new_count

            # If the number of loaded items exceeds the maximum, exit the loop
            if current_count >= self.max_candidates:
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

        #Extract Personal Basic Information
        try:
            content = self.driver.find_element(By.XPATH, "//meta[@name='description']").get_attribute("content")
            meta_content = content.split(',')
            name = meta_content[0].strip()
            description = meta_content[1].strip()
            location = meta_content[2].strip() + "," + meta_content[3].strip()
            industry = meta_content[4].strip()
            info["Name"] = name
            info["Description"] = description
            info["Location"] = location
            info["Industry"] = industry
            print(f"Name: {name}\n")
            #print(f"Descfiption: {description}\n")
            #print(f"location: {location}\n")
            #print(f"industry: {industry}\n")
        except NoSuchElementException:
            print("Cant find content")

        #Extract IP address
        try:
            ip_location_element = self.driver.find_element(By.XPATH, "//span[contains(@style, 'color: rgb(175, 177, 188)') and contains(@style, 'font-size: 12px') and contains(@style, 'line-height: 1.2')]")
            ip_ref, ip = ip_location_element.text.split('：')
            info["IP Location"] = ip
        except NoSuchElementException:
            print("IP Location not found")

        #Extract Work Information
        try:
            ul_element = self.driver.find_element(By.XPATH, "//span[contains(text(), '工作经历')]/ancestor::div[@class='p-b-5 p-t p-x gray-bg-f2f6f7 text-info']/following-sibling::ul[@class='list-group m-b-0']")
            div_elements = ul_element.find_elements(By.XPATH, ".//div[contains(@class, 'sc-cpmLhU')]")

            for i in range(min(3, len(div_elements))):
                div_element = div_elements[i]

                try:
                    position_element = div_element.find_element(By.CLASS_NAME, "info-position")
                    position_text = position_element.text.strip()
                    #print(f"Position {i + 1}: {position_text}")
                    info[f"Position {i + 1}"] = position_text
                except NoSuchElementException:
                    print("Work position not found")

                try:
                    company_element = div_element.find_element(By.CLASS_NAME, "info-text")
                    company_text = company_element.text.strip()
                    #print(f"Company {i + 1}: {company_text}")
                    info[f"Company {i + 1}"] = company_text
                except NoSuchElementException:
                    print("Company not found")

                try:
                    duration_element = div_element.find_element(By.CLASS_NAME, "info-sub-title")
                    duration_text = duration_element.text.strip()
                    #print(f"Duration {i + 1}: {duration_text}")
                    info[f"Duration {i + 1}"] = duration_text
                except:
                    print("Duration not found")

                try:
                    job_details_element = div_element.find_element(By.CLASS_NAME, "des-content")
                    job_details_text = job_details_element.text.strip()
                    #print(f"Job Details {i + 1}: {job_details_text}")
                    info[f"Job Details {i + 1}"] = job_details_text
                except:
                    print("Job Details not found")

                try:
                    job_keywords_element = div_element.find_element(By.CSS_SELECTOR, "div.list-group-item-text.tag-list")
                    job_keywords = job_keywords_element.find_elements(By.CSS_SELECTOR, "div.exp_tag_bg.exp_tag_text")
                    job_keywords_text = ""

                    for keyword in job_keywords:
                        job_keywords_text = job_keywords_text + keyword.text.strip() + ","
    
                    info[f"Job Keywords {i + 1}"] = job_keywords_text[:-1]
                except:
                    print("Job Keywords not found")
    
        except NoSuchElementException:
            print("Work Details not found")

        #Extract Personal Education Background
        try:
            ul_element = self.driver.find_element(By.XPATH, "//span[contains(text(), '教育经历')]/ancestor::div[@class='p-b-5 p-t p-x gray-bg-f2f6f7 text-info']/following-sibling::ul[@class='list-group m-b-0']")
            div_elements = ul_element.find_elements(By.XPATH, ".//div[contains(@class, 'sc-cpmLhU')]")

            for i in range(min(3, len(div_elements))):
                div_element = div_elements[i]
                try:
                    university_element = div_element.find_element(By.CLASS_NAME, "info-text")
                    university_text = university_element.text.strip()
                    #print(f"University {i + 1}: {university_text}")
                    info[f"University {i + 1}"] = university_text
                except NoSuchElementException:
                    print("University not found")

                try:
                    university_details = div_element.find_element(By.CLASS_NAME, "info-sub-title")
                    meta_details = university_details.text.split('，')
                    university_time_text = meta_details[0].strip()
                    #print(f"University Time {i + 1}: {university_time_text}")
                    info[f"University Time {i + 1}"] = university_time_text
                except NoSuchElementException:
                    print("University Time not found")

                try:
                    university_details = div_element.find_element(By.CLASS_NAME, "info-sub-title")
                    meta_details = university_details.text.split('，')
                    major_text = meta_details[1].strip()
                    #print(f"Major {i + 1}: {major_text}")
                    info[f"Major {i + 1}"] = major_text
                except NoSuchElementException:
                    print("Major not found")

                try:
                    university_details = div_element.find_element(By.CLASS_NAME, "info-sub-title")
                    meta_details = university_details.text.split('，')

                    if len(meta_details) > 2:
                        degree_text = meta_details[2].strip()
                    else:
                        degree_text = meta_details[1].strip()
                    
                    #print(f"Degree {i + 1}: {degree_text}")
                    info[f"Degree {i + 1}"] = degree_text
                except NoSuchElementException:
                    print("Degree not found")

        except NoSuchElementException:
            print("Education Details not found")

        return info
    
    def click_and_extract(self):
        candidates = self.driver.find_elements(By.XPATH, "//ul[contains(@class, 'list-group')]//div[starts-with(@id, 'contactcard')]//*[contains(@class, 'Tappable-inactive list-group-item')]")
        candidate_count = 1
        for candidate in candidates:
            #Max candidates to be searched
            if candidate_count > self.max_candidates:
                break

            # Scroll to the candidate element
            self.driver.execute_script("arguments[0].scrollIntoView(true);", candidate)
            self.driver.execute_script("window.scrollBy(0, -100);")

            candidate.click()

            # Switch to the new tab
            new_window = self.driver.window_handles[-1]
            self.driver.switch_to.window(new_window)

            time.sleep(2)

            # Extract the information from the profile page
            try:
                candidate_info = self.extract_info()
                self.candidate_df = pd.concat([self.candidate_df, pd.DataFrame([candidate_info])], ignore_index=True)
                candidate_count += 1
            except Exception as e:
                print(f"Failed to extract information: {e}")

            # Close the new tab
            self.driver.close()

            # Switch back to the original tab
            self.driver.switch_to.window(self.driver.window_handles[0])

            time.sleep(1)  # Wait for the page to load

    def export_df_to_excel(self):
        current_dir = os.getcwd()
        output_file_path = f"{current_dir}/{self.tag}_candidates_info.xlsx"
        self.candidate_df.to_excel(output_file_path, index=False)
        print(f"Exported candidate information to {output_file_path}")

        messagebox.showinfo("Scrape Completed", "Excel file has been created and exported successfully!")

    def run(self):

        self.driver.maximize_window()

        if(self.excel_path):

            self.login_ez()

            self.extract_keywords_from_excel(self.excel_path)
            self.keywords_url = self.convert_keywords_to_urls(self.excel_keywords)

            for url in self.keywords_url:
                self.upload_link(url)
                time.sleep(2)
                self.scroll_and_load()
                time.sleep(1)
                self.click_and_extract()
                time.sleep(5)
        
            self.export_df_to_excel()
            time.sleep(5)
            self.quit()

        elif(self.url_page):

            self.login_ez()

            self.upload_link(self.url_page)
            time.sleep(2)
            self.scroll_and_load()
            time.sleep(1)
            self.click_and_extract()
            time.sleep(10)
            self.quit()

        elif(self.filter_instance == True and self.filter_session == None):
            self.login_ez()
            time.sleep(600)

        elif(self.filter_instance == True and self.filter_session != None):
            self.login_ez()




if __name__ == "__main__":
    #Specify the necessary parameters
    url_page = "https://maimai.cn/web/search_center?type=contact&query=Bytedance&highlight=true"
    tag = "AnyHelper"
    max_candidates = 100

    # Create an instance of MaiMaiScraper
    scraper = MaiMaiScraper(tag = tag + "_", max_candidates=max_candidates, filter_instance=True, filter_session=None)

    # Run the scraper
    scraper.run()
