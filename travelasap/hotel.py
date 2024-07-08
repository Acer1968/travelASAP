from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time

class Hotel:
    def __init__(self, hotel_id, name=None, description=None, amenities=None):
        self.hotel_id = hotel_id
        self.name = name
        self.description = description
        self.amenities = amenities or []
        self.driver = None
        self.initialize_driver()

    def initialize_driver(self):
        try:
            # Pokus o použití lokálního WebDriveru
            try:
                self.driver = webdriver.Chrome(service=Service(r"d:\PetrVavrinec\PythonProjects\webdrivers\chromedriver.exe"))
            except Exception as local_error:
                print(f"Chyba s lokálním WebDriverem: {local_error}")
                # Pokud selže, pokusí se stáhnout nejnovější verzi z webu
                self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        except Exception as e:
            print(f"Chyba při inicializaci WebDriveru: {e}")

    
    def scrape_terms(self, adults=2, children=0, children_ages=[]):
        url = f"https://www.travelasap.cz/a/{self.hotel_id}"
        self.driver.get(url)

        # Pauza pro načtení stránky
        time.sleep(5)

        # Scrapování jména hotelu
        self.name = driver.find_element(By.CSS_SELECTOR, "css_selector_for_hotel_name").text

        # Scrapování popisu hotelu
        self.description = driver.find_element(By.CSS_SELECTOR, "css_selector_for_hotel_description").text

        # Scrapování vybavení hotelu
        amenities_elements = driver.find_elements(By.CSS_SELECTOR, "css_selector_for_amenities")
        self.amenities = [element.text for element in amenities_elements]

    def scrape_descriptions(self):
        url = f"https://www.travelasap.cz/admin/AccommodationMasters/view/{self.hotel_id}"
        self.driver.get(url)

        # Pauza pro načtení stránky
        time.sleep(5)

        # Scrapování jména hotelu
        self.name = self.driver.find_element(By.CSS_SELECTOR, "css_selector_for_hotel_name").text

        # Scrapování popisu hotelu
        self.description = self.driver.find_element(By.CSS_SELECTOR, "css_selector_for_hotel_description").text

        # Scrapování vybavení hotelu
        amenities_elements = self.driver.find_elements(By.CSS_SELECTOR, "css_selector_for_amenities")
        self.amenities = [element.text for element in amenities_elements]
    
    def save_to_db(self, db_connection):
        # Uložení dat o hotelu do databáze
        pass
    
    def load_from_db(self, db_connection):
        # Načtení dat o hotelu z databáze
        pass

    def __del__(self):
        if self.driver:
            self.driver.quit()
