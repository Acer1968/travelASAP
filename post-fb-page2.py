"""
My "app" allows our fans to find great travel opportunities. Every trip has a lot of parameters according to which the fans decide, so I don't want to make the mistake of "manual rewriting". We are preparing for invoiced campaigns on Facebook, so we must be accurate and interesting in terms of content. We will also use the script to add UTM parameters to the URL.

Script obsahuje sadu funkcí, které připravují podklady pro vytvoření příspěvku na Facebooku.
"""
import facebook
import requests
from bs4 import BeautifulSoup as BS
import os
import random as rnd
from string import Template
from collections import namedtuple
import csv
from datetime import datetime

Testovani = True

utm_params_string = "${website_url}?utm_source=${campaign_source}&utm_medium=${campaign_medium}&utm_campaign=${campaign_name}&utm_term=${campaign_term}&utm_content=${campaign_content}"


def get_adjective(adj, capitalize=False, pad=4, rod="mžj"):
    """
    Vytvoří přídavná jména v příslušném pádu a rodu.
    Vstup:
    adj - přídavné jméno, zkrácený tvar před přiřazením koncovky
    (např. ze slova krásný předáme jen krásn)
    capitalize - True - pokud je přídavné jméno první ve větě
    False (default) - pokud je přídavné jméno uprostřed věty
    pad - v jakém pádu chci vrátit přídavné jméno
    rod - v jakém rodě a čísle bude následující podstatné jméno, je to zkratka, která je ve slovníku koncovky
    Výstup:
    přídavné jméno ve správném tvaru
    Poznámka: koncovky je slovník, kde klíčem jsou zkratky určující rod a číslo a u mužského rodu rozlišuje i životný a neživotný tvar. Hodnotou slovníku j e seznam koncovek přídavného jména v příslušném pádu. Samozřejmě díky indexaci pythonu od nuly má první pád hodnotu 0, sedmý pád hodnotu 6.
    """
    koncovky_tvrde = {
        "mžj": "ý ého ému ého ý ém ým".split(),  # mužský životný jednotný
        "mnj": "ý ého ému ý ý ém ým".split(),  # mužský neživotný jednotný
        "žj": "á é é ou á é ou".split(),  # ženský jednotný
        "sj": "é ého ému é é ém ým".split(),  # střední jednotný
        "mžm": "í ých ým é í ých ými".split(),  # mužský životný množný
        "mnm": "é ých ým é é ých ými".split(),  # mužský neživotný množný
        "žm": "é ých ým é é ých ými".split(),  # ženský množný
        "sm": "á ých ým á á ých ými".split()  # střední množný
    }
    koncovky_mekke = {
        "mžj": "í ího ímu ího í ím ím".split(),  # mužský životný jednotný
        "mnj": "í ího ímu ího í ím ím".split(),  # mužský neživotný jednotný
        "žj": "í í í í í í í".split(),  # ženský jednotný
        "sj": "í ího ímu í í ím ím".split(),  # střední jednotný
        "mžm": "í ích ím í í ích ími".split(),  # mužský životný množný
        "mnm": "í ích ím í í ích ími".split(),  # mužský neživotný množný
        "žm": "í ích ím í í ích ími".split(),  # ženský množný
        "sm": "í ích ím í í ích ími".split()  # střední množný
    }

    prid_jm_tvrda = "příjemn jedinečn skvěl krásn romantick rodinn pohodov exotick báječn dokonal úžasn oblíben".split()  #
    prid_jm_mekka = "jarn letn zimn podzimn relaxačn tradičn".split()

    # Pokud je potřeba první písmeno velké, udělám ho
    adj = adj[0].capitalize() + adj[1:] if capitalize else adj
    # vrátím přídavné jméno v příslušném rodě a pádu
    if adj in prid_jm_mekka:
        adj = adj + koncovky_mekke[rod][pad - 1]
    else:
        adj = adj + koncovky_tvrde[rod][pad - 1]
    return adj


def post_to_fb(msg, trip_param):
    # (page_url,title,hotel,hotel2,board,price,price2,duration,date_whole,date_from,date_to,discount,pictures) = trip_param
    # Fill in the values noted in previous steps here
    cfg = {
        "page_id": my_pages[0]["page_id"],
        "access_token": fb_app["access_token"]
    }

    api = get_api(cfg)

    status = api.put_object(
        parent_object="me",
        connection_name="feed",
        message=msg,
        link=trip_param["url_full"])


def get_api(cfg):
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


def get_num_days(num):
    """
    Vrátí řetězec obsahující číslo vyjadřující počet dní a správný tvar slova den
    """
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


def get_msg_type(trip_param):
    pass


def get_msg(trip_param, msg_type="price1"):
    # msg_type_index_list = [msg_type_index]
    # msg_type_index = rnd.choice(msg_type_index_list)
    # msg_type_index = 3
    # print("\n"+msg_type + ":")
    msg = Templates[msg_type][0].substitute(trip_param)
    return msg


def select_best_msg_type(trip_parameters, last_msg_type, this_trip_last_msg_type):
    """
    Pokusí se vybrat nejvhodnější typ zprávy na FB. Měl by vyloučit typ zprávy, která byla u tohoto zájezdu použita naposledy a také ten typ zprávy, který byl použit naposledy u posledního příspěvku,
    Vstup:
        trip_parameters - kompletní parametry daného zájezdu
        last_msg_type - úplně poslední typ zprávy, který byl použit u posledního příspěvku
        this_trip_last_msg_type - úplně poslední typ zprávy, který byl použit u příspěvku s tímto zájezdem
    """

    def mySortFunc(e):
        """
        Funkce vytváří klíč pro třídění vhodných typů zpráv.
        Jenže se mi vracely pořád dokola podobné zprávy, protože operátoři poskytují číselně stejné slevy a v tipech týdne jsou hlavně zájezdy se slevami.
        Takže nakonec jsem se rozhodl, že celou funkci více znáhodním.
        """
        r = rnd.randint(1, 10)
        if r > 6:
            g = str(r) + e[0]
        else:
            g = e[-1:] + e[0]
        return g

    best_msg_type = []
    """
    Podle hodnoty slevy rozhodne, jestli jsou texty zaměřené na slevu vhodné
    Podle hodnoty cena rozhodne, jestli jsou texty zaměřené na cenu vhodné
    Podle hodnoty odlet rozhodne, jestli jsou texty zaměřené na brzký odlet vhodné
    """
    if trip_parameters["discount"] != "":
        sale = int(trip_parameters["discount"].replace(" ", "").replace("-", "").replace("%", ""))
        sale = 6 - (sale // 6)
        sale = 1 if sale <= 1 else sale
        msg_type_str = "sale" + str(sale)
        if msg_type_str != last_msg_type and msg_type_str != this_trip_last_msg_type:
            best_msg_type.append(msg_type_str)

    priceday = int(trip_parameters["price_oneday"])
    if trip_parameters["country"] in ceny_denni_limity:
        price = priceday // ceny_denni_limity[trip_parameters["country"]] + 1
    else:
        price = priceday // ceny_denni_limity["ostatní"] + 1
    price = 6 if price >= 6 else price
    msg_type_str = "price" + str(price)
    if msg_type_str != last_msg_type and msg_type_str != this_trip_last_msg_type:
        best_msg_type.append(msg_type_str)

    time = trip_parameters["date_from_dif"] // 12 + 1
    time = 6 if time >= 6 else time
    msg_type_str = "time" + str(time)
    if msg_type_str != last_msg_type and msg_type_str != this_trip_last_msg_type:
        best_msg_type.append(msg_type_str)

    # Znáhodnění všech typů zprávy
    for i in range(1, 7):
        msg_type_str = rnd.choice("sale price time".split(" "))
        msg_type_str += str(i)
        best_msg_type.append(msg_type_str)

    if len(best_msg_type) > 0:
        best_msg_type.sort(key=mySortFunc)
    return best_msg_type


def get_parameters_from_ta(trip_no):
    """
    Získá všechny parametry daného zájezdu pomocí webscrapingu ze stránek www.travelasap.cz.
    Vstup: číslo zájezdu
    Návratová hodnota: slovník s jednotlivými parametry

    Parametry zájezdu je možné získat pomocí requests, protože všechny parametry se načítají již v těle HTML a nikoli až dodatečně pomocí Javascriptu.
    """

    trip_parameters = {}
    status = 0
    page_url = os.path.join(ta_url, str(trip_no))
    # print(page_url)
    while status != 200:
        page = requests.get(page_url)
        status = page.status_code
    soup = BS(page.content, 'html.parser')
    with open("output1.html", "w", encoding='utf-8') as file:
        file.write(str(soup))

    # Zjistím, jestli se zájezd koná v budoucnu (eliminace starých) a jestli je ještě aktivní (tzn. není vyprodaný)
    trip_parameters["title"] = soup.find("h1").text.strip()
    trip_parameters["date_from"] = trip_parameters["title"].split(" ")[-3]
    # Pokud není aktivní, vrátím informace do logu, jinak načtu zbylé parametry
    if soup.find("div", class_='other-info__erased').text == "TENTO TERMÍN BYL JIŽ VYPRODÁN.":
        trip_parameters["is_active"] = False
        print("TENTO TERMÍN BYL JIŽ VYPRODÁN.")
    elif datetime.strptime(trip_parameters["date_from"], "%d.%m.%y") < datetime.today():
        trip_parameters["is_active"] = False
        print("TOHLE JE MINULOST...")
    else:
        trip_parameters["is_active"] = True
    # Tady naparsuju všechny parametry, které potřebuju, a přiřadím do slovníku s parametry

    if trip_parameters["is_active"]:
        trip_parameters["trip_no"] = str(trip_no)
        trip_parameters["url"] = page_url
        trip_parameters["url_full"] = page.url.split(sep="?")[0]
        trip_parameters["hotel"] = soup.find("div", class_='hotel').text.strip()
        trip_parameters["hotel2"] = trip_parameters["title"].split(" za cenu ")[0].strip()
        trip_parameters["board"] = soup.find("div", class_='board').text.strip()
        trip_parameters["price_f"] = soup.find("a", class_="change-structured-content pric b-pric").text.strip().replace(" ", "")  # cena včetně nedělitelných mezer
        trip_parameters["price_c"] = trip_parameters["title"].split(" ")[-5]  # cena kompaktní bez mezer, ale s jednotkou měny
        trip_parameters["price_n"] = int(trip_parameters["price_c"][:-2])
        trip_parameters["duration"] = soup.find("div", class_='dur').text.strip()
        trip_parameters["duration_text"] = get_adjective_days(trip_parameters["duration"])
        trip_parameters["price_oneday"] = int(trip_parameters["price_n"] / int(trip_parameters["duration"].split(" ")[0]))
        trip_parameters["date_whole"] = soup.find("div", class_='date').text.strip()
        # date_from = soup.find("div", class_='date').text.strip()
        # date_to = soup.find("div", class_='date').text.strip()
        trip_parameters["destination"] = soup.find("div", class_='dest').text.strip()
        trip_parameters["country"] = trip_parameters["destination"].split(sep="»")[0].strip()
        trip_parameters["rating"] = "5*"
        trip_parameters["date_to"] = trip_parameters["title"].split(" ")[-1]
        trip_parameters["date_from_obj"] = datetime.strptime(trip_parameters["date_from"], '%d.%m.%y')
        trip_parameters["date_from_dif"] = (trip_parameters["date_from_obj"] - datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)).days
        trip_parameters["date_from_dif_text"] = get_num_days(trip_parameters["date_from_dif"])
        trip_parameters["airport"] = soup.find("div", class_='air').text.strip()
        trip_parameters["discount"] = soup.find("div", class_='dis').text.strip()
        trip_parameters["pictures"] = ["https:" + ['href'] for a in soup.find("div", class_='pics-inner').find_all('a', href=True) if a.text]
        trip_parameters["rating"] = str(len(soup.find(dir, class_="rating").find_all("img", class_="nb star"))) + "*"

    return trip_parameters


def print_all_messages(trip_parameters):
    msg_types_list = list(Templates.keys())
    msg_types_list.sort()
    for msg_type in msg_types_list:
        print("\n" + msg_type + ":")
        message = get_msg(trip_parameters, msg_type)
        print(message)
    return True


ceny_denni_limity = {
    "Egypt": 1000,
    "Maledivy": 2000,
    "Tunisko": 1000,
    "Turecko": 1500,
    "ostatní": 2000
}

TemplateType = namedtuple("TemplateTuple", "template utm")
Templates = {
    "time1": TemplateType(Template("ODLET UŽ ZA ${date_from_dif_text} 🕒!!!\nUž ${date_from} můžete odletět 🛫 do " + get_adjective(rnd.choice("hezk krásn oblíben".split(" ")), pad=2) + " hotelu ${hotel} za bombovou cenu ${price_c} . To je ${duration_text} v oblasti ${destination}! To je přesně to, co potřebujete!\nNEVÁHEJTE."), "utm"),

    "time2": TemplateType(Template("Už jen ${date_from_dif_text} 🕒 zbývá do odletu do hotelu ${hotel}!\nOdletět můžete ${date_from} 🛫 a užít si dovolenou v oblasti ${destination}.\nCena je " + get_adjective(rnd.choice("velmi\u00A0přízniv skutečně\u00A0krásn nehorázně\u00A0přitažliv".split(" ")), pad=1, rod='žj') + " - ${price_c}. Po prožití krásných ${duration_text} se budete vracet 🛬 ${date_to} na letiště ${airport}.\nNebo snad máte nějaké jiné, lepší plány?"), "utm"),

    "time3": TemplateType(Template("Za 🕒📅 ${date_from_dif_text} 📅🕒 můžete frčet z letiště ${airport}!!!\nOdletět do hotelu ${hotel} se stravováním ${board} v oblasti ${destination} můžete ${date_from} 🛫🛫🛫🛫.\nDo kapsy hluboko sahat nemusíte, cena ${price_c} potěší každého. Prožití ${duration_text} dovolené se hodí každému, kdo nutně po složitém roce 2020 potřebuje odpočinek. Návrat je 🛬 ${date_to}.\nNám to připadá jako bezva nápad..."), "utm"),

    "time4": TemplateType(Template("Už jen ${date_from_dif_text} 🕒 zbývá do odletu do hotelu ${hotel}!\nOdletět můžete ${date_from} 🛫 a užít si dovolenou v oblasti ${destination}.\nCena je " + get_adjective(rnd.choice("velmi\u00A0přízniv skutečně\u00A0krásn nehorázně\u00A0přitažliv".split(" ")), pad=1, rod='žj') + " - ${price_c}. Po prožití krásných ${duration_text} se budete vracet 🛬 ${date_to} na letiště ${airport}.\nNebo snad máte nějaké jiné, lepší plány?"), "utm"),

    "time5": TemplateType(Template("Už jen ${date_from_dif_text} 🕒 zbývá do odletu do hotelu ${hotel}!\nOdletět můžete ${date_from} 🛫 a užít si dovolenou v oblasti ${destination}.\nCena je " + get_adjective(rnd.choice("velmi\u00A0přízniv skutečně\u00A0krásn nehorázně\u00A0přitažliv".split(" ")), pad=1, rod='žj') + " - ${price_c}. Po prožití krásných ${duration_text} se budete vracet 🛬 ${date_to} na letiště ${airport}.\nNebo snad máte nějaké jiné, lepší plány?"), "utm"),

    "time6": TemplateType(Template("Už jen ${date_from_dif_text} 🕒 zbývá do odletu do hotelu ${hotel}!\nOdletět můžete ${date_from} 🛫 a užít si dovolenou v oblasti ${destination}.\nCena je " + get_adjective(rnd.choice("velmi\u00A0přízniv skutečně\u00A0krásn nehorázně\u00A0přitažliv".split(" ")), pad=1, rod='žj') + " - ${price_c}. Po prožití krásných ${duration_text} se budete vracet 🛬 ${date_to} na letiště ${airport}.\nNebo snad máte nějaké jiné, lepší plány?"), "utm"),

    "price1": TemplateType(Template("Tak to budete 😲😲 čubrnět 😲😲!!!\nHotel ${hotel} za 💣💣bombovou💣💣 cenu ${price_c} s odletem ${date_from}. Prožijte ${duration_text} v " + get_adjective(rnd.choice("hezk krásn oblíben".split(" ")), pad=2, rod='žj') + " oblasti ${destination}.\nAle pospěšte si, protože odlet je už za ${date_from_dif_text}."), "utm"),

    "price2": TemplateType(Template("✏️✏️✏️ To si hned musíte napsat!!! ✏️✏️✏️\nOdlet ${date_from} do " + get_adjective(rnd.choice('příjemn krásn nádhern'.split(" ")), pad=2) + " hotelu ${hotel} za " + get_adjective(rnd.choice('skvěl dobr nádhern'.split(" ")), pad=4, rod='žj') + " cenu ${price_c}.\nOPAKUJEME: ${hotel} za " + get_adjective(rnd.choice('příjemn krásn nádhern'.split(" ")), pad=4, rod='žj') + " cenu ${price_c}."), "utm"),

    "price3": TemplateType(Template("Zaplaťte jen ${price_c}, " + get_adjective(rnd.choice("fantasticky\u00A0nízk skutečně\u00A0neuvěřiteln".split(" ")), pad=4, rod='žj') + " cenu a navštivte " + get_adjective(rnd.choice("oblíben osvědčen nezapomenuteln".split(" ")), pad=1) + " hotel ${hotel} s odletem ${date_from}.\nV " + get_adjective(rnd.choice("oblíben osvědčen tradičn".split(" ")), pad=2, rod='žj') + " oblasti ${destination} se už na Vás těší..."), "utm"),

    "price4": TemplateType(Template("Nemažeme Vám 🍯🍯 med 🍯🍯 kolem pusy, vážně ne!\nZa " + get_adjective(rnd.choice("libov neskutečn opravdu\u00A0nízk".split(" ")), pad=2, rod='mnm') + " ${price_c} od ${date_from} do ${rating} hotelu ${hotel} do destinace ${destination}."), "utm"),

    "price5": TemplateType(Template("Co takhle ${country}?\n${destination} (" + get_adjective(rnd.choice("oblíben osvědčen tradičn".split(" ")), pad=1, rod='žj') + " destinace).\n${rating} " + get_adjective(rnd.choice("klienty\u00A0oblíben hojně\u00A0navštěvovan cenově\u00A0dostupn".split(" ")), pad=1, rod='mnj') + " hotel ${hotel} v termínu ${date_whole} za ${price_f}."), "utm"),

    "price6": TemplateType(Template("📉 Jenom holá fakta! 📉\n" + get_adjective(rnd.choice("fantastick nízk neuvěřiteln".split()), capitalize=True, pad=2, rod='sm') + " ${price_c}.\nOdlet 🛫 ${date_from}, přílet 🛬 ${date_to} z/na letiště ${airport}.\n${rating} hotel ${hotel}.\n" + get_adjective(rnd.choice("tradičn hezk krásn oblíben prosluněn".split(" ")), capitalize=True, pad=1, rod='žj') + " destinace ${destination}.\nTak co? Poletíte?"), "utm"),

    "sale1": TemplateType(Template("💰Kolik chcete dát za " + get_adjective(rnd.choice("kompletně\u00A0vyřešen opravdu\u00A0bezproblémov cenově\u00A0dostupn".split(" ")), pad=1, rod='mnm') + " ${date_from_dif_text} dovolené?💰\nNemusíte moc, protože z letiště ${airport} můžete ${date_from} 🛫🛫🛫🛫 odletět do hotelu ${hotel} se stravováním ${board} v oblasti ${destination}.\nŽe to není odpověď na naší otázku? Že jsme se ptali na cenu?\nA co třeba cena ${price_c}? Za ${duration_text} dovolené! Vrátíte se 🛬 ${date_to}.\nTyhle bláznivé nápady 😲"), "utm"),

    "sale2": TemplateType(Template("Za 🕒📅 ${date_from_dif_text} 📅🕒 můžete frčet z letiště ${airport}!!!\nOdletět do hotelu ${hotel} se stravováním ${board} v oblasti ${destination} můžete ${date_from} 🛫🛫🛫🛫.\nDo kapsy hluboko sahat nemusíte, cena ${price_c} potěší každého. "), "utm"),

    "sale3": TemplateType(Template("Za 🕒📅 ${date_from_dif_text} 📅🕒 můžete frčet z letiště ${airport}!!!\nOdletět do hotelu ${hotel} se stravováním ${board} v oblasti ${destination} můžete ${date_from} 🛫🛫🛫🛫.\nDo kapsy hluboko sahat nemusíte, cena ${price_c} potěší každého. ${duration_text} dovolené se hodí každému, kdo nutně po složitém roce 2020 potřebuje odpočinek. Návrat je 🛬 ${date_to}.\nNám to připadá jako bezva nápad..."), "utm"),

    "sale4": TemplateType(Template("Za 🕒📅 ${date_from_dif_text} 📅🕒 můžete frčet z letiště ${airport}!!!\nOdletět do hotelu ${hotel} se stravováním ${board} v oblasti ${destination} můžete ${date_from} 🛫🛫🛫🛫.\nDo kapsy hluboko sahat nemusíte, cena ${price_c} potěší každého. ${duration_text} dovolené se hodí každému, kdo nutně po složitém roce 2020 potřebuje odpočinek. Návrat je 🛬 ${date_to}.\nNám to připadá jako bezva nápad..."), "utm"),

    "sale5": TemplateType(Template("Za 🕒📅 ${date_from_dif_text} 📅🕒 můžete frčet z letiště ${airport}!!!\nOdletět do hotelu ${hotel} se stravováním ${board} v oblasti ${destination} můžete ${date_from} 🛫🛫🛫🛫.\nDo kapsy hluboko sahat nemusíte, cena ${price_c} potěší každého. ${duration_text} dovolené se hodí každému, kdo nutně po složitém roce 2020 potřebuje odpočinek. Návrat je 🛬 ${date_to}.\nNám to připadá jako bezva nápad..."), "utm"),

    "sale6": TemplateType(Template("Za 🕒📅 ${date_from_dif_text} 📅🕒 můžete frčet z letiště ${airport}!!!\nOdletět do hotelu ${hotel} se stravováním ${board} v oblasti ${destination} můžete ${date_from} 🛫🛫🛫🛫.\nDo kapsy hluboko sahat nemusíte, cena ${price_c} potěší každého. ${duration_text} dovolené se hodí každému, kdo nutně po složitém roce 2020 potřebuje odpočinek. Návrat je 🛬 ${date_to}.\nNám to připadá jako bezva nápad..."), "utm"),
}

my_pages = [
    {"page_id": "633916606749334", "page_title": "Cestuj hned", "page_user_name": "@travelasap.cz"},
    {"page_id": "1645656035685167", "page_title": "Travelasap", "page_user_name": "@cestujhned"}
]
fb_app = {
    "access_token": "EAAEmaBNOAYYBANbCLqByui1QksGsq77TyuUYfn5GCyJdVeDTEU0HJvgChZAZBuqMWk0lDFSfPP7oyiWHYASl2Iga2SASETDv6ZC2dnoAEJgY3XUsGgOvBAzTaVJFsFLZAsZARwf7NgczSSZCEZBXZBufyX5zoZAxu8UfvH8qcfyyUlwZDZD",
    "app_id": "323703419044230",
    "app_sec": "fc4558854f4718fd420c7adeeb3c7798"
}

ta_url = "https://www.travelasap.cz/d/"

trip_nos = [231567910]
# trip_nos = [221298947]


def select_trip_nos_from_file(filename="./trip_nos.csv"):
    trip_nos = []
    with open(filename) as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        for row in readCSV:
            if len(row) > 1:
                print("Zájezd: ", row[0], " poslední typ zprávy: ", row[1])
                trip_nos.append([row[0], row[1]])
            else:
                print("Zájezd: ", row[0])
                trip_nos.append([row[0], ""])
    return trip_nos


def main():
    all_types = {}
    trip_nos = select_trip_nos_from_file()
    if len(trip_nos[-1]) >= 1:
        last_msg_type = trip_nos[-1][1]
    else:
        last_msg_type = "price5"
    for trip_no in trip_nos[:15]:
        trip_parameters = get_parameters_from_ta(trip_no[0])
        # print(trip_param)
        if Testovani:
            msg_type = select_best_msg_type(trip_parameters, last_msg_type, trip_no[1])
            print("\n----------- ", trip_no, " Sleva ", trip_parameters["discount"], " Cena na den ", trip_parameters["price_oneday"], " Odlet za ", trip_parameters["date_from_dif_text"])
            print("Pořadí vhodnosti zpráv: ", msg_type)
            print("Podle pořadí bych měl vypsat: ", msg_type[0])
            print("Poslední vypsaný typ všech: ", last_msg_type)
            print("Poslední vypsaný typ tohoto: ", trip_no[1])
            # print_all_messages(trip_parameters)
            if last_msg_type in msg_type:
                msg_type.remove(last_msg_type)
            if trip_no[1] in msg_type:
                msg_type.remove(trip_no[1])
            last_msg_type = msg_type[0]
            print("Nakonec tedy vypisuju: ", msg_type[0])
            if last_msg_type in all_types:
                all_types[last_msg_type] += 1
            else:
                all_types[last_msg_type] = 1
            message = get_msg(trip_parameters, msg_type[0])
            print(message)
            print(all_types)
        else:
            if trip_parameters["is_active"]:
                msg_type = select_best_msg_type(trip_parameters)
                message = get_msg(trip_parameters, msg_type[0])
                print(message)
                post_to_fb(message, trip_parameters)


if __name__ == "__main__":
    main()
