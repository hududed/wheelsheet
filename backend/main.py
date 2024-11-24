import json
import logging
import os

import robin_stocks.robinhood as r
from dotenv import load_dotenv
from fastapi import Body, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from supabase import Client, create_client

logging.basicConfig(level=logging.INFO)

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
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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

    # Fetch and insert orders after successful login
    await fetch_and_insert_orders(username, password)

    return JSONResponse({"message": "Login successful"})


async def fetch_and_insert_orders(username: str, password: str):
    # Fetch orders
    response = await fetch_robinhood_orders_internal(
        username=username, password=password
    )
    if response.status_code != 200:
        logging.error(f"Failed to fetch orders: {await response.body.decode()}")
        return

    response_data = json.loads(response.body.decode())
    orders = response_data.get("orders", [])
    if not orders:
        logging.info("No orders to insert.")
        return

    # Insert orders
    await insert_orders_internal(orders)


@app.post("/api/fetch_robinhood_orders")
async def fetch_robinhood_orders(username: str = Body(...), password: str = Body(...)):
    return await fetch_robinhood_orders_internal(username, password)


async def fetch_robinhood_orders_internal(username: str, password: str):
    # Log in to Robinhood
    login_response = r.login(username, password)
    if not login_response:
        return JSONResponse({"error": "Failed to log in to Robinhood"}, status_code=400)

    # Fetch order history
    orders = r.orders.get_all_option_orders()

    # Log the keys of the order dictionary
    if orders:
        logging.info(f"Order keys: {orders[0].keys()}")

    # Map the orders to the desired format
    formatted_orders = []
    for order in orders:
        # Skip orders where the state is not filled
        if order["state"] != "filled":
            continue

        # Log the order to understand its structure
        logging.info(f"Order: {order}")

        # Fetch the required keys
        created_at = order.get("created_at", "Unknown")
        account_number = order.get("account_number", "Unknown")
        chain_symbol = order.get("chain_symbol", "Unknown")
        expiration_date = order["legs"][0].get("expiration_date", "Unknown")
        strike_price = float(order["legs"][0].get("strike_price", "Unknown"))
        net_amount = float(order.get("net_amount", "Unknown"))
        net_amount_direction = order.get("net_amount_direction", "Unknown")
        quantity = float(order.get("quantity", "Unknown"))
        state = order.get("state", "Unknown")

        formatted_order = {
            "created_at": created_at,
            "account_number": account_number,
            "chain_symbol": chain_symbol,
            "expiration_date": expiration_date,
            "strike_price": strike_price,
            "net_amount": net_amount,
            "net_amount_direction": net_amount_direction,
            "quantity": quantity,
            "state": state,
        }
        formatted_orders.append(formatted_order)

    return JSONResponse({"orders": formatted_orders})


@app.post("/api/insert_orders")
async def insert_orders(orders: list = Body(...)):
    return await insert_orders_internal(orders)


async def insert_orders_internal(orders: list):
    for order in orders:
        data = {
            "created_at": order["created_at"],
            "account_number": order["account_number"],
            "chain_symbol": order["chain_symbol"],
            "expiration_date": order["expiration_date"],
            "strike_price": order["strike_price"],
            "net_amount": order["net_amount"],
            "net_amount_direction": order["net_amount_direction"],
            "quantity": order["quantity"],
            "state": order["state"],
        }
        # logging.info(f"Inserting order: {data}")
        try:
            supabase.table("orders").insert(data).execute()
        except Exception as e:
            if "duplicate key value violates unique constraint" in str(e):
                # logging.warning(
                #     f"Duplicate order found: {data['created_at']}, skipping."
                # )
                continue
            else:
                # logging.error(f"Error inserting order: {e}")
                return JSONResponse({"error": str(e)}, status_code=500)

    return JSONResponse({"message": "Order history has been saved to Supabase!"})
