import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime, timedelta
from functions import open_page, populate_tour_operators, show_description

# Globální proměnné pro počet dospělých, dětí a věky dětí
USUAL_ADULTS_NUMBER = 2
adults = USUAL_ADULTS_NUMBER
USUAL_CHILDREN_NUMBER = 0
children = USUAL_CHILDREN_NUMBER
USUAL_CHILDREN_AGE = 5
children_ages = [USUAL_CHILDREN_AGE] * 4

# Globální nastavení vzorové stránky
ROOT_URL = "https://www.travelasap.cz/a/"
SAMPLE_PAGE = "218582"

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

# Funkce pro získání URL


def get_full_url(url, via_param):
    if url.isdigit():
        url = ROOT_URL + url
    if via_param:
        params = f"?sm=1&ac={adults}&cc={children}"
        for i in range(children):
            params += f"&ca{i+1}={children_ages[i]}"
        df = departure_date_entry.get_date().strftime("%Y-%m-%d")
        dt = return_date_entry.get_date().strftime("%Y-%m-%d")
        params += f"&df={df}&dt={dt}"
        url += params
    return url


# Vytvoření hlavního okna
root = tk.Tk()
root.title("Otevři stránku pomocí Selenia")

# Vytvoření záložek
notebook = ttk.Notebook(root)
notebook.grid(row=0, column=0, columnspan=2)

# Vytvoření rámce pro záložku Zadání
frame_input = ttk.Frame(notebook)
notebook.add(frame_input, text="Zadání")

# Vytvoření rámce pro záložku Termíny
frame_dates = ttk.Frame(notebook)
notebook.add(frame_dates, text="Termíny")
notebook.tab(1, state='disabled')

# Vytvoření rámce pro záložku Popisy
frame_descriptions = ttk.Frame(notebook)
notebook.add(frame_descriptions, text="Popisy")
notebook.tab(2, state='disabled')

# Vytvoření vstupního pole pro URL
url_label = tk.Label(frame_input, text="Zadej URL nebo číslo hotelu:")
url_label.grid(row=0, column=0, columnspan=2)

url_entry = tk.Entry(frame_input, width=50)
url_entry.insert(0, SAMPLE_PAGE)  # Nastavení počáteční hodnoty URL
url_entry.grid(row=1, column=0, columnspan=2)

# Checkbox pro URL s parametry
via_param = tk.BooleanVar(value=True)
url_param_checkbox = tk.Checkbutton(
    frame_input, text="URL s parametry", variable=via_param)
url_param_checkbox.grid(row=2, column=0, columnspan=2)

# Vytvoření tlačítka pro otevření stránky
open_button = tk.Button(frame_input, text="Otevři stránku", command=lambda: open_page(get_full_url(
    url_entry.get(), via_param.get()), adults, children, children_ages, status_label, notebook, via_param.get()))
open_button.grid(row=3, column=0, columnspan=2)

# Vytvoření výběru pro počet dospělých
adults_label = tk.Label(frame_input, text="Počet dospělých:")
adults_label.grid(row=4, column=0)
adults_spinbox = tk.Spinbox(frame_input, from_=1, to=16, width=5,
                            command=lambda: update_adults(int(adults_spinbox.get())))
adults_spinbox.grid(row=4, column=1)
adults_spinbox.delete(0, "end")
adults_spinbox.insert(0, USUAL_ADULTS_NUMBER)

# Vytvoření výběru pro počet dětí
children_label = tk.Label(frame_input, text="Počet dětí:")
children_label.grid(row=5, column=0)
children_spinbox = tk.Spinbox(frame_input, from_=0, to=4, width=5,
                              command=lambda: update_children(int(children_spinbox.get())))
children_spinbox.grid(row=5, column=1)
children_spinbox.delete(0, "end")
children_spinbox.insert(0, USUAL_CHILDREN_NUMBER)

# Vytvoření výběrových políček pro věky dětí
age_spinboxes = []
for i in range(4):
    age_label = tk.Label(frame_input, text=f"Věk dítěte {i+1}:")
    age_label.grid(row=6+i, column=0)
    age_spinbox = tk.Spinbox(frame_input, from_=0, to=18, width=5, state='disabled',
                             command=lambda i=i: update_child_age(i, int(age_spinboxes[i].get())))
    age_spinbox.grid(row=6+i, column=1)
    age_spinbox.delete(0, "end")
    age_spinbox.insert(0, USUAL_CHILDREN_AGE)
    age_spinboxes.append(age_spinbox)

# Vytvoření kalendářových widgetů pro výběr data odletu a návratu
today = datetime.now()
departure_date_label = tk.Label(frame_input, text="Odlet nejdříve:")
departure_date_label.grid(row=10, column=0)
departure_date_entry = DateEntry(frame_input, width=12, year=today.year, month=today.month, day=today.day+7,
                                 date_pattern='dd.mm.yyyy', background='darkblue', foreground='white', borderwidth=2, locale='cs_CZ')
departure_date_entry.grid(row=10, column=1)

return_date_label = tk.Label(frame_input, text="Návrat nejpozději:")
return_date_label.grid(row=11, column=0)
return_date_entry = DateEntry(frame_input, width=12, year=today.year, month=today.month, day=today.day+30,
                              date_pattern='dd.mm.yyyy', background='darkblue', foreground='white', borderwidth=2, locale='cs_CZ')
return_date_entry.grid(row=11, column=1)

# Vytvoření labelu pro zobrazení stavu
status_label = tk.Label(frame_input, text="")
status_label.grid(row=12, column=0, columnspan=2)

# Popisy - GUI komponenty
tour_operator_selector = ttk.Combobox(frame_descriptions, state='readonly')
tour_operator_selector.grid(row=0, column=0, padx=10, pady=10)
tour_operator_selector.bind("<<ComboboxSelected>>", show_description)

description_label = tk.Label(
    frame_descriptions, text="", wraplength=600, justify="left")
description_label.grid(row=1, column=0, padx=10, pady=10)

# Spuštění hlavní smyčky TkInter
root.mainloop()
