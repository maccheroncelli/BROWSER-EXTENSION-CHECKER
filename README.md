---

# Extension Checker for Cryptocurrency Wallets (DApp Wallets)

## Description
The Extension Checker is a Python-based tool designed specifically to identify and analyze Cryptocurrency wallets operating as browser extensions, commonly known as Decentralized Application (DApp) wallets. This tool aids in scanning various browsers like Google Chrome, Microsoft Edge, Mozilla Firefox, and Brave to find extensions that might be DApp wallets. It's particularly useful for digital forensics purposes to track and audit such wallets across different browsers and user accounts. An active internet connection is required for the tool to fetch extension names and descriptions directly from the respective browser add-on stores, ensuring up-to-date and accurate identification.

## Database File (Optional)
The tool comes with an optional SQLite database file `EXTENSIONS.db`, which contains a comprehensive list of known DApp Chrome extensions. While not mandatory, utilizing this database can enhance the tool's effectiveness in offline mode, offering a broader range of extension identification without needing to access online browser stores.

## Installation

### Prerequisites
- Python 3.8 or higher
- PyQt5
- psutil
- glob
- sqlite3

### Setup
1. Clone the repository or download the source code.
2. Navigate to the folder containing `EXTENSION-CHECKER.py`.
3. Install required Python packages:
   ```sh
   pip install PyQt5 psutil requests
   ```

## Usage

### Starting the Application
Run the script using Python:
```sh
python EXTENSION-CHECKER.py
```

### Interface
The application presents a user-friendly interface with the following sections:
- Drive Selection: Choose one or multiple drives to scan for browser extensions.
- Extension ID Input: Manually input extension IDs for identification.
- Search Button: Initiates the search based on the selected drives or entered IDs.
- Results Table: Displays identified extensions along with details like name, description, associated user account, browser, and source.

### Saving Results
- Enter a filename in the provided text box and click 'Save Results' to export the table data as a CSV file.

## Features

- **Multi-Browser Support**: Identifies extensions from Google Chrome, Microsoft Edge, Mozilla Firefox, and Brave.
- **Multiple Drives Handling**: Capable of scanning multiple drives for browser extensions.
- **Manual ID Input**: Allows manual input of extension IDs for identification.
- **User Account Association**: Associates identified extensions with user accounts.
- **Online and Offline Operation**: Works both online (fetches data from browser stores) and offline (uses local database).
- **Export Functionality**: Enables users to save identified extensions and their details as a CSV file.

## Contributing

Contributions to the Extension Checker are welcome. Here are ways you can contribute:
- Reporting bugs
- Suggesting enhancements
- Submitting pull requests for new features or bug fixes

For major changes, please open an issue first to discuss what you would like to change.

---
