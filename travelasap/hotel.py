import random
from playwright.sync_api import sync_playwright
import time
import sqlite3
import logging
from travelasap.settings import *
import re
import html2text
from slugify import slugify
import time
from datetime import datetime

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
        self.page = None
        self.db_path = db_path

        if not self.load_from_db():
            print(f"Hotel with ID {self.hotel_id} not found in database.")



    def get_all_full_desc_from_web(self, url_base=BASE_URL, hotel_order=None):
        start_time = datetime.now()
        if not self.page:
            raise ValueError("Page object is not set. Please set it before calling this method.")
        
        frag_1, frag_2, all_slug = self.generate_url_fragments()
        url = f"{url_base}/{frag_2 if url_base == BASE_URL else frag_1}"
        url += "?sm=1&#tab-informace-o-hotelu"
        print(f"Scraping from {url}")
        print("#"*60)
        
        self.page.goto(url)
        self.page.wait_for_load_state('networkidle')
        
        selector_ID = f"SelectAccommodationTourOperatorId-{self.hotel_id}-none"
        all_descriptions = {
            "hotel_order": hotel_order,
            "total_processing_time": None,
            "operators": {}
        }
        
        try:
            select_element = self.page.query_selector(f"select#{selector_ID}")
            if not select_element:
                raise ValueError(f"Select element with ID {selector_ID} not found")

            options = self.page.query_selector_all(f"select#{selector_ID} > option")
            options = [option for option in options if option.inner_text().strip()]
            
            for option in options:
                operator_name = option.inner_text().strip()
                option_value = option.get_attribute('value')
                print(f"Zpracování operátora: {operator_name}")
                
                description = self.get_description_for_operator(selector_ID, option_value, operator_name)
                
                if description:
                    all_descriptions["operators"][operator_name] = description
                    # print(f"Popis:\n{description['content'][:POCET_ZNAKU]}")
                    print(f"Operátor: {operator_name}, celkem {description['processing_time']} sekund")
                    print("#"*60)
                else:
                    print(f"Nepodařilo se získat popis pro operátora {operator_name}")

        except Exception as e:
            logging.debug(f"Chyba při zpracování hotelu s ID {self.hotel_id}: {str(e)}")
        
        all_descriptions["total_processing_time"] = (datetime.now() - start_time).total_seconds()
        logging.info(f"Celkem spotřebovaný čas na hotel: {all_descriptions['total_processing_time']} sekund")
        self.description = all_descriptions
        return all_descriptions

    def get_description_for_operator(self, selector_ID, option_value, operator_name, max_retries=3):
        for attempt in range(max_retries):
            try:
                operator_start_time = datetime.now()
                
                # Vybrat nového operátora
                self.page.select_option(f"select#{selector_ID}", value=option_value)
                
                # Čekat na změnu DOM
                self.wait_for_dom_change()
                
                # Získat nový obsah
                content = self.get_current_content()
                
                if content:
                    return {
                        "content": self.html_to_markdown(content),
                        "processing_time": (datetime.now() - operator_start_time).total_seconds()
                    }
                else:
                    print(f"Pokus {attempt + 1}: Nepodařilo se získat obsah pro operátora {operator_name}. Zkouším znovu.")
                    time.sleep(2)  # Delší pauza před dalším pokusem
            except Exception as e:
                print(f"Pokus {attempt + 1}: Chyba při získávání popisu pro operátora {operator_name}: {str(e)}")
                time.sleep(2)  # Delší pauza před dalším pokusem
        
        logging.info(f"Nepodařilo se získat popis pro operátora {operator_name} po {max_retries} pokusech.")
        return None

    def get_current_content(self):
        content_element = self.page.query_selector('.trip-information__text')
        return content_element.inner_html() if content_element else ""

    def wait_for_dom_change(self, timeout=20000):
        try:
            # Čekáme na zmizení indikátoru načítání, pokud existuje
            self.page.wait_for_selector('.loading-indicator', state='hidden', timeout=timeout)
        except:
            pass  # Pokud indikátor neexistuje, pokračujeme dál
        
        # Čekáme na viditelnost elementu s obsahem
        self.page.wait_for_selector('.trip-information__text', state='visible', timeout=timeout)
        
        # Přidáme krátkou pauzu pro jistotu
        time.sleep(1)

    def html_to_markdown(self, raw_html):
        h = html2text.HTML2Text()
        h.ignore_links = True
        markdown_text = h.handle(raw_html)
        return markdown_text
    
    def generate_country_and_destination(self):
        country = self.country_and_destination.split(" » ")[0]
        destination = self.country_and_destination.split(" » ")[1]
        
        return country, destination
    
    def generate_url_fragments(self):
        hotel_name_slug = slugify(self.name)
        if self.country_and_destination is None:
            logging.info(f"Tento hotel nemá určenu Zemi a Destinaci: {self.hotel_id} {self.name}")
            url_fragment_1 = f"a/{self.hotel_id}"
            return url_fragment_1, None

        else:
            sluged_country_and_destination = self.country_and_destination.split(" » ")
            logging.info(f"{self.hotel_id}: {sluged_country_and_destination}")
            country_slug = slugify(sluged_country_and_destination[0])
            if len(sluged_country_and_destination) > 1:
                destination_slug = slugify(sluged_country_and_destination[1])
            else:
                destination_slug = None
            
            url_fragment_1 = f"a/{self.hotel_id}"
            url_fragment_2 = f"chcete-jet-do/{hotel_name_slug}/{country_slug}/{destination_slug+'/' if destination_slug else ''}{self.hotel_id}a"
            all_slugs = [hotel_name_slug, country_slug, destination_slug]

            return url_fragment_1, url_fragment_2, all_slugs


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
    
    def load_from_db(self):
        print(f"Attempting to load hotel with ID {self.hotel_id} from database")
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get column names
            cursor.execute("PRAGMA table_info(hotels)")
            columns = [column[1] for column in cursor.fetchall()]
            print(f"Available columns in hotels table: {columns}")
            
            cursor.execute("SELECT * FROM hotels WHERE Hotel_ID = ?", (self.hotel_id,))
            row = cursor.fetchone()
            
            if row:
                self.name = row['Hotel_Name']
                self.exname = row['Hotel_Exname']  # nebo jiný sloupec podle skutečné struktury
                self.country_and_destination = row['Country_and_Destination']
                self.accommodation_type = row['Accommodation_Type']
                self.hotel_category = row['Hotel_Category']
                self.recommendation = row['Recommendation']
                self.own_rating = row['Own_Rating']
                self.own_texts = row['Own_Texts']

                print(f"Found hotel data for ID {self.hotel_id}")
                # expected_columns = ['Hotel_Name', 'Hotel_Exname', 'Country_and_Destination', 
                #                     'Accommodation_Type', 'Hotel_Category', 'Recommendation', 
                #                     'Own_Rating', 'Own_Texts']
                
                # for column in expected_columns:
                #     if column in columns:
                #         setattr(self, column.lower(), row[column])
                #         print(f"Set {column}: {row[column]}")
                #     else:
                #         print(f"Warning: Expected column '{column}' not found in database")
                #         setattr(self, column.lower(), None)
                
                return True
            else:
                print(f"No data found for hotel with ID {self.hotel_id}")
                return False
        
        except sqlite3.Error as e:
            print(f"SQLite error occurred: {e}")
            return False
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return False
        finally:
            if conn:
                conn.close()
                print("Database connection closed")
    

    def save_descriptions_to_db(self, descriptions=None, description_type="full_desc", database=DATABASE):
        if descriptions is None:
            descriptions = self.description
        
        conn = sqlite3.connect(database)
        cursor = conn.cursor()
        
        if 'operators' in descriptions:
            for operator, data in descriptions['operators'].items():
                cursor.execute("""
                    INSERT OR REPLACE INTO hotel_descriptions 
                    (Hotel_ID, source, description_type, description, Processing_Time, timestamp) 
                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                """, (self.hotel_id, operator, description_type, data['content'], data['processing_time']))
        else:
            # Zachování kompatibility se starším formátem dat
            for source, description in descriptions.items():
                if isinstance(description, dict) and 'content' in description:
                    cursor.execute("""
                        INSERT OR REPLACE INTO hotel_descriptions 
                        (Hotel_ID, source, description_type, description, Processing_Time, timestamp) 
                        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """, (self.hotel_id, source, description_type, description['content'], description.get('processing_time', None)))
                else:
                    cursor.execute("""
                        INSERT OR REPLACE INTO hotel_descriptions 
                        (Hotel_ID, source, description_type, description, timestamp) 
                        VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """, (self.hotel_id, source, description_type, description))
        
        # Uložení celkového času zpracování do samostatné tabulky
        # if 'total_processing_time' in descriptions:
        #     cursor.execute("""
        #         INSERT OR REPLACE INTO hotel_processing_times 
        #         (Hotel_ID, Description_Type, Total_Processing_Time, timestamp) 
        #         VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        #     """, (self.hotel_id, description_type, descriptions['total_processing_time']))
        
        conn.commit()
        conn.close()


    # def __del__(self):
    #     if self.page:
    #         self.page.context.close()

# Ostatní metody zůstávají stejné...