import sys
import os
import requests
import urllib
import json
import gzip
from PyQt6.QtWidgets import (QApplication, QMainWindow, QHeaderView, QAbstractItemView, QMessageBox, QTableView)
from PyQt6.QtCore import QFile, Qt, pyqtSlot, QModelIndex
from PyQt6.uic import loadUi
from PyQt6.QtSql import QSqlDatabase, QSqlQueryModel, QSqlQuery
from PyQt6.QtGui import QColor, QBrush, QFont
import travelasap as ta

# Base directory for storing fetched requests
BASE_DIR = "./fetched_requests"

# Sample requests to perform
requests_data = []

class CustomSqlModel(QSqlQueryModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_row = -1

    def data(self, index, role):
        if role == Qt.ItemDataRole.BackgroundRole and index.row() == self.selected_row:
            return QBrush(QColor(173, 216, 230))  # Light blue color
        if role == Qt.ItemDataRole.FontRole and index.column() == 0:  # Assuming ID is in the first column
            font = QFont()
            font.setBold(True)
            return font
        return super().data(index, role)

class HotelManagementApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Load the UI
        ui_file = QFile("hotel_management_app.ui")
        ui_file.open(QFile.OpenModeFlag.ReadOnly)
        loadUi(ui_file, self)
        ui_file.close()

        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("travelasap.db")
        if not self.db.open():
            print("Nelze otevřít databázi")
            sys.exit(1)

        self.setup_hotel_tab()

        # Napojení tabulky hotelů (název z UI je tableView_hotels)
        self.table_view = self.findChild(QTableView, "tableView_hotels")

        # Napojení tlačítka getTermsButton na funkci on_get_terms_button_clicked
        self.getTermsButton.clicked.connect(self.on_get_terms_button_clicked)

    def setup_hotel_tab(self):
        self.hotel_model = CustomSqlModel()
        self.tableView_hotels.setModel(self.hotel_model)
        self.tableView_hotels.verticalHeader().setVisible(False)
        self.tableView_hotels.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.tableView_hotels.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableView_hotels.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)


        self.description_model = CustomSqlModel()
        self.tableView_descriptions.setModel(self.description_model)
        self.tableView_descriptions.verticalHeader().setVisible(False)
        self.tableView_descriptions.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Fixed)
        self.tableView_descriptions.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableView_descriptions.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        self.lineEdit_id_filter.textChanged.connect(self.update_hotel_filter)
        self.lineEdit_name_filter.textChanged.connect(self.update_hotel_filter)
        self.lineEdit_destination_filter.textChanged.connect(self.update_hotel_filter)

        self.lineEdit_source.textChanged.connect(self.enable_save_button)
        self.lineEdit_type.textChanged.connect(self.enable_save_button)
        self.lineEdit_version.textChanged.connect(self.enable_save_button)
        self.textEdit_description.textChanged.connect(self.enable_save_button)

        self.tableView_hotels.clicked.connect(self.on_hotel_select)
        self.tableView_descriptions.clicked.connect(self.on_description_select)
        # Napojení tlačítka na funkci uložení změn do databáze
        self.pushButton_save.setEnabled(False)
        self.pushButton_save.clicked.connect(self.save_description)
        # Napojení tlačítka na funkci kopírování popisu jako nové položky u hotelu pro případné změny
        self.pushButton_copy.setEnabled(False)
        self.pushButton_copy.clicked.connect(self.copy_as_new)
        # Napojení tlačítka na funkci exportu všech popisů do JSON souboru
        self.pushButton_export_desc_to_json.setEnabled(True)
        self.pushButton_export_desc_to_json.clicked.connect(self.export_description_to_json)
        
        self.lineEdit_source.textChanged.connect(self.enable_save_button)
        self.lineEdit_type.textChanged.connect(self.enable_save_button)
        self.lineEdit_version.textChanged.connect(self.enable_save_button)
        self.textEdit_description.textChanged.connect(self.enable_save_button)

        self.update_hotel_filter()

        self.tableView_hotels.setColumnWidth(0, 60)  # První sloupec (ID)
        self.tableView_hotels.setColumnWidth(1, 200)  # Druhý sloupec (Název hotelu)
        self.tableView_hotels.setColumnWidth(2, 290)  # Třetí sloupec (Země a destinace)

    @pyqtSlot()
    def update_hotel_filter(self):
        query = """
        SELECT Hotel_ID, Hotel_Name, Country_and_Destination 
        FROM hotels 
        WHERE Hotel_Picture IS NOT NULL
        """
        conditions = []
        if self.lineEdit_id_filter.text():
            if self.lineEdit_id_filter.text().startswith("="):
                conditions.append(f"Hotel_ID = '{self.lineEdit_id_filter.text()[1:]}'")
            else:
                conditions.append(f"Hotel_ID LIKE '%{self.lineEdit_id_filter.text()}%'")
        if self.lineEdit_name_filter.text():
            conditions.append(f"Hotel_Name LIKE '%{self.lineEdit_name_filter.text()}%'")
        if self.lineEdit_destination_filter.text():
            conditions.append(f"Country_and_Destination LIKE '%{self.lineEdit_destination_filter.text()}%'")

        if conditions:
            query += " AND " + " AND ".join(conditions)

        self.hotel_model.setQuery(query, self.db)
        self.tableView_hotels.setColumnWidth(0, 60)  # Hotel ID
        self.tableView_hotels.setColumnWidth(1, 300)  # Hotel Name
        self.tableView_hotels.setColumnWidth(2, 440)  # Country and Destination
        self.hotel_model.setHeaderData(0, Qt.Orientation.Horizontal, "ID")
        self.hotel_model.setHeaderData(1, Qt.Orientation.Horizontal, "Název hotelu")
        self.hotel_model.setHeaderData(2, Qt.Orientation.Horizontal, "Země a destinace")

    @pyqtSlot(QModelIndex)
    def on_hotel_select(self, index):
        row = index.row()
        hotel_id = self.hotel_model.record(row).value("Hotel_ID")
        hotel_name = self.hotel_model.record(row).value("Hotel_Name")
        destination = self.hotel_model.record(row).value("Country_and_Destination")
        
        self.label_selected_hotel.setText(f"Vybraný hotel: ID: {hotel_id}, Název: {hotel_name}, Destinace: {destination}")
        
        query = f"""
        SELECT source, description_type, description_type_version, output_format, description
        FROM hotel_descriptions
        WHERE Hotel_ID = {hotel_id}
        """
        self.description_model.setQuery(query, self.db)
        self.description_model.setHeaderData(0, Qt.Orientation.Horizontal, "Zdroj")
        self.description_model.setHeaderData(1, Qt.Orientation.Horizontal, "Typ popisu")
        self.description_model.setHeaderData(2, Qt.Orientation.Horizontal, "Verze")
        self.description_model.setHeaderData(3, Qt.Orientation.Horizontal, "Formát popisu")
        self.description_model.setHeaderData(4, Qt.Orientation.Horizontal, "Popis")
        self.tableView_descriptions.setColumnWidth(0, 90)  # První sloupec (Zdroj)
        self.tableView_descriptions.setColumnWidth(1, 60)  # Druhý sloupec (Typ popisu)
        self.tableView_descriptions.setColumnWidth(2, 40)  # Třetí sloupec (Verze)
        self.tableView_descriptions.setColumnWidth(3, 90)  # Čtvrtý sloupec (Formát popisu)
        self.tableView_descriptions.setColumnWidth(2, 270)  # Pátý sloupec (Popis)
        self.tableView_descriptions.resizeColumnsToContents()
        
        if self.description_model.rowCount() > 0:
            self.on_description_select(self.description_model.index(0, 0))
        else:
            self.clear_description_fields()

    @pyqtSlot(QModelIndex)
    def on_description_select(self, index):
        self.description_model.selected_row = index.row()
        self.description_model.dataChanged.emit(index, index)
        
        source = self.description_model.record(index.row()).value("source")
        description_type = self.description_model.record(index.row()).value("description_type")
        description_type_version = self.description_model.record(index.row()).value("description_type_version")
        description = self.description_model.record(index.row()).value("description")
        
        self.lineEdit_source.setText(source)
        self.lineEdit_type.setText(description_type)
        self.lineEdit_version.setText(str(description_type_version))
        self.textEdit_description.setText(description)
        
        self.pushButton_save.setEnabled(False)
        self.pushButton_copy.setEnabled(False)

    def export_description_to_json(self):
        print("Export description to JSON - tlačítko stisknuto")
        # Získání vybraného hotelu z tabulky (předpokládáme, že je v tabulce QTableView)
        selected_row = self.table_view.selectionModel().currentIndex().row()
        if selected_row < 0:
            QMessageBox.warning(self, "Žádný výběr", "Vyberte prosím hotel, abyste mohli exportovat popis.")
            return

        # Získání hotel_id z prvního sloupce tabulky
        hotel_id = self.table_view.model().index(selected_row, 0).data()

        # Vytvoření instance třídy Hotel
        hotel = ta.Hotel(hotel_id)

        # Zavolání metody create_descriptions_jsonfile()
        hotel.create_descriptions_jsonfile(description_types=['full_desc', 'discrepancies'])

        # Potvrzení exportu uživateli
        QMessageBox.information(self, "Export dokončen", f"Popis hotelu {hotel.name} byl exportován do JSON souboru.")

    def get_terms_request(self, hotel_id, number_of_adults, departure_date, arrival_date):
        """Generates the URL for fetching terms based on the provided parameters."""
        url_template = "https://www.travelasap.cz/searchmasks/generation_dates_terms?ht%5B%5D={hotel_id}&df={departure_date}&dt={arrival_date}&ac={number_of_adults}&cc=0&rop=30&hotel={hotel_id}&skip=0&source=cesys_default&sm=1&sort=room_price&direction=asc&pg=1&currency=CZK"
        url = url_template.format(
            hotel_id=hotel_id,
            departure_date=departure_date,
            arrival_date=arrival_date,
            number_of_adults=number_of_adults
        )

        headers = {
        "sec-ch-ua": '"Chromium";v="127", "Not)A;Brand";v="99"',
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-encoding": "deflate",  # Odebrání 'br' a 'gzip' 
        "accept-language": "cs-CZ,cs;q=0.9,en;q=0.8",
        "referer": "https://www.travelasap.cz/",
        "x-requested-with": "XMLHttpRequest",
        "sec-ch-ua-mobile": "?0",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "connection": "keep-alive",
        "cache-control": "no-cache",
        "pragma": "no-cache"
        }
        return {
            "url": url,
            "method": "GET",
            "headers": headers
        }
    
    def save_response_content(self, response, filename):
        """Uloží pouze obsah odpovědi do JSON souboru."""
        try:
            # Dekompresování obsahu, pokud je gzipovaný
            if response.headers.get('Content-Encoding') == 'gzip':
                import gzip
                from io import BytesIO
                buffer = BytesIO(response.content)
                with gzip.GzipFile(fileobj=buffer) as f:
                    decompressed_content = f.read().decode('utf-8')
            else:
                decompressed_content = response.text
            
            # Pokus o parsování JSON
            try:
                content_json = json.loads(decompressed_content)
            except json.JSONDecodeError as e:
                print(f"Chyba při parsování JSON: {e}")
                print("Obsah odpovědi pro ladění:")
                print(decompressed_content)
                content_json = {"raw_content": decompressed_content}
            
            # Uložení pouze obsahu
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(content_json, f, indent=4, ensure_ascii=False)
            
            print(f"Soubor byl úspěšně uložen: {filename}")
            return os.path.getsize(filename)
        
        except Exception as e:
            print(f"Chyba při ukládání odpovědi: {e}")
            import traceback
            traceback.print_exc()
            return 0


    def fetch_and_save_response(self, request_info, request_number):
        """
        Fetch response from a URL and save it to a file.
        
        Args:
            request_info (dict): Dictionary containing request information
            request_number (int): Request sequence number
        
        Returns:
            dict: Processed response data
        """
        try:
            # Extract request information
            url = request_info['url']
            method = request_info.get('method', 'GET')
            headers = request_info.get('headers', {})
            
            # Make the request
            response = requests.request(
                method=method,
                url=url,
                headers=headers
            )
            response.raise_for_status()
            
            # Process the response
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                response_data = response.text
                
            # Save response to file
            save_dir = './fetched_requests'
            os.makedirs(save_dir, exist_ok=True)
            
            # Create a clean filename from the URL
            filename = f"request_{request_number}__{url.split('/')[-1].split('?')[0]}.json"
            filepath = os.path.join(save_dir, filename)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                if isinstance(response_data, dict):
                    json.dump(response_data, f, indent=2, ensure_ascii=False)
                else:
                    f.write(response_data)
                    
            print(f"Response for request #{request_number} saved to {filepath}")
            return response_data
            
        except requests.RequestException as e:
            print(f"Error making request: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

    def save_response(self, response, filename):
        """Saves the response content to a JSON file."""
        try:
            # Log response information
            print(f"Response Status Code: {response.status_code}")
            print(f"Response Content-Type: {response.headers.get('Content-Type')}")
            print(f"Response Content-Encoding: {response.headers.get('Content-Encoding')}")
            print(f"Response Content-Length: {response.headers.get('Content-Length')}")
            
            # Attempt to parse JSON using response.json()
            try:
                content_json = response.json()
                # Check if content_json is a string (double-encoded)
                if isinstance(content_json, str):
                    print("Content is a JSON string, parsing again.")
                    content_json = json.loads(content_json)
            except json.JSONDecodeError as e:
                print(f"JSON parsing failed: {e}")
                # Output the content for inspection
                print("Response text for debugging:")
                print(response.text)
                # If parsing fails, store the raw text
                content_json = {"raw_content": response.text}
            
            # Prepare output data
            output_data = {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content": content_json
            }
            
            # Save to file
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=4, ensure_ascii=False)
                
            print(f"File saved successfully: {filename}")
            
            # Return the file size for verification
            return os.path.getsize(filename)
        
        except Exception as e:
            print(f"Failed to save response: {e}")
            import traceback
            traceback.print_exc()
            return 0



    def perform_requests(self):
        """Perform each request and save the responses."""
        if not os.path.exists(BASE_DIR):
            os.makedirs(BASE_DIR)
        
        session = requests.Session()
        
        for i, req_data in enumerate(requests_data, start=1):
            url = req_data.get("url")
            method = req_data.get("method", "GET")
            headers = req_data.get("headers", {})
            post_data = req_data.get("post_data", None)
        
            # Odebrání 'br' z 'Accept-Encoding'
            if 'accept-encoding' in headers:
                encodings = headers['accept-encoding'].split(', ')
                encodings = [enc for enc in encodings if enc != 'br']
                headers['accept-encoding'] = ', '.join(encodings)
        
            try:
                # Vytvoření požadavku
                if method == "GET":
                    response = session.get(url, headers=headers)
                elif method == "POST":
                    response = session.post(url, headers=headers, data=post_data)
                else:
                    print(f"Unsupported method {method} for request #{i}")
                    continue
        
                # Kontrola délky obsahu
                content_length = response.headers.get('Content-Length')
                actual_length = len(response.content)
                print(f"Request #{i}: Expected Content-Length = {content_length}, Actual = {actual_length}")
        
                # Uložení obsahu odpovědi
                parsed_url = urllib.parse.urlparse(url)
                filename = os.path.join(BASE_DIR, f"request_{i}_{parsed_url.path.replace('/', '_')}.json")
                filename_content = filename.replace(".json", "_content.json")
                self.save_response_content(response, filename_content)
                self.save_response(response, filename)
                print(f"Response for request #{i} saved to {filename}")
            except Exception as e:
                print(f"Failed to perform request #{i}: {e}")


    @pyqtSlot()
    def on_get_terms_button_clicked(self):
        """Handles the get terms button click event."""
        hotel_id = self.get_selected_hotel_id()  # Replace with actual method to get selected hotel ID
        number_of_adults = self.numberOfAdultsSpinBox.value()
        departure_date = self.departureCalendarWidget.selectedDate().toString("yyyy-MM-dd")
        arrival_date = self.arrivalCalendarWidget.selectedDate().toString("yyyy-MM-dd")
        request = self.get_terms_request(hotel_id, number_of_adults, departure_date, arrival_date)
        print(request)
        global requests_data
        requests_data.append(request)
        self.perform_requests()
        QMessageBox.information(self, "Info", "Terms data fetched successfully and saved.")

    def get_selected_hotel_id(self):
        # Placeholder for getting the selected hotel ID from the UI (e.g., from a table or dropdown)
        selected_row = self.tableView_hotels.currentIndex().row()
        if selected_row != -1:
            return self.hotel_model.record(selected_row).value("Hotel_ID")
        return 354  # Example hotel ID

    def clear_description_fields(self):
        self.lineEdit_source.clear()
        self.lineEdit_type.clear()
        self.lineEdit_version.clear()
        self.textEdit_description.clear()
        self.pushButton_save.setEnabled(False)

    def copy_as_new(self):
        if self.description_model.selected_row == -1:
            return

        hotel_id = self.hotel_model.record(self.tableView_hotels.currentIndex().row()).value("Hotel_ID")
        source = self.lineEdit_source.text()
        description_type = self.lineEdit_type.text()
        
        # Zjistit nejvyšší verzi
        query = QSqlQuery()
        query.prepare("""
        SELECT MAX(description_type_version) 
        FROM hotel_descriptions 
        WHERE Hotel_ID = ? AND source = ? AND description_type = ?
        """)
        query.addBindValue(hotel_id)
        query.addBindValue(source)
        query.addBindValue(description_type)
        
        if query.exec() and query.next():
            max_version = query.value(0) or 0
        else:
            max_version = 0

        new_version = max_version + 1
        new_description = self.textEdit_description.toPlainText()

        # Vložit nový záznam
        insert_query = QSqlQuery()
        insert_query.prepare("""
        INSERT INTO hotel_descriptions 
        (Hotel_ID, source, description_type, description_type_version, output_format, description)
        VALUES (?, ?, ?, ?, ?, ?)
        """)
        insert_query.addBindValue(hotel_id)
        insert_query.addBindValue(source)
        insert_query.addBindValue(description_type)
        insert_query.addBindValue(new_version)
        insert_query.addBindValue(self.description_model.record(self.description_model.selected_row).value("output_format"))
        insert_query.addBindValue(new_description)

        if insert_query.exec():
            print(f"Nový popis byl úspěšně vytvořen s verzí {new_version}")
            self.on_hotel_select(self.tableView_hotels.currentIndex())
            self.pushButton_save.setEnabled(False)
            self.pushButton_copy.setEnabled(False)
        else:
            print("Chyba při vytváření nového popisu:", insert_query.lastError().text())
    @pyqtSlot()
    def enable_save_button(self):
        if self.description_model.selected_row != -1:
            self.pushButton_save.setEnabled(True)
            self.pushButton_copy.setEnabled(True)

    @pyqtSlot()
    def save_description(self):
        if self.description_model.selected_row == -1:
            return

        hotel_id = self.hotel_model.record(self.tableView_hotels.currentIndex().row()).value("Hotel_ID")
        new_source = self.lineEdit_source.text()
        new_description_type = self.lineEdit_type.text()
        new_description = self.textEdit_description.toPlainText()

        # Zjistit nejvyšší verzi
        query = QSqlQuery()
        query.prepare("""
        SELECT MAX(description_type_version) 
        FROM hotel_descriptions 
        WHERE Hotel_ID = ? AND source = ? AND description_type = ?
        """)
        query.addBindValue(hotel_id)
        query.addBindValue(new_source)
        query.addBindValue(new_description_type)
        
        if query.exec() and query.next():
            max_version = query.value(0) or 0
        else:
            max_version = 0

        new_version = max_version + 1

        # Vložit nový záznam
        insert_query = QSqlQuery()
        insert_query.prepare("""
        INSERT OR REPLACE INTO hotel_descriptions 
        (Hotel_ID, source, description_type, description_type_version, output_format, description)
        VALUES (?, ?, ?, ?, ?, ?)
        """)
        insert_query.addBindValue(hotel_id)
        insert_query.addBindValue(new_source)
        insert_query.addBindValue(new_description_type)
        insert_query.addBindValue(new_version)
        insert_query.addBindValue(self.description_model.record(self.description_model.selected_row).value("output_format"))
        insert_query.addBindValue(new_description)

        if insert_query.exec():
            print(f"Popis byl úspěšně aktualizován/vytvořen s verzí {new_version}")
            self.on_hotel_select(self.tableView_hotels.currentIndex())
            self.pushButton_save.setEnabled(False)
            self.pushButton_copy.setEnabled(False)
        else:
            print("Chyba při aktualizaci/vytváření popisu:", insert_query.lastError().text())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = HotelManagementApp()
    window.show()
    sys.exit(app.exec())