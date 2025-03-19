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

    # Function to get dictionary data
    def get_dictionary():
        dictionary_url = f"{base_url}/config/dictionaries?device_type=esa"
        headers = {
            "jwttoken": jwt_token,
            "cache-control": "no-cache",
            "Accept": "*/*",
            "Connection": "keep-alive"
        }

        response = requests.get(dictionary_url, headers=headers)

        if response.status_code == 200:
            print("Dictionaries:", response.json())
        else:
            print("Error fetching dictionaries:", response.status_code, response.text)

    # Function to add words to a dictionary
    def post_to_dictionary(dictionary_name, words):
        post_url = f"{base_url}/config/dictionaries/{dictionary_name}/words?device_type=esa"
        headers = {
            "jwttoken": jwt_token,
            "Content-Type": "application/json"
        }
        payload = {
            "data": {
                "words": words
            }
        }

        response = requests.post(post_url, json=payload, headers=headers)

        if response.status_code == 200:
            print(f"Successfully added words to {dictionary_name}")
        else:
            print(f"Error adding words: {response.status_code}, {response.text}")

    # Fetch dictionaries
   # get_dictionary()

    # Example: Add words to MyDictionary
    words_to_add = [
            ["example-bad.com"],
        ["internetbadguys.com"],
        ["iamalicious.com"]
    ]
    post_to_dictionary("URL-Blocklist", words_to_add)

else:
    print("Login failed:", response.status_code, response.text)

