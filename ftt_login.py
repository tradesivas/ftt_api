import requests
import hashlib
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)
api_key = os.getenv("api_key")
api_secret = os.getenv("api_secret")
request_code = input("Enter request_code: ")    # 1. Open the Authorization URL https://auth.flattrade.in/?app_key=APIKEY 2. Enter your Client id (UCC), Password, PAN/DOB and submit 3. copy request code from https://yourRedirectURL.com/?request_code=requestCodeValue

# Create the SHA-256 hash for the api_secret
hash_input = api_key + request_code + api_secret
print("-------- hash input ---------")
print(hash_input)
print("-----------------------------")
hashed_secret = hashlib.sha256(hash_input.encode()).hexdigest()
print("-------- hash secret ---------")
print(hashed_secret)
print("-----------------------------")

# Set up the payload
payload = {
    "api_key": api_key,
    "request_code": request_code,
    "api_secret": hashed_secret
}

# Send the POST request to obtain the token
response = requests.post(os.getenv("app_access_token_endpoint"), json=payload)
print("---------   Response ---------")
print(response.status_code)
print(response.text)
print("------------------------------")

# Check if the request was successful
if response.status_code == 200:
    response_data = response.json()
    if response_data.get("stat") == "Ok":
        app_access_token = response_data.get("token")
        client_code = response_data.get("client")
        print("Token:", app_access_token)
        print("Client Code:", client_code)
        # Update the .env file with the new access token
        with open(".env", 'r') as file:
            filedata = file.read()
        
        # Replace old token in .env file
        filedata = filedata.replace(os.getenv("app_access_token"), app_access_token)

        with open(".env", 'w') as file:
            file.write(filedata)
    else:
        print("Error:", response_data.get("emsg"))
else:
    print(f"Failed to obtain token. Status Code: {response.status_code}")
    print("Response:", response.text)