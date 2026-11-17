
from src.reconciler import reconcile_documents


def create_document(delivery_date):
    """Create fictional document text for testing."""

    return f"""
    Supplier Northstar Office Supplies
    GSTIN: 29ABCDE1234F1Z5

    Bill to / Ship to BrightPath Learning Services
    42 Residency Road

    Expected delivery: {delivery_date}
    Supplier Northstar Office Supplies

    Subtotal INR 8600.00
    GST (18%) INR 1548.00
    Purchase order total INR 10148.00

    NS-101 A4 copier paper (ream) 20 250.00 5000.00
    NS-205 Ballpoint pens (box of 50) 10 180.00 1800.00
    NS-310 Desk file folders (pack of 10) 15 120.00 1800.00
    """


def test_all_fields_match():
    """Check that identical documents produce 20 matches."""

    po_text = create_document("20 November 2026")
    invoice_text = create_document("20 November 2026")

    results = reconcile_documents(po_text, invoice_text)

    assert len(results) == 20
    assert all(item["status"] == "MATCH" for item in results)


def test_delivery_date_mismatch():
    """Check that a different delivery date is detected."""

    po_text = create_document("20 November 2026")
    invoice_text = create_document("27 November 2026")

    results = reconcile_documents(po_text, invoice_text)

    mismatches = [
        item for item in results
        if item["status"] == "MISMATCH"
    ]

    assert len(mismatches) == 1
    assert mismatches[0]["field"] == "Expected delivery date"
    assert mismatches[0]["purchase_order"] == "20 November 2026"
    assert mismatches[0]["invoice"] == "27 November 2026"


def test_missing_product_is_detected():
    """Check that a product missing from the invoice is flagged."""

    po_text = create_document("20 November 2026")

    invoice_text = create_document("20 November 2026")

    invoice_text = invoice_text.replace(
        "NS-310 Desk file folders (pack of 10) 15 120.00 1800.00",
        ""
    )

    results = reconcile_documents(po_text, invoice_text)

    mismatches = [
        item for item in results
        if item["status"] == "MISMATCH"
    ]

    assert any(
        item["field"] == "Product NS-310"
        for item in mismatches
    )
