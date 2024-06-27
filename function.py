from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
import time

tour_operator_texts = {}

def open_page(url, adults, children, children_ages, status_label, notebook, via_param):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(url)
    
    if not via_param:
        # Pauza pro načtení stránky
        time.sleep(5)
        
        try:
            # Kontrola existence prvků a nastavení hodnot pro dospělé a děti
            adults_select = driver.find_element(By.XPATH, '/html/body/div[1]/main/div/div/div/div/div[2]/div/section/div/div[1]/section/div/div[1]/div[2]/div/div[1]/select')
            children_select = driver.find_element(By.XPATH, '/html/body/div[1]/main/div/div/div/div/div[2]/div/section/div/div[1]/section/div/div[1]/div[2]/div/div[2]/select')
            
            select_adults = Select(adults_select)
            select_adults.select_by_value(str(adults))
            
            select_children = Select(children_select)
            select_children.select_by_value(str(children))
            
            # Pauza pro načtení nových prvků
            time.sleep(1)
            
            # Kontrola a nastavení věků dětí
            for i in range(children):
                try:
                    child_select = driver.find_element(By.XPATH, f'/html/body/div[1]/main/div/div/div/div/div[2]/div/section/div/div[1]/section/div/div[1]/div[2]/div/div[{i+3}]/select')
                    select_child_age = Select(child_select)
                    select_child_age.select_by_value(str(children_ages[i]))
                except Exception as e:
                    print(f"Chyba při nastavování věku dítěte {i+1}: ", e)
            
            # Kliknutí na tlačítko Uložit
            save_button = driver.find_element(By.XPATH, '/html/body/div[1]/main/div/div/div/div/div[2]/div/section/div/div[1]/section/div/div[1]/div[2]/div/div[7]/button')
            save_button.click()
            
            # Pauza pro zpracování uložit
            time.sleep(3)
            
            # Kontrola přítomnosti chybové zprávy
            try:
                error_message = driver.find_element(By.XPATH, '/html/body/div[1]/main/div/div/div/div/div[2]/div/section/div/div[1]/section/div/div[4]/div/div')
                if error_message and error_message.text.strip() == "Skladbě osob nevyhovuje žádný pokoj. Prosím změňte skladbu osob.":
                    messagebox.showwarning("Varování", "Skladba osob nevyhovuje, prosím změňte skladbu.")
                    driver.quit()
                    return
            except:
                pass
            
            result = messagebox.askquestion("Úspěch", "Počet osob a věky dětí úspěšně uloženy a skladba osob odpovídá možnostem ubytování. Pokračujte na dalších záložkách pro získání dat.", icon='info', type=messagebox.YESNO, detail="Vyberte Popisy nebo Termíny")
            if result == 'yes':
                notebook.select(2)  # Přepnutí na záložku Popisy
            else:
                notebook.select(1)  # Přepnutí na záložku Termíny
            
            notebook.tab(1, state='normal')
            notebook.tab(2, state='normal')
            
        except Exception as e:
            status_label.config(text=f"Chyba: {e}")
    
    driver.quit()

def get_descriptions(status_label, notebook):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(url)
    
    # Kliknutí na záložku Informace
    info_tab = driver.find_element(By.XPATH, '/html/body/div[1]/main/div/div/div/div/div[2]/div/section/nav/div/a[2]')
    info_tab.click()
    
    # Pauza pro načtení informací
    time.sleep(2)
    
    # Načtení textů s popisem hotelů od všech pořadatelů
    tour_operator_select = driver.find_element(By.XPATH, '/html/body/div[1]/main/div/div/div/div/div[2]/div/section/div/div[2]/article/div/form/select')
    tour_operator_options = tour_operator_select.find_elements(By.TAG_NAME, 'option')
    
    global tour_operator_texts
    tour_operator_texts = {}
    for option in tour_operator_options:
        if option.get_attribute('value') != "0":
            option.click()
            time.sleep(2)
            tour_operator_text = driver.find_element(By.XPATH, '/html/body/div[1]/main/div/div/div/div/div[2]/div/section/div/div[2]/article/div/div[1]/div').text
            tour_operator_texts[option.text] = tour_operator_text
    
    populate_tour_operators()
    notebook.select(2)
    
    print(tour_operator_texts)
    driver.quit()

# Funkce pro naplnění selectoru pořadateli
def populate_tour_operators():
    for operator in tour_operator_texts.keys():
        tour_operator_selector['values'] = (*tour_operator_selector['values'], operator)

# Funkce pro zobrazení popisu pořadatele
def show_description(event):
    selected_operator = tour_operator_selector.get()
    description_label.config(text=tour_operator_texts.get(selected_operator, ""))
