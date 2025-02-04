from travelasap import Hotel, FrontScraper
from travelasap.settings import *
import sqlite3
import pprint as pp
import logging
import time
from playwright.sync_api import sync_playwright

# Vytvoření loggeru
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)  # Změněno na DEBUG pro více detailů

# Vytvoření file handleru, který loguje i debug messages
file_handler = logging.FileHandler('hotel_scraping_debug.log', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)

# Vytvoření console handleru
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Vytvoření formatteru
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Přidání handlerů k loggeru
logger.addHandler(file_handler)
logger.addHandler(console_handler)

def get_hotel_ids_with_conditions(database_path=DATABASE):
    # SQL dotaz, který získá požadovaná Hotel_ID
    query = """
    SELECT DISTINCT h.Hotel_ID
    FROM hotels h
    LEFT JOIN hotel_descriptions hd ON h.Hotel_ID = hd.Hotel_ID AND hd.description_type = 'full_desc'
    WHERE h.Hotel_Picture IS NOT NULL AND (hd.Hotel_ID IS NULL OR hd.timestamp IS NULL);
    """

    # Připojení k databázi
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()

    # Provedení dotazu
    cursor.execute(query)
    
    # Získání všech hotelů ID z dotazu
    hotel_ids = [row[0] for row in cursor.fetchall()]

    # Zavření spojení s databází
    conn.close()

    return hotel_ids

def main():
    # hotel_ids = [4602]  # Testujeme pouze jeden hotel
    # hotel_ids = [62622, 52235, 94, 69480, 109, 8818, 65, 68380, 7706, 83, 4581, 69584, 4603, 102, 24804, 3134, 49656, 18412, 7779, 4638, 112, 23912, 56796, 10482, 3138, 94004, 18944, 26359, 10907, 197, 9969, 23909, 37466, 8350, 60, 3584, 91257, 130, 48463, 61, 48252, 104, 47099, 7200, 48462, 68, 24493, 8777, 7290, 70186, 93322, 95, 7545, 8810, 24788, 4623, 7628, 7452, 395, 4602, 32345, 49762, 87, 70848, 23932, 9931, 67, 37688, 108, 86891, 22008, 9983, 86439, 91193, 10679, 52498, 11997, 4615, 135, 68394, 69737, 7798, 50205, 14312, 24810, 86066, 9951, 7778, 7700, 31539, 422, 7773, 7416, 358, 7630, 3481, 4617, 22008, 279, 74, 14809, 70126, 19202, 100, 70107, 370, 39122, 244, 40157, 13788, 132, 451, 60393, 7239, 28493, 4603, 93598, 69757, 3761, 24793, 62005, 23274, 8311, 51102, 3272, 56436, 62283, 61093, 4621, 60443, 108, 7417, 62784, 73323, 48252, 10447, 62607, 22496, 85, 400, 85, 26592, 18412, 7109, 3787, 70235, 239, 7572, 7234, 70294, 3531, 50050, 533, 8807, 3760, 30895, 79280, 18410, 82680, 52239, 73097, 70997, 4627, 62810, 24750, 60857, 7574, 16246, 7608, 74768, 22689, 60442, 4625, 49873, 3795, 3799, 40332, 14291, 7240, 10422, 4611, 71, 31986, 56793, 60422, 32295, 63, 91, 185, 22155, 70108, 69583, 7777, 7353, 7636, 52048, 16043, 4610, 8765, 15161, 11400, 85636, 3774, 64, 3772, 7341, 58579, 86244, 28497, 82923, 82923, 80109, 80109, 24510, 52, 52, 450, 8744, 396, 48477, 10462, 23931, 7113, 24783, 9930, 82679, 3793, 52237, 4621, 68450, 7196, 70203, 3147, 26676, 3775, 70043, 88407, 52089, 87524, 7633, 31542, 50213, 60527, 62883, 195, 18284, 75409, 62760, 62761, 10443, 31467, 63841, 63841, 15570, 193, 81316, 10419, 7414, 11980, 14262, 7354, 50370, 193, 3141, 73321, 27815, 92846, 3275, 60683, 3576, 56266, 7705, 7379, 67752, 7340, 54, 7195, 4610, 280, 231, 50058, 3126, 47802, 58895, 192, 186, 28285, 60782, 60782, 83, 262, 33667, 73893, 10436, 23931, 23931, 67, 68, 419, 24797, 69463, 321, 3762, 73298, 84917, 229, 316, 70043, 8766, 62411, 62411, 4628, 23288, 56826, 8779, 62035, 15790, 366, 9950, 234, 51712, 257, 68113, 7190, 3142, 93886, 188, 8764, 35956, 4609, 8752, 62536, 50734, 79533, 10161, 354, 28130, 55, 57, 69, 123, 123, 3478, 11134, 10814, 32283, 72, 30476, 10468, 32260, 52034, 3803, 14293, 69757, 377, 38101, 7788, 32348, 24486, 10590, 9965, 3764, 9924, 7574, 16033, 3797, 89172, 47372, 27478, 10474, 94006, 23283, 24819, 70145, 7709, 189, 38202, 69723, 23918, 363, 12053, 255, 255, 16028, 70481, 7544, 70587, 422, 60718, 62861, 394, 81170, 7354, 70844, 9977, 472, 7339, 7540, 60415, 86447, 7779, 19991, 528, 246, 91352, 7420, 91195, 68823, 23934, 370, 369, 94001, 4637, 30935, 47084, 96, 60667, 78430, 31043, 7111, 7510, 126, 49652, 49652, 50049, 68220, 49746, 196, 37195, 73322, 137, 4640, 117, 190, 24803, 18526, 49916, 320, 76, 4614, 191, 26592, 16036, 404, 52098, 10445, 3273, 50211, 81031, 19223, 19202, 7739, 52045, 19990, 244, 256, 87442, 32917, 8812, 82674, 8783, 49763, 52431, 452, 10460, 26673, 7198, 93724, 28501, 10161, 22156, 23925, 361, 88418, 93731, 28286, 24817, 49303, 32278, 7524, 69552, 10866, 7773, 49670, 8430, 23917, 72054, 68245, 7590, 63250, 3766, 3796, 82686, 3480, 24808, 4608, 85448, 64589, 49872, 62542, 32265, 55480, 14328, 3477, 127, 357, 70995, 83400, 10442, 7491, 90860, 3128, 62904, 24814, 73116, 62038, 85644, 4639, 455, 60436, 7288, 40451, 63285, 456, 10167, 68178, 6151, 7237, 60671, 78839, 7780, 12121, 428, 82672, 50041, 51038, 121, 69758, 69752, 8573, 9970, 196, 8784, 28510, 68228, 68086, 62, 24821, 24823, 58358, 61421, ]  # OR get_hotels_in_egypt_or_turkey()
    hotel_ids = get_hotel_ids_with_conditions()[:3]

    POCET_ZNAKU = 90
    OD_ZNAKU = 3
    pocitadlo = 1
    celkem = len(hotel_ids)

    logger.debug("Inicializace Playwright")
    with sync_playwright() as p:
        logger.debug("Spouštění prohlížeče")
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        try:
            for n, hotel_id in enumerate(hotel_ids):
                logger.debug(f"Začínám zpracovávat hotel s ID: {hotel_id}")
                try:
                    logger.debug(f"Vytvářím objekt Hotel pro ID: {hotel_id}")
                    h = Hotel(hotel_id)
                    logger.debug(f"Objekt Hotel vytvořen: {h}")
                    
                    logger.debug("Nastavuji page objekt pro Hotel")
                    h.page = page  # Use the same page for all hotels
                    
                    logger.info(f"Zpracovávám {pocitadlo}/{celkem} hotel: {h.name} (ID: {hotel_id})")
                    #print(f"Zpracovávám {n}/{pocitadlo}/{celkem} hotel: {h.name} (ID: {hotel_id})")
                    
                    logger.debug("Volám metodu get_all_full_desc_from_web")
                    h.get_all_full_desc_from_web("https://www.cestovkasadska.cz")
                    
                    logger.debug("Volám metodu save_descriptions_to_db")
                    h.save_descriptions_to_db()
                    
                    pp.pprint(h.description)
                    # logger.info(f"Uloženo {len(h.description[operators])} popisů pro hotel {h.name}")
                    # print(f"Získaný popis (pouze prvních {POCET_ZNAKU} znaků) o {len(h.description)} prvcích:")
                    # pp.pprint(h.description[:POCET_ZNAKU])
                    
                    logger.debug("Čekám 2 sekundy před zpracováním dalšího hotelu")
                    time.sleep(2)  # 2 sekundová pauza mezi hotely
                    pocitadlo += 1
                except Exception as e:
                    logger.error(f"Chyba při zpracování hotelu {hotel_id}: {str(e)}", exc_info=True)
        finally:
            logger.debug("Zavírám context a browser")
            context.close()
            browser.close()

    logger.info("Scrapování dokončeno")

if __name__ == "__main__":
    logger.debug("Spouštím main funkci")
    main()