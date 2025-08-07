# Backend Setup and Running Instructions

This is the backend server for the Database Application using Flask.

## Prerequisites

- Python 3.x installed on your system
- pip (Python package installer)

## First-Time Setup

1. Open a terminal in the `backend` directory
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Server

1. Make sure you're in the `backend` directory
2. Activate the virtual environment (if not already activated):
   - On Windows:
     ```bash
     .\venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

3. Run the Flask application:
   ```bash
   python app.py
   ```

4. The server will start at `http://localhost:5000`

## Verifying the Server is Running

- Open your web browser and go to `http://localhost:5000`
- You should see a JSON response: `{"message": "Backend server is running"}`

## Development Notes

- The server runs in debug mode, which means:
  - It will automatically reload when you make code changes
  - It will show detailed error messages
- CORS is enabled for all routes, allowing frontend access
- The server runs on port 5000 by default

## Stopping the Server

- Press `Ctrl+C` in the terminal to stop the server
- To deactivate the virtual environment:
  ```bash
  deactivate
  ```