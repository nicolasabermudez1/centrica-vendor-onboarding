"""
Generate a blank, Centrica-branded PDF template on demand.
Used by the pre-qual tab so vendors can download a blank form, fill it,
sign it, and re-upload it for ARIA to mock-process.
"""

import io


def generate_blank_form(form_name: str, description: str = "", reference: str = "") -> bytes:
    """Return a one-page A4 Centrica-branded blank-form PDF as bytes."""
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib.utils import simpleSplit

    NAVY = (0.06, 0.13, 0.40)   # #0F2067
    MINT = (0.52, 0.86, 0.61)   # #85DB9C
    GREY_TEXT = (0.32, 0.32, 0.32)
    LIGHT_GREY = (0.78, 0.78, 0.78)

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    width, height = A4

    # ── Header band ─────────────────────────────────────────────────────────
    c.setFillColorRGB(*NAVY)
    c.rect(0, height - 32 * mm, width, 32 * mm, fill=1, stroke=0)
    # Mint accent stripe
    c.setFillColorRGB(*MINT)
    c.rect(0, height - 34 * mm, width, 2 * mm, fill=1, stroke=0)

    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(20 * mm, height - 18 * mm, "Centrica plc")
    c.setFillColorRGB(*MINT)
    c.setFont("Helvetica", 9)
    c.drawString(20 * mm, height - 25 * mm,
                 "Procurement Transformation · Supplier Pre-Qualification")

    # Reference (top-right)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica", 8)
    ref = reference or f"PQ-{form_name[:3].upper()}-BLANK"
    c.drawRightString(width - 20 * mm, height - 18 * mm, f"Ref: {ref}")
    c.drawRightString(width - 20 * mm, height - 23 * mm, "Form revision: 2026.1")
    c.drawRightString(width - 20 * mm, height - 28 * mm, "Classification: Confidential")

    # ── Form title ──────────────────────────────────────────────────────────
    c.setFillColorRGB(*NAVY)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(20 * mm, height - 52 * mm, form_name)

    # Description
    if description:
        c.setFillColorRGB(*GREY_TEXT)
        c.setFont("Helvetica", 10)
        lines = simpleSplit(description, "Helvetica", 10, width - 40 * mm)
        for i, line in enumerate(lines[:3]):
            c.drawString(20 * mm, height - 62 * mm - i * 5 * mm, line)

    # ── Vendor information block ─────────────────────────────────────────────
    y = height - 88 * mm
    c.setFillColorRGB(*NAVY)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(20 * mm, y, "1.  VENDOR INFORMATION")
    y -= 8 * mm
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 10)

    vendor_fields = [
        "Company name",
        "Companies House / Registration number",
        "Registered address",
        "Primary contact name",
        "Primary contact email",
        "Authorised signatory name",
        "Authorised signatory position / title",
    ]
    for field in vendor_fields:
        c.drawString(20 * mm, y, f"{field}:")
        c.setStrokeColorRGB(*LIGHT_GREY)
        c.line(85 * mm, y - 1 * mm, width - 20 * mm, y - 1 * mm)
        y -= 10 * mm

    # ── Form content placeholder ────────────────────────────────────────────
    y -= 4 * mm
    c.setFillColorRGB(*NAVY)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(20 * mm, y, "2.  DECLARATION / FORM CONTENT")
    y -= 8 * mm
    c.setStrokeColorRGB(*LIGHT_GREY)
    box_height = 55 * mm
    c.rect(20 * mm, y - box_height, width - 40 * mm, box_height, fill=0, stroke=1)
    c.setFillColorRGB(0.65, 0.65, 0.65)
    c.setFont("Helvetica-Oblique", 9)
    c.drawString(22 * mm, y - 8 * mm,
                 "[ Blank template provided for demonstration purposes.")
    c.drawString(22 * mm, y - 13 * mm,
                 "  Vendor to complete with policy text, certificate details,")
    c.drawString(22 * mm, y - 18 * mm,
                 "  reference numbers and any required supporting statements. ]")

    y -= box_height + 10 * mm

    # ── Signature block ─────────────────────────────────────────────────────
    c.setFillColorRGB(*NAVY)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(20 * mm, y, "3.  AUTHORISED SIGNATURE")
    y -= 15 * mm
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 10)
    c.drawString(20 * mm, y, "Signed:")
    c.setStrokeColorRGB(*LIGHT_GREY)
    c.line(35 * mm, y - 1 * mm, 105 * mm, y - 1 * mm)
    c.drawString(115 * mm, y, "Date:")
    c.line(128 * mm, y - 1 * mm, width - 20 * mm, y - 1 * mm)

    y -= 10 * mm
    c.drawString(20 * mm, y, "Print name:")
    c.line(42 * mm, y - 1 * mm, 105 * mm, y - 1 * mm)
    c.drawString(115 * mm, y, "Position:")
    c.line(133 * mm, y - 1 * mm, width - 20 * mm, y - 1 * mm)

    # ── Footer ───────────────────────────────────────────────────────────────
    c.setFillColorRGB(*NAVY)
    c.rect(0, 0, width, 12 * mm, fill=1, stroke=0)
    c.setFillColorRGB(*MINT)
    c.rect(0, 12 * mm, width, 1 * mm, fill=1, stroke=0)
    c.setFillColorRGB(1, 1, 1)
    c.setFont("Helvetica", 7)
    c.drawString(20 * mm, 5 * mm,
                 "Centrica plc · Registered in England & Wales 03033654 · "
                 "Confidential · For supplier pre-qualification use only")
    c.drawRightString(width - 20 * mm, 5 * mm, "Page 1 of 1")

    c.showPage()
    c.save()
    return buf.getvalue()
