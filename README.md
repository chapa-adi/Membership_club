# Membership Club

A FastAPI application for member login and golf day-pass tickets. It stores users and tickets in SQLite, emails ticket attachments, and optionally generates PDFs with Documint and save links for Google Wallet.

## Prerequisites

- Python 3.10 or newer and pip.
- SMTP server credentials for sending ticket emails. These settings are required when the application starts.
- Optional: a Documint API key and template for real PDF tickets, and a Google Wallet issuer account and service-account JSON key for wallet passes.

## Install

Run these commands in PowerShell from the repository's parent folder:

```powershell
cd Membership_club
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install python-dotenv requests "PyJWT[crypto]"
```

The last command installs packages imported by the application but currently missing from `requirements.txt`. The `bcrypt` package used for passwords is installed through the listed `passlib[bcrypt]` dependency.

On macOS/Linux, activate the environment with `source .venv/bin/activate` instead. If PowerShell blocks activation, skip activation and use `.\.venv\Scripts\python.exe` in place of `python` for subsequent commands.

## Configure

Create or update `.env` in the `Membership_club` folder using your own values:

```dotenv
MAIL_USERNAME=your-smtp-username
MAIL_PASSWORD=your-smtp-password
MAIL_FROM=sender@example.com
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_STARTTLS=True
MAIL_SSL_TLS=False

DOCUMINT_LIVE=false
DOCUMINT_API_KEY=
DOCUMINT_TEMPLATE_ID=

GOOGLE_WALLET_ISSUER_ID=
GOOGLE_WALLET_KEY_PATH=
```

Use the port and TLS settings supplied by your email provider. The mail configuration recognizes the exact value `True` for the TLS flags. Some providers require an app password.

Keep `.env` and service-account key files private; do not commit credentials or share them in documentation.

### Optional Documint PDFs

Set `DOCUMINT_LIVE=true`, provide your API key and template ID, and configure the template to accept `first_name`, `last_name`, `date`, and `ticket_id`.

With `DOCUMINT_LIVE=false`, the application generates a development text attachment with a `.pdf` extension; it is **not a valid PDF**. A failed live Documint request also falls back to this attachment. Missing live credentials prevent startup.

### Optional Google Wallet passes

Set `GOOGLE_WALLET_ISSUER_ID` to your issuer ID and `GOOGLE_WALLET_KEY_PATH` to your service-account JSON file path, for example `./wallet_key.json`. The service account must have access to your Wallet issuer account. The code uses the class ID `<issuer_id>.golf_day_pass` and includes that generic class in the signed save link.

Wallet generation errors are logged and do not prevent ticket email delivery. The signed links expire after 10 minutes, and the configured origins are `http://localhost:8000` and `http://127.0.0.1:8000`.

## Run locally

From the `Membership_club` folder, with the virtual environment active:

```powershell
python -m uvicorn app.main:app --reload
```

Keep this working directory: template, static-file, database, and generated-ticket paths are relative to it. Stop the server with `Ctrl+C`.

- Health check: http://127.0.0.1:8000/
- Login page: http://127.0.0.1:8000/login
- Ticket form: http://127.0.0.1:8000/buy-ticket
- Interactive API documentation: http://127.0.0.1:8000/docs

SQLite tables are created automatically on startup in `club.db`; no separate database server or migration command is required.

## Try the ticket flow

1. Visit http://127.0.0.1:8000/create-test-user once to create the built-in development user. The response includes its email and password.
2. Sign in at `/login` using those credentials.
3. Complete the ticket form with a recipient email address you control and submit it.
4. Check the recipient inbox for the attachment and, if configured, the Google Wallet link.

Tickets are saved to `club.db`, and attachments are written as `ticket_<id>.pdf` in the project folder. Submitting the form sends a real email; there is no payment-processing integration. SMTP failures cause the request to fail after the ticket has already been stored, so retrying creates another ticket.

The built-in test-user endpoint and login flow are for local development. Login redirects to the ticket form without establishing an authenticated session, and the ticket routes do not enforce authentication. Add access controls and remove the test-user endpoint before deploying publicly.

## Documint helper scripts

With Documint credentials configured, run these from the project folder:

```powershell
python list.py
python test_documint.py
```

`list.py` lists templates available to your API key. `test_documint.py` calls the live generation API and writes `test_ticket.pdf`, even when `DOCUMINT_LIVE=false`; it may consume your Documint quota.

## Troubleshooting

- **Missing module:** install both `requirements.txt` and the additional packages in the install section using the same Python environment that runs Uvicorn.
- **Mail configuration error at startup:** check the required `MAIL_*` values in the project-root `.env`.
- **Email fails:** verify the SMTP host, port, credentials, sender address, and TLS settings; inspect the server traceback.
- **Attachment will not open as a PDF:** enable and configure live Documint generation, then check the server logs for fallback errors.
- **No Wallet button/link:** check the issuer ID, key-file path, service-account permissions, and terminal message beginning `Google Wallet generation failed`.
- **Templates or static directory not found:** run Uvicorn from `Membership_club`, not its parent folder.
