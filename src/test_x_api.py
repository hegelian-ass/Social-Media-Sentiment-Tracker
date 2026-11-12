
import os
import requests
from dotenv import load_dotenv

# Load credentials from the project's .env file
load_dotenv()

TOKEN = os.getenv("X_BEARER_TOKEN")

if not TOKEN:
    print("ERROR: X_BEARER_TOKEN not found in .env")
    raise SystemExit(1)

url = "https://api.x.com/2/users/by/username/xdevelopers"

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

try:
    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    print("HTTP Status:", response.status_code)

    if response.status_code == 200:
        data = response.json()["data"]
        print("\nSUCCESS! X API connection is working.")
        print("Account name:", data["name"])
        print("Username:", data["username"])
        print("User ID:", data["id"])

    else:
        print("\nAPI request failed.")
        print(response.text[:1000])

except requests.RequestException as error:
    print("Connection error:", error)
