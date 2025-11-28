
import json
import os
from datetime import datetime, timedelta

import jwt  
from dotenv import load_dotenv

load_dotenv()

GOOGLE_WALLET_ISSUER_ID = os.getenv("GOOGLE_WALLET_ISSUER_ID")
GOOGLE_WALLET_CLASS_ID = os.getenv("GOOGLE_WALLET_CLASS_ID")  # full id: issuerId.classSuffix
SERVICE_ACCOUNT_KEY_PATH = os.getenv("GOOGLE_WALLET_KEY_PATH")  # path to .json key


def generate_wallet_save_url(ticket_id: int, name: str, email: str) -> str:
# generating a url that gives us a generic pass in google wallet

    if not all([GOOGLE_WALLET_ISSUER_ID, GOOGLE_WALLET_CLASS_ID, SERVICE_ACCOUNT_KEY_PATH]):
        raise RuntimeError("Google Wallet env vars not fully configured")

    # Load service account private key + email from JSON key
    with open(SERVICE_ACCOUNT_KEY_PATH, "r") as f:
        key_data = json.load(f)

    private_key = key_data["private_key"]
    service_account_email = key_data["client_email"]  # required for `iss`

    # Google requires object id format: issuerId.objectId (unique per ticket)
    object_id = f"{GOOGLE_WALLET_ISSUER_ID}.ticket_{ticket_id}"

    #  Define a minimal generic object
    generic_object = {
        "id": object_id,
        "classId": GOOGLE_WALLET_CLASS_ID,  
        "state": "ACTIVE",
        "header": {
            "defaultValue": {
                "language": "en-US",
                "value": "Paradise Golf Day Pass",
            }
        },
        "subheader": {
            "defaultValue": {
                "language": "en-US",
                "value": name,
            }
        },
        "barcode": {
            "type": "QR_CODE",
            "value": f"TICKET-{ticket_id}",
        },
        "textModulesData": [
            {
                "id": "holder",
                "header": "Ticket holder",
                "body": f"{name}\n{email}",
            }
        ],
    }

    now = datetime.utcnow()

    # JWT payload for Save to Wallet
    payload = {
        "iss": service_account_email,
        "aud": "google",
        "typ": "savetowallet",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=10)).timestamp()),
        "origins": [
            "http://localhost:8000",
            "http://127.0.0.1:8000",
        ],
        "payload": {
            "genericObjects": [generic_object],
        },
    }

    # Sign the JWT
    signed_jwt = jwt.encode(payload, private_key, algorithm="RS256")
    if isinstance(signed_jwt, bytes):
        signed_jwt = signed_jwt.decode("utf-8")
    #  getting the actuall URL
    save_url = f"https://pay.google.com/gp/v/save/{signed_jwt}"
    return save_url
