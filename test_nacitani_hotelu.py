from travelasap import Hotel, FrontScraper
import sqlite3
import pprint as pp
import logging
import time

logging.basicConfig(filename='hotel_scraping.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def get_hotels_in_egypt_or_turkey(database='travelasap.db'):
    conn = sqlite3.connect(database)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT h.Hotel_ID
            FROM hotels h
            WHERE h.Country_and_Destination LIKE '%Tunisko%';


    """)
    
    hotel_ids = [row[0] for row in cursor.fetchall()]
    
    conn.close()

    """ POUŽIJ TENTO FRAGMENT KÓDU V PŘÍPADĚ TESTŮ nebo CHYBNÝCH VÝSLEDKŮ
    # Dočasné ids pro testy:
    hotel_ids = [41,42,354,14308]
    # Testy pro metodu Hotel.get_all_full_desc_from_web("https://www.cestovkasadska.cz"):
    # 41: Měl by vrátit prázdný slovník bez jakéhokoli popisu - to udělá, ale je otázka, jestli k tomu dojde správnou cestou
    # 42: Měl by vrátit neprázdný slovník s právě JEDNÍM popisem, ale to neudělá, vrátí prázdný slovník
    # 354: Měl by vrátit neprázdný slovník se 6ti neprázdnými popisy - to udělá, ale z nějakého důvodu nemohu přeskočit první prázdný prvek v selektoru
    # 14308: Měl by vrátit neprázdný slovník s právě JEDNÍM popisem, kde sice nenajde operátora (nahradí text slove Exkluzivní), ale popis by najít měl, ale to neudělá, vrátí prázdný slovník
    """
    return hotel_ids

hotel_ids = get_hotels_in_egypt_or_turkey()

POCET_ZNAKU = 60
OD_ZNAKU = 50
pocitadlo = 1
celkem = len(hotel_ids)
for hotel_id in hotel_ids[:2]:
    try:
        h = Hotel(hotel_id)
        h.initialize_driver()
        logging.info(f"Zpracovávám {pocitadlo}/{celkem} hotel: {h.name} (ID: {hotel_id})")
        print(f"Zpracovávám {pocitadlo}/{celkem} hotel: {h.name} (ID: {hotel_id})")
        h.get_all_full_desc_from_web("https://www.cestovkasadska.cz")
        h.save_descriptions_to_db()
        logging.info(f"Uloženo {len(h.description)} popisů pro hotel {h.name}")
        print(f"Získaný popis (pouze prvních {POCET_ZNAKU} znaků) o {len(h.description)} prvcích:")
        pp.pprint({k: v[OD_ZNAKU:OD_ZNAKU+POCET_ZNAKU] for k, v in h.description.items()})
        time.sleep(2)  # 2 sekundová pauza mezi hotely
        pocitadlo += 1
    except Exception as e:
        logging.error(f"Chyba při zpracování hotelu {hotel_id}: {str(e)}")
    finally:
        if h.driver:
            h.driver.quit()

logging.info("Scrapování dokončeno")