#This is the router for ticket creation

from datetime import datetime

from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session
from fastapi_mail import MessageSchema

from app.database import get_session
from app.models import Ticket
from app.utils.documint import (
    generate_ticket_pdf_via_documint,
    fake_generate_ticket_pdf,
    DOCUMINT_LIVE,
)
from app.mail_config import fastmail
from app.utils.wallet import generate_wallet_save_url


router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


# ---------- GET: show Buy Ticket page ----------
@router.get("/buy-ticket", response_class=HTMLResponse)
def buy_ticket_page(
    request: Request,
    success: str | None = None,
):
    return templates.TemplateResponse(
        "buy_ticket.html",
        {
            "request": request,
            "success": success,
            "wallet_url": None,  # nothing on initial load
        },
    )


# ---------- POST: handle form, save ticket, generate PDF, send email ----------
@router.post("/buy-ticket", response_class=HTMLResponse)
async def buy_ticket_submit(
    request: Request,
    session: Session = Depends(get_session),
    first_name: str = Form(...),
    last_name: str = Form(...),
    phone: str = Form(...),
    email: str = Form(...),
):
    #  Save ticket in DB
    ticket = Ticket(
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        email=email,
    )
    session.add(ticket)
    session.commit()
    session.refresh(ticket)

    #  for Documint
    created_at = getattr(ticket, "created_at", datetime.utcnow())
    date_str = created_at.strftime("%m/%d/%Y")  # e.g. 11/29/2025
    ticket_id_str = str(ticket.id)

    #  Try generating Google Wallet URL
    wallet_url = None
    try:
        wallet_url = generate_wallet_save_url(
            ticket_id=ticket.id,
            name=f"{first_name} {last_name}",
            email=email,
        )
    except Exception as e:
        # just in the terminal 
        print("Google Wallet generation failed:", e)

    #  Generate PDF-- we have a true/ false condition in env to reduce documint use
    if DOCUMINT_LIVE:
        try:
            pdf_bytes = generate_ticket_pdf_via_documint(
                first_name=first_name,
                last_name=last_name,
                date=date_str,
                ticket_id=ticket_id_str,
            )
        except Exception as e:
            # printing error in terminal to not break the flow
            print("Documint live generation failed, falling back to fake PDF:", e)
            pdf_bytes = fake_generate_ticket_pdf(
                first_name=first_name,
                last_name=last_name,
                date=date_str,
                ticket_id=ticket_id_str,
            )
    else:
        pdf_bytes = fake_generate_ticket_pdf(
            first_name=first_name,
            last_name=last_name,
            date=date_str,
            ticket_id=ticket_id_str,
        )

    #  Save PDF on server
    filename = f"ticket_{ticket_id_str}.pdf"
    with open(filename, "wb") as f:
        f.write(pdf_bytes)

    #  The Email mail body 
    body_lines = [
        f"Hi {first_name},",
        "",
        "Thank you for your purchase! Attached is your Round of Golf ticket.",
    ]

    if wallet_url:
        body_lines.append("")
        body_lines.append("You can also save your ticket to Google Wallet using this link:")
        body_lines.append(wallet_url)

    body_lines.append("")
    body_lines.append("We look forward to seeing you !!!!")

    body_text = "\n".join(body_lines)

    #  Email the ticket to the user
    message = MessageSchema(
        subject="Your Paradise Golf Day Pass",
        recipients=[email],
        body=body_text,
        subtype="plain",
        attachments=[filename],  # path to the saved PDF
    )

    await fastmail.send_message(message)

    #  Render success page with Save to Wallet button
    success_msg = f"{email}"

    return templates.TemplateResponse(
        "buy_ticket.html",
        {
            "request": request,
            "success": success_msg,
            "wallet_url": wallet_url,
        },
    )
