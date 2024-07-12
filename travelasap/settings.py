import dotenv

TIMEOUT = 10  # Konstanta pro timeouty
TOTAL_PAGES = 17738  # Počet stránek na scrapování
START_PAGE = 350  # Nebo nahraď číslo literálem/číslicí 1  # Stránka, od které se bude scrapovat
END_PAGE = 370  # Nebo nahraď číslo konstantou TOTAL_PAGES  # Stránka, do které se bude scrapovat

ADMINSCRAP = False
FRONTSCRAP = True
REPLACING = False
FILE_PATH = '20240710_266037_hotels_data.csv'
BASE_URL = "https://www.travelasap.cz"
DRIVER_PATH = r"d:\\PetrVavrinec\\PythonProjects\\webdrivers\\chromedriver.exe"
ACCOMMODATION_RATING_URL = r"https://www.travelasap.cz/admin/LocalAccommodationRatings/index/page:"