# hotel_app.py
import tkinter as tk
from tkinter import ttk
from travelasap.hotel import Hotel, HotelDatabase

# Hlavní třída aplikace
class HotelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("travelASAP - Hotel Database Viewer")
        
        self.selected_hotel_id = None
        self.db = HotelDatabase()
        
        # Label pro vybraný hotel
        self.selected_hotel_label = tk.Label(root, text="Vybraný hotel: Žádný", font=('Arial', 12))
        self.selected_hotel_label.pack(pady=10)
        
        # Vyhledávací pole
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(root, textvariable=self.search_var, width=50)
        self.search_entry.pack(pady=5)
        
        # Tlačítko pro vyhledávání
        self.search_button = tk.Button(root, text="Vyhledat", command=self.search_hotel)
        self.search_button.pack(pady=5)
        
        # Frame pro grid hotelů
        self.grid_frame = tk.Frame(root)
        self.grid_frame.pack(pady=10)
        
        self.hotel_tree = ttk.Treeview(self.grid_frame, columns=("ID", "Název", "Destinace"), show='headings')
        self.hotel_tree.heading("ID", text="Hotel ID")
        self.hotel_tree.column("ID", width=60, anchor='center')
        self.hotel_tree.heading("Název", text="Hotel Název")
        self.hotel_tree.column("Název", width=200, anchor='w')
        self.hotel_tree.heading("Destinace", text="Země a Destinace")
        self.hotel_tree.column("Destinace", width=340, anchor='w')
        self.hotel_tree.pack()
        
        self.hotel_tree.bind('<<TreeviewSelect>>', self.on_hotel_select)
        
        self.load_hotels_to_grid()
        
        # Select menu a textové pole pro popisy
        self.desc_var = tk.StringVar()
        self.desc_select = ttk.Combobox(root, textvariable=self.desc_var)
        self.desc_select.pack(pady=5)
        self.desc_select.bind("<<ComboboxSelected>>", self.on_description_select)
        self.desc_text = tk.Text(root, height=15, width=80)
        self.desc_text.pack(pady=10)

    def load_hotels_to_grid(self):
        hotels = self.db.get_all_hotels()
        for hotel in hotels:
            self.hotel_tree.insert('', 'end', values=hotel)

    def search_hotel(self):
        search_text = self.search_var.get()
        for item in self.hotel_tree.get_children():
            self.hotel_tree.delete(item)
        
        hotels = self.db.get_all_hotels()
        filtered_hotels = [hotel for hotel in hotels if search_text.lower() in hotel[1].lower() or search_text in str(hotel[0])]
        
        for hotel in filtered_hotels:
            self.hotel_tree.insert('', 'end', values=hotel)

    def on_hotel_select(self, event):
        selected_item = self.hotel_tree.selection()[0]
        hotel_id = self.hotel_tree.item(selected_item, "values")[0]
        hotel_name = self.hotel_tree.item(selected_item, "values")[1]
        
        self.selected_hotel_id = hotel_id
        self.selected_hotel_label.config(text=f"Vybraný hotel: {hotel_name}")
        
        hotel = Hotel(hotel_id)
        descriptions = hotel.get_descriptions_from_db()
        self.desc_select['values'] = [f"{desc[0]} - {desc[1]}" for desc in descriptions]
        self.desc_text.delete(1.0, tk.END)
        
        if descriptions:
            self.desc_select.current(0)
            self.desc_text.insert(tk.END, descriptions[0][2])

    def on_description_select(self, event):
        if self.selected_hotel_id:
            hotel = Hotel(self.selected_hotel_id)
            descriptions = hotel.get_descriptions_from_db()
            selected_desc = self.desc_select.get().split(" - ")
            for desc in descriptions:
                if desc[0] == selected_desc[0] and desc[1] == selected_desc[1]:
                    self.desc_text.delete(1.0, tk.END)
                    self.desc_text.insert(tk.END, desc[2])
                    break

if __name__ == "__main__":
    root = tk.Tk()
    app = HotelApp(root)
    root.mainloop()
