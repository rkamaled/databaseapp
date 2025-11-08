# Database Application Setup Guide
 
This guide provides instructions for setting up and running both the frontend and backend components of the Database Application.
## Get the code

- clone the repo into any folder by opening a terminal in your desired folder and pasting 
    ```bash
    git clone https://github.com/rkamaled/databaseapp.git
    ```

## System Requirements
 
### Required Software Downloads
 
#### For Windows:
- Node.js
  - Download from: [Node.js Official Website](https://nodejs.org/)
  - Choose the "LTS" (Long Term Support) version
  - npm (Node Package Manager) will be automatically installed with Node.js
- Python 3.x
  - Download from: [Python Official Website](https://www.python.org/downloads/)
  - Important: During installation, check the box that says "Add Python to PATH"
- Git
  - Download from: [Git for Windows](https://gitforwindows.org/)
 
#### For macOS:
- Node.js
  - Download from: [Node.js Official Website](https://nodejs.org/)
  - Choose the "LTS" (Long Term Support) version
  - npm (Node Package Manager) will be automatically installed with Node.js
  - Alternatively, install using Homebrew:
    ```bash
    brew install node
    ```
- Python 3.x
  - Download from: [Python Official Website](https://www.python.org/downloads/)
  - Alternatively, install using Homebrew:
    ```bash
    brew install python
    ```
 
#### Installing Homebrew (for macOS users):
If you want to use Homebrew for installation (recommended for macOS):
1. Visit [Homebrew Website](https://brew.sh/)
2. Copy and paste the installation command from the website into your Terminal
 
## ODBC Driver 17 for SQL Server

The backend uses `pyodbc` and requires the "ODBC Driver 17 for SQL Server".

#### macOS (Homebrew)
Run the following commands in Terminal:
```bash
brew update
brew install unixodbc
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
ACCEPT_EULA=Y brew install msodbcsql17
```

#### Windows
Download and install from Microsoft:
- [Download ODBC Driver for SQL Server (Windows)](https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server)

On that page, choose Windows and select the installer for "ODBC Driver 17 for SQL Server", then run the `.msi` and follow the prompts.
 
#### Verify installation

macOS:
```bash
odbcinst -q -d
```

Windows (PowerShell):
```powershell
Get-OdbcDriver | Where-Object Name -like "*ODBC Driver 17*"
```

If the command prints a matching entry, the driver is installed. If it prints an empty list or nothing, the driver is not detected.
 
## Installation Steps
 
### 1. Backend Setup
 
#### Windows:
1. Open Command Prompt or PowerShell in the `backend` directory
2. Create a Python virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   ```bash
   .\venv\Scripts\activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
 
#### macOS:
1. Open Terminal in the `backend` directory
2. Create a Python virtual environment using this command:
   ```bash
   python3 -m venv venv
   ```
3. Activate the virtual environment:
   ```bash
   source venv/bin/activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
 
### 2. Frontend Setup
 
#### Windows & macOS:
1. Open a terminal in the `frontend` directory
2. Install Node.js dependencies:
   ```bash
   npm install
   ```
    ```bash
   npm ci
   ```
 
 
Setup database connection file:
go to backend folder and create a file called ".env"
then paste the db credentials:
   ```bash
   DB_SERVER=msdatatest2022.cfs.uoguelph.ca
   DB_DATABASE=GFHS_PSDB
   DB_USERNAME=gfhsUser
   DB_PASSWORD= *
   DB_DRIVER=ODBC Driver 17 for SQL Server
   ```

 
*put password for DB in password variable
 
## Running the Application
 
Connect to vpn the open the main folder(DATABASEAPP) in terminal and run the following command:
 
   ```bash
   python3 start_app.py
   ```
 
the App should now open in your browser!


## Fetching New Updates from Github

- Fetch latest updates from the repo by opening the terminal in the DATABASEAPP folder and run the following:
    ```bash
   git reset --hard
   git fetch origin
    ```

 
