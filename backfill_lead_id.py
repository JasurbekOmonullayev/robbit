import argparse
import os
from pathlib import Path
from typing import Any

from sync_excel_to_clickup import (
    ClickUpClient,
    GoogleSheetsReader,
    LEAD_COLUMN_NAME,
    TASK_NAME_COLUMN,
    canonical_lead_id,
    extract_spreadsheet_id,
    load_env_file,
    normalize_text,
    rows_to_records,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Backfill ClickUp Lead ID by matching phone + name from Google Sheets"
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Real update qiladi. Berilmasa dry-run rejimida ishlaydi.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Maksimal qancha taskga Lead ID yozilsin (0 = cheksiz).",
    )
    return parser.parse_args()


def digits_only(value: Any) -> str:
    return "".join(ch for ch in str(value or "") if ch.isdigit())


def normalize_phone(value: Any) -> str:
    d = digits_only(value)
    if not d:
        return ""
    # Uzbekistan raqamlari uchun oxirgi 9 xonani olish orqali bir xillash.
    if d.startswith("998") and len(d) >= 12:
        return d[-9:]
    if len(d) > 9:
        return d[-9:]
    return d


def normalize_name(value: Any) -> str:
    # Harf-raqamdan tashqari belgilarni olib tashlab case-insensitive solishtirish.
    return "".join(ch.lower() for ch in str(value or "").strip() if ch.isalnum())


def extract_phone_field_ids(field_meta: dict[str, dict[str, Any]]) -> list[str]:
    result: list[str] = []
    for field_id, meta in field_meta.items():
        name = normalize_text(meta.get("name")).lower()
        if "phone" in name or "telefon" in name:
            result.append(field_id)
    return result


def sheet_phone_index(lead_records: list[dict[str, Any]]) -> dict[str, list[dict[str, str]]]:
    idx: dict[str, list[dict[str, str]]] = {}
    for rec in lead_records:
        lead_id = canonical_lead_id(rec.get(LEAD_COLUMN_NAME))
        if not lead_id:
            continue
        name = normalize_name(rec.get(TASK_NAME_COLUMN))
        p1 = normalize_phone(rec.get("4. Bog'lanish uchun telefon raqamingizni yozing!"))
        p2 = normalize_phone(rec.get("5. Phone number"))
        for p in (p1, p2):
            if not p:
                continue
            idx.setdefault(p, []).append({"lead_id": lead_id, "name_norm": name})
    return idx


def task_custom_field_map(task: dict[str, Any]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for cf in task.get("custom_fields", []):
        field_id = normalize_text(cf.get("id"))
        if field_id:
            result[field_id] = cf.get("value")
    return result


def set_task_custom_field(client: ClickUpClient, task_id: str, field_id: str, value: str) -> None:
    url = f"https://api.clickup.com/api/v2/task/{task_id}/field/{field_id}"
    # faqat Lead ID field update qilinadi; status yoki boshqa fieldlarga tegilmaydi.
    client._request("POST", url, {"value": value})  # noqa: SLF001


def main() -> int:
    args = parse_args()
    load_env_file(Path(".env"))

    token = os.getenv("CLICKUP_API_TOKEN", "").strip()
    list_id = os.getenv("CLICKUP_LIST_ID", "").strip()
    lead_field_id = os.getenv("CLICKUP_LEAD_ID_FIELD_ID", "").strip()
    credentials_file = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "").strip()
    spreadsheet_raw = os.getenv("GOOGLE_SPREADSHEET_ID", "").strip() or os.getenv(
        "GOOGLE_SHEETS_URL", ""
    ).strip()
    leads_sheet_name = os.getenv("GOOGLE_LEADS_SHEET_NAME", "Leads").strip() or "Leads"

    if not token or not list_id or not lead_field_id or not credentials_file or not spreadsheet_raw:
        print("ERROR: .env ichida kerakli CLICKUP_* / GOOGLE_* konfiguratsiya to'liq emas")
        return 1

    spreadsheet_id = extract_spreadsheet_id(spreadsheet_raw)
    client = ClickUpClient(token=token)

    try:
        tasks = client.list_tasks(list_id)
        field_meta = client.list_fields(list_id)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: ClickUp ma'lumotlarini o'qishda xatolik: {exc}")
        return 1

    phone_field_ids = extract_phone_field_ids(field_meta)
    if not phone_field_ids:
        print("ERROR: ClickUp listda phone fieldlari topilmadi")
        return 1

    try:
        reader = GoogleSheetsReader(credentials_file=credentials_file, spreadsheet_id=spreadsheet_id)
        lead_records = rows_to_records(reader.read_sheet(leads_sheet_name))
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: Google Sheets o'qishda xatolik: {exc}")
        return 1

    p_index = sheet_phone_index(lead_records)

    missing_lead_tasks: list[dict[str, Any]] = []
    for task in tasks:
        cf_map = task_custom_field_map(task)
        if cf_map.get(lead_field_id) in (None, ""):
            missing_lead_tasks.append(task)

    updated = 0
    would_update = 0
    skipped_no_match = 0
    skipped_ambiguous = 0
    errors = 0
    processed_updates = 0

    for task in missing_lead_tasks:
        task_id = normalize_text(task.get("id"))
        task_name_norm = normalize_name(task.get("name"))
        cf_map = task_custom_field_map(task)

        phones = {normalize_phone(cf_map.get(fid)) for fid in phone_field_ids}
        phones = {p for p in phones if p}

        candidates: set[str] = set()
        for p in phones:
            for item in p_index.get(p, []):
                if item["name_norm"] and item["name_norm"] == task_name_norm:
                    candidates.add(item["lead_id"])

        if not candidates:
            skipped_no_match += 1
            continue
        if len(candidates) > 1:
            skipped_ambiguous += 1
            print(f"SKIP_AMBIGUOUS task_id={task_id} name={task.get('name')} candidates={sorted(candidates)}")
            continue

        lead_id = next(iter(candidates))

        if args.limit and processed_updates >= args.limit:
            break

        if not args.apply:
            would_update += 1
            print(f"DRY-RUN update task_id={task_id} name={task.get('name')} lead_id={lead_id}")
            processed_updates += 1
            continue

        try:
            set_task_custom_field(client, task_id=task_id, field_id=lead_field_id, value=lead_id)
            updated += 1
            processed_updates += 1
            print(f"UPDATED task_id={task_id} name={task.get('name')} lead_id={lead_id}")
        except Exception as exc:  # noqa: BLE001
            errors += 1
            print(f"ERROR update task_id={task_id}: {exc}")

    print("--- SUMMARY ---")
    print(f"tasks_total={len(tasks)}")
    print(f"tasks_missing_lead={len(missing_lead_tasks)}")
    print(f"would_update={would_update}")
    print(f"updated={updated}")
    print(f"skipped_no_match={skipped_no_match}")
    print(f"skipped_ambiguous={skipped_ambiguous}")
    print(f"errors={errors}")
    if not args.apply:
        print("mode=dry-run")
    else:
        print("mode=apply")

    return 0 if errors == 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
