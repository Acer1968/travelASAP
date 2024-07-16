from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
import pandas as pd
from dotenv import load_dotenv
import os
import time
import logging
from travelasap.settings import TIMEOUT, BASE_URL, DRIVER_PATH, ACCOMMODATION_RATING_URL, TEST_URL

load_dotenv()  # načtení hodnot z .env souboru

class AdminLoginHandler:
    def __init__(self, driver_path=DRIVER_PATH, base_url=BASE_URL):
        self.driver_path = driver_path
        self.base_url = base_url.rstrip('/')  # Odstranění koncového lomítka
        self.username = os.getenv("CESYS_LOGIN")
        self.password = os.getenv("CESYS_PASSWORD")
        if not self.username or not self.password:
            logging.error("Username or password not found in .env file or ENVIROMENT VARIABLES.")
            raise ValueError("Username or password not found in .env file or ENVIROMENT VARIABLES.")
        self.driver = self.initialize_driver()

    def initialize_driver(self):
        driver = None
        try:
            # Pokus o použití lokální verze webdriveru
            if self.driver_path:
                driver = webdriver.Chrome(service=Service(self.driver_path))
                # Testujeme, zda je lokální verze kompatibilní
                driver.get(TEST_URL)
        except WebDriverException as e:
            logging.error(f"Local WebDriver not compatible or not found: {e}")
            # Pokus o stažení a použití nejnovější verze webdriveru
            driver = self.try_fallback_driver()
        logging.info(f"WebDriver is found and loaded: {driver}")
        return driver

    def try_fallback_driver(self):
        try:
            return webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        except Exception as e:
            logging.error(f"Error initializing WebDriver from ChromeDriverManager: {e}")
            return None

    def login(self):
        if not self.driver:
            logging.error("WebDriver is not initialized.")
            return False
        
        print("Navigating to admin login page.")
        self.driver.get(f"{self.base_url}/admin/")
        try:
            print("Waiting for username input.")
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
            return True
        except TimeoutException:
            print("Timeout while waiting for login elements")
            self.driver.save_screenshot("timeout_error.png")
            return False

    def close(self):
        if self.driver:
            self.driver.quit()


class BaseScraper:
    def __init__(self, driver):
        self.driver = driver

class AdminScraper(BaseScraper):
    def __init__(self, driver):
        super().__init__(driver)
    

    def scrape_hotel_data_from_ratting_page(self, page_number):
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
            hotel_data = self.scrape_hotel_data_from_ratting_page(page)
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
    def __init__(self, driver, base_url=BASE_URL):
        super().__init__(driver)
        self.base_url = base_url.rstrip('/')  # Odstranění koncového lomítka

    def scrap_html_selector(self, url_fragment, html_selector):
        try:
            url = f"{self.base_url}/{url_fragment.lstrip('/')}"  # Odstranění počátečního lomítka u fragmentu, pokud tam nějaké je
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

