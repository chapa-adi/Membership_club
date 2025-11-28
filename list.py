import os
import requests
from dotenv import load_dotenv

load_dotenv()

DOCUMINT_API_KEY = os.getenv("DOCUMINT_API_KEY")

resp = requests.get(
    "https://api.documint.me/1/templates",
    headers={"api_key": DOCUMINT_API_KEY}
)

print("STATUS:", resp.status_code)
print("BODY:", resp.text)
