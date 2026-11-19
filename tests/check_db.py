import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from database.repository import InvoiceRepository

repo = InvoiceRepository()
runs = repo.list_runs(limit=30)
print(f"Total historical runs in DB: {len(runs)}")
print(f"KPIs: {repo.get_kpis()}")
print("\nRecent 10 runs:")
for r in runs[:10]:
    print(f"- File: {r['filename']:<45} | Decision: {r['decision']:<15} | Reason: {r['reason_code']:<35} | Total: ₹{r['invoice_total']:>10,.2f} | Reviewer: {str(r.get('reviewer_decision'))}")
