import requests

# ========== USER CONFIGURATION ==========
ESA_HOST = "192.168.0.125:6080"  # ESA Hostname/IP
USERNAME = "YXBp"  # Base64-encoded username
PASSWORD = "QyFzY28xMzU="  # Base64-encoded password
DICTIONARY_NAME = "URL-Blocklist"  # Dictionary to update

WORDS_TO_ADD = [
    ["tetsting123.com"]  # Simple word entry
#    ["*credit", 2, "prefix"]  # Word with weight and match rule
]

# ========== SCRIPT STARTS HERE ==========
BASE_URL = f"http://{ESA_HOST}/esa/api/v2.0"

def login():
    """Authenticate and retrieve JWT token."""
    login_url = f"{BASE_URL}/login"
    headers = {"Content-Type": "application/json"}
    payload = {"data": {"userName": USERNAME, "passphrase": PASSWORD}}

    response = requests.post(login_url, json=payload, headers=headers)
    
    if response.status_code == 200:
        return response.json()["data"]["jwtToken"]
    else:
        print(f"Login failed: {response.status_code}, {response.text}")
        return None

def get_dictionaries(jwt_token):
    """Fetch and display available dictionaries."""
    url = f"{BASE_URL}/config/dictionaries?device_type=esa"
    headers = {"jwttoken": jwt_token, "Accept": "*/*"}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print("Dictionaries:", response.json())
    else:
        print(f"Error fetching dictionaries: {response.status_code}, {response.text}")

def add_words_to_dictionary(jwt_token, dictionary_name, words):
    """Add words to a specified dictionary."""
    url = f"{BASE_URL}/config/dictionaries/{dictionary_name}/words?device_type=esa"
    headers = {"jwttoken": jwt_token, "Content-Type": "application/json"}
    payload = {"data": {"words": words}}

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        print(f"Successfully added words to {dictionary_name}")
    else:
        print(f"Error adding words: {response.status_code}, {response.text}")

# Main Execution
jwt_token = login()
if jwt_token:
    get_dictionaries(jwt_token)  # Optional: Show available dictionaries
    add_words_to_dictionary(jwt_token, DICTIONARY_NAME, WORDS_TO_ADD)

