# Run yo'riqnoma (Google Sheets -> ClickUp)

## 1) Kutubxonalar
pip install openpyxl google-api-python-client google-auth

## 2) `.env` sozlamasi
Quyidagilar bo'lishi kerak:
- CLICKUP_API_TOKEN
- CLICKUP_LIST_ID
- CLICKUP_LEAD_ID_FIELD_ID
- GOOGLE_SERVICE_ACCOUNT_FILE
- GOOGLE_SPREADSHEET_ID
- GOOGLE_LEADS_SHEET_NAME=Leads
- GOOGLE_MAPPING_SHEET_NAME=columns

## 3) Dry-run (tavsiya)
python .\sync_excel_to_clickup.py --source google --dry-run

## 4) Real sync
python .\sync_excel_to_clickup.py --source google

## 5) Scheduler
`setup_scheduler.ps1` taskni har 2 soatda ishga tushiradi.
