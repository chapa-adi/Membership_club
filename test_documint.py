from app.utils.documint import generate_ticket_pdf_via_documint


def main():
    pdf_bytes = generate_ticket_pdf_via_documint(
        first_name="Aditi",
        last_name="Chapagain",
        date="11/29/2025",      # same format you used in cURL
        ticket_id="TEST-12345",
    )

    with open("test_ticket.pdf", "wb") as f:
        f.write(pdf_bytes)

    print("✅ Saved test_ticket.pdf in this folder. Open it and check!")


if __name__ == "__main__":
    main()
