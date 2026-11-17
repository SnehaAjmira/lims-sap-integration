import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
TMP = tempfile.mkdtemp()
os.environ["AUDIT_LOG_PATH"] = os.path.join(TMP, "audit.jsonl")

from fastapi.testclient import TestClient  # noqa: E402

from audit_logger import log_event, verify_chain  # noqa: E402
from data_transformer import TransformError, transform_lims_to_sap  # noqa: E402
from webhook_listener import app  # noqa: E402

EVENT = json.loads((ROOT / "examples" / "sample_event.json").read_text())


class TestTransformer(unittest.TestCase):
    def test_maps_fields(self):
        r = transform_lims_to_sap(EVENT)
        self.assertEqual((r["ResultValue"], r["ResultUnit"], r["Valuation"], r["InspectionDate"]),
                         (4.21, "G/L", "A", "20260302"))

    def test_unit_conversion(self):
        r = transform_lims_to_sap({**EVENT, "test_result": 250, "unit": "mg/L"})
        self.assertEqual(r["ResultValue"], 0.25)

    def test_rejects_non_final_status(self):
        with self.assertRaises(TransformError):
            transform_lims_to_sap({**EVENT, "status": "PENDING"})

    def test_rejects_missing_fields(self):
        with self.assertRaisesRegex(TransformError, "inspection_lot"):
            transform_lims_to_sap({**EVENT, "inspection_lot": ""})


class TestAuditLog(unittest.TestCase):
    def test_tamper_detected(self):
        path = os.path.join(TMP, "chain.jsonl")
        for i in range(3):
            log_event(path, "TEST", f"S-{i}")
        self.assertTrue(verify_chain(path))
        lines = Path(path).read_text().splitlines()
        lines[1] = lines[1].replace("S-1", "S-9")
        Path(path).write_text("\n".join(lines) + "\n")
        self.assertFalse(verify_chain(path))


class TestWebhook(unittest.TestCase):
    client = TestClient(app)

    def test_success(self):
        resp = self.client.post("/webhook/lims-result", json=EVENT)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["sap_response"]["status"], "MOCK_ACCEPTED")

    def test_rejection_is_logged(self):
        resp = self.client.post("/webhook/lims-result", json={**EVENT, "unit": "ppb"})
        self.assertEqual(resp.status_code, 422)
        self.assertTrue(verify_chain(os.environ["AUDIT_LOG_PATH"]))


if __name__ == "__main__":
    unittest.main()
