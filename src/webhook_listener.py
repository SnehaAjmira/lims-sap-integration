"""
webhook_listener.py
-------------------
FastAPI webhook listener that receives LIMS events and triggers SAP integration.
Compliant with FDA 21 CFR Part 11 audit trail requirements.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import logging
import json
from datetime import datetime

from data_transformer import transform_lims_to_sap
from sap_api_client import SAPApiClient
from audit_logger import log_event
from config import settings

app = FastAPI(title="LIMS-SAP Integration Webhook Listener")
logger = logging.getLogger(__name__)
sap_client = SAPApiClient(base_url=settings.SAP_BASE_URL, api_key=settings.SAP_API_KEY)


@app.post("/webhook/lims-event")
async def receive_lims_event(request: Request):
      """
          Receives incoming webhook events from LIMS.
              Validates payload, transforms data, and pushes to SAP ERP.
                  """
      try:
                payload = await request.json()
                event_type = payload.get("event_type")
                sample_id = payload.get("sample_id")

          logger.info(f"[{datetime.utcnow()}] Received LIMS event: {event_type} for sample {sample_id}")
        log_event(event_type="WEBHOOK_RECEIVED", sample_id=sample_id, payload=payload)

        # Transform LIMS payload to SAP schema
        sap_payload = transform_lims_to_sap(payload)

        # Push to SAP
        response = sap_client.post_inspection_result(sap_payload)

        log_event(event_type="SAP_PUSH_SUCCESS", sample_id=sample_id, response=response)
        return JSONResponse({"status": "success", "sap_response": response}, status_code=200)

except KeyError as e:
        logger.error(f"Missing required field: {e}")
        raise HTTPException(status_code=400, detail=f"Missing field: {e}")
except Exception as e:
        logger.error(f"Integration error: {e}")
        log_event(event_type="INTEGRATION_ERROR", sample_id=None, error=str(e))
        raise HTTPException(status_code=500, detail="Internal integration error")


@app.get("/health")
async def health_check():
      return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


if __name__ == "__main__":
      import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
