import sqlite3
import pandas as pd
import unidecode

# Připojení k databázi
conn = sqlite3.connect('travelasap.db')

# Načtení dat z databáze do pandas DataFrame
df = pd.read_sql_query("SELECT * FROM hotels WHERE Hotel_Picture IS NOT NULL AND Hotel_Picture != '' LIMIT 20", conn)

# Uzavření spojení s databází
conn.close()

# Funkce pro úpravu textu
def format_text(text):
    text = text.lower()
    text = unidecode.unidecode(text)
    text = text.replace(" ", "-")
    return text

# Vytvoření slovníku
result_dict = {}
for row in df.itertuples():
    hotel_id = row.Hotel_ID
    hotel_name = format_text(row.Hotel_Name)
    country = format_text(row.Country_and_Destination.split(" » ")[0])
    destination = format_text(row.Country_and_Destination.split(" » ")[1])
    
    url_fragment_1 = f"a/{hotel_id}"
    url_fragment_2 = f"chcete-jet-do/{hotel_name}/{country}/{destination}/{hotel_id}a"

    forbiden_chars = ["|", "&"]

    for char in forbiden_chars:
        if char in url_fragment_2:
            url_fragment_2 = url_fragment_2.replace(char+"-", "")
    
    result_dict[hotel_id] = (url_fragment_1, url_fragment_2)

# Výpis výsledného slovníku
print(result_dict)
