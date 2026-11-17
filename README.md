# LIMS-to-SAP Integration Service

An event-driven service that receives approved test results from a Laboratory Information Management System (LIMS), maps them to SAP Quality Management inspection results, posts them to SAP, and records every step in a tamper-evident audit log.

| | |
|---|---|
| **Domain** | Laboratory systems integration, quality management, regulated (GxP) environments |
| **Tools** | Python 3, FastAPI, pytest-compatible unittest |
| **Techniques** | Webhooks, REST, field mapping and unit conversion, hash-chained audit trail, mock-first testing |
| **Contents** | 5 modules, sample event, 7 passing tests |

---

## 1. Flow

```
LIMS result approved
    -> POST /webhook/lims-result        (optional shared-secret header)
    -> audit: WEBHOOK_RECEIVED
    -> data_transformer: validate, map, convert units
         -> on failure: audit TRANSFORM_REJECTED, return 422
    -> sap_api_client: post inspection result (mock or live)
         -> on failure: audit SAP_POST_FAILED, return 502
    -> audit: SAP_POST_SUCCESS, return 200
```

## 2. Field Mapping

| LIMS field | SAP QM field | Rule |
|---|---|---|
| `inspection_lot` | `InspectionLot` | Required |
| `characteristic` | `InspectionCharacteristic` | Required |
| `sample_id` | `Batch` | Required |
| `test_result`, `unit` | `ResultValue`, `ResultUnit` | Converted to SAP base unit (for example mg/L to G/L) |
| `status` | `Valuation` | APPROVED to A, REJECTED to R. Non-final results are not posted. |
| `analyst_id` | `InspectorUser` | Upper case, 12 characters max |
| `test_date` | `InspectionDate` | YYYYMMDD |

## 3. Design Decisions

| Decision | Reason |
|---|---|
| Only final results (APPROVED or REJECTED) are posted | Prevents in-progress data from reaching the ERP |
| Rejections return 422 with a specific reason | LIMS administrators can correct and resend without log digging |
| Audit entries are hash-chained | Any edit or deletion of an entry is detectable with `verify_chain()` (supports 21 CFR 11.10(e)) |
| SAP client defaults to mock mode | The full pipeline runs and is testable without SAP access |

## 4. How to Run

```bash
pip install -r requirements.txt

# Tests
python -m unittest discover -s tests -v

# Local service (mock SAP)
uvicorn webhook_listener:app --app-dir src --port 8000
curl -X POST localhost:8000/webhook/lims-result -H "Content-Type: application/json" -d @examples/sample_event.json
```

Environment variables (`src/config.py`): `SAP_MODE` (mock or live), `SAP_BASE_URL`, `SAP_API_KEY`, `WEBHOOK_SECRET`, `AUDIT_LOG_PATH`.

## 5. Repository Structure

```
lims-sap-integration/
├── src/
│   ├── webhook_listener.py   # FastAPI endpoints
│   ├── data_transformer.py   # LIMS to SAP mapping rules
│   ├── sap_api_client.py     # SAP client (mock and live)
│   ├── audit_logger.py       # Hash-chained JSONL audit log
│   └── config.py             # Environment settings
├── examples/sample_event.json
├── tests/test_pipeline.py
└── requirements.txt
```

## 6. Scope

SAP endpoint paths and field names follow SAP QM conventions but are simplified. A production deployment needs the customer's actual SAP API (OData or RFC), OAuth, retry queueing, and validation under the site's quality system.

Author: [Sneha Ajmira](https://linkedin.com/in/contactsnehaajmira)
