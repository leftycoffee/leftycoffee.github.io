import requests

# API URL
base_url = "http://192.168.0.125:6080/esa/api/v2.0"

# Login Credentials (Base64 Encoded)
login_payload = {
    "data": {
        "userName": "YXBp",
        "passphrase": "QyFzY28xMzU="
    }
}

# Login Request
login_url = f"{base_url}/login"
headers = {"Content-Type": "application/json"}

response = requests.post(login_url, json=login_payload, headers=headers)

# Check if login was successful
if response.status_code == 200:
    jwt_token = response.json()["data"]["jwtToken"]
    print("JWT Token:", jwt_token)

    # Use the token to fetch dictionary data
    dictionary_url = f"{base_url}/config/dictionaries/URL-Blocklist?device_type=esa"
    headers = {
        "jwttoken": jwt_token,
        "cache-control": "no-cache",
        "Accept": "*/*",
        "Connection": "keep-alive"
    }

    response = requests.get(dictionary_url, headers=headers)

    # Print dictionary response
    if response.status_code == 200:
        print("Dictionaries:", response.json())
    else:
        print("Error fetching dictionaries:", response.status_code, response.text)
else:
    print("Login failed:", response.status_code, response.text)

