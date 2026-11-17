"""
sap_api_client.py

Client for posting inspection results to SAP. In "mock" mode (default) it
returns a simulated response so the pipeline can run without an SAP system.
"""

import uuid
from typing import Any, Dict


class SAPApiClient:
    def __init__(self, base_url: str = "", api_key: str = "", mode: str = "mock", timeout: int = 15):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.mode = mode
        self.timeout = timeout

    def post_inspection_result(self, record: Dict[str, Any]) -> Dict[str, Any]:
        if self.mode == "mock":
            return {"status": "MOCK_ACCEPTED", "document_id": f"MOCK-{uuid.uuid4().hex[:10].upper()}",
                    "inspection_lot": record["InspectionLot"]}

        import requests  # imported only in live mode
        resp = requests.post(
            f"{self.base_url}/inspection-results",
            json=record,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            timeout=self.timeout,
        )
        resp.raise_for_status()
        return resp.json()
