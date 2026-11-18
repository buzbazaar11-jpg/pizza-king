"""80 mm thermal receipt PDF generator using ReportLab."""
from io import BytesIO

from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from app.core.config import settings


async def generate_receipt_pdf(order, items: list) -> bytes:
    line_count = len(items)
    page_height = max((90 + line_count * 7) * mm, 120 * mm)
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=(80 * mm, page_height))

    y = page_height - 8 * mm

    def line(text: str, right: str = "", bold: bool = False, size: int = 8):
        nonlocal y
        font = "Helvetica-Bold" if bold else "Helvetica"
        c.setFont(font, size)
        c.drawString(4 * mm, y, text)
        if right:
            c.drawRightString(76 * mm, y, right)
        y -= (size * 0.5 + 2) * mm

    def divider():
        nonlocal y
        c.setFont("Helvetica", 7)
        c.drawString(4 * mm, y, "-" * 44)
        y -= 4 * mm

    # Header
    line(settings.APP_NAME, bold=True, size=11)
    line("Fresh Fast Food & More", size=7)
    line("Tel: 03173712950", size=7)
    divider()

    # Order meta
    order_id = str(getattr(order, "id", "N/A"))[-8:].upper()
    order_type = str(getattr(order, "order_type", ""))
    table_no = getattr(order, "table_no", None) or getattr(order, "table_id", None)
    created_at = getattr(order, "created_at", None)
    date_str = created_at.strftime("%Y-%m-%d %H:%M") if created_at else "N/A"

    line(f"Order #: {order_id}", bold=True)
    line(f"Date   : {date_str}", size=7)
    line(f"Type   : {order_type.replace('_', ' ').title()}", size=7)
    if table_no:
        line(f"Table  : {table_no}", size=7)
    divider()

    # Items
    for item in items:
        name = str(getattr(item, "name", getattr(item, "title", "Item")))
        qty = int(getattr(item, "quantity", 1))
        price = float(getattr(item, "line_total", getattr(item, "subtotal", 0)))
        label = f"{qty} x {name[:28]}"
        line(label, f"Rs {price:,.0f}")

    divider()

    subtotal = float(getattr(order, "subtotal", 0))
    discount = float(getattr(order, "discount", getattr(order, "discount_amount", 0)))
    delivery = float(getattr(order, "delivery_fee", getattr(order, "delivery_charges", 0)))
    total = float(getattr(order, "total", 0))
    payment = str(getattr(order, "payment_method", "cash")).title()
    amount_paid = getattr(order, "amount_paid", None)
    change = getattr(order, "change_amount", None)

    line("Subtotal", f"Rs {subtotal:,.0f}")
    if discount > 0:
        line("Discount", f"- Rs {discount:,.0f}")
    line("Delivery", f"Rs {delivery:,.0f}")
    line("TOTAL", f"Rs {total:,.0f}", bold=True, size=10)
    divider()
    line(f"Payment : {payment}", size=7)
    if amount_paid is not None:
        line(f"Paid    : Rs {float(amount_paid):,.0f}", size=7)
    if change is not None:
        line(f"Change  : Rs {float(change):,.0f}", size=7)
    divider()

    line("Thank you for your order!", size=7)
    line("Please come again!", size=7)
    y -= 3 * mm
    c.setFont("Helvetica", 6)
    c.drawCentredString(40 * mm, y, settings.CREDIT)

    c.showPage()
    c.save()
    return buf.getvalue()
