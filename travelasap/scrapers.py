import logging
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import os
from settings import TIMEOUT, TOTAL_PAGES, START_PAGE, END_PAGE, ADMINSCRAP, FRONTSCRAP, REPLACING, FILE_PATH, BASE_URL, DRIVER_PATH, ACCOMMODATION_RATING_URL


class AdminLoginHandler:
    def __init__(self, driver, base_url, username, password):
        self.driver = driver
        self.base_url = base_url
        self.username = username
        self.password = password

    def login(self):
        print("Navigating to admin login page.")
        self.driver.get(f"{self.base_url}/admin/")
        try:
            username_input = WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_element_located((By.NAME, 'data[User][username]'))
            )
            password_input = WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_element_located((By.NAME, 'data[User][password]'))
            )
            login_button = WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, '//input[@type="submit" and @value="Přihlásit"]'))
            )
            username_input.send_keys(self.username)
            password_input.send_keys(self.password)
            self.driver.execute_script("arguments[0].click();", login_button)
            time.sleep(2)
        except TimeoutException:
            print("Timeout while waiting for login elements")
            self.driver.save_screenshot("timeout_error.png")


class BaseScraper:
    def __init__(self, driver_path=DRIVER_PATH):
        self.driver = None
        self.initialize_driver(driver_path)

    def initialize_driver(self, driver_path):
        try:
            if driver_path:
                self.driver = webdriver.Chrome(service=Service(driver_path))
            else:
                self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        except Exception as e:
            logging.error(f"Error initializing WebDriver from path {driver_path}: {e}")
            self.try_fallback_driver()

    def try_fallback_driver(self):
        try:
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        except Exception as e:
            logging.error(f"Error initializing WebDriver from fallback: {e}")
            self.driver = None

    def get_driver(self):
        return self.driver

class AdminScraper(BaseScraper):
    def __init__(self, driver_path=None):
        super().__init__(driver_path)
        load_dotenv()
        self.base_url = BASE_URL
        self.admin_username = os.getenv('CESYS_LOGIN')
        self.admin_password = os.getenv('CESYS_PASSWORD')
        print(f"Loaded credentials: {self.admin_username}, {self.admin_password}")
        self.driver = None
        self.initialize_driver()
    
    def initialize_driver(self):
        try:
            print("Trying to initialize WebDriver.")
            self.driver = webdriver.Chrome(service=Service(DRIVER_PATH))
        except Exception as local_error:
            print(f"Chyba s lokálním WebDriverem: {local_error}")
            print("Trying to initialize WebDriver from WebDriverManager.")
            self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        
    def login(self):
        print("Navigating to admin login page.")
        self.driver.get(f"{self.base_url}/admin/")
        try:
            print("Waiting for username input.")
            username_input = WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_element_located((By.NAME, 'data[User][username]'))
            )
            print("Waiting for password input.")
            password_input = WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_element_located((By.NAME, 'data[User][password]'))
            )
            print("Waiting for login button.")
            login_button = WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_element_located((By.XPATH, '//input[@type="submit" and @value="Přihlásit"]'))
            )

            print("Sending login credentials.")
            username_input.send_keys(self.admin_username)
            password_input.send_keys(self.admin_password)
            
            print("Clicking the login button.")
            self.driver.execute_script("arguments[0].click();", login_button)
            print("Saving screenshot after login.")
            time.sleep(2)
            self.driver.save_screenshot("login_page_after_click.png")
        except TimeoutException:
            print("Timeout while waiting for login elements")
            self.driver.save_screenshot("timeout_error.png")

    def scrape_hotel_data_from_page(self, page_number):
        url = f"{self.base_url}{ACCOMMODATION_RATING_URL}{page_number}"
        print(f"Navigating to page {page_number}")
        try:
            self.driver.get(url)
            WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_element_located((By.TAG_NAME, 'table'))
            )
            rows = self.driver.find_elements(By.XPATH, "//table/tbody/tr")
            logging.info(f"Found {len(rows)} rows on page {page_number}")
        except TimeoutException:
            logging.error(f"Timeout on page {page_number}")
            return []

        data = []
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, 'td')
            if len(cells) < 8:
                logging.warning(f"Row skipped due to insufficient number of cells: {row.text}")
                continue

            
            hotel_id = cells[0].text.strip()
            
            hotel_picture = None
            hotel_name = None
            hotel_exname = None
            anchors = cells[1].find_elements(By.TAG_NAME, 'a')
            
            if len(anchors) == 1:
                hotel_name = anchors[0].text.strip()
            elif len(anchors) == 2:
                hotel_picture = anchors[0].get_attribute('href')
                hotel_name = anchors[1].text.strip()
            else:
                print(f"Unexpected number of anchors in cell[1] for hotel ID {hotel_id}: {cells[1].get_attribute('outerHTML')}")

            paragraphs = cells[1].find_elements(By.TAG_NAME, 'p')
            if paragraphs:
                for paragraph in paragraphs:
                    if paragraph.text.startswith("ex: "):
                        hotel_exname = paragraph.text[4:].strip()
                    else:
                        print(f"Unexpected paragraph in cell[1] for hotel ID {hotel_id}: {cells[1].get_attribute('outerHTML')}")
            else:
                print(f"No paragraphs in cell[1] for hotel ID {hotel_id}")

            country_destination = cells[2].text.strip()
            accommodation_type = cells[3].text.strip()
            hotel_category = cells[4].text.strip()
            recommendation = cells[5].text.strip()
            own_rating = cells[6].text.strip()
            own_texts = cells[7].text.strip()

            data.append({
                'Hotel ID': hotel_id,
                'Hotel Picture': hotel_picture,
                'Hotel Name': hotel_name,
                'Hotel Exname': hotel_exname,
                'Country and Destination': country_destination,
                'Accommodation Type': accommodation_type,
                'Hotel Category': hotel_category,
                'Recommendation': recommendation,
                'Own Rating': own_rating,
                'Own Texts': own_texts,
            })

        # print(f"Scraped {len(data)} entries from page {page_number}")
        logging.info(f"Scraped {len(data)} entries from page {page_number}")
        return data
    
    def scrape_all_pages(self, start_page, end_page):
        all_hotel_data = []
        for page in range(start_page, end_page + 1):
            print(f"Scraping page {page} of {end_page}")
            hotel_data = self.scrape_hotel_data_from_page(page)
            all_hotel_data.extend(hotel_data)
            print(f"Total entries so far: {len(all_hotel_data)}")
        return all_hotel_data
    
    def replace_text_to_boolean(self, file_path, columns_to_replace, conversion_list):
        import pandas as pd

        df = pd.read_csv(file_path)
        conversion_dict = dict(conversion_list)
        df[columns_to_replace] = df[columns_to_replace].replace(conversion_dict)

        # Explicitní konverze na integer, pokud jsou hodnoty 0 a 1
        for col in columns_to_replace:
            if set(df[col].dropna().unique()).issubset({0, 1}):
                df[col] = df[col].astype(int)

        modified_file_path = file_path.replace('.csv', '_modified.csv')
        df.to_csv(modified_file_path, index=False)
        return modified_file_path

    def replace_boolean_to_text(self, file_path, columns_to_replace, conversion_list):
        import pandas as pd

        df = pd.read_csv(file_path)
        conversion_dict = dict(conversion_list)
        inverse_conversion_dict = {v: k for k, v in conversion_dict.items()}
        df[columns_to_replace] = df[columns_to_replace].replace(inverse_conversion_dict)

        # Explicitní konverze na string
        for col in columns_to_replace:
            df[col] = df[col].astype(str)

        modified_file_path = file_path.replace('.csv', '_modified.csv')
        df.to_csv(modified_file_path, index=False)
        return modified_file_path


        
    def close(self):
        self.driver.quit()

    def save_to_csv(self, data, filename):
        df = pd.DataFrame(data, columns=[
            'Hotel ID', 'Hotel Picture', 'Hotel Name', 'Hotel Exname', 
            'Country and Destination', 'Accommodation Type', 'Hotel Category',
            'Recommendation', 'Own Rating', 'Own Texts'
        ])
        df.to_csv(filename, index=False)

class FrontScraper(BaseScraper):
    def __init__(self, driver_path=DRIVER_PATH, base_url=BASE_URL):
        super().__init__(driver_path)
        self.base_url = base_url
        self.driver = self.initialize_driver()

    def initialize_driver(self):
        try:
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        except Exception as e:
            print(f"Error initializing WebDriver: {e}")
            driver = None
        return driver

    def scrap_description(self, url_fragment, html_selector):
        try:
            url = f"{self.base_url}/{url_fragment}"
            print(f"Scraping description from {url}")
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, html_selector))
            )
            element = self.driver.find_element(By.CSS_SELECTOR, html_selector)
            return element.text
        except TimeoutException:
            print(f"Timeout while waiting for element {html_selector} on {url}")
            return None

    def close(self):
        self.driver.quit()

if __name__ == "__main__":
    scraper = AdminScraper()
    if ADMINSCRAP:  
        scraper.login()
        all_data = scraper.scrape_all_pages(start_page=START_PAGE, end_page=END_PAGE)  # Limit pro testování #all_data = scraper.scrape_all_pages(start_page1, end_page=TOTAL_PAGES)
        scraper.save_to_csv(all_data, FILE_PATH)
        scraper.close()
    if REPLACING:
        conversion_list = [("Ano", 1), ("Ne", 0)]
        file_path = FILE_PATH
        columns_to_replace = ['Recommendation', 'Own Rating', 'Own Texts']
        scraper.replace_text_to_boolean(file_path, columns_to_replace, conversion_list)

