import os

import requests
import robin_stocks.robinhood as r
from dotenv import load_dotenv
from fastapi import Body, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from supabase import Client, create_client

load_dotenv()

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Supabase setup
url: str = os.getenv("SB_URL")
key: str = os.getenv("SB_API_KEY")
supabase: Client = create_client(url, key)

# Configure CORS
origins = [
    "http://localhost:5173",  # SvelteKit frontend
    "http://localhost:3000",  # SvelteKit frontend (alternative port)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/login")
async def login(
    username: str = Body(...), password: str = Body(...), mfa_code: str = Body(None)
):
    # Log in to Robinhood
    try:
        if mfa_code:
            login_response = r.login(username, password, mfa_code=mfa_code)
        else:
            login_response = r.login(username, password)
    except Exception as e:
        if "MFA" in str(e):
            return JSONResponse({"error": "MFA required"}, status_code=401)
        return JSONResponse({"error": str(e)}, status_code=400)

    if not login_response:
        return JSONResponse({"error": "Failed to log in to Robinhood"}, status_code=400)

    return JSONResponse({"message": "Login successful"})


@app.post("/api/fetch_robinhood_orders")
async def fetch_robinhood_orders(username: str = Body(...), password: str = Body(...)):
    # Log in to Robinhood
    login_response = r.login(username, password)
    if not login_response:
        return JSONResponse({"error": "Failed to log in to Robinhood"}, status_code=400)

    # Fetch order history
    orders = r.orders.get_all_stock_orders()

    # Map the orders to the desired format
    formatted_orders = []
    for order in orders:
        instrument_url = order["instrument"]
        instrument_response = requests.get(instrument_url)
        instrument_data = instrument_response.json()
        symbol = instrument_data["symbol"]

        formatted_order = {
            "instrument": symbol,
            "quantity": float(order["quantity"]),
            "price": float(order["average_price"]) if order["average_price"] else None,
            "state": order["state"],
        }
        formatted_orders.append(formatted_order)

    return JSONResponse({"orders": formatted_orders})


@app.post("/api/insert_orders")
async def insert_orders(orders: list = Body(...)):
    # Insert orders into Supabase
    for order in orders:
        data = {
            "user_id": "example_user",  # Replace with actual user ID
            "instrument": order["instrument"],
            "quantity": order["quantity"],
            "price": order["price"],
            "state": order["state"],
        }
        supabase.table("orders").insert(data).execute()

    return JSONResponse({"message": "Order history has been saved to Supabase!"})
