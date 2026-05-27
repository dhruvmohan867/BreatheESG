from datetime import datetime
from emissions.models import EmissionRecord
from .base_parser import BaseParserService, EMISSION_FACTORS


FUEL_FACTOR_MAP = {
    'diesel': EMISSION_FACTORS['diesel'],
    'petrol': EMISSION_FACTORS['petrol'],
    'lpg': EMISSION_FACTORS['lpg'],
    'natural gas': EMISSION_FACTORS['natural_gas'],
    'furnace oil': EMISSION_FACTORS['furnace_oil'],
}


class SAPParserService(BaseParserService):
    def _guess_fuel_factor(self, material_desc):
        desc = material_desc.lower()
        for keyword, factor in FUEL_FACTOR_MAP.items():
            if keyword in desc:
                return factor
        return None

    def process(self):
        rows = self.read_csv()
        records = []

        for idx, row in enumerate(rows, start=1):
            plant = row.get('WERKS', '').strip()
            material_num = row.get('MATNR', '').strip()
            material_desc = row.get('MAKTX', '').strip()
            raw_unit = row.get('MEINS', '').strip()
            date_str = row.get('BUDAT', '').strip()
            quantity_str = row.get('MENGE', '').strip()
            cost_center = row.get('KOSTL', '').strip()

            is_suspicious = False
            reasons = []

            raw_value, bad_number = self.parse_float(quantity_str)
            if bad_number:
                is_suspicious = True
                reasons.append("Invalid quantity format")

            if raw_value < 0:
                is_suspicious = True
                reasons.append("Negative quantity")

            if not raw_unit:
                is_suspicious = True
                reasons.append("Missing unit (MEINS)")

            normalized_unit, normalized_value = self.normalize_unit(raw_unit, raw_value)

            reporting_date = self.parse_date(date_str)
            if not reporting_date:
                is_suspicious = True
                reasons.append("Invalid or missing date (BUDAT)")
                reporting_date = datetime.now().date()

            ef = self._guess_fuel_factor(material_desc)
            co2 = None
            if ef and normalized_value > 0 and normalized_unit == 'L':
                co2 = round(normalized_value * ef, 2)

            category = f"{material_desc} [{plant}/{cost_center}]"

            records.append(EmissionRecord(
                company=self.upload.company,
                upload=self.upload,
                row_number=idx,
                source_type='sap_fuel',
                scope=1,
                category=category,
                raw_value=raw_value,
                normalized_value=normalized_value,
                raw_unit=raw_unit,
                normalized_unit=normalized_unit,
                emission_factor=ef,
                co2_kg=co2,
                reporting_date=reporting_date,
                is_suspicious=is_suspicious,
                suspicious_reason="; ".join(reasons),
            ))

        EmissionRecord.objects.bulk_create(records)
        return self.finalize_upload(records)
