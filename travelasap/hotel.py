from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from slugify import slugify
import time
import sqlite3
import logging
from travelasap.settings import *
import re
import html2text

# Nastavení logování do souboru
logging.basicConfig(filename='hotels_errors.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')



class Hotel:
    def __init__(self, hotel_id, db_path=DATABASE):
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
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-images")
            # Ztlumení výstupu logů prohlížeče
            chrome_options.add_argument("--log-level=3")  # 3 = fatal, zobrazují se pouze závažné chyby

            # Zakázání výpisu JavaScriptových chyb
            chrome_options.add_argument("--disable-logging")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
            # Pokus o použití lokálního WebDriveru
            try:
                self.driver = webdriver.Chrome(service=Service(DRIVER_PATH), options=chrome_options)
            except Exception as local_error:
                print(f"Chyba s lokálním WebDriverem: {local_error}")
                # Pokud selže, pokusí se stáhnout nejnovější verzi z webu
                self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        except Exception as e:
            print(f"Chyba při inicializaci WebDriveru: {e}")

    
    def scrape_terms(self, adults=2, children=0, children_ages=[]):
        url = f"{BASE_URL}/a/{self.hotel_id}"
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

    def scrape_descriptions_from_admin(self):
        url = f"{BASE_URL}/admin/AccommodationMasters/view/{self.hotel_id}"
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
        if self.country_and_destination is None:
            logging.info(f"Tento hotel nemá určenu Zemi a Destinaci: {self.hotel_id} {self.name}")
            url_fragment_1 = f"a/{self.hotel_id}"
            return url_fragment_1, None

        else:
            sluged_country_and_destination = self.country_and_destination.split(" » ")
            print(f"{self.hotel_id}: {sluged_country_and_destination}")
            country_slug = slugify(sluged_country_and_destination[0])
            if len(sluged_country_and_destination) > 1:
                destination_slug = slugify(sluged_country_and_destination[1])
            else:
                destination_slug = None
            
            url_fragment_1 = f"a/{self.hotel_id}"
            url_fragment_2 = f"chcete-jet-do/{hotel_name_slug}/{country_slug}/{destination_slug+'/' if destination_slug else ''}{self.hotel_id}a"
            
            return url_fragment_1, url_fragment_2
    
    def generate_country_and_destination(self):
        country = self.country_and_destination.split(" » ")[0]
        destination = self.country_and_destination.split(" » ")[1]
        
        return country, destination
    
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
    

    def get_all_full_desc_from_web(self, url_base=BASE_URL):
        frag_1, frag_2 = self.generate_url_fragments()
        if url_base == BASE_URL:
            url = f"{BASE_URL}/{frag_2}"
        else:
            url = f"{url_base}/{frag_1}"
        url += "?sm=1&#tab-informace-o-hotelu"
        print(f"Scraping from {url}")
        self.driver.get(url)
        
        selector_ID = f"SelectAccommodationTourOperatorId-{self.hotel_id}-none"
        selector_X_Path = f"//select[@id='{selector_ID}']"
        trip_info_text_xpath = "//div[@class='trip-information__text']"
        
        wait = WebDriverWait(self.driver, 10)
        all_descriptions = {}
        
        try:
            # Nejprve zkontrolujeme, zda existuje select element
            select_elements = self.driver.find_elements(By.XPATH, selector_X_Path)
            
            if select_elements:
                select_element = select_elements[0]
                select = Select(select_element)
                options = select.options

                for option in options:
                    operator_name = option.text.strip()
                    if not operator_name:
                        continue
                    
                    print(f"Zpracování operátora: {operator_name}")
                    
                    select.select_by_visible_text(operator_name)
                    
                    # Čekání na načtení obsahu
                    try:
                        content_element = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "trip-information__text")))
                        content = content_element.get_attribute('innerHTML')
                        all_descriptions[operator_name] = self.html_to_markdown(content)
                    except TimeoutException:
                        print(f"Timeout při načítání obsahu pro operátora {operator_name}")
                        continue
            else:
                # Pokud neexistuje select, zkusíme najít jediný popis
                try:
                    content_element = wait.until(EC.presence_of_element_located((By.XPATH, trip_info_text_xpath)))
                    content = content_element.get_attribute('innerHTML')
                    all_descriptions["Exkluzivní"] = self.html_to_markdown(content)
                except TimeoutException:
                    print(f"Nenalezen žádný popis pro hotel s ID {self.hotel_id}")
        
        except Exception as e:
            print(f"Chyba při zpracování hotelu s ID {self.hotel_id}: {str(e)}")
        
        self.description = all_descriptions
        return all_descriptions
    
    def clean_html(self, raw_html):
    # Odebrání všech HTML tagů
        clean_text = re.sub('<.*?>', '', raw_html)
        
        # Odebrání přebytečných tabulátorů a prázdných řádků
        clean_text = clean_text.replace('\t', '').strip()
        clean_text = "\n".join([line.strip() for line in clean_text.splitlines() if line.strip()])
        
        return clean_text
    
    def html_to_markdown(self, raw_html):
            # Převod HTML na Markdown
            h = html2text.HTML2Text()
            h.ignore_links = True  # Ignorovat odkazy v markdownu
            markdown_text = h.handle(raw_html)
            return markdown_text


    def get_descriptions_from_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT Source, Description_Type, Description FROM hotel_descriptions WHERE Hotel_ID = ?", (self.hotel_id,))
        descriptions = cursor.fetchall()
        conn.close()
        return descriptions
    
    def save_descriptions_to_db(self, descriptions=None, description_type="full_desc", database=DATABASE):
        if descriptions is None:
            descriptions = self.description
        
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        
        for source, description in descriptions.items():
            cursor.execute("""
                INSERT OR REPLACE INTO hotel_descriptions (Hotel_ID, Source, Description_Type, Description) 
                VALUES (?, ?, ?, ?)
            """, (self.hotel_id, source, description_type, description))
        
        conn.commit()
        conn.close()

    def __del__(self):
        if self.driver:
            self.driver.quit()


class HotelDatabase:
    def __init__(self, db_path=DATABASE):
        self.db_path = db_path

    def get_all_hotels(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT Hotel_ID, Hotel_Name, Country_and_Destination FROM hotels")
        hotels = cursor.fetchall()
        conn.close()
        return hotels
    
