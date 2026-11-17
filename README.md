# BusinessDoc AI
### AI-Powered Invoice and Purchase Order Reconciliation

BusinessDoc AI is a Python-based application that automates the comparison of invoices and purchase orders using document processing, rule-based validation, and AI-powered explanations.

## Problem Statement

Businesses regularly process invoices against purchase orders. Manually checking supplier information, GST details, delivery dates, quantities, prices, and totals can be time-consuming and prone to human error.

BusinessDoc AI helps simplify this process by automatically identifying discrepancies and presenting them for human review.

## Key Features

- Upload invoice and purchase order PDF documents.
- Extract document text using PyMuPDF.
- Compare supplier, GSTIN, buyer, delivery dates, financial information, and product line items.
- Detect missing products and mismatched values.
- Generate AI-powered explanations using Amazon Bedrock and Nova 2 Lite.
- Download a professional PDF reconciliation report.
- Run automated tests using pytest.
- Containerize the application using Docker.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Application development |
| Streamlit | Web interface |
| PyMuPDF | PDF text extraction |
| Amazon Bedrock | AI-powered discrepancy explanations |
| Amazon Nova 2 Lite | Foundation model |
| Boto3 | AWS SDK for Python |
| ReportLab | PDF report generation |
| Pandas | Tabular results |
| Pytest | Automated testing |
| Docker | Application containerization |

## Architecture and Workflow

1. User uploads an invoice and purchase order.
2. PyMuPDF extracts text from both PDFs.
3. Python reconciliation logic extracts and compares document fields.
4. Discrepancies are identified using deterministic validation rules.
5. Amazon Bedrock generates explanations for detected discrepancies.
6. Streamlit displays the results.
7. ReportLab generates a downloadable PDF report.

**Important:** Python validation rules determine whether values match. The AI model only explains discrepancies; it does not approve or reject payments.

## Project Structure

```text
BusinessDoc-AI/
│
├── app.py
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── .gitignore
├── README.md
│
├── src/
│   ├── __init__.py
│   ├── pdf_extractor.py
│   ├── reconciler.py
│   ├── bedrock_explainer.py
│   └── report_generator.py
│
└── tests/
    └── test_reconciler.py
```

## Local Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd BusinessDoc-AI
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the environment

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure AWS credentials

Configure AWS credentials using the AWS CLI or another secure AWS credential provider.

Create a `.env` file in the project root:

```env
AWS_REGION=ap-south-1
BEDROCK_MODEL_ID=global.amazon.nova-2-lite-v1:0
```

Ensure your AWS account has the necessary Amazon Bedrock model access and permissions.

Never upload AWS credentials or `.env` files to GitHub.

### 6. Run the application

```bash
streamlit run app.py
```

## Running Tests

```bash
python -m pytest -v
```

The current automated test suite covers:

- Matching documents.
- Delivery date mismatches.
- Missing product detection.

## Docker

A Dockerfile is included to package the application.

Build:

```bash
docker build -t businessdoc-ai .
```

Run:

```bash
docker run -p 8501:8501 businessdoc-ai
```

AWS credentials must be configured securely for the container when using Bedrock. Never bake credentials into the Docker image.

## Limitations

- Designed primarily for the current sample document format.
- PDF text extraction does not currently perform OCR on scanned documents.
- Additional document formats and more complex invoice layouts require further parsing support.
- AI explanations depend on Amazon Bedrock availability and AWS permissions.
- Human review remains necessary before financial decisions.

## Future Improvements

- OCR support for scanned documents.
- Support for multiple invoice and purchase order formats.
- Improved validation and exception handling.
- AWS cloud deployment.
- Monitoring, logging, and audit trails.
- Expanded automated test coverage.

## Disclaimer

This project is a portfolio demonstration using fictional sample business documents. It is not a payment approval system. All flagged discrepancies require human review.