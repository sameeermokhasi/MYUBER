# MYUBER Project

A FastAPI-based project with server-side and client-side code.

## Project Structure

```
MYUBER/
├── server/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   └── ping.py
│   │   └── config/
│   │       ├── __init__.py
│   │       └── settings.py
│   └── requirements.txt
├── client/
│   ├── __init__.py
│   ├── client.py
│   └── requirements.txt
└── README.md
```

## Setup Instructions

### Server Setup
1. Navigate to the server directory: `cd server`
2. Install dependencies: `pip install -r requirements.txt`
3. Run the server: `uvicorn app.main:app --reload --host 0.0.0.0 --port 8000`

### Client Setup
1. Navigate to the client directory: `cd client`
2. Install dependencies: `pip install -r requirements.txt`
3. Run the client: `python client.py`

## API Endpoints

- `POST /ping` - Returns "pong" when sent JSON with "data": "ping"

## Note
This project intentionally contains bugs for testing purposes.

