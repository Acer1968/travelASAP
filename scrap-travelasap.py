from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options

import lxml

urls="https://www.travelasap.cz/chcete-jet-do/sunny-days-el-palacio/egypt/hurghada/369a"

##driver = webdriver.PhantomJS()

options = Options()
options.headless = True

PATHGECKO = "D:\PetrVavrinec\PythonProjects\webdrivers\geckodriver.exe"

PATHCHROME = "D:\PetrVavrinec\PythonProjects\webdrivers\chromedriver.exe"

#print(PATH)
profile = webdriver.FirefoxProfile("C:\\Users\\vavri\\AppData\\Roaming\\Mozilla\\Firefox\\Profiles\\4za1xpn2.default-release")
profile.accept_untrusted_certs = True
#driver = webdriver.Firefox(firefox_profile=profile)

##driver = webdriver.Firefox(options=options, firefox_profile=profile, executable_path=PATHGECKO)

driver = webdriver.Chrome(PATHCHROME)

driver.get(urls)

innerHTML = driver.execute_script("return document.body")

##print(driver.page_source)

import bs4

import re

from time import sleep

sleep(2)

html = driver.page_source
soup=bs4.BeautifulSoup(html,"lxml")

odjezdy = soup.find_all("td",{"aria-describedby":"grid_date_from"})
trvani = soup.find_all("td",{"aria-describedby":"grid_duration"})
strava = soup.find_all("td",{"aria-describedby":"grid_boarding_id"})
letiste = soup.find_all("td",{"aria-describedby":"grid_transport_id"})
ceny = soup.find_all("td",{"aria-describedby":"grid_price"})

informace = list(map(lambda x, y: "odlet "+str(x.text).replace("\xa0","")+" na "+str(y.text).replace("\xa0",""), odjezdy, trvani))
informace2 = list(map(lambda x, y: str(x).replace("\xa0","")+" s "+str(y.text).replace("\xa0",""),informace,strava))
informace3 = list(map(lambda x, y: str(x).replace("\xa0","")+" za "+str(y.text).replace("\xa0",""),informace2,ceny))

for info in informace3[0:5]:

    print(info)

driver.quit()