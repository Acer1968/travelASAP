import sqlite3

# Připojení k databázi (nebo vytvoření nové)
conn = sqlite3.connect('travelasap.db')  # Použij relativní nebo absolutní cestu podle potřeby
cursor = conn.cursor()

# Vytvoření tabulky
cursor.execute('''
    CREATE TABLE hotels (
        Hotel_ID INTEGER PRIMARY KEY,
        Hotel_Picture TEXT,
        Hotel_Name TEXT,
        Hotel_Exname TEXT,
        Country_and_Destination TEXT,
        Accommodation_Type TEXT,
        Hotel_Category REAL,
        Recommendation INTEGER,  -- BOOLEAN represented as INTEGER
        Own_Rating INTEGER,      -- BOOLEAN represented as INTEGER
        Own_Texts INTEGER        -- BOOLEAN represented as INTEGER
    )
''')

# Uložení změn a uzavření spojení
conn.commit()
conn.close()
