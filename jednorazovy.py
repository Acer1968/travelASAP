# main_script.py
import travelasap as ta

# Použití třídy Hotel
myhotel = ta.Hotel(354)
if myhotel.name:
    url_fragment_1, url_fragment_2 = myhotel.generate_url_fragments()
    print(url_fragment_1)  # Např. a/354
    print(url_fragment_2)  # Např. chcete-jet-do/nazevhotelu/zeme/destinace/354a


scraper = ta.scrapers.AdminLoginHandler()

scraper.close()