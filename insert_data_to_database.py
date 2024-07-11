import sqlite3
import pandas as pd

# Načtení CSV souboru do DataFrame
df = pd.read_csv('20240710_266037_hotels_data_modified.csv')

# Připojení k databázi
conn = sqlite3.connect('travelasap.db')
cursor = conn.cursor()

# Vložení dat do tabulky
for row in df.itertuples(index=False):
    cursor.execute('''
        INSERT INTO hotels (
            Hotel_ID, Hotel_Picture, Hotel_Name, Hotel_Exname, Country_and_Destination,
            Accommodation_Type, Hotel_Category, Recommendation, Own_Rating, Own_Texts
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', row)

# Uložení změn a uzavření spojení
conn.commit()
conn.close()

# Spuštění interaktivního režimu
import code
code.interact(local=locals())
