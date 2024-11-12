import requests
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv(override=True)

# Define the data payload required by the API
jData = {
    "uid": os.getenv("trade_userid")  # Logged-in User ID
}

# Set up headers
user_detail_headers = {
    "Content-Type": "application/json"
}
user_detail_payload = 'jData=' + json.dumps(jData) + f'&jKey={os.getenv("app_access_token")}'
user_detail_response = requests.post(os.getenv("user_detail_endpoint"), headers=user_detail_headers, data=user_detail_payload)

# Check if the request was successful
if user_detail_response.status_code == 200:
    # Parse the JSON response
    response_data = user_detail_response.json()

    # Handle success or failure based on the response
    if response_data["stat"] == "Ok":
        print("User Details Fetched successfully.")
        # Access various fields from the response
        print("Broker Name:", response_data.get("brkname"))
        print("Branch ID:", response_data.get("brnchid"))
        print("Email:", response_data.get("email"))
        print("Account ID:", response_data.get("actid"))
        print("Access Type:", response_data.get("uprev"))
        print("Products_Enabled:", response_data.get("prarr"))
        # Additional fields can be accessed here as needed
    else:
        print(f"Failed to fetch user details. Error message: {response_data.get('emsg', 'Unknown error')}")

else:
    print(f"Failed to fetch user details. Status Code: {user_detail_response.status_code}")
    print(f"Response: {user_detail_response.text}")