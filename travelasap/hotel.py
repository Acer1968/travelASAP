from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from slugify import slugify
import time
import sqlite3


class Hotel:
    def __init__(self, hotel_id, db_path='travelasap.db'):
        self.hotel_id = hotel_id
        self.name = None
        self.exname = None
        self.picture = None
        self.description = None
        self.amenities = []
        self.country_and_destination = None
        self.accommodation_type = None
        self.hotel_category = None
        self.recommendation = None
        self.own_rating = None
        self.own_texts = None
        self.driver = None
        self.db_path = db_path

        # Pokus o načtení dat z databáze
        if not self.load_from_db():
            print(f"Hotel with ID {self.hotel_id} not found in database.")
            # Přidat logiku pro stažení dat z webu, pokud není nalezeno v databázi

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

    def generate_url_fragments(self):
        hotel_name_slug = slugify(self.name)
        country_slug = slugify(self.country_and_destination.split(" » ")[0])
        destination_slug = slugify(self.country_and_destination.split(" » ")[1])
        
        url_fragment_1 = f"a/{self.hotel_id}"
        url_fragment_2 = f"chcete-jet-do/{hotel_name_slug}/{country_slug}/{destination_slug}/{self.hotel_id}a"
        
        return url_fragment_1, url_fragment_2
    
    def save_to_db(self, db_connection):
        # Uložení dat o hotelu do databáze
        pass
    
    def load_from_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM hotels WHERE Hotel_ID = ?", (self.hotel_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            self.name = row['Hotel_Name']
            self.exname = row['Hotel_Exname']  # nebo jiný sloupec podle skutečné struktury
            self.country_and_destination = row['Country_and_Destination']
            self.accommodation_type = row['Accommodation_Type']
            self.hotel_category = row['Hotel_Category']
            self.recommendation = row['Recommendation']
            self.own_rating = row['Own_Rating']
            self.own_texts = row['Own_Texts']
            return True
        return False

    def __del__(self):
        if self.driver:
            self.driver.quit()
