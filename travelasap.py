import facebook
import requests
from bs4 import BeautifulSoup as BS
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import myconfig as mc
import logging
from datetime import datetime
import time

logging.basicConfig(filename='travelasap.log',
                    encoding='utf-8', level=logging.INFO)


class Trip():
    """
    Pro zájezd trip_no získá pomocí scrapingu z našich stránek všechny důležité údaje o zájezdu.

    Obsahuje několik metod na získání informací z dané stránky, na vytváření screenshotů, na vytváření FB příspěvků.


    trip_no - číslo termínu v CeSYSu
    page_user_name - uživatelský název stránky na FB, defaultně @cestujhned

    """

    # třídní proměnná evidující všechny zájezdy načtené pomocí třídy Trip
    trips = []

    def __init__(self, trip_no):
        self.trip_no = str(trip_no)

        # KONSTANTY a předem známé hodnoty
        # základní bázová (krátká) adresa URL pro dotazy na konkrétní zájezd na travelasap
        self.page_url = os.path.join(
            mc.URL_BASE, 'd/', self.trip_no, '?sm=1&ac=2&cc=0')
        # self.page_url = os.path.join(self.base_url, str(self.trip_no),)
        # přidá zájezd (jeho číslo a krátkou adresu) do třídní proměnné
        self.__class__.trips.append(
            {"Object": self, "Trip number": self.trip_no, "Trip URL": self.page_url})
        self.last_adding = datetime.now().strftime("%d-%b-%Y (%H:%M:%S.%f)")
        logmessage = "Trip number: " + \
            str(self.trip_no) + " Trip URL: " + \
            self.page_url + " Added: " + self.last_adding
        logging.info(logmessage)
        # získá všechny zbylé parametry z mých webových stránek o cestování
        self.get_all_parameters()
        # parametry aplikace na FB, která potom na PB přistupuje

    @classmethod
    def printInstances(cls):
        for trip in cls.trips:
            print(trip)

    # Nastavení bázové adresy dotazu
    def set_base_url(self, new_url=None):
        if new_url is None:
            self.base_url = self.BASE_URL
        else:
            self.base_url = new_url
        return self.base_url

    # Získání bázové adresy dotazu
    def get_base_url(self):
        return self.base_url

    # Získání API přístupu na FB
    def get_api2(self, page_user_name=None):
        """
        Vrací přístup na FB stránku.
        Na základě předaného jména stránky:
        @travelasap.cz
        @cestujhned
        si sestaví si cfg, což je konfigurační slovník, kde:
        cfg = {
        "page_id"      : id stránky na FB],
        "access_token" : přístupový token pro danou stránku
        }

        Pokud předané jméno stránky neexistuje nebo nebylo žádné předáno, nastaví ho na @travelasap.cz
        """
        if page_user_name is None or not any(i['page_user_name'] == page_user_name for i in self.my_pages):
            page_user_name = "@travelasap.cz"

        cfg = {
            "page_id": self.my_pages[[i for i, _ in enumerate(self.my_pages) if _['page_user_name'] == page_user_name][0]]["page_id"],
            "access_token": self.fb_app["access_token"],
        }

        graph = facebook.GraphAPI(cfg['access_token'])
        # Get page token to post as the page. You can skip
        # the following if you want to post as yourself.
        resp = graph.get_object('me/accounts')
        page_access_token = None
        for page in resp['data']:
            if page['id'] == cfg['page_id']:
                page_access_token = page['access_token']
        graph = facebook.GraphAPI(page_access_token)
        return graph

    # Získání veškerých dat o zájezdu ze stránek travelasap.cz
    def get_all_parameters(self):
        """
        Vrací všechny parametry daného zájezdu:
        """
        # Initialize Selenium webdriver
        options = webdriver.ChromeOptions()

        options.add_argument("--ignore-certificate-errors")

        driver = webdriver.Chrome(mc.PATH_CHROME, options=options)
        # Load the web page
        driver.get(self.page_url)
        # Wait for JavaScript to load
        wait_time = 15  # Adjust as needed
        time.sleep(wait_time)
        driver.implicitly_wait(wait_time)
        # Get the rendered HTML source
        html_source = driver.page_source
        print(html_source)

        # Close the browser window
        driver.quit()
        # self.status = 0
        # while self.status != 200:
        #     self.page = requests.get(self.page_url)
        #     self.status = self.page.status_code
        # self.soup = BS(self.page.content, 'html.parser')

        # Tady naparsuju všechny parametry, které potřebuju, a přiřadím do instančních proměnných
        self.soup = BS(html_source, 'html.parser')
        # self.page_url_full = html_source.url.split(sep="?")[0]
        self.title = self.soup.find("h1").text.strip()
        self.hotel = self.soup.find("h1", class_='hotel').text.strip()
        self.hotel2 = self.title.split(" nabízí ")[0].strip()
        self.board = self.soup.find("div", class_='boarding').text.strip()
        # cena včetně nedělitelných mezer
        # MUSÍ SE NAHRADIT FUNKCÍ NA ČTENÍ TERMÍNOPOKOJŮ !!!
        """ self.price_full = self.soup.find(
            "a", class_="change-structured-content pric b-pric").text.strip().replace(" ", "")
        # cena kompaktní bez mezer, ale s jednotkou měny
        self.price_compact = self.title.split(" ")[-5]
        # cena pouze jako číslo int v korunách
        self.price_number = int(self.price_compact[:-2]) """
        dates_lists = self.soup.find_all('div', class_='dates__item')
        print(dates_lists)

        # Vytvořte prázdný slovník pro uložení dat
        vacation_dates = {}

        # Projděte seznam div.dates__list prvků
        for dates_list in dates_lists:
            # Projděte každý div.dates__item prvek uvnitř div.dates__list
            dates_items = dates_list.find_all('div', class_='dates__item')
            for number, dates_item in enumerate(dates_items.items()):
                trip_no_room = dates_item.get('data-id')
                print(f"Průchod: {number}:\n{trip_no_room}")

        """
        self.duration = self.soup.find("div", class_='dur').text.strip()
        # self.duration_text = get_adjective_days(self.duration)
        self.price_oneday = int(
            self.price_number / int(self.duration.split(" ")[0]))
        self.date_whole = self.soup.find("div", class_='date').text.strip()
        self.date_from = self.soup.find("div", class_='date').text.strip()
        self.date_to = self.soup.find("div", class_='date').text.strip()
        self.destination = self.soup.find("div", class_='dest').text.strip()
        self.country = self.destination.split(sep="»")[0].strip()
        self.rating = "5*"
        self.date_from = self.title.split(" ")[-3]
        self.date_to = self.title.split(" ")[-1]
        self.date_from_obj = datetime.strptime(self.date_from, '%d.%m.%y')
        self.date_from_dif = (
            self.date_from_obj - datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)).days
        # self.date_from_dif_text = get_num_days(self.date_from_dif)
        self.airport = self.soup.find("div", class_='air').text.strip()
        self.discount = self.soup.find("div", class_='dis').text.strip()
        self.pictures = ["https:" + a['href'] for a in self.soup.find(
            "div", class_='pics-inner').find_all('a', href=True) if a.text]
        self.rating = str(len(self.soup.find(
            dir, class_="rating").find_all("img", class_="nb star"))) + "*"
"""
        self.status = 200
        return self.status

    def post_to_fb(self, msg, *publish_time):
        cfg = {
            "page_id": mc.FB_PAGES["travelasap.cz"]["page_id"],
            "access_token": mc.FB_APP["access_token"]
        }

        api = self.get_api(cfg)
        status = api.put_object(
            parent_object="me",
            connection_name="feed",
            message=msg,
            published=False,
            scheduled_publish_time="2021-05-13T21:13:30+01:00",
            link=self.page_url_full)
        return status

    def get_api(self, cfg):
        graph = facebook.GraphAPI(cfg['access_token'])
        # Get page token to post as the page. You can skip
        # the following if you want to post as yourself.
        resp = graph.get_object('me/accounts')
        page_access_token = None
        for page in resp['data']:
            if page['id'] == cfg['page_id']:
                page_access_token = page['access_token']
        graph = facebook.GraphAPI(page_access_token)
        return graph


if __name__ == '__main__':

    zajezd1 = Trip("346324751")
    if zajezd1.status != 200:
        zajezd1.get_all_parameters()

    z1 = zajezd1

    print(z1.trip_no, z1.title)

    """z1.post_to_fb("Odleťte " + z1.date_from + " za málo peněz (" +
                  z1.price_full + ") do destinace " + z1.destination)
    logmessage = "Trip number: " + \
        str(z1.trip_no) + " Trip URL: " + z1.page_url + \
        " Posted to Facebook: " + z1.last_adding
    logging.info(logmessage)
    """
