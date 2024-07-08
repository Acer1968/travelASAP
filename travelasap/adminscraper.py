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

class AdminScraper:
    def __init__(self):
        load_dotenv()
        self.base_url = 'https://www.travelasap.cz'
        self.admin_username = os.getenv('CESYS_LOGIN')
        self.admin_password = os.getenv('CESYS_PASSWORD')
        self.driver = None
        self.initialize_driver()
    
    def initialize_driver(self):
        try:
            try:
                self.driver = webdriver.Chrome(service=Service(r"d:\PetrVavrinec\PythonProjects\webdrivers\chromedriver.exe"))
            except Exception as local_error:
                print(f"Chyba s lokálním WebDriverem: {local_error}")
                self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        except Exception as e:
            print(f"Chyba při inicializaci WebDriveru: {e}")
        
        # Přidání implicitního čekání
        self.driver.implicitly_wait(10)
    
    def login(self):
        self.driver.get(f"{self.base_url}/admin/")
        try:
            # Čekání na načtení prvků pro přihlášení
            username_input = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.NAME, 'data[User][username]'))
            )
            password_input = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.NAME, 'data[User][password]'))
            )
            login_button = WebDriverWait(self.driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, '//input[@type="submit" and @value="Login"]'))
            )

            # Odeslání přihlašovacích údajů
            username_input.send_keys(self.admin_username)
            password_input.send_keys(self.admin_password)
            
            # Počkáme na screenshot
            time.sleep(5)
            self.driver.save_screenshot("login_page.png")
            
            # Použití JavaScriptu pro kliknutí na tlačítko, pokud běžná metoda nefunguje
            self.driver.execute_script("arguments[0].click();", login_button)
        except TimeoutException:
            print("Timeout while waiting for login elements")
            self.driver.save_screenshot("timeout_error.png")

    def scrape_page(self, page_number):
        url = f"{self.base_url}/admin/LocalAccommodationRatings/index/page:{page_number}"
        self.driver.get(url)
        
        hotel_data = []
        
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'table.table tbody tr'))
            )
            rows = self.driver.find_elements(By.CSS_SELECTOR, 'table.table tbody tr')
            for row in rows:
                cells = row.find_elements(By.TAG_NAME, 'td')
                if len(cells) >= 5:  # Kontrola, zda jsou k dispozici alespoň tři buňky
                    hotel_id = cells[0].text.strip()
                    hotel_name = cells[1].find_element(By.TAG_NAME, 'a').text.strip() if cells[1].find_elements(By.TAG_NAME, 'a') else 'N/A'
                    hotel_area = cells[2].text.strip()
                    hotel_type = cells[3].text.strip()
                    hotel_category = cells[4].text.strip()
                    hotel_data.append((hotel_id, hotel_name, hotel_area, hotel_type, hotel_category))
                else:
                    print(f"Row skipped due to insufficient number of cells: {row.text}")
        except TimeoutException:
            print(f"Timeout on page {page_number}")
    
        return hotel_data
    
    def scrape_all_pages(self, total_pages):
        all_hotel_data = []
        for page in range(1, total_pages + 1):
            hotel_data = self.scrape_page(page)
            all_hotel_data.extend(hotel_data)
            time.sleep(1)  # To prevent overloading the server
        return all_hotel_data
    
    def close(self):
        self.driver.quit()

    def save_to_csv(self, data, filename):
        df = pd.DataFrame(data, columns=['Hotel ID', 'Hotel Name', 'Hotel Area', 'Hotel Type', 'Hotel Category'])
        df.to_csv(filename, index=False)

if __name__ == "__main__":
    scraper = AdminScraper()
    scraper.login()
    all_data = scraper.scrape_all_pages(total_pages=2661)
    scraper.save_to_csv(all_data, 'hotels_data.csv')
    scraper.close()
