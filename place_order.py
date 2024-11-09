import requests
import os
from dotenv import load_dotenv
import json
import pandas as pd
import tvDatafeed
from tvDatafeed import TvDatafeed,Interval
from datetime import date, time, datetime as dt

#read scripmaster file
nse_cm = pd.read_csv (r"scripmaster_files\nse_cm.csv",sep=",")
# Load environment variables
load_dotenv(override=True)

# Define the endpoint and sId (server id)
place_order_endpoint = os.getenv("place_order_endpoint") + os.getenv("server_id")
stop_amount_per_trade = os.getenv("stop_amount_per_trade")
symbol = input("Enter Symbol: ")
tt = input("Buy or Sell (B/S): ")
pTrdSymbol  = nse_cm.loc[(nse_cm['pSymbolName'] == symbol.upper()) & (nse_cm['pGroup'] == 'EQ') & (nse_cm['pExchSeg'] == 'nse_cm') & (nse_cm['pSegment'] == 'CASH'), 'pTrdSymbol'].iloc[0]
#######        Position Sizing     #################
todays_date = date.today()
todays_date = date.today()
tdate = str(todays_date.year)+'-'+str(todays_date.month)+'-'+str(todays_date.day)
data = TvDatafeed().get_hist(symbol=symbol,exchange='NSE',interval=Interval.in_daily,n_bars=1)
ltp= data.loc[tdate+' 09:15:00']['close']
print(f"LTP for {pTrdSymbol}: {ltp}")
sl = input("Enter stoploss Price: ")
if tt == "b":
    qty = str(int(float(stop_amount_per_trade)/(float(ltp)-float(sl))))
elif tt == "s":
    qty = str(int(float(stop_amount_per_trade)/(float(sl)-float(ltp))))

print(f"qty = {qty}")
if int(qty) > 0:

    # Set up headers
    place_order_headers = {
        "Content-Type": "application/json"
    }

    # Define the order payload
    jData = {
        "uid": "VIDYA",  # Logged in User ID
        "actid": "CLIENT1",  # Account ID
        "exch": "NSE",  # Exchange (e.g., NSE, NFO, BSE, MCX)
        "tsym": "ACC-EQ",  # Trading symbol (replace with actual symbol)
        "qty": "50",  # Quantity to buy/sell
        "prc": "1400",  # Price (ensure it's not 0 if price type is LMT)
        "prd": "H",  # Product type (e.g., CNC, NRML, CO, etc.)
        "trantype": "B",  # Transaction type (B -> Buy, S -> Sell)
        "prctyp": "LMT",  # Price type (e.g., LMT, MKT, SL-LMT)
        "ret": "DAY",  # Retention type (DAY, EOS, IOC)
        "amo": "Yes"  # After Market Order indicator (Yes or not present)
    }

    jKey = os.getenv("app_access_token")

    # Convert the order details to a URL-encoded string
    #place_order_payload = f"jData={requests.utils.quote(str(place_order_details))}"
    place_order_payload = {
        "jData": json.dumps(jData),  # Convert jData dictionary to JSON string
        "jKey": jKey  # API key obtained after successful login
    }

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