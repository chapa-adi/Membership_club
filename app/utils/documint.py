
import os
import requests
from dotenv import load_dotenv

load_dotenv()

DOCUMINT_API_KEY = os.getenv("DOCUMINT_API_KEY")
DOCUMINT_TEMPLATE_ID = os.getenv("DOCUMINT_TEMPLATE_ID")
DOCUMINT_LIVE = os.getenv("DOCUMINT_LIVE", "false").lower() == "true"

# Only enforce API key/template if we are actually trying to use live Documint
if DOCUMINT_LIVE and (not DOCUMINT_API_KEY or not DOCUMINT_TEMPLATE_ID):
    raise RuntimeError("Documint API key or template ID not set in .env")

DOCUMINT_URL = (
    f"https://api.documint.me/1/templates/{DOCUMINT_TEMPLATE_ID}/content"
    if DOCUMINT_TEMPLATE_ID
    else None
)


def generate_ticket_pdf_via_documint(
    first_name: str,
    last_name: str,
    date: str,
    ticket_id: str,
) -> bytes:

   # Call Documint API to generate a real PDF. Used when DOCUMINT_LIVE is True.


    if not DOCUMINT_URL or not DOCUMINT_API_KEY:
        raise Exception("Documint is not configured")

    payload = {
        "first_name": first_name,
        "last_name": last_name,
        "date": date,
        "ticket_id": ticket_id,
    }

    headers = {
        "api_key": DOCUMINT_API_KEY,
        "Content-Type": "application/json",
    }

    resp = requests.post(DOCUMINT_URL, json=payload, headers=headers)
    content_type = resp.headers.get("Content-Type", "")

    # CASE 1: Direct PDF
    if resp.status_code == 200 and content_type.startswith("application/pdf"):
        if not resp.content.startswith(b"%PDF"):
            raise Exception("Documint said PDF but bytes are invalid")
        return resp.content

    # CASE 2: JSON with URL
    try:
        data = resp.json()
    except Exception:
        # Documint might be returning HTML like "Service Unavailable"
        raise Exception(f"Documint sent non-PDF, non-JSON: {resp.text[:300]}")

    if resp.status_code != 200:
        raise Exception(f"Documint error: {data}")

    pdf_url = data.get("url")
    if not pdf_url:
        raise Exception(f"No PDF URL in Documint JSON: {data}")

    pdf_resp = requests.get(pdf_url)
    if pdf_resp.status_code != 200:
        raise Exception(f"Failed to download PDF: {pdf_resp.status_code}")

    if not pdf_resp.content.startswith(b"%PDF"):
        raise Exception("Downloaded file is not a real PDF")

    return pdf_resp.content


def fake_generate_ticket_pdf(
    first_name: str,
    last_name: str,
    date: str,
    ticket_id: str,
) -> bytes:
    # This function is just here for testing so that we do not run out of free trial from Documint
    content = (
        "FAKE TICKET (DEV ONLY)\n\n"
        f"Name: {first_name} {last_name}\n"
        f"Date: {date}\n"
        f"Ticket ID: {ticket_id}\n"
    )
    return content.encode("utf-8")
