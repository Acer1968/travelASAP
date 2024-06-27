# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
#%%
import facebook
import requests
from bs4 import BeautifulSoup as BS
import os
import random as rnd
from string import Template
from collections import namedtuple

utm_params_string = "${website_url}?utm_source=${campaign_source}&utm_medium=${campaign_medium}&utm_campaign=${campaign_name}&utm_term=${campaign_term}&utm_content=${campaign_content}"

trip_nos=[186694188] #pole s id všech zájezdů, pro které chci vytvořit příspěvky

TemplateType = namedtuple("TemplateTuple","type template utm")
Templates = {
    1:TemplateType("price1",Template("Hotel ${hotel} za cenu ${price_c} s odletem ${date_from}."),"utm"),
    2:TemplateType("price2",Template("Odleťte už ${date_from} do hotelu ${hotel} za úžasnou cenu ${price_c}."),"utm"),
    3:TemplateType("price3",Template("Zaplaťte jen ${price_c} a navštivte ${hotel} od ${date_from}."),"utm"),
    4:TemplateType("price4",Template("Za ${price_c} od ${date_from} do ${rating} hotelu ${hotel} do prosluněné destinace ${destination}."),"utm"),
    5:TemplateType("price5",Template("${country}, ${destination} do ${rating} hotelu ${hotel} v termínu ${date_whole} za ${price_f}."),"utm")
}

my_pages=[
    {"page_id":"633916606749334","page_title":"Cestuj hned","page_user_name":"@travelasap.cz"},
    {"page_id":"1645656035685167","page_title":"Travelasap","page_user_name":"@cestujhned"}
]
fb_app={"access_token":"EAAEmaBNOAYYBANbCLqByui1QksGsq77TyuUYfn5GCyJdVeDTEU0HJvgChZAZBuqMWk0lDFSfPP7oyiWHYASl2Iga2SASETDv6ZC2dnoAEJgY3XUsGgOvBAzTaVJFsFLZAsZARwf7NgczSSZCEZBXZBufyX5zoZAxu8UfvH8qcfyyUlwZDZD",
"app_id":"323703419044230",
"app_sec":"fc4558854f4718fd420c7adeeb3c7798"}


# %%
ta_url = "https://www.travelasap.cz/d/" #zkrácená verze url, kde se na konec připojuje číslo zájezdu


# %%
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


# %%
def get_params_from_ta(trip_no):
  '''
  Funkce vrátí slovník se všemi parametry zájezdu, které umím vyskrapovat ze stránek.

  Vstup:
   trip_no: číslo JEDNOHO zájezdu 
   pokud chci zadávat více zájezdů najednou, musím tuhle funkci volat ve smyčce
  
  Výstup:
   trip_params: slovník, kde klíče jsou názvy jednotlivých parametrů a hodnoty jsou vyparsované

  '''
  trip_params = {}
  status=0
  page_url = os.path.join(ta_url,str(trip_no))
  #print(page_url)
  while status!=200:
    page = requests.get(page_url)
    status = page.status_code
  soup = BS(page.content, 'html.parser')

  # Tady naparsuju všechny parametry, které potřebuju, a přiřadím do slovníku s parametry
  trip_params["trip_no"] = str(trip_no) #číslo zájezdu
  trip_params["url"] = page_url #url zájezdu zkrácené: https://www.travelasap.cz/d/194614167
  trip_params["url_full"] = page.url.split(sep="?")[0] #url zájezdu plné sestavené CeSYSem: https://www.travelasap.cz/chcete-jet-do/sunwing-waterworld-makadi/egypt/hurghada/150361a/194614167d
  trip_params["title"] = soup.find("h1").text.strip() #titulek stránky sestavená CeSYSem
  trip_params["hotel"] = soup.find("div", class_='hotel').text.strip() #jméno hotelu získané z DIVu
  trip_params["hotel2"] = trip_params["title"].split(" za cenu ")[0].strip() #jméno hotelu vyseparované z titulku
  trip_params["board"] = soup.find("div", class_='board').text.strip() #stravování z DIVu
  trip_params["price_f"] = soup.find("a", class_="change-structured-content pric b-pric").text.strip().replace(" ","") #cena včetně nedělitelných mezer
  trip_params["price_c"] = trip_params["title"].split(" ")[-5] #cena kompaktní bez mezer, ale s jednotkou měny
  trip_params["duration"] = soup.find("div", class_='dur').text.strip() #doba trvání zájezdu
  trip_params["date_whole"] = soup.find("div", class_='date').text.strip() #celé datum zájezdu od-do z DIVu
  trip_params["date_from"] = trip_params["title"].split(" ")[-3] #datum od(odjezd) vyseparované z titulku
  trip_params["date_to"] = trip_params["title"].split(" ")[-1] #datum do(příjezd) vyseparované z titulku
  #date_from = soup.find("div", class_='date').text.strip()
  #date_to = soup.find("div", class_='date').text.strip()
  trip_params["destination"] = soup.find("div", class_='dest').text.strip() #cílová destinace z drobečkové navigace
  trip_params["country"] = trip_params["destination"].split(sep="»")[0].strip() #země vyseparovaná z drobečkové destinace
  #trip_params["rating"] = "5*" #rating - MUSÍM DOPLNIT
  trip_params["rating"] = str(len(soup.find(dir,class_="rating").find_all("img", class_="nb star")))+"*"
  trip_params["airport"] = soup.find("div", class_='air').text.strip() #letiště odletu
  trip_params["discount"] = soup.find("div", class_='dis').text.strip() #sleva včetně mínusu a procent
  trip_params["pictures"] = ["https:"+a['href'] for a in soup.find("div", class_='pics-inner').find_all('a', href=True) if a.text] #pole s názvy obrázků na ccdn serveru
  
  return trip_params


# %%
def get_msg(trip_no, trip_param, msg_type="3"):
  if type(msg_type) == int:
    msg_type_index = msg_type
  elif type(msg_type) == str:
    msg_type_index = rnd.randint(1,len(Templates))
  msg = Templates[msg_type_index].template.substitute(trip_param)
  return msg


# %%
def post_to_fb(msg, trip_param):
  '''
  Funkce odesílá na FB příspěvek.

  Vstup:
    msg: je zpráva sestavená pomocí funkce get_msg(). Obsahuje vybranou šablonu pro zájezd naplněnou skutečnými parametry zájezdu
    trip_param: kompletní parametry zájezdu. Asi je sem vůbec nepotřebuju předávat, jen se prostě musím přesvědčit, proč ne.
    target_page: cílová stránka na FB, na kterou posílám příspěvek.

  Výstup: příspěvek na FB na danou stránku

  '''
        # Fill in the values noted in previous steps here
  cfg = {
    "page_id"      : my_pages[0]["page_id"],
    "access_token" : fb_app["access_token"]
    }

  api = get_api(cfg)
    
  status = api.put_object(
    parent_object="me",
    connection_name="feed",
    message=msg,
    link=trip_param["url_full"])

  print("Povedlo se?", status)


# %%
#Simulace hlavní programové smyčky
for trip_no in trip_nos:
    trip_param = get_params_from_ta(trip_no)
    print(trip_param)
    message = get_msg(trip_no,trip_param)
    print(message)
    post_to_fb(message,trip_param)


# %%
message = get_msg(trip_no,trip_param,5)
print(message)

# %% [markdown]
# Pro pokusy, co se dá vyparsovat, si natáhnu tady znovu stránku.

# %%
page_url = os.path.join(ta_url,str(trip_no))
status = 0
while status!=200:
    page = requests.get(page_url)
    status = page.status_code
soup = BS(page.content, 'html.parser')

# %% [markdown]
# A odsud mohu dělat pokusy, co se dá vyparsovat:

# %%
s = soup.find(dir,class_="rating").find_all("img", class_="nb star")


# %%
len(s)


# %%
type(s)


# %%



