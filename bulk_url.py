import requests
import base64

# ========== USER CONFIGURATION ==========
ESA_HOST = "192.168.0.125:6080"  # ESA Hostname/IP, supported over API HTTP(6080) currently 
USERNAME = "api"  # Plain-text username
PASSWORD = "C!sco135"  # Plain-text password
DICTIONARY_NAME = "1-URL-Blocklist"  # Dictionary to update

WORDS_TO_ADD_CSV = "badurl.com, testbad.com"  # Comma-separated words, example "test.com, url.com"

# ========== SCRIPT STARTS HERE ==========
BASE_URL = f"http://{ESA_HOST}/esa/api/v2.0"

def encode_base64(value):
    """Encode a string in Base64 format (without newline)."""
    encoded_value = base64.b64encode(value.encode()).decode().strip()
  #  print(f"DEBUG: Base64-encoded '{value}' → '{encoded_value}'")  # Debug print
    return encoded_value

def parse_words(csv_text):
    """Convert comma-separated words into the required list format."""
    words = []
    for item in csv_text.split(","):
        parts = item.strip().split(":")
        if len(parts) == 1:
            words.append([parts[0]])
        else:
            words.append([parts[0]] + [int(parts[1])] + parts[2:])
    return words

def login():
    """Authenticate and retrieve JWT token."""
    encoded_username = encode_base64(USERNAME)
    encoded_password = encode_base64(PASSWORD)

    print(f"Attempting login with encoded credentials...")  # Debug print

    login_url = f"{BASE_URL}/login"
    headers = {"Content-Type": "application/json"}
    payload = {"data": {"userName": encoded_username, "passphrase": encoded_password}}

    response = requests.post(login_url, json=payload, headers=headers)
    
    if response.status_code == 200:
        print("Login successful!")
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
    # If ESA is on cluster, use this instead 
    # url = f"{BASE_URL}/config/dictionaries/{dictionary_name}/words?device_type=esa&mode=cluster"
    url = f"{BASE_URL}/config/dictionaries/{dictionary_name}/words?device_type=esa"
    headers = {"jwttoken": jwt_token, "Content-Type": "application/json"}
    payload = {"data": {"words": words}}

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code in [200, 201]:
        print(f"Successfully added words to {dictionary_name}")
    else:
        print(f"Error adding words: {response.status_code}, {response.text}")

# Main Execution
WORDS_TO_ADD = parse_words(WORDS_TO_ADD_CSV)  # Convert CSV to list format
jwt_token = login()
if jwt_token:
  #  get_dictionaries(jwt_token)  # Optional: Show available dictionaries
    add_words_to_dictionary(jwt_token, DICTIONARY_NAME, WORDS_TO_ADD)

