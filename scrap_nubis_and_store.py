import sqlite3
import travelasap as ta
import logging

# Nastavení logování do souboru
logging.basicConfig(filename='app.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Připojení k databázi
db_path = 'travelasap.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Načtení všech záznamů z tabulky hotels
cursor.execute("    SELECT Hotel_ID, Hotel_name \
                    FROM hotels \
                    WHERE Hotel_picture IS NOT NULL AND Hotel_picture != '';"
    )
hotels = cursor.fetchall()

# Inicializace AdminLoginHandler a přihlášení
admin_handler = ta.AdminLoginHandler()
if admin_handler.login():
    # Inicializace FrontScraper s base_url
    front_scraper = ta.FrontScraper(admin_handler.driver, "https://www.nubis.cz")
    source_name = 'Nubis'
    desc_type = 'short_text1'

    # Iterace přes všechny hotely a scrapování popisů
    for hotel in hotels:
        hotel_id = hotel[0]
        url_fragment = f"a/{hotel_id}"
        css_selector = "#accommodation-tmpl > div > div.box.position-relative.bg-white.shadow.overflow-hidden.mb-lg-3.py-2.px-3.pt-lg-3.pb-lg-4.px-lg-4 > div.local-rating.pt-3.pt-lg-4"
        description = front_scraper.scrap_html_selector(url_fragment, css_selector)
        # print(f"Zjištěn na frontendu {front_scraper.base_url} tento text o hotelu:\n{description}")
        
        if description:
            cursor.execute(
                "INSERT OR REPLACE INTO hotel_descriptions (Hotel_ID, source, description_type, description) VALUES (?, ?, ?, ?)",
                (hotel_id, source_name, desc_type, description)
            )
            logging.info(f"Description for hotel ID {hotel_id} stored successfully.")
        else:
            logging.warning(f"No description found for hotel ID {hotel_id}.")

    # Uzavření scraperu
    front_scraper.close()
else:
    logging.error("Login failed.")

# Uzavření databáze
admin_handler.close()
conn.commit()
conn.close()
