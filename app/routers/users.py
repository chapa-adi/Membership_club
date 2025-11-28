from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.database import get_session
from app.models import User
from app.auth import verify_password, hash_password

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


# ---------- Used to create a test user (atleast one if we have none) ----------
@router.get("/create-test-user")
def create_test_user(session: Session = Depends(get_session)):
    existing = session.exec(
        select(User).where(User.email == "aditichapagain@usf.edu")
    ).first()
    if existing:
        return {"message": "Test user already exists"}

    user = User(
        email="aditichapagain@usf.edu",
        password_hash=hash_password("test123"),
        role="member",
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message": "User created", "email": user.email, "password": "test123"}


# ---------- GET: show login page ----------
@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, error: str | None = None):
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": error}
    )


# ---------- POST: handle login form ----------
@router.post("/login", response_class=HTMLResponse)
def login_submit(
    request: Request,
    session: Session = Depends(get_session),
    email: str = Form(...),
    password: str = Form(...),
):
    user = session.exec(select(User).where(User.email == email)).first()

    if not user:
        # if Email not found  we show error on login page
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Email not found"},
            status_code=400,
        )

    if not verify_password(password, user.password_hash):
        # Wrong password we show error on login page
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Wrong password"},
            status_code=400,
        )

    # If we sucessfully login then go to the buy_ticket page
    return RedirectResponse(url="/buy-ticket", status_code=303)
