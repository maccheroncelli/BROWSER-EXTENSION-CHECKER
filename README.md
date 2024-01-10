---

# Extension Checker

## Description
The Extension Checker is a Python-based tool designed for digital forensic investigators. It automates the process of identifying browser extensions across different browsers like Google Chrome, Microsoft Edge, Mozilla Firefox, and Brave. This tool is particularly useful for analyzing systems with multiple drives or user profiles.

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
   pip install PyQt5 psutil
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
