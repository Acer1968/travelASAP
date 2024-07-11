# main_script.py
import travelasap as ta

# Použití třídy Hotel
myhotel = ta.Hotel(354)
if myhotel.name:
    url_fragment_1, url_fragment_2 = myhotel.generate_url_fragments()
    print(url_fragment_1)  # Např. a/354
    print(url_fragment_2)  # Např. chcete-jet-do/nazevhotelu/zeme/destinace/354a


scraper = ta.FrontScraper()
description = scraper.scrap_description(url_fragment_1+"#tab-recenze-hotelu", "#tab-recenze-hotelu > div > div.local-rating")
print(description)
scraper.close()