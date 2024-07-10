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

TIMEOUT = 10  # Konstanta pro timeouty
TOTAL_PAGES = 17738  # Počet stránek na scrapování
START_PAGE = 1  # Stránka, od které se bude scrapovat
END_PAGE = TOTAL_PAGES  # Stránka, do které se bude scrapovat

class AdminScraper:
    def __init__(self):
        load_dotenv()
        self.base_url = 'https://www.travelasap.cz'
        self.admin_username = os.getenv('CESYS_LOGIN')
        self.admin_password = os.getenv('CESYS_PASSWORD')
        print(f"Loaded credentials: {self.admin_username}, {self.admin_password}")
        self.driver = None
        self.initialize_driver()
    
    def initialize_driver(self):
        try:
            print("Trying to initialize WebDriver.")
            self.driver = webdriver.Chrome(service=Service(r"d:\\PetrVavrinec\\PythonProjects\\webdrivers\\chromedriver.exe"))
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

    def scrape_page(self, page_number):
        url = f"{self.base_url}/admin/LocalAccommodationRatings/index/page:{page_number}"
        print(f"Navigating to page {page_number}")
        self.driver.get(url)

        try:
            WebDriverWait(self.driver, TIMEOUT).until(
                EC.presence_of_element_located((By.TAG_NAME, 'table'))
            )
        except TimeoutException:
            print(f"Timeout on page {page_number}")
            return []

        rows = self.driver.find_elements(By.XPATH, "//table/tbody/tr")
        print(f"Found {len(rows)} rows on page {page_number}")

        data = []
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, 'td')
            if len(cells) < 8:
                print(f"Row skipped due to insufficient number of cells: {row.text}")
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

        print(f"Scraped {len(data)} entries from page {page_number}")
        return data
    
    def scrape_all_pages(self, start_page, end_page):
        all_hotel_data = []
        for page in range(start_page, end_page + 1):
            print(f"Scraping page {page} of {end_page}")
            hotel_data = self.scrape_page(page)
            all_hotel_data.extend(hotel_data)
            print(f"Total entries so far: {len(all_hotel_data)}")
        return all_hotel_data
    
    def close(self):
        self.driver.quit()

    def save_to_csv(self, data, filename):
        df = pd.DataFrame(data, columns=[
            'Hotel ID', 'Hotel Picture', 'Hotel Name', 'Hotel Exname', 
            'Country and Destination', 'Accommodation Type', 'Hotel Category',
            'Recommendation', 'Own Rating', 'Own Texts'
        ])
        df.to_csv(filename, index=False)

if __name__ == "__main__":
    scraper = AdminScraper()
    scraper.login()
    all_data = scraper.scrape_all_pages(start_page=START_PAGE, end_page=END_PAGE)  # Limit pro testování #all_data = scraper.scrape_all_pages(start_page1, end_page=TOTAL_PAGES)
    scraper.save_to_csv(all_data, 'hotels_data.csv')
    scraper.close()
