import sys
import sqlite3
import requests
import re
import csv
import socket
import datetime
import os
import psutil
import glob
import winreg
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLineEdit, QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, QTextEdit, QTableWidget, QTableWidgetItem, QListWidget
from PyQt5.QtCore import pyqtSlot, Qt
from threading import Thread

class DatabaseHandler:
    def __enter__(self):
        self.conn = sqlite3.connect("extensions.db")  # Make sure this path is correct for your database
        self.cursor = self.conn.cursor()
        # Create a table if it doesn't exist. Adjust fields as needed, excluding 'Browser'
        self.cursor.execute("CREATE TABLE IF NOT EXISTS EXTENSIONS (ExtensionID TEXT PRIMARY KEY, ExtensionName TEXT, Description TEXT)")
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.commit()
            self.conn.close()

class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.title = 'Extension Details'
        self.user_account = 'N/A'  # Initialize user_account
        self.browser = 'N/A'
        self.initUI()

    def find_extensions(self, selected_drives, browser_name, path_components):
        extensions = set()
        for drive_info in selected_drives:
            # Extract the actual drive letter from the drive info
            drive_letter_match = re.match(r"([A-Za-z]:)", drive_info)
            if not drive_letter_match:
                continue  # Skip if no valid drive letter found
            drive_letter = drive_letter_match.group(1)

            users_dir = os.path.join(drive_letter, "\\", "Users")
            
            #Possible future code for E01's added as a physical drive with FTK..
            # if not os.path.exists(users_dir):
                # # If Users directory not found at root level, search one level deeper
                # for root_dir in os.listdir(drive_letter):
                    # potential_users_dir = os.path.join(drive_letter, "\\", root_dir, "Users")
                    # print(f"Potential users dir: {potential_users_dir}")
                    # if os.path.exists(potential_users_dir):
                        # users_dir = potential_users_dir
                        # break
                # else:
                    # continue  # Skip the drive if Users directory still not found

            user_accounts = [d for d in os.listdir(users_dir) if os.path.isdir(os.path.join(users_dir, d))]
            for user in user_accounts:
                extension_path = os.path.join(users_dir, user, *path_components)
                print(f"Checking extension path: {extension_path}")
                extension_paths_found = glob.glob(extension_path)
                if not extension_paths_found:
                    print(f"No extensions found at: {extension_path}")
                    continue
                for extension_full_path in extension_paths_found:
                    extension_id = os.path.basename(extension_full_path)
                    print(f"Found extension ID: {extension_id}")
                    # Special handling for Firefox .xpi files
                    if browser_name == "Mozilla Firefox" and os.path.isfile(extension_full_path) and extension_id.endswith('.xpi'):
                        extension_id = extension_id[:-4]  # Remove '.xpi'
                    if browser_name != "Mozilla Firefox" or "@" in extension_id:
                        extensions.add((extension_id, user, browser_name))
        return extensions


    def find_chrome_extensions(self, selected_drives):
        path_components = ["AppData", "Local", "Google", "Chrome", "User Data", "Default", "Extensions", "*"]
        return self.find_extensions(selected_drives, "Google Chrome", path_components)

    def find_edge_extensions(self, selected_drives):
        path_components = ["AppData", "Local", "Microsoft", "Edge", "User Data", "Default", "Extensions", "*"]
        return self.find_extensions(selected_drives, "Microsoft Edge", path_components)

    def find_firefox_extensions(self, selected_drives):
        path_components = ["AppData", "Roaming", "Mozilla", "Firefox", "Profiles", "*", "extensions", "*"]
        return self.find_extensions(selected_drives, "Mozilla Firefox", path_components)
        
    def find_brave_extensions(self, selected_drives):
        path_components = ["AppData", "Local", "BraveSoftware", "Brave-Browser", "User Data", "Default", "Extensions", "*"]
        return self.find_extensions(selected_drives, "Brave", path_components)
 

    def on_identify(self):
        text_area_content = self.extensions_text_area.toPlainText()
        all_extensions = set()
        self.result_table.setSortingEnabled(False)  # Disable sorting while updating table

        if self.devices_list.selectedItems():
            selected_drives = [item.text() for item in self.devices_list.selectedItems()]
            print(f"selected drive: {selected_drives}")

            chrome_extensions = self.find_chrome_extensions(selected_drives)
            edge_extensions = self.find_edge_extensions(selected_drives)
            firefox_extensions = self.find_firefox_extensions(selected_drives)
            brave_extensions = self.find_brave_extensions(selected_drives)

            all_extensions.update(chrome_extensions.union(edge_extensions).union(firefox_extensions).union(brave_extensions))
            
            # Filter and include extension tuples that are 32 characters or longer, or contain an '@' symbol
            filtered_extensions = [ext for ext in all_extensions if len(ext[0]) >= 32 or '@' in ext[0]]

            # Set the text of the text area to the newline-joined filtered extension_ids
            self.extensions_text_area.setText("\n".join(ext[0] for ext in filtered_extensions))

            #print(f"All extensions {all_extensions}") #Debug purposes

        else:
            # If no drive is selected, use the content from the text area
            # Assuming all unknown extensions are from a single browser or user intervention is needed.
            all_extensions.update([(ext_id, 'N/A', 'Unknown') for ext_id in text_area_content.strip().split('\n')])
            filtered_extensions = [extension for extension in all_extensions if len(extension[0]) >= 32 or '@' in extension[0]]

        self.result_table.setRowCount(0)
        for extension_id, user_account, browser in filtered_extensions:
            extension_id = extension_id.strip()
            if extension_id:
                extension_id, extension_name, extension_description, source = self.get_extension_details(extension_id, browser)
                row_position = self.result_table.rowCount()
                self.result_table.insertRow(row_position)
                self.result_table.setItem(row_position, 0, QTableWidgetItem(extension_id))
                self.result_table.setItem(row_position, 1, QTableWidgetItem(extension_name))
                self.result_table.setItem(row_position, 2, QTableWidgetItem(extension_description))
                self.result_table.setItem(row_position, 3, QTableWidgetItem(user_account))
                self.result_table.setItem(row_position, 4, QTableWidgetItem(browser))
                self.result_table.setItem(row_position, 5, QTableWidgetItem(source))
        
        self.result_table.setSortingEnabled(True)  # Re-enable sorting after updates

    def insert_extension_into_database(self, extension_id, extension_name, extension_description):
        with DatabaseHandler() as cursor:
            cursor.execute("INSERT INTO EXTENSIONS (ExtensionID, ExtensionName, Description) VALUES (?, ?, ?)", 
                           (extension_id, extension_name, extension_description))
        print(f"Inserted {extension_name} into the database.")

    def get_extension_details_from_store(self, extension_id, store_url, name_pattern, description_pattern):
        try:
            response = requests.get(store_url)
            response.raise_for_status()

            html_content = response.text
            #print(f"HTML RESPONSE: {html_content}")  
            extension_name_match = re.search(name_pattern, html_content)
            extension_name = extension_name_match.group(1).strip() if extension_name_match else 'N/A'

            extension_description_match = re.search(description_pattern, html_content)
            extension_description = extension_description_match.group(1).strip() if extension_description_match else "N/A"

            if extension_name != "N/A":
                self.insert_extension_into_database(extension_id, extension_name, extension_description)
                return extension_id, extension_name, extension_description
            else:
                return extension_id,'N/A','N/A'  # Extension details not found

        except requests.exceptions.HTTPError as http_error:
            print(f"HTTP error from store: {http_error}")
            return extension_id,'N/A','N/A'  # HTTP error, details not found
        except Exception as e:
            print(f"An error occurred: {e}")
            return extension_id,'N/A','N/A'  # Other errors, details not found

    def get_edge_extension_details(self, extension_id):
        store_url = f"https://microsoftedge.microsoft.com/addons/detail/extension-name/{extension_id}"
        title_pattern = r'<title>([^<]+) - Microsoft Edge Addons</title>'
        description_pattern = "N/A"
        result = self.get_extension_details_from_store(extension_id, store_url, title_pattern, description_pattern)
        if result[0] == 'N/A' or result[0] is None:  # Found details
            return result + ("Research..",)
        else:  # Found details
            return result + ("Edge Extension",)

    def get_chrome_extension_details(self, extension_id, checked_edge_first=False):
        store_url = f'https://chrome.google.com/webstore/detail/{extension_id}'
        title_pattern = r'<meta property="og:title" content="([^"]+)"'
        description_pattern = r'<meta property="og:description" content="([^"]+)"'
        result = self.get_extension_details_from_store(extension_id, store_url, title_pattern, description_pattern)
        
        # If result contains 'N/A' or is None (assuming this is how you represent not found), return with 'Research..'
        if result[0] == 'N/A' or result[0] is None:  
            return result + ("Research..",)
        else:  # Found details
            return result + ("Chrome Extension",)
            
    def get_firefox_extension_details(self, extension_id):
        store_url = f'https://addons.mozilla.org/en-US/firefox/addon/{extension_id}/'

        # Updated HTML patterns for title and description based on Mozilla Add-on page structure
        # This title pattern captures text until the first occurrence of ' – ' which usually precedes the standard suffix
        title_pattern = r'<title data-react-helmet="true">([^–]+)'
        description_pattern = r'<meta data-react-helmet="true" name="description" content="([^"]+)"/>'

        result = self.get_extension_details_from_store(extension_id, store_url, title_pattern, description_pattern)

        if result[0] == 'N/A' or result[0] is None:
            return result + ("Research..",)
        else:
            return result + ("Firefox Extension",)


    def get_extension_details(self, extension_id, browser_source):
        with DatabaseHandler() as cursor:
            cursor.execute("SELECT * FROM EXTENSIONS WHERE ExtensionID=?", (extension_id,))
            existing_entry = cursor.fetchone()

        if existing_entry:
            extension_id, extension_name, extension_description = existing_entry
            return extension_id, extension_name, extension_description, 'Database'

        if not self.is_internet_available():
            return extension_id, 'N/A', 'N/A', 'No Internet'

        result = extension_id, 'N/A', 'N/A', "Research.."
        
        if browser_source == "Mozilla Firefox" or (browser_source == "Unknown" and "@" in extension_id):
            result = self.get_firefox_extension_details(extension_id)
            # If Firefox details are not found, return the result without trying other stores
        elif browser_source == "Microsoft Edge" or (browser_source == "Unknown"):
            result = self.get_edge_extension_details(extension_id)
            #print(f"RESULT: {result}") #Debug Purposes
            if result[1] == 'N/A' or result[1] is None:
                result = self.get_chrome_extension_details(extension_id)
        elif browser_source == "Google Chrome" or browser_source == "Brave":
            result = self.get_chrome_extension_details(extension_id)

        return result


    def on_save(self):
        file_name = self.line_edit.text().strip() + "_" + datetime.datetime.now().strftime("%d%m%y_%H%M%S") + ".csv"
        data = []

        row_count = self.result_table.rowCount()
        column_count = self.result_table.columnCount()

        for row in range(row_count):
            row_data = []
            for column in range(column_count):
                item = self.result_table.item(row, column)
                row_data.append(item.text() if item else "N/A")
            data.append(row_data)

        # Use utf-8 encoding and add errors='replace' to handle any characters that can't be encoded
        with open(file_name, 'w', newline='', encoding='utf-8', errors='replace') as file:
            writer = csv.writer(file)
            writer.writerow(["Extension ID", "Extension Name", "Description", "User Account", "Browser", "Source"])
            writer.writerows(data)
        print(f"Results saved to {file_name}")

    def on_import(self):
        options = QFileDialog.Options()
        file_path = QFileDialog.getOpenFileName(self, "Import Extensions", "", "CSV Files (*.csv);;Text Files (*.txt)", options=options)[0]
        if file_path:
            with open(file_path, 'r', encoding='utf-8') as file:  # Set encoding to utf-8
                if file_path.lower().endswith('.txt'):
                    content = file.read()
                elif file_path.lower().endswith('.csv'):
                    lines = file.readlines()[1:]
                    content = '\n'.join(line.split(',')[0] for line in lines)
                else:
                    content = ''
                self.extensions_text_area.setText(content)

    def is_internet_available(self):
        try:
            socket.create_connection(("www.google.com", 80))
            return True
        except OSError:
            return False

    def get_default_browser(self):
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice") as key:
                http_prog_id = winreg.QueryValueEx(key, "ProgId")[0]
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\https\UserChoice") as key:
                https_prog_id = winreg.QueryValueEx(key, "ProgId")[0]

            # Compare both ProgIds, if they differ, return 'Multiple - Inspect'
            if http_prog_id != https_prog_id:
                return 'Multiple - Inspect'

            # Map the common ProgIds to browser names
            browser_map = {
                'ChromeHTML': 'Google Chrome',
                'FirefoxURL': 'Mozilla Firefox',
                'IE.HTTP': 'Internet Explorer',
                'MSEdgeHTM': 'Microsoft Edge',
                'BraveHTML': 'Brave'
                # ... add other mappings ...
            }

            return browser_map.get(http_prog_id, http_prog_id)  # Return the browser name or ProgId if unknown

        except Exception as e:
            print(f"Error retrieving default browser: {e}")
            return "Error"

    def populate_devices(self):
        self.devices_list.clear()
        for partition in psutil.disk_partitions():
            if 'rw' in partition.opts:  # Filter for writable drives if necessary
                drive_letter_match = re.match(r"([A-Za-z]:)\\", partition.device)
                if drive_letter_match:
                    drive_letter = drive_letter_match.group(1)
                    usage = psutil.disk_usage(drive_letter)
                    total_gb = usage.total / (1024**3)  # convert from bytes to gigabytes

                    # Initialize default browser
                    default_browser = 'No O/S found'

                    # Check at the root level for the existence of SYSTEM32 directory
                    system32_path_root = os.path.join(drive_letter, "\\" "Windows", "System32")
                    if os.path.exists(system32_path_root):
                        default_browser = self.get_default_browser()
                    
                    #Possible future code for E01's added as a physical drive with FTK..
                    # else:
                        # # Check one level deep for the existence of SYSTEM32 directory
                        # for root_dir in os.listdir(drive_letter):
                            # system32_path = os.path.join(drive_letter, "\\", root_dir, "Windows", "System32")
                            # if os.path.exists(system32_path):
                                # default_browser = self.get_default_browser()
                                # break  # Break the loop if found

                    # Format and add the device string to the list
                    device_string = f"{drive_letter} Drive - {total_gb:.2f}GB - Default Browser: {default_browser}"
                    self.devices_list.addItem(device_string)


    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(100, 100, 1725, 1000)

        layout = QVBoxLayout()
        top_layout = QHBoxLayout()

        left_vertical_layout = QVBoxLayout()
        self.devices_list = QListWidget(self)
        self.devices_list.setSelectionMode(QListWidget.MultiSelection)
        self.populate_devices()
        left_vertical_layout.addWidget(self.devices_list)

        right_vertical_layout = QVBoxLayout()
        self.extensions_text_area = QTextEdit(self)
        self.extensions_text_area.setPlaceholderText("Individually select drive letters or enter/import Extension ID's here one per line...")
        right_vertical_layout.addWidget(self.extensions_text_area)
        self.import_button = QPushButton('Import Extension IDs..', self)
        self.import_button.clicked.connect(self.on_import)
        right_vertical_layout.addWidget(self.import_button)
        self.search_button = QPushButton('Search/Identify Extension IDs..', self)
        self.search_button.clicked.connect(self.on_identify)
        right_vertical_layout.addWidget(self.search_button)

        top_layout.addLayout(left_vertical_layout)
        top_layout.addLayout(right_vertical_layout)

        bottom_layout = QVBoxLayout()
        self.result_table = QTableWidget(self)
        self.result_table.setColumnCount(6)
        self.result_table.setHorizontalHeaderLabels(["Extension ID", "Extension Name", "Description", "User Account", "Browser", "Source"])
        self.result_table.verticalHeader().setDefaultSectionSize(5)
        self.result_table.setColumnWidth(2, 420)
        bottom_layout.addWidget(self.result_table)

        self.line_edit = QLineEdit(self)
        self.line_edit.setPlaceholderText("Enter filename here...")
        self.line_edit.textChanged.connect(self.toggle_save_button)
        bottom_layout.addWidget(self.line_edit, alignment=Qt.AlignCenter)

        self.save_button = QPushButton('Save Results', self)
        self.save_button.clicked.connect(self.on_save)
        self.save_button.setEnabled(False)
        bottom_layout.addWidget(self.save_button, alignment=Qt.AlignCenter)

        layout.addLayout(top_layout)
        layout.addLayout(bottom_layout)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.show()

    def toggle_save_button(self):
        self.save_button.setEnabled(bool(self.line_edit.text().strip()))

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())