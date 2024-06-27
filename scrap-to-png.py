import facebook
import requests
from bs4 import BeautifulSoup as BS
import os
import random as rnd
from string import Template
from collections import namedtuple
import csv
from datetime import datetime

ta_url = "https://www.travelasap.cz/a/"

hotel_nos=[354]

def get_msg(trip_no, trip_param, msg_type="price1"):
  msg_type_index_list = [3]
  msg_type_index = rnd.choice(msg_type_index_list)
  #msg_type_index = 3
  print("\n"+Templates[msg_type_index].type+":")
  msg = Templates[msg_type_index].template.substitute(trip_param)
  return msg

def get_params_from_ta(hotel_no):
  hotel_params = {}
  status=0
  page_url = os.path.join(ta_url,str(hotel_no))
  #print(page_url)
  while status!=200:
    page = requests.get(page_url)
    status = page.status_code
  soup = BS(page.content, 'html.parser')

  # Tady naparsuju všechny parametry, které potřebuju, a přiřadím do slovníku s parametry
  # Tady naparsuju všechny parametry, které potřebuju, a přiřadím do slovníku s parametry
  hotel_params["hotel_no"] = str(hotel_no)
  hotel_params["url"] = page_url
  hotel_params["url_full"] = page.url.split(sep="?")[0]
  hotel_params["title"] = soup.find("h1").text.strip()
  hotel_params["hotel"] = soup.find("div", class_='hotel').text.strip()
  hotel_params["hotel2"] = hotel_params["title"].split(" za cenu ")[0].strip()
  hotel_params["board"] = soup.find("div", class_='board').text.strip()
  #hotel_params["price_f"] = soup.find("a", class_="change-structured-content pric b-pric").text.strip().replace(" ","") #cena včetně nedělitelných mezer
  hotel_params["price_min"] = hotel_params["title"].split(" ")[-1] #cena OD včetně nedělitelných mezer, ale s jednotkou měny
  hotel_params["trips-count"] = hotel_params["title"].split(" ")[-5] #počet termínů nabízených hotelem
  #hotel_params["price_n"] = int(hotel_params["price_c"][:-2])
  #hotel_params["duration"] = soup.find("div", class_='dur').text.strip()
  #hotel_params["duration_text"] = get_adjective_days(hotel_params["duration"])
  #hotel_params["price_oneday"] = int(hotel_params["price_n"]/int(hotel_params["duration"].split(" ")[0]))
  #hotel_params["date_whole"] = soup.find("div", class_='date').text.strip()
  #date_from = soup.find("div", class_='date').text.strip()
  #date_to = soup.find("div", class_='date').text.strip()
  hotel_params["destination"] = soup.find("div", class_='dest').text.strip()
  hotel_params["country"] = hotel_params["destination"].split(sep="»")[0].strip()
  hotel_params["rating"] = "5*"
  hotel_params["date_from"] = hotel_params["title"].split(" ")[-3]
  hotel_params["date_to"] = hotel_params["title"].split(" ")[-1]
  #hotel_params["date_from_obj"] = datetime.strptime(hotel_params["date_from"],'%d.%m.%y')
  #hotel_params["date_from_dif"] = (hotel_params["date_from_obj"]-datetime.today().replace(hour = 0, minute = 0, second = 0, microsecond = 0)).days
  #hotel_params["date_from_dif_text"] = get_num_days(hotel_params["date_from_dif"])
  hotel_params["airport"] = soup.find("div", class_='air').text.strip()
  #hotel_params["discount"] = soup.find("div", class_='dis').text.strip()
  hotel_params["pictures"] = ["https:"+a['href'] for a in soup.find("div", class_='unique-image').find_all('a', href=True) if a.text]
  hotel_params["rating"] = str(len(soup.find(dir,class_="rating").find_all("img", class_="nb star")))+"*"
  hotel_params["trips_table"] = soup.select("tbody")
  return hotel_params



def main():
  for hotel_no in hotel_nos:
    hotel_param = get_params_from_ta(hotel_no)
    print(hotel_param)
    #message = get_msg(trip_no,trip_param)
    #print(message)
    #post_to_fb(message, trip_param)

if __name__ == "__main__":
    main()