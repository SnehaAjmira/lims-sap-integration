"""
webhook_listener.py

FastAPI service that receives LIMS result events, transforms them, posts them
to SAP, and writes every step to a hash-chained audit log.

Run locally (mock SAP):
    uvicorn webhook_listener:app --app-dir src --port 8000
"""

import logging

from fastapi import FastAPI, Header, HTTPException, Request

from audit_logger import log_event
from config import settings
from data_transformer import TransformError, transform_lims_to_sap
from sap_api_client import SAPApiClient

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger("lims-sap")

app = FastAPI(title="LIMS to SAP Integration")
sap_client = SAPApiClient(settings.SAP_BASE_URL, settings.SAP_API_KEY, settings.SAP_MODE)


@app.post("/webhook/lims-result")
async def receive_lims_result(request: Request, x_webhook_secret: str = Header(default="")):
    if settings.WEBHOOK_SECRET and x_webhook_secret != settings.WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="invalid webhook secret")

    event = await request.json()
    sample_id = event.get("sample_id")
    audit = settings.AUDIT_LOG_PATH
    log_event(audit, "WEBHOOK_RECEIVED", sample_id, payload=event)

    try:
        record = transform_lims_to_sap(event)
    except TransformError as exc:
        log_event(audit, "TRANSFORM_REJECTED", sample_id, reason=str(exc))
        raise HTTPException(status_code=422, detail=str(exc))

    try:
        response = sap_client.post_inspection_result(record)
    except Exception as exc:  # network or SAP-side failure
        log_event(audit, "SAP_POST_FAILED", sample_id, error=str(exc))
        raise HTTPException(status_code=502, detail="SAP post failed; event logged for retry")

    log_event(audit, "SAP_POST_SUCCESS", sample_id, sap_record=record, sap_response=response)
    logger.info("Posted %s to SAP lot %s", sample_id, record["InspectionLot"])
    return {"status": "posted", "sap_record": record, "sap_response": response}


@app.get("/health")
async def health():
    return {"status": "ok", "sap_mode": settings.SAP_MODE}
