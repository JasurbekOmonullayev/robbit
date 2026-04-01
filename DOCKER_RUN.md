# Docker orqali ishga tushirish

## 1) Bir martalik build
`docker compose build`

## 2) Background'da ishga tushirish
`docker compose up -d`

## 3) Loglarni ko'rish
`docker compose logs -f clickup-sync`

## 4) To'xtatish
`docker compose down`

## 5) Qo'lda test run (bir marta)
`docker compose run --rm clickup-sync python /app/sync_excel_to_clickup.py --source google --dry-run`

## Eslatma
- `secrets/forms-463112-ed41b17dee78.json` konteynerga read-only ulanadi.
- Local state fayli: `data/.sync_state.json`
- Interval: `SYNC_INTERVAL_SECONDS=7200` (2 soat)
