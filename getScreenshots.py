# %%
"""
SKRIPT POUŽÍVÁ PIL
Skript vezme všechny zájezdy z proměnné items a vyrobí pro ně screenshoty 1080x1920 na displej do okna, kde zobrazí základní informace o konkrétním zájezdu a celkový popis hotelu.

Stejně to umí i se stránkami hotelů, tam ale zobrazuje místo popisu hotelu seznam dalších termínů.
"""

from selenium import webdriver
from time import sleep
import os
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
from bs4 import BeautifulSoup as BS
import random as rnd
from string import Template
from collections import namedtuple
import csv
from datetime import datetime, date
import re
from urllib.request import urlopen
import logging
import myconfig as mc

logging.basicConfig(
    filename=mc.LOG_FILENAME, encoding=mc.LOG_ENCODING, level=logging.DEBUG
)

# items = {"type": "hotel","items": [192584]}#,107314,369]}
items = {
    "type": "trip",
    "items": [
        304278707,
        304203107,
        304201889,
        304209209,
        304285651,
        304260832,
        304201831,
        304283085,
        304267536,
        304202976,
        304285624,
        304286075,
        304211202,
        304208415,
        304269816,
        304285587,
        304206724,
        304285221,
        304285515,
        289856365,
        291071355,
        286371631,
        304262512,
        304201879,
        304285937,
        304210693,
        285388912,
        285529360,
        304284921,
        304208404,
    ],
}


def get_num_days(num):
    if num == 0:
        return str(num) + " dnů"
    if num == 1:
        return str(num) + " den"
    if num >= 2 and num <= 4:
        return str(num) + " dny"
    if num >= 5:
        return str(num) + " dnů"


def get_adjective_days(duration):
    num = int(duration.split()[0])
    adjectives = ["krásn", "úžasn", "nádhern", "příjemn", "odpočinkov", "exotick"]
    adjective = rnd.choice(adjectives)
    if num == 0:
        return adjective + "ých " + str(num) + " dnů"
    if num == 1:
        return adjective + "ý " + str(num) + " den"
    if 2 >= num <= 4:
        return adjective + "é " + str(num) + " dny"
    if num >= 5:
        return adjective + "ých " + str(num) + " dnů"


def chrome_fullpage_access(itemtype, item):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("window-size=1120,4000")
    # chrome_options.add_argument('--start-maximized')
    driver = webdriver.Chrome(mc.PATH_CHROME, options=chrome_options)
    driver.get(os.path.join(mc.URL_BASE, mc.URL_TYPEITEM_SELECTOR[itemtype], str(item)))
    return driver


def chrome_fullpage_screenshot(driver, filename):
    driver.set_window_size(
        mc.HIDE_BROWSER_WINDOW_SIZE["width"], mc.HIDE_BROWSER_WINDOW_SIZE["height"]
    )
    driver.execute_script("document.body.style.zoom='150%'")
    element = driver.find_element_by_xpath('//*[@id="heading"]')
    sleep(5)
    # print("Souřadnice nalezeného elementu jsou: ", element.location['x'], element.location['y'])

    filename = os.path.join(mc.PATH_DISPLAY, filename)
    driver.save_screenshot(filename)

    x = element.location["x"]
    # to get the y axis
    # POZOR, pokud používám stránku v režimu zoom, tak musím souřadnice prvku vynásobit také tím zoomem, protože skutečné souřadnice jsou posunuté díky tomu zoomu
    y = int(mc.ZOOM_PAGE_RATIO["trip"] * element.location["y"])
    # to get the length the element
    height = y + 1920
    # to get the width the element
    width = x + 1080
    # to open the captured image
    imgOpen = Image.open(filename)
    # to crop the captured image to size of that element
    imgOpen = imgOpen.crop((int(x), int(y), int(width), int(height)))
    # to save the cropped image
    imgOpen.resize((1080, 1920))

    imgNew = imgOpen.rotate(90, expand=True)
    imgNew.save(filename)
    return imgOpen


def get_trip_parameters_from_fullpage(driver, item):
    trip_parameters = {}
    trip_no = item
    soup = BS(driver.page_source, "html.parser")
    page_url = driver.current_url
    # Tady si zjistím jen titulek, odlet a přílet
    trip_parameters["title"] = soup.find("h1").text.strip()
    trip_parameters["date_from"] = trip_parameters["title"].split(" ")[-3]
    trip_parameters["date_to"] = trip_parameters["title"].split(" ")[-1]
    # Tady zjistím, jestli termín není vyprodaný nebo jestli už není špatný datum odletu
    if (
        soup.find("div", class_="other-info__erased").text
        == "TENTO TERMÍN BYL JIŽ VYPRODÁN."
    ):
        trip_parameters["is_active"] = False
        logmessage = ("Trip: ", trip_no, " - TENTO TERMÍN BYL JIŽ VYPRODÁN.").join()
        print("WARNING:", logmessage)
        logging.warning = logmessage
    elif datetime.strptime(trip_parameters["date_from"], "%d.%m.%y") < datetime.today():
        trip_parameters["is_active"] = False
        logmessage = (
            "Trip: ",
            trip_no,
            " - TOHLE JE MINULOST... s odletem ",
            trip_parameters["date_from"],
        ).join()
        print(logmessage)
        logging.warning = logmessage
    else:
        trip_parameters["is_active"] = True
    # Tady naparsuju všechny parametry, které potřebuju (pro zájezdy, které nejsou vyprodané a které mají odlet v budoucnu), a přiřadím do slovníku s parametry

    if trip_parameters["is_active"]:
        trip_parameters["trip_no"] = str(trip_no)
        trip_parameters["url"] = page_url
        trip_parameters["url_full"] = page_url.split(sep="?")[0]
        trip_parameters["hotel_no"] = re.findall(
            "\/[0-9]*a\/", trip_parameters["url_full"]
        )[0][1:-2]
        trip_parameters["hotel"] = soup.find("div", class_="hotel").text.strip()
        trip_parameters["hotel2"] = (
            trip_parameters["title"].split(" za cenu ")[0].strip()
        )
        trip_parameters["board"] = soup.find("div", class_="board").text.strip()
        trip_parameters["price_f"] = (
            soup.find("a", class_="change-structured-content pric b-pric")
            .text.strip()
            .replace(" ", "")
        )  # cena včetně nedělitelných mezer
        trip_parameters["price_c"] = trip_parameters["title"].split(" ")[
            -5
        ]  # cena kompaktní bez mezer, ale s jednotkou měny
        trip_parameters["price_n"] = int(
            trip_parameters["price_c"][:-2]
        )  # cena kompaktní jenom číslo
        trip_parameters["price_old_f"] = soup.find(
            "div", class_="old-price"
        ).text  # původní cena včetně nedělitelných mezer
        trip_parameters["price_old_c"] = (
            trip_parameters["price_old_f"].replace(".", "").replace("\xa0", "")
        )  # původní cena kompaktní bez mezer, ale s jednotkou měny
        trip_parameters["price_old_n"] = (
            int(trip_parameters["price_old_c"][:-2])
            if trip_parameters["price_old_c"][:-2] != ""
            else 0
        )  # původní cena kompaktní jenom číslo
        trip_parameters["duration"] = soup.find("div", class_="dur").text.strip()
        trip_parameters["duration_text"] = get_adjective_days(
            trip_parameters["duration"]
        )
        trip_parameters["price_oneday"] = int(
            trip_parameters["price_n"] / int(trip_parameters["duration"].split(" ")[0])
        )
        trip_parameters["date_whole"] = soup.find("div", class_="date").text.strip()
        # date_from = soup.find("div", class_='date').text.strip()
        # date_to = soup.find("div", class_='date').text.strip()
        trip_parameters["destination"] = soup.find("div", class_="dest").text.strip()
        trip_parameters["country"] = (
            trip_parameters["destination"].split(sep="»")[0].strip()
        )
        trip_parameters["rating"] = "5*"
        trip_parameters["date_from_obj"] = datetime.strptime(
            trip_parameters["date_from"], "%d.%m.%y"
        )
        trip_parameters["date_from_dif"] = (
            trip_parameters["date_from_obj"]
            - datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        ).days
        trip_parameters["date_from_dif_text"] = get_num_days(
            trip_parameters["date_from_dif"]
        )
        trip_parameters["airport"] = soup.find("div", class_="air").text.strip()
        trip_parameters["discount"] = soup.find("div", class_="dis").text.strip()
        trip_parameters["pictures"] = [
            "https:" + a["href"]
            for a in soup.find("div", class_="pics-inner").find_all("a", href=True)
            if a.text
        ]
        trip_parameters["rating"] = (
            str(len(soup.find(dir, class_="rating").find_all("img", class_="nb star")))
            + "*"
        )
    return trip_parameters


def get_hotel_parameters_from_fullpage(driver, item):
    hotel_params = {}
    hotel_no = item
    soup = BS(driver.page_source, "html.parser")
    page_url = driver.current_url
    hotel_params["url"] = page_url
    hotel_params["url_full"] = page_url.split(sep="?")[0]
    hotel_params["hotel_no"] = re.findall("\/[0-9]*a", hotel_params["url_full"])[0][
        1:-1
    ]
    hotel_params["title"] = soup.find("h1").text.strip()
    hotel_params["hotel"] = soup.find("div", class_="hotel").text.strip()
    hotel_params["hotel2"] = hotel_params["title"].split(" za cenu ")[0].strip()
    hotel_params["board"] = soup.find("div", class_="board").text.strip()
    hotel_params["price_min"] = hotel_params["title"].split(" ")[
        -1
    ]  # cena OD včetně nedělitelných mezer, ale s jednotkou měny
    hotel_params["trips_count"] = hotel_params["title"].split(" ")[
        -5
    ]  # počet termínů nabízených hotelem
    hotel_params["destination"] = soup.find("div", class_="dest").text.strip()
    hotel_params["country"] = hotel_params["destination"].split(sep="»")[0].strip()
    hotel_params["rating"] = "5*"
    hotel_params["date_from"] = hotel_params["title"].split(" ")[-3]
    # hotel_params["date_to"] = hotel_params["title"].split(" ")[-1]
    hotel_params["airport"] = soup.find("div", class_="air").text.strip()
    hotel_params["pictures"] = [
        "https:" + a["href"]
        for a in soup.find("div", class_="hotel-gallery").find_all("a", href=True)
    ]
    hotel_params["rating"] = (
        str(len(soup.find(dir, class_="rating").find_all("img", class_="nb star")))
        + "*"
    )
    hotel_params["trips_table"] = soup.select("tbody")
    return hotel_params


def set_image_filename(itemtype, params):
    filename = params["country"].replace(" ", "-") + "-" + params["hotel_no"]
    if itemtype == "trip":
        filename += "-" + params["trip_no"]
        tempdate = params["date_from"].split(".")
        filename += "-" + tempdate[2] + tempdate[1] + tempdate[0]
    elif itemtype == "hotel":
        tempdate = datetime.today()
        filename += "-" + tempdate.strftime("%y%m%d")
    filename += "-" + params["hotel"].replace(" ", "-")
    filename += ".png"
    return filename


def generate_hotel_offers(params):
    from PIL import Image, ImageDraw, ImageFont

    # define parameters
    radek = 0
    radek_prvni = 810
    vyska_radku = 85
    start_radku = 30
    start_suma = 750
    start_sleva = 1000
    posun_sumy = -25
    barva_bila = (255, 255, 255, 255)
    barva_zlata = (247, 147, 32, 255)
    barva_cervena = (255, 0, 0, 255)
    barva_modra = (175, 218, 238, 255)
    levy_okraj = 35

    # get a font
    UBbig = ImageFont.truetype(
        "D:/PetrVavrinec/Downloads/fonty/Ubuntu/Ubuntu-Bold.ttf", 72
    )
    Usmall = ImageFont.truetype(
        "D:/PetrVavrinec/Downloads/fonty/Ubuntu/Ubuntu-Regular.ttf", 40
    )
    UBImiddle = ImageFont.truetype(
        "D:/PetrVavrinec/Downloads/fonty/Ubuntu/Ubuntu-BoldItalic.ttf", 55
    )

    # get an image
    base = Image.open(
        "D:/PetrVavrinec/Dokumenty/www/www.travelasap.cz/grafika/displej-v-okne/podklady/podklad.png"
    ).convert("RGBA")

    # make a blank image for the text, initialized to transparent text color
    txt = Image.new("RGBA", base.size, (255, 255, 255, 0))
    d = ImageDraw.Draw(txt)

    sconto = Image.new("RGBA", base.size, (255, 255, 255, 0))
    e = ImageDraw.Draw(sconto)

    # get a drawing context
    hotel = params["hotel"]
    if len(hotel) > 25:
        hotel = hotel[:25] + "…"

    # draw text, half opacity
    d.text((levy_okraj, 40), hotel, font=UBbig, fill=barva_modra)
    # draw text, full opacity
    d.text((levy_okraj, 140), params["destination"], font=Usmall, fill=barva_bila)
    d.text(
        (levy_okraj + 200, 180),
        "nabízí " + params["trips_count"] + " termínů již od ",
        font=Usmall,
        fill=barva_bila,
    )
    d.text((levy_okraj + 650, 150), params["price_min"], font=UBbig, fill=barva_zlata)

    # draw text, full opacity
    odlety = get_departures(driver, 7)

    for odlet in odlety:
        sleva = "0"
        suma = odlet.split(" za ")[-1]
        odlet = odlet[: -(len(suma) + 1)]
        d.text(
            (start_radku, radek_prvni + vyska_radku * radek),
            odlet,
            font=UBImiddle,
            fill=barva_bila,
        )
        if "-" in suma and "%" in suma:
            sleva = suma.split("-")[1].replace(" ", "")
            suma = suma.split("-")[0]
        d.text(
            (start_suma, radek_prvni + vyska_radku * radek + posun_sumy),
            suma,
            font=UBbig,
            fill=barva_zlata,
        )
        if sleva != "0":
            e.text(
                (start_suma, radek_prvni + vyska_radku * radek + posun_sumy),
                sleva,
                font=UBbig,
                fill=barva_cervena,
            )
            pass
        radek += 1

    out1 = Image.alpha_composite(base, txt)
    out = Image.alpha_composite(out1, sconto)
    return out


def get_departures(driver, count_dep):
    soup = BS(driver.page_source, "html.parser")
    odjezdy = soup.find_all("td", {"aria-describedby": "grid_date_from"})
    trvani = soup.find_all("td", {"aria-describedby": "grid_duration"})
    strava = soup.find_all("td", {"aria-describedby": "grid_boarding_id"})
    letiste = soup.find_all("td", {"aria-describedby": "grid_transport_id"})
    ceny = soup.find_all("td", {"aria-describedby": "grid_price"})

    informace = list(
        map(
            lambda x, y: "od "
            + str(x.text).replace("\xa0", "").replace("2021", "21")
            + " na "
            + str(y.text).replace("\xa0", ""),
            odjezdy,
            trvani,
        )
    )
    informace2 = list(
        map(
            lambda x, y: str(x).replace("\xa0", "")
            + " s "
            + str(y.text).replace("\xa0", ""),
            informace,
            strava,
        )
    )
    informace3 = list(
        map(
            lambda x, y: str(x).replace("\xa0", "")
            + " za "
            + str(y.text).replace("\xa0", ""),
            informace2,
            ceny,
        )
    )
    return informace3[:count_dep]


def get_photos(driver, params, img_origin):
    counter = 0
    img_copy = img_origin.copy()
    number_of_photos = len(params["pictures"])
    for photo in params["pictures"]:
        counter += 1
        img = Image.open(urlopen(photo))
        size = img.size
        new_img = None
        if counter == 1:
            if size[0] > 800 or size[1] > 600:
                img = img.resize((800, 600), Image.ANTIALIAS)
                size = new_img.size
            x = 1080 - size[0] // 2
            y = 700
            img_copy.paste(img, (x, y))
        if counter > 1:
            img = img.resize((400, 300), Image.ANTIALIAS)
            img_copy.paste(
                img,
                (100 + 420 * (counter - 2) % 3, 800 + 320 * int((counter - 2) // 3)),
            )


# %%
def get_items_from_admin():
    chrome_options = Options()
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument("window-size=1120,900")
    driver = webdriver.Chrome(mc.PATH_CHROME, options=chrome_options)
    driver.get(os.path.join(mc.URL_BASE, "admin"))
    username = driver.find_element_by_id("UserUsername")
    userpass = driver.find_element_by_id("UserPassword")
    username.send_keys("vavrinec")
    userpass.send_keys("tra789")
    userbutt = driver.find_element_by_xpath(
        "/html/body/div[1]/div/div/div/div/form/div/div[2]/div[1]/input"
    )
    userbutt.click()
    # userbutt = driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div[1]/div/ul/li[1]/span')
    # userbutt.click()
    # userbutt = driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div[2]/div/ul[1]/li[6]/a')
    # userbutt.click()
    driver.get(os.path.join(mc.URL_BASE, "admin", "offer_conditions", "date", "2"))
    items_element = driver.find_element_by_id("OfferConditionsDateTripNumbers")
    found_terms = list(items_element.text.split(","))
    print(f"Nalezeno celkem {len(found_terms)} zájezdů - hitů týdne...")
    return found_terms
    pass


# %%
if __name__ == "__main__":
    if items["items"] == []:
        items["items"] = get_items_from_admin()
        logmessage = "Source: webpage - "
    else:
        logmessage = "Source: list - "
    logmessage += ",".join([str(item) for item in items["items"]])
    print("Logmessage = ", logmessage)
    logging.info(logmessage)
    remaining_terms = len(items["items"])
    current_term = 0
    for item in items["items"]:
        print(f"Zbývá ke zpracování {remaining_terms} zájezdů...")
        current_term += 1
        print(f"Zpracovávám {current_term}. zájezd...")
        driver = chrome_fullpage_access(items["type"], item)
        # print(driver.page_source)
        if items["type"] == "trip":
            params = get_trip_parameters_from_fullpage(driver, item)
        elif items["type"] == "hotel":
            params = get_hotel_parameters_from_fullpage(driver, item)
        else:
            pass
        if params["is_active"]:
            new_filename = set_image_filename(items["type"], params)
            print(new_filename)
            filename = os.path.join(mc.PATH_DISPLAY, new_filename)
            screenshot = chrome_fullpage_screenshot(driver, filename)
        # screenshot = generate_hotel_offers(params)
        # get_photos(driver, params, screenshot)
        # screenshot.show()
        # get_departures(driver, 7)
        # print(params)
        driver.quit()
        remaining_terms -= 1

# %%
