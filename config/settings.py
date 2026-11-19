import os
from pathlib import Path
from typing import Any, Dict, List
import yaml
from dotenv import load_dotenv

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

CONFIG_DIR = BASE_DIR / "config"
DATA_DIR = BASE_DIR / "data"
SAMPLE_INVOICES_DIR = DATA_DIR / "sample_invoices"
DB_PATH = Path(os.getenv("INVOICEIQ_DB_PATH", str(BASE_DIR / "invoiceiq.db")))

# Data file paths
VENDORS_CSV = DATA_DIR / "vendors.csv"
PURCHASE_ORDERS_CSV = DATA_DIR / "purchase_orders.csv"
PO_LINE_ITEMS_CSV = DATA_DIR / "po_line_items.csv"

# AI Provider Settings
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
AI_PROVIDER = os.getenv("AI_PROVIDER", "auto").lower()  # "gemini", "openai", "deterministic", "auto"

def load_rules() -> Dict[str, Any]:
    rules_path = CONFIG_DIR / "rules.yaml"
    if not rules_path.exists():
        return {
            "tolerances": {
                "amount_tolerance_percentage": 0.02,
                "amount_tolerance_cap": 500.0,
                "tax_tolerance_percentage": 0.01,
                "tax_tolerance_cap": 100.0,
                "line_item_price_tolerance_pct": 0.01,
            },
            "decision_policy": {
                "duplicate_action": "REJECTED",
                "unapproved_vendor_action": "REJECTED",
                "inactive_vendor_action": "REJECTED",
                "amount_mismatch_action": "PENDING REVIEW",
                "missing_fields_action": "PENDING REVIEW",
                "low_confidence_action": "PENDING REVIEW",
                "ambiguous_po_action": "PENDING REVIEW",
            },
            "mandatory_fields": [
                "invoice_number",
                "invoice_date",
                "vendor_name",
                "invoice_total",
            ],
            "currency": {"default_currency": "INR"},
            "ocr": {"min_text_length_threshold": 50, "confidence_warning_threshold": 0.70},
        }
    with open(rules_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

RULES = load_rules()
