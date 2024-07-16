import sqlite3

# Připojení k databázi
db_path = 'travelasap.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Vytvoření nové tabulky hotel_descriptions
create_table_query = '''
CREATE TABLE IF NOT EXISTS hotel_descriptions (
    Hotel_ID INTEGER,
    source TEXT,
    description_type TEXT,
    description TEXT,
    FOREIGN KEY (Hotel_ID) REFERENCES hotels (Hotel_ID)
);
'''
cursor.execute(create_table_query)

# Uložení změn a zavření připojení
conn.commit()
conn.close()