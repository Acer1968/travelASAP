import tkinter as tk
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager
import time

# Globální proměnné pro počet dospělých, dětí a věky dětí
USUAL_ADULTS_NUMBER = 2
adults = USUAL_ADULTS_NUMBER
USUAL_CHILDREN_NUMBER = 0
children = USUAL_CHILDREN_NUMBER
USUAL_CHILDREN_AGE = 5
children_ages = [USUAL_CHILDREN_AGE, USUAL_CHILDREN_AGE,
                 USUAL_CHILDREN_AGE, USUAL_CHILDREN_AGE]

# Funkce pro otevření stránky a nastavení počtu dospělých, dětí a věků dětí


def open_page():
    url = url_entry.get()
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get(url)

    # Pauza pro načtení stránky
    time.sleep(5)

    try:
        # Kontrola existence prvků a nastavení hodnot pro dospělé a děti
        adults_select = driver.find_element(
            By.XPATH, '/html/body/div[1]/main/div/div/div/div/div[2]/div/section/div/div[1]/section/div/div[1]/div[2]/div/div[1]/select')
        children_select = driver.find_element(
            By.XPATH, '/html/body/div[1]/main/div/div/div/div/div[2]/div/section/div/div[1]/section/div/div[1]/div[2]/div/div[2]/select')

        select_adults = Select(adults_select)
        select_adults.select_by_value(str(adults))

        select_children = Select(children_select)
        select_children.select_by_value(str(children))

        # Pauza pro načtení nových prvků
        time.sleep(1)

        # Kontrola a nastavení věků dětí
        for i in range(children):
            try:
                child_select = driver.find_element(
                    By.XPATH, f'/html/body/div[1]/main/div/div/div/div/div[2]/div/section/div/div[1]/section/div/div[1]/div[2]/div/div[{i+3}]/select')
                select_child_age = Select(child_select)
                select_child_age.select_by_value(str(children_ages[i]))
            except Exception as e:
                print(f"Chyba při nastavování věku dítěte {i+1}: ", e)

        # Kliknutí na tlačítko Uložit
        save_button = driver.find_element(
            By.XPATH, '/html/body/div[1]/main/div/div/div/div/div[2]/div/section/div/div[1]/section/div/div[1]/div[2]/div/div[7]/button')
        save_button.click()

        # Pauza pro zpracování uložit
        time.sleep(3)

        # Kontrola přítomnosti chybové zprávy
        try:
            error_message = driver.find_element(
                By.XPATH, '/html/body/div[1]/main/div/div/div/div/div[2]/div/section/div/div[1]/section/div/div[4]/div/div')
            if error_message and error_message.text.strip() == "Skladbě osob nevyhovuje žádný pokoj. Prosím změňte skladbu osob.":
                messagebox.showwarning(
                    "Varování", "Skladba osob nevyhovuje, prosím změňte skladbu.")
                driver.quit()
                return
        except:
            pass

        status_label.config(
            text="Hodnoty byly úspěšně nastaveny a formulář byl uložen.")

        # Kliknutí na záložku Informace
        info_tab = driver.find_element(
            By.XPATH, '/html/body/div[1]/main/div/div/div/div/div[2]/div/section/nav/div/a[2]')
        info_tab.click()

        # Pauza pro načtení informací
        time.sleep(2)

        # Načtení textů s popisem hotelů od všech pořadatelů
        tour_operator_select = driver.find_element(
            By.XPATH, '/html/body/div[1]/main/div/div/div/div/div[2]/div/section/div/div[2]/article/div/form/select')
        tour_operator_options = tour_operator_select.find_elements(
            By.TAG_NAME, 'option')

        tour_operator_texts = {}
        for option in tour_operator_options:
            if option.get_attribute('value') != "0":
                option.click()
                time.sleep(2)
                tour_operator_text = driver.find_element(
                    By.XPATH, '/html/body/div[1]/main/div/div/div/div/div[2]/div/section/div/div[2]/article/div/div[1]/div').text
                tour_operator_texts[option.text] = tour_operator_text

        print(tour_operator_texts)

    except Exception as e:
        status_label.config(text=f"Chyba: {e}")

    # Pauza na 10 sekund, aby stránka zůstala otevřená
    time.sleep(40)

    driver.quit()

# Funkce pro změnu počtu dospělých


def update_adults(value):
    global adults
    adults = value
    print(f"Počet dospělých: {adults}, Počet dětí: {children}")

# Funkce pro změnu počtu dětí a aktualizaci viditelnosti políček pro věky dětí


def update_children(value):
    global children
    children = value
    print(f"Počet dospělých: {adults}, Počet dětí: {children}")
    for i in range(4):
        if i < children:
            age_spinboxes[i].config(state='normal')
        else:
            age_spinboxes[i].config(state='disabled')
            age_spinboxes[i].delete(0, "end")
            age_spinboxes[i].insert(0, USUAL_CHILDREN_AGE)
            children_ages[i] = USUAL_CHILDREN_AGE

# Funkce pro změnu věku dětí


def update_child_age(index, value):
    children_ages[index] = value
    print(f"Věky dětí: {children_ages}")


# Vytvoření hlavního okna
root = tk.Tk()
root.title("Otevři stránku pomocí Selenia")

# Vytvoření vstupního pole pro URL
url_label = tk.Label(root, text="Zadej URL:")
url_label.grid(row=0, column=0, columnspan=2)

url_entry = tk.Entry(root, width=50)
# Nastavení počáteční hodnoty URL
url_entry.insert(0, "https://www.travelasap.cz/a/218582")
url_entry.grid(row=1, column=0, columnspan=2)

# Vytvoření tlačítka pro otevření stránky
open_button = tk.Button(root, text="Otevři stránku", command=open_page)
open_button.grid(row=2, column=0, columnspan=2)

# Vytvoření výběru pro počet dospělých
adults_label = tk.Label(root, text="Počet dospělých:")
adults_label.grid(row=3, column=0)
adults_spinbox = tk.Spinbox(root, from_=1, to=16, width=5,
                            command=lambda: update_adults(int(adults_spinbox.get())))
adults_spinbox.grid(row=3, column=1)
adults_spinbox.delete(0, "end")
adults_spinbox.insert(0, USUAL_ADULTS_NUMBER)

# Vytvoření výběru pro počet dětí
children_label = tk.Label(root, text="Počet dětí:")
children_label.grid(row=4, column=0)
children_spinbox = tk.Spinbox(root, from_=0, to=4, width=5,
                              command=lambda: update_children(int(children_spinbox.get())))
children_spinbox.grid(row=4, column=1)
children_spinbox.delete(0, "end")
children_spinbox.insert(0, USUAL_CHILDREN_NUMBER)

# Vytvoření výběrových políček pro věky dětí
age_spinboxes = []
for i in range(4):
    age_label = tk.Label(root, text=f"Věk dítěte {i+1}:")
    age_label.grid(row=5+i, column=0)
    age_spinbox = tk.Spinbox(root, from_=0, to=18, width=5, state='disabled',
                             command=lambda i=i: update_child_age(i, int(age_spinboxes[i].get())))
    age_spinbox.grid(row=5+i, column=1)
    age_spinbox.delete(0, "end")
    age_spinbox.insert(0, USUAL_CHILDREN_AGE)
    age_spinboxes.append(age_spinbox)

# Vytvoření labelu pro zobrazení stavu
status_label = tk.Label(root, text="")
status_label.grid(row=9, column=0, columnspan=2)

# Spuštění hlavní smyčky TkInter
root.mainloop()
