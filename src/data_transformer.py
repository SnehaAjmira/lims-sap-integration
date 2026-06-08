"""
  data_transformer.py
  -------------------
  Maps LIMS payload fields to SAP ERP schema.
  Handles unit conversions, status code mapping, and date formatting.
    """

    from datetime import datetime
    from typing import Dict, Any

      # LIMS status to SAP verification status code mapping
      STATUS_MAP = {
          "APPROVED": "01",
          "REJECTED": "02",
          "PENDING": "03",
          "IN_PROGRESS": "04",
          "ON_HOLD": "05",
    }

# Unit conversion factors (LIMS unit -> SAP unit)
  UNIT_CONVERSIONS = {
      ("mg/L", "g/L"): 0.001,
      ("ppm", "mg/L"): 1.0,
      ("CFU/mL", "CFU/mL"): 1.0,
}


def transform_lims_to_sap(lims_payload: Dict[str, Any]) -> Dict[str, Any]:
    """
          Transforms a LIMS event payload into a SAP-compatible inspection result.

          Args:
        lims_payload: Raw LIMS webhook payload

              Returns:
        SAP-formatted inspection result dictionary

              Raises:
        KeyError: If required fields are missing from the payload
                  ValueError: If status code or unit conversion is unsupported
                        """
                        sample_id = lims_payload["sample_id"]
                        test_result = lims_payload["test_result"]
                        lims_unit = lims_payload.get("unit", "mg/L")
                        analyst = lims_payload["analyst_name"]
                        status = lims_payload["status"].upper()
                        test_date = lims_payload["test_date"]

                        # Convert status to SAP code
                        sap_status = STATUS_MAP.get(status)
                        if not sap_status:
                            raise ValueError(f"Unsupported LIMS status: {status}")

                        # Convert result to SAP units
                        sap_result = _convert_units(test_result, lims_unit, "g/L")

                        # Format date to ISO 8601
                        sap_date = _format_date(test_date)

                        return {
                            "CHARG": sample_id,
                            "ERGEBNIS": sap_result,
                            "ERGEBNISEINHEIT": "G/L",
                            "PRUEFANWENDER": _lookup_user_id(analyst),
                            "VERID": sap_status,
                            "PRUEFDAT": sap_date,
                            "PRUEFZEIT": datetime.utcnow().strftime("%H%M%S"),
                  }


def _convert_units(value: float, from_unit: str, to_unit: str) -> float:
    """Converts a measurement value between units."""
          if from_unit == to_unit:
              return value
          factor = UNIT_CONVERSIONS.get((from_unit, to_unit))
          if factor is None:
              raise ValueError(f"No conversion defined from {from_unit} to {to_unit}")
          return round(value * factor, 6)


      def _format_date(date_str: str) -> str:
    """Normalizes date string to ISO 8601 (YYYYMMDD) for SAP."""
          for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y"):
              try:
                  return datetime.strptime(date_str, fmt).strftime("%Y%m%d")
              except ValueError:
                  continue
          raise ValueError(f"Unrecognized date format: {date_str}")


      def _lookup_user_id(analyst_name: str) -> str:
    """Maps analyst full name to SAP user ID (placeholder — replace with DB lookup)."""
          # TODO: Replace with actual user directory lookup
                return analyst_name.replace(" ", "_").upper()[:12]
