"""
data_transformer.py

Maps a LIMS result event to an SAP QM inspection result record.
Handles required-field checks, status mapping, unit conversion, and date formats.
"""

from datetime import datetime
from typing import Any, Dict

REQUIRED_FIELDS = ("sample_id", "inspection_lot", "characteristic", "test_result",
                   "unit", "status", "analyst_id", "test_date")

# LIMS result status -> SAP valuation code (A = accepted, R = rejected)
STATUS_MAP = {"APPROVED": "A", "REJECTED": "R"}

# Factors to convert each LIMS unit to the SAP base unit for that dimension
TO_SAP_UNIT = {
    "g/L": ("G/L", 1.0),
    "mg/L": ("G/L", 0.001),
    "mg/mL": ("G/L", 1.0),
    "ug/mL": ("G/L", 0.001),
    "%": ("%", 1.0),
    "CFU/mL": ("CFU/ML", 1.0),
}

DATE_FORMATS = ("%Y-%m-%d", "%m/%d/%Y", "%Y-%m-%dT%H:%M:%S")


class TransformError(ValueError):
    """Raised when a LIMS event cannot be mapped to SAP."""


def transform_lims_to_sap(event: Dict[str, Any]) -> Dict[str, Any]:
    missing = [f for f in REQUIRED_FIELDS if event.get(f) in (None, "")]
    if missing:
        raise TransformError(f"missing required fields: {', '.join(missing)}")

    status = str(event["status"]).upper()
    if status not in STATUS_MAP:
        raise TransformError(f"status '{status}' is not final; only APPROVED or REJECTED results are posted")

    unit = event["unit"]
    if unit not in TO_SAP_UNIT:
        raise TransformError(f"no SAP unit mapping for '{unit}'")
    sap_unit, factor = TO_SAP_UNIT[unit]

    try:
        value = float(event["test_result"])
    except (TypeError, ValueError):
        raise TransformError(f"test_result '{event['test_result']}' is not numeric")

    return {
        "InspectionLot": str(event["inspection_lot"]),
        "InspectionCharacteristic": str(event["characteristic"]),
        "Batch": str(event["sample_id"]),
        "ResultValue": round(value * factor, 6),
        "ResultUnit": sap_unit,
        "Valuation": STATUS_MAP[status],
        "InspectorUser": str(event["analyst_id"]).upper()[:12],
        "InspectionDate": _format_date(str(event["test_date"])),
    }


def _format_date(value: str) -> str:
    """Return SAP date format YYYYMMDD."""
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt).strftime("%Y%m%d")
        except ValueError:
            continue
    raise TransformError(f"unrecognized date format: '{value}'")
