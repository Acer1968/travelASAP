import firebase_admin
from firebase_admin import credentials, firestore
import sqlite3

# Načti JSON klíč služby
cred = credentials.Certificate("D:/PetrVavrinec/PythonProjects/webdrivers/travelasap-flask-server-access-key.json")
firebase_admin.initialize_app(cred)

# Připojení k Firestore
db = firestore.client()

# Připojení k SQLite
conn = sqlite3.connect('travelasap.db')
cursor = conn.cursor()

# Nastavení mezní hodnoty pro dávku
batch_size = 8000
start_id = 59996
end_id = 80000  # Nastav ručně podle potřeby

# SELECT s podmínkou WHERE
while start_id < end_id:
    # Vyber data z tabulky s omezením
    cursor.execute("""
        SELECT 
            Hotel_ID, 
            Hotel_Picture, 
            Hotel_Name, 
            Hotel_Exname, 
            Country_and_Destination, 
            Accommodation_Type, 
            Hotel_Category, 
            Recommendation, 
            Own_Rating, 
            Own_Texts
        FROM hotels
        WHERE Hotel_ID >= ? AND Hotel_ID < ?
    """, (start_id, end_id))
    rows = cursor.fetchall()

    # Pokud je dat víc než batch_size, omez je
    if len(rows) > batch_size:
        rows = rows[:batch_size]
    counter = 1
    # Nahrávání do Firestore
    for row in rows:
        hotel_id = str(row[0])  # ID bude odpovídat Hotel_ID
        data = {
            "Hotel_Picture": row[1],
            "Hotel_Name": row[2],
            "Hotel_Exname": row[3],
            "Country_and_Destination": row[4],
            "Accommodation_Type": row[5],
            "Hotel_Category": row[6],
            "Recommendation": bool(row[7]),  # BOOLEAN z INTEGER
            "Own_Rating": bool(row[8]),      # BOOLEAN z INTEGER
            "Own_Texts": bool(row[9])        # BOOLEAN z INTEGER
        }

        # Ulož data do Firestore
        db.collection("hotels").document(hotel_id).set(data)
        print(f"Uploaded {counter}: {hotel_id}")
        counter += 1

    print(f"Dávka {start_id} až {end_id - 1} dokončena.")
    start_id = end_id

# Uzavření spojení
conn.close()
print("Všechna data byla úspěšně nahrána!")
