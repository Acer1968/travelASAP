import facebook
import requests
from bs4 import BeautifulSoup as BS
import os
# import random as rnd
# from string import Template
# from collections import namedtuple
# import csv
from selenium import webdriver
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
from datetime import datetime
# from datetime import date
# from time import sleep
# import re
# from urllib.request import urlopen
import myconfig as mc


class Hotel():
    """
    Pro konkrétní hotel hotel_no získá pomocí scrapingu z našich stránek
    všechny důležité údaje o hotelu.

    hotel_no - číslo hotelu v CeSYSu
    page_user_name - uživatelský název stránky na FB, defaultně @cestujhned

    """

    def get_page_source(self, url, *args, path_driver=mc.PATH_CHROME,):
        self.page_status = 0
        while self.page_status != 200:
            if path_driver is mc.PATH_CHROME:
                chrome_options = Options()
                for arg in args:
                    chrome_options.add_argument(arg)
                self.driver = webdriver.Chrome(path_driver, options=chrome_options)
                self.driver.get(url)
                delay = mc.DELAY_TIME
                try:
                    myElem = WebDriverWait(self.driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, "ui-row-ltr")))
                    print("Page is ready!")
                    print(myElem)
                except TimeoutError:
                    print("Loading took too much time!")
                self.html_element = self.driver.find_element_by_tag_name("html")
                self.html_source = self.driver.page_source
                self.page_status = 200
            else:
                pass

    def set_image_filename(self):
        filename = self.country.replace(" ", "-") + "-" + self.hotel_no
        tempdate = datetime.today()
        filename += "-" + tempdate.strftime("%y%m%d")
        filename += "-" + self.hotel.replace(" ", "-")
        filename += ".png"
        return filename

    def chrome_fullpage_screenshot(self):
        # self.driver.set_window_size(1120, 4000)
        myzoom = 110
        self.driver.execute_script("document.body.style.zoom='{myzoom}%'")
        element = self.driver.find_element_by_xpath('//*[@id="heading"]')
        print("Souřadnice nalezeného elementu jsou: ", element.location['x'], element.location['y'])
        self.screenshot_filename = self.set_image_filename()
        self.screenshot_filename = os.path.join(mc.PATH_DISPLAY, self.screenshot_filename)
        self.driver.save_screenshot(self.screenshot_filename)
        x = element.location['x']
        # to get the y axis
        # POZOR, pokud používám stránku v režimu zoom, tak musím souřadnice
        # prvku vynásobit také tím zoomem, protože skutečné souřadnice jsou posunuté díky tomu zoomu
        y = int(myzoom / 100 * element.location['y'])
        # to get the length the element
        height = y + 1920
        # to get the width the element
        width = x + 1080
        # to open the captured image
        imgOpen = Image.open(self.screenshot_filename)
        # to crop the captured image to size of that element
        imgOpen = imgOpen.crop((int(x), int(y), int(width), int(height)))
        # to save the cropped image
        imgOpen.resize((1080, 1920))
        i2 = imgOpen.transpose(Image.ROTATE_90)
        i2.save(self.screenshot_filename)
        i2.close
        imgOpen.close
        return True

    def __init__(self, hotel_no):
        if isinstance(hotel_no, str):
            self.hotel_no = str(hotel_no)
        elif isinstance(hotel_no, int):
            self.hotel_no = str(hotel_no)
        # KONSTANTY a předem známé hodnoty
        # základní bázová adresa URL pro dotazy na travelasap
        self.base_url = mc.URL_BASE
        self.short_url = os.path.join(self.base_url, mc.URL_TYPEITEM_SELECTOR["hotel"], self.hotel_no, mc.URL_START_TAB["hotel"])
        print(self.short_url)
        self.get_page_source(self.short_url, 'window-size=1120,4000', '--headless')
        self.get_all_parameters()  # natáhni všechny parametry
        self.chrome_fullpage_screenshot()  # Udělej screenshot hotelu
        self.driver.close()

    # Získání veškerých dat o zájezdu ze stránek travelasap.cz
    def get_all_parameters(self):
        self.soup = BS(self.html_source, 'html.parser')

        # Tady naparsuju všechny parametry, které potřebuju, a přiřadím do
        # slovníku s parametry
        # self.url_full1 = self.page.url.split(sep="?")[0]

        self.title = self.soup.find("h1").text.strip()
        self.hotel = self.soup.find("div", class_='hotel').text.strip()
        self.hotel2 = self.title.split(" za cenu ")[0].strip()
        self.board = self.soup.find("div", class_='board').text.strip()
        # self.price_f = self.soup.find("a", class_="change-structured-content pric b-pric").text.strip().replace(" ","") #cena včetně nedělitelných mezer
        self.price_c = self.title.split(" ")[-5]  # cena kompaktní bez mezer, ale s jednotkou měny
        self.price_n = int(self.price_c[:-2])
        # self.duration = self.soup.find("div", class_='dur').text.strip()
        # self.duration_text = get_adjective_days(self.duration)
        # self.price_oneday = int(self.price_n/int(self.duration.split(" ")[0]))
        # self.date_whole = self.soup.find("div", class_='date').text.strip()
        # date_from = self.soup.find("div", class_='date').text.strip()
        # date_to = self.soup.find("div", class_='date').text.strip()
        self.destination = self.soup.find("div", class_='dest').text.strip()
        self.country = self.destination.split(sep="»")[0].strip()
        self.rating = "5*"
        self.date_from = self.title.split(" ")[-3]
        self.date_to = self.title.split(" ")[-1]
        # self.date_from_obj = datetime.strptime(self.date_from,'%d.%m.%y')
        # self.date_from_dif = (self.date_from_obj-datetime.today().replace(hour = 0, minute = 0, second = 0, microsecond = 0)).days
        # self.date_from_dif_text = get_num_days(self.date_from_dif)
        self.airport = self.soup.find("div", class_='air').text.strip()
        # self.discount = self.soup.find("div", class_='dis').text.strip()
        # self.pictures = ["https:"+a['href'] for a in self.soup.find("div", class_='pics-inner').find_all('a', href=True) if a.text]
        self.rating = str(len(self.soup.find(dir, class_="rating").find_all("img", class_="nb star"))) + "*"
        return True


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
        self.trip_no = trip_no
        self.__class__.trips.append((self, trip_no))
        # KONSTANTY a předem známé hodnoty
        # základní bázová adresa URL pro dotazy na travelasap
        self.base_url = os.path.join(mc.URL_BASE, "d")

        # parametry mých FB stránek o cestování

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
    def get_api(self, page_user_name=None):
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

        Pokud předané jméno stránky neexistuje nebo nebylo žádné předáno, nastaví ho na @cestujhned
        """
        if page_user_name is None or not any(i['page_user_name'] == page_user_name for i in self.my_pages):
            page_user_name = "@cestujhned"

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
    def get_all_trip_parameters(self):
        """
        Vrací všechny parametry daného zájezdu:


        """
        # self.page_url = os.path.join(self.base_url, str(self.trip_no))
        self.page_url = self.base_url + "/" + self.trip_no
        self.trip_params = {}
        self.status = 0

        # print(page_url)
        while self.status != 200:
            self.page = requests.get(self.page_url)
            self.status = self.page.status_code
        self.soup = BS(self.page.content, 'html.parser')

        # Tady naparsuju všechny parametry, které potřebuju, a přiřadím do slovníku s parametry

        self.trip_no = str(self.trip_no)
        self.url = self.page_url
        self.url_full = self.page.url.split(sep="?")[0]
        self.title = self.soup.find("h1").text.strip()
        self.hotel = self.soup.find("div", class_='hotel').text.strip()
        self.hotel2 = self.title.split(" za cenu ")[0].strip()
        self.board = self.soup.find("div", class_='board').text.strip()
        self.price_f = self.soup.find("a", class_="change-structured-content pric b-pric").text.strip().replace(" ", "")  # cena včetně nedělitelných mezer
        self.price_c = self.title.split(" ")[-5]  # cena kompaktní bez mezer, ale s jednotkou měny
        self.price_n = int(self.price_c[:-2])
        self.duration = self.soup.find("div", class_='dur').text.strip()
        # self.duration_text = get_adjective_days(self.duration)
        self.price_oneday = int(self.price_n / int(self.duration.split(" ")[0]))
        self.date_whole = self.soup.find("div", class_='date').text.strip()
        # date_from = self.soup.find("div", class_='date').text.strip()
        # date_to = self.soup.find("div", class_='date').text.strip()
        self.destination = self.soup.find("div", class_='dest').text.strip()
        self.country = self.destination.split(sep="»")[0].strip()
        self.rating = "5*"
        self.date_from = self.title.split(" ")[-3]
        self.date_to = self.title.split(" ")[-1]
        self.date_from_obj = datetime.strptime(self.date_from, '%d.%m.%y')
        self.date_from_dif = (self.date_from_obj - datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)).days
        # self.date_from_dif_text = get_num_days(self.date_from_dif)
        self.airport = self.soup.find("div", class_='air').text.strip()
        self.discount = self.soup.find("div", class_='dis').text.strip()
        self.pictures = ["https:" + a['href'] for a in self.soup.find("div", class_='pics-inner').find_all('a', href=True) if a.text]
        self.rating = str(len(self.soup.find(dir, class_="rating").find_all("img", class_="nb star"))) + "*"
        return self.status, self.trip_params


if __name__ == '__main__':
    # hotel1 = Hotel("19270")
    zajezd1 = Trip("222502811")
    zajezd1.get_all_trip_parameters()
    zajezd2 = Trip("224262696")
    zajezd2.get_all_trip_parameters()
    z1 = zajezd1
    z2 = zajezd2
    print(z1.trip_no, z1.title)
    print(z2.trip_no, z2.title)
