#%%
from bs4 import BeautifulSoup as BS
from selenium import webdriver 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import myconfig as mc
#%%
def get_page_source(url, path_driver = mc.PATH_CHROME,*args):
    page_status = 0
    while page_status != 200:
        if path_driver is mc.PATH_CHROME:
            chrome_options = Options()
            for arg in args:
                chrome_options.add_argument(arg)
            driver = webdriver.Chrome(path_driver, options = chrome_options)
            driver.get(url)
            delay = 3
            try:
                myElem = WebDriverWait(driver,delay).until(EC.presence_of_element_located((By.CLASS_NAME,"ui-row-ltr")))
                print ("Page is ready!")
                print("Nalezený element je typu WebElement? ",type(myElem))
                print("Co je to za druh tagu? ",myElem.tag_name)
                print("A tady je jeho obsah: ",myElem.text)
            except TimeoutException:
                print("Loading took too much time!")
            html_element = driver.find_element_by_tag_name("html") #Tady získávám objekt WebElement ze selenia, obsahující kompletní HTML stránku
            html_source = driver.page_source #Tady získávám kompletní zdrojový kód stránky, ale jako string, ale obsah by měl být identický
            page_status = 200
        else:
            page = requests.get(url)
            page_status = page.status_code
    return html_element,html_source

#%%
r = get_page_source("https://www.travelasap.cz/chcete-jet-do/pensee-royal-garden/egypt/marsa-alam/19270a?sm=1#tab-terminy",mc.PATH_CHROME,'window-size=1120,4000')

#%%
print("Typ odpovědi: ",type(r)) #Očekávám tuple
print("Délka pole (n-tice) odpovědi: ",len(r)) #s délkou 2
selenium_html = r[0] #První by měl být element ze selenia
soup_html = r[1] #Druhý by měl být string s webovou stránkou pro zpracování BeautifulSoup
# ALE OBSAH INFORMACÍ UVNITŘ PŘEDPOKLÁDÁM STEJNÝ
print("Typ prvku pro selenium: ",type(selenium_html)) #Ano, je to <class 'selenium.webdriver.remote.webelement.WebElement'>
print("Typ prvku pro soup: ",type(soup_html)) #Ano, je to <class 'str'>
# %%
print("Prvních 1000 znaků pro selenium:\n",selenium_html.text[:1000]) #Prvních 1000 znaků pro selenium (odproštěné všech html tagů, protože jsou to jen vnitřky, ten objekt už je vlastně ===DOM===)
print("- - - - - - - - - - - - - - - ")
print("Délka HTML kódu pro soup: ",len(soup_html))
start_poz = 130648
print(f"1000 znaků pro soup od pozice {start_poz}:\n",soup_html[start_poz:start_poz+1000]) #1000 znaků pro BeautifulSoup (je to pozice, na které by se podle počítání v browseru měly nacházet tagy <tr> s parametry zájezdu! Je to vlastně obsah html stránky včetně tagů, vhodný na parsování)
poz = soup_html.find("20.03.2021")
print("Na jaké pozici se nachází zájezd s odjezdem 20.03.2021: ","NENALEZENO" if poz == -1 else "NALEZENO na pozici ",poz) #NENALEZENO!!! A to používám funkci find() pro stringy, čili žádné find pro soup!!! Ale jak to? Vždyť v těch datech pro selenium je! Viz. další výpis!
# %%
terms = selenium_html.find_elements_by_class_name("ui-row-ltr") #Najdi všechny elementy v objektu ze selenia, jejichž třída je "ui-row-ltr"
print(type(terms)) #Bude to seznam, což očekávám
print(len(terms)) #s 32 prvky, přičemž mě zajímají jen prvky na indexech 1-30
print(type(terms[1])) #a každý prvek pole je opět objekt WebElement ze selenia, což očekávám
print("Parametry prvního zájezdu (a má datum 20.03.2021!!!): ",terms[1].text) #A tohle jsou parametry prvního zájezdu (a má datum 20.03.2021), takže v těch datech od selenia jednoznačně je!

# %%
print("Ještě jednou pro jistotu, je to string??? ",type(soup_html))
soup = BS(soup_html,"html.parser") #pro jistotu ten zdrojový kód ještě proženu parserem BeautifulSoupu a zkusím najít prvky s IDENTICKOU třídou!!!
# %%
print("A tohle by měl být objekt BeautifulSoupu: ",type(soup))
print(soup.text.find("20.03.2021")) #Tak proč ho nenajde???? 
termssoup = soup.find_all("tr",{"class":"ui-row-ltr"})
print(type(termssoup))
print(len(termssoup))
#Tak proč nenajde tagy <tr> se stejnou třídou, jako našlo selenium???
# %%
