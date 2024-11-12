import requests
import os
from dotenv import load_dotenv
import json
import pandas as pd
import urllib.parse

#read scripmaster file
nse_cm = pd.read_csv (r"scripmaster_files\nse_cm.csv",sep=",")
# Load environment variables
load_dotenv(override=True)

# Define the endpoint and sId (server id)
place_order_endpoint = os.getenv("place_order_endpoint")
nse_symbol = input("Enter NSE nse_symbol: ")
tt = input("Buy or Sell (B/S): ")
qty = input("Enter Qty: ")
target_price = input("Enter Target Price: ")
pTrdsymbol  = nse_cm.loc[(nse_cm['pSymbolName'] == nse_symbol.upper()) & (nse_cm['pGroup'] == 'EQ') & (nse_cm['pExchSeg'] == 'nse_cm') & (nse_cm['pSegment'] == 'CASH'), 'pTrdSymbol'].iloc[0]


# Set up headers
place_order_headers = {
    "Content-Type": "application/json"
}

# Define the order payload
jData = {
    "uid": os.getenv("trade_userid"),  # Logged in User ID
    "actid": os.getenv("trade_userid"),  # Account ID
    "exch": "NSE",  # Exchange (e.g., NSE, NFO, BSE, MCX)
    "tsym": urllib.parse.quote(pTrdsymbol),  # Trading nse_symbol (replace with actual nse_symbol)
    "qty": qty,  # Quantity to buy/sell
    "prc": target_price,  # Price (ensure it's not 0 if price type is LMT)
    "prd": "I",  # Product type (e.g., CNC, NRML, CO, etc.)
    "trantype": tt.upper(),  # Transaction type (B -> Buy, S -> Sell)
    "prctyp": "LMT",  # Price type (e.g., LMT, MKT, SL-LMT)
    "ret": "DAY"  # Retention type (DAY, EOS, IOC)
    #"amo": "Yes"  # After Market Order indicator (Yes or not present)
}

place_order_payload = 'jData=' + json.dumps(jData) + f'&jKey={os.getenv("app_access_token")}'

# Make the POST request to place the order
place_order_response = requests.post(place_order_endpoint, headers=place_order_headers, data=place_order_payload)

# Check if the request was successful
if place_order_response.status_code == 200:
    # Parse the JSON response
    response_data = place_order_response.json()

    # Handle the success or failure based on the response
    if response_data["stat"] == "Ok":
        print(f"Order placed successfully. Order number: {response_data['norenordno']}")
        # Extract the order ID (nOrdNo)
        order_id = response_data.get("norenordno")
    else:
        print(f"Failed to place order. Error message: {response_data.get('emsg', 'Unknown error')}")

else:
    print(f"Failed to place order. Status Code: {place_order_response.status_code}")
    print(f"Response: {place_order_response.text}")