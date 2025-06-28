# FastAPI Backend

A lightweight Flask backend for handling API requests for our Instagram MCP server.

## 🚀 Features

- Python 3 & FastAPI-based API backend  
- Modular structure for scalability  
- Built-in environment variable support  
- Integrated with Supabase (PostgreSQL)

---

## 🛠 Installation Guide

### 1. Enter the backend

```bash
cd backend
```

### 2. Set Up a Virtual Environment

It's recommended to use a virtual environment to manage dependencies.

```bash
# For Unix/MacOS
python3 -m venv venv
source venv/bin/activate

# For Windows
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root and add your environment variables. Example:

```env
ENV=local

MCP_URL=http://localhost:8000/mcp

LOG_LEVEL=INFO

SUPABASE_URL=https://xyzsupabase.co/
SUPABASE_KEY=secret-key
```

### 5. Initialize the Database

This project uses Supabase, create a new organisation and table in a new database project and create a table called discounts. Make sure it has the following columns:

id(int8), product(text), category(text), price(numeric), min_discount(numeric), max_discount(numeric), coupon(text), created_at(timestamp), duration(numeric), product_url(text)

---

## ▶️ Running the App

Start the development server from the backend folder:

```bash
uvicorn app.main:app --host 127.0.0.1 --port 8001 --reload
```
