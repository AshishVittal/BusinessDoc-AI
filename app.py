
import streamlit as st
import pandas as pd

from src.pdf_extractor import extract_text
from src.reconciler import reconcile_documents
from src.bedrock_explainer import explain_discrepancies
from src.report_generator import generate_report


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="BusinessDoc AI",
    page_icon="📄",
    layout="wide"
)


# --------------------------------------------------
# INITIALIZE SESSION STATE
# --------------------------------------------------

if "results" not in st.session_state:
    st.session_state.results = None

if "mismatches" not in st.session_state:
    st.session_state.mismatches = []

if "explanation" not in st.session_state:
    st.session_state.explanation = None


# --------------------------------------------------
# APPLICATION HEADER
# --------------------------------------------------

st.title("📄 BusinessDoc AI")

st.subheader(
    "AI-powered Invoice & Purchase Order Reconciliation"
)

st.write(
    "Upload an invoice and its corresponding purchase order "
    "to identify discrepancies automatically."
)

st.divider()


# --------------------------------------------------
# PDF UPLOAD SECTION
# --------------------------------------------------

col1, col2 = st.columns(2)

with col1:

    st.markdown("### 🧾 Invoice")

    invoice_file = st.file_uploader(
        "Upload Invoice PDF",
        type=["pdf"],
        key="invoice"
    )


with col2:

    st.markdown("### 📋 Purchase Order")

    po_file = st.file_uploader(
        "Upload Purchase Order PDF",
        type=["pdf"],
        key="purchase_order"
    )


st.divider()


# --------------------------------------------------
# START RECONCILIATION
# --------------------------------------------------

if st.button("Start Reconciliation", type="primary"):

    # Reset previous results

    st.session_state.results = None
    st.session_state.mismatches = []
    st.session_state.explanation = None

    if invoice_file is None or po_file is None:

        st.warning(
            "Please upload both documents first."
        )

    else:

        try:

            with st.spinner(
                "Extracting and comparing documents..."
            ):

                # Extract invoice text

                invoice_text = extract_text(
                    invoice_file.getvalue()
                )

                # Extract purchase order text

                po_text = extract_text(
                    po_file.getvalue()
                )

                # Reconcile documents

                results = reconcile_documents(
                    po_text,
                    invoice_text
                )

                # Identify discrepancies

                mismatches = [
                    item for item in results
                    if item["status"] == "MISMATCH"
                ]

                # Save results in session state

                st.session_state.results = results
                st.session_state.mismatches = mismatches

            st.success(
                "Reconciliation completed successfully!"
            )

        except Exception as error:

            st.error(
                f"Reconciliation failed: {error}"
            )


# --------------------------------------------------
# DISPLAY RECONCILIATION RESULTS
# --------------------------------------------------

if st.session_state.results is not None:

    results = st.session_state.results

    mismatches = st.session_state.mismatches

    # Calculate statistics

    matches = sum(
        1 for item in results
        if item["status"] == "MATCH"
    )

    # Summary

    st.header("Reconciliation Results")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Checks",
        len(results)
    )

    col2.metric(
        "Matches",
        matches
    )

    col3.metric(
        "Discrepancies",
        len(mismatches)
    )

    # Overall status

    if mismatches:

        st.warning(
            f"{len(mismatches)} discrepancy(s) found. "
            "Human review required."
        )

    else:

        st.success(
            "All checked fields match."
        )


    # --------------------------------------------------
    # DETAILED COMPARISON
    # --------------------------------------------------

    st.subheader("Detailed Comparison")

    df = pd.DataFrame(results)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )


    # --------------------------------------------------
    # ISSUES REQUIRING ATTENTION
    # --------------------------------------------------

    if mismatches:

        st.subheader(
            "Issues Requiring Attention"
        )

        for item in mismatches:

            st.error(
                f"**{item['field']}**\n\n"
                f"Purchase Order: {item['purchase_order']}\n\n"
                f"Invoice: {item['invoice']}"
            )


        # --------------------------------------------------
        # AI-POWERED EXPLANATION
        # --------------------------------------------------

        st.divider()

        st.subheader(
            "AI-Powered Explanation"
        )

        if st.button("Generate AI Explanation"):

            try:

                with st.spinner(
                    "Amazon Nova is analysing the discrepancy..."
                ):

                    explanation = explain_discrepancies(
                        mismatches
                    )

                st.session_state.explanation = explanation

            except Exception as error:

                st.error(
                    f"AI explanation failed: {error}"
                )


        # Display saved AI explanation

        if st.session_state.explanation:

            st.success(
                "AI explanation generated!"
            )

            st.write(
                st.session_state.explanation
            )


    # --------------------------------------------------
    # DOWNLOAD RECONCILIATION REPORT
    # --------------------------------------------------

    st.divider()

    st.subheader(
        "Download Reconciliation Report"
    )

    try:

        report = generate_report(
            results,
            st.session_state.explanation
        )

        st.download_button(
            label="📥 Download PDF Report",
            data=report,
            file_name="BusinessDoc_AI_Reconciliation_Report.pdf",
            mime="application/pdf"
        )

    except Exception as error:

        st.error(
            f"Report generation failed: {error}"
        )
