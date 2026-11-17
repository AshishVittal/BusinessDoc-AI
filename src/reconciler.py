
import re


def extract_value(pattern, text, field_name):
    """Extract a value using a regular expression."""

    match = re.search(pattern, text, re.IGNORECASE)

    if not match:
        raise ValueError(
            f"Could not find {field_name} in document."
        )

    return match.group(1).strip()


def parse_document(text):
    """Extract structured information from PDF text."""

    text = re.sub(r"\s+", " ", text).strip()

    data = {}

    # Basic document information
    data["supplier"] = extract_value(
        r"Supplier\s+(.+?)\s+GSTIN:",
        text,
        "supplier"
    )

    data["gstin"] = extract_value(
        r"GSTIN:\s*([A-Z0-9]+)",
        text,
        "GSTIN"
    )

    data["buyer"] = extract_value(
        r"Bill to\s*/\s*Ship to\s+(.+?)\s+\d{1,3}\s+Residency Road",
        text,
        "buyer"
    )

    data["delivery_date"] = extract_value(
        r"Expected delivery:\s*(.+?)\s+Supplier",
        text,
        "expected delivery date"
    )

    # Financial information
    data["subtotal"] = float(
        extract_value(
            r"Subtotal\s+INR\s+([\d,]+\.\d{2})",
            text,
            "subtotal"
        ).replace(",", "")
    )

    data["gst_amount"] = float(
        extract_value(
            r"GST\s*\(\d+%\)\s*INR\s+([\d,]+\.\d{2})",
            text,
            "GST amount"
        ).replace(",", "")
    )

    data["gst_rate"] = int(
        extract_value(
            r"GST\s*\((\d+)%\)",
            text,
            "GST rate"
        )
    )

    data["total"] = float(
        extract_value(
            r"(?:Purchase order|Invoice) total\s+INR\s+([\d,]+\.\d{2})",
            text,
            "document total"
        ).replace(",", "")
    )

    # Extract product line items
    item_pattern = (
        r"(NS-\d+)\s+(.+?)\s+"
        r"(\d+)\s+([\d,]+\.\d{2})\s+([\d,]+\.\d{2})"
    )

    data["items"] = []

    for match in re.finditer(item_pattern, text):
        data["items"].append({
            "code": match.group(1),
            "description": match.group(2).strip(),
            "quantity": int(match.group(3)),
            "unit_price": float(
                match.group(4).replace(",", "")
            ),
            "line_total": float(
                match.group(5).replace(",", "")
            )
        })

    if not data["items"]:
        raise ValueError(
            "No product line items found."
        )

    return data


def reconcile_documents(po_text, invoice_text):
    """Compare purchase order and invoice information."""

    po = parse_document(po_text)
    invoice = parse_document(invoice_text)

    results = []

    def add_check(name, po_value, invoice_value):
        results.append({
            "field": name,
            "purchase_order": po_value,
            "invoice": invoice_value,
            "status": (
                "MATCH"
                if po_value == invoice_value
                else "MISMATCH"
            )
        })

    # Compare basic document information
    for field in ["supplier", "gstin", "buyer"]:
        add_check(
            field.replace("_", " ").title(),
            po[field],
            invoice[field]
        )

    # Compare delivery dates
    add_check(
        "Expected delivery date",
        po["delivery_date"],
        invoice["delivery_date"]
    )

    # Compare financial information
    for field in ["subtotal", "gst_rate", "gst_amount", "total"]:
        add_check(
            field.replace("_", " ").title(),
            po[field],
            invoice[field]
        )

    # Compare product line items
    po_items = {
        item["code"]: item for item in po["items"]
    }

    invoice_items = {
        item["code"]: item for item in invoice["items"]
    }

    for code in sorted(set(po_items) | set(invoice_items)):
        po_item = po_items.get(code)
        invoice_item = invoice_items.get(code)

        if po_item is None or invoice_item is None:
            results.append({
                "field": f"Product {code}",
                "purchase_order": (
                    "Present" if po_item else "Missing"
                ),
                "invoice": (
                    "Present" if invoice_item else "Missing"
                ),
                "status": "MISMATCH"
            })
            continue

        for field in [
            "description",
            "quantity",
            "unit_price",
            "line_total"
        ]:
            add_check(
                f"{code} - {field.replace('_', ' ').title()}",
                po_item[field],
                invoice_item[field]
            )

    return results
