import os
from pathlib import Path

# Use isolated test database for all pytest executions
test_db = Path(__file__).resolve().parent / "test_invoiceiq.db"
os.environ["INVOICEIQ_DB_PATH"] = str(test_db)

import config.settings
config.settings.DB_PATH = test_db
