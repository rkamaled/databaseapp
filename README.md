# Database Application Setup Guide

This guide provides instructions for setting up and running both the frontend and backend components of the Database Application.

## System Requirements

### Required Software Downloads

#### For Windows:
- Node.js 18.x or higher
  - Download from: [Node.js Official Website](https://nodejs.org/)
  - Choose the "LTS" (Long Term Support) version
  - npm (Node Package Manager) will be automatically installed with Node.js
- Python 3.x
  - Download from: [Python Official Website](https://www.python.org/downloads/)
  - Important: During installation, check the box that says "Add Python to PATH"
- Git (optional, for version control)
  - Download from: [Git for Windows](https://gitforwindows.org/)

#### For macOS:
- Node.js 18.x or higher
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
- Git (optional, for version control)
  - macOS usually comes with Git pre-installed
  - If needed, download from: [Git Official Website](https://git-scm.com/download/mac)
  - Or install using Homebrew:
    ```bash
    brew install git
    ```

#### Installing Homebrew (for macOS users):
If you want to use Homebrew for installation (recommended for macOS):
1. Visit [Homebrew Website](https://brew.sh/)
2. Copy and paste the installation command from the website into your Terminal

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
2. Create a Python virtual environment:
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

## Running the Application

### Starting the Backend Server

#### Windows:
1. Navigate to the `backend` directory
2. Activate the virtual environment (if not already activated):
   ```bash
   .\venv\Scripts\activate
   ```
3. Run the server:
   ```bash
   python app.py
   ```

#### macOS:
1. Navigate to the `backend` directory
2. Activate the virtual environment (if not already activated):
   ```bash
   source venv/bin/activate
   ```
3. Run the server:
   ```bash
   python app.py
   ```

The backend server will start at `http://localhost:5000`

### Starting the Frontend Application

#### Windows & macOS:
1. Open a new terminal in the `frontend` directory
2. Start the development server:
   ```bash
   npm start
   ```

The frontend application will start at `http://localhost:3000`

## Verifying the Setup

1. Backend verification:
   - Open your browser and navigate to `http://localhost:5000`
   - You should see a JSON response: `{"message": "Backend server is running"}`

2. Frontend verification:
   - Open your browser and navigate to `http://localhost:3000`
   - You should see the application's user interface

## Stopping the Application

### Backend:
1. Press `Ctrl+C` in the terminal running the backend server
2. Deactivate the virtual environment:
   ```bash
   deactivate
   ```

### Frontend:
- Press `Ctrl+C` in the terminal running the frontend server

## Troubleshooting

### Common Issues:

1. Port already in use:
   - Backend: Try using a different port by modifying the port number in `app.py`
   - Frontend: Kill the process using port 3000 or use a different port:
     ```bash
     npm start -- --port 3001
     ```

2. Python virtual environment issues:
   - Delete the `venv` directory and recreate it following the setup steps

3. Node.js dependency issues:
   - Delete the `node_modules` directory and `package-lock.json`
   - Run `npm install` again

4. CORS issues:
   - Ensure the backend CORS settings match your frontend URL
   - Check if both servers are running on the expected ports

## Development Notes

- The backend runs in debug mode by default
- Frontend hot-reloading is enabled for development
- Both servers will automatically reload when you make code changes
- The frontend is configured to proxy API requests to the backend

## Additional Resources

- [React Documentation](https://reactjs.org/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Python Documentation](https://docs.python.org/)
- [Node.js Documentation](https://nodejs.org/)
