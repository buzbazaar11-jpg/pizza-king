from io import BytesIO
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from app.models import Order


def receipt_pdf(order: Order, brand: str = "The Young Malang") -> bytes:
    lines = len(order.items)
    h = (90 + lines * 6) * mm
    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=(80 * mm, h))
    y = h - 10 * mm
    def row(text: str, right: str = "", bold: bool = False):
        nonlocal y
        c.setFont("Helvetica-Bold" if bold else "Helvetica", 8)
        c.drawString(5 * mm, y, text)
        if right:
            c.drawRightString(75 * mm, y, right)
        y -= 5 * mm
    row(brand, bold=True)
    row(f"Order #{order.order_number}  ({order.order_type})")
    row(order.created_at.strftime("%Y-%m-%d %H:%M"))
    row(f"{order.customer_name}  {order.customer_phone}")
    row("-" * 48)
    for it in order.items:
        row(f"{it.quantity} x {it.name}"[:34], f"{float(it.line_total):.0f}")
    row("-" * 48)
    row("Subtotal", f"{float(order.subtotal):.0f}")
    row("Delivery", f"{float(order.delivery_fee):.0f}")
    row("Discount", f"-{float(order.discount):.0f}")
    row("TOTAL (Rs)", f"{float(order.total):.0f}", bold=True)
    row("")
    row("Software Developed by AM Enterprises")
    c.showPage()
    c.save()
    return buf.getvalue()
