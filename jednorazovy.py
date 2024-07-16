# main_script.py
import travelasap as ta
import logging

# Nastavení logování do souboru
logging.basicConfig(filename='app.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Inicializace AdminLoginHandler
admin_handler = ta.AdminLoginHandler()

# Přihlášení
if admin_handler.login():
    front_scraper = ta.FrontScraper(admin_handler.driver, "https://www.nubis.cz")
    selected_html_selector = "#accommodation-tmpl > div > div.box.position-relative.bg-white.shadow.overflow-hidden.mb-lg-3.py-2.px-3.pt-lg-3.pb-lg-4.px-lg-4 > div.local-rating.pt-3.pt-lg-4"
    # Použití třídy Hotel
    myhotel = ta.Hotel(354)
    if myhotel.name:
        url_fragment_1, url_fragment_2 = myhotel.generate_url_fragments()
        print(url_fragment_1)  # Např. a/354
        print(url_fragment_2)  # Např. chcete-jet-do/nazevhotelu/zeme/destinace/354a

    # Inicializace AdminScraper s již přihlášeným driverem
    # back_scraper = ta.AdminScraper(admin_handler.driver)

    # Inicializace FrontScraper s různou base_url
    
    description = front_scraper.scrap_html_selector(url_fragment_1, )
    print(f"Zjištěn na frontendu {front_scraper.base_url} tento text o hotelu:\n{description}")

    # Uzavření driveru
    # back_scraper.close()
    front_scraper.close()
else:
    print("Login failed.")

admin_handler.close()
