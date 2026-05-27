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

    def _get_val(self, row, keys, default=''):
        for k in keys:
            if k in row:
                return row.get(k, default).strip()
        for key in row.keys():
            if key.lower() in [k.lower() for k in keys]:
                return row.get(key, default).strip()
        return default

    def process(self):
        rows = self.read_csv()
        records = []

        for idx, row in enumerate(rows, start=1):
            plant = self._get_val(row, ['WERKS', 'Plant'])
            material_num = self._get_val(row, ['MATNR', 'Material'])
            material_desc = self._get_val(row, ['MAKTX', 'Material_Description', 'Description'])
            raw_unit = self._get_val(row, ['MEINS', 'Unit', 'UOM'])
            date_str = self._get_val(row, ['BUDAT', 'Posting_Date', 'PostingDate', 'Date'])
            quantity_str = self._get_val(row, ['MENGE', 'Quantity', 'Qty', 'DMBTR', 'Amount_LC', 'Amount'])
            cost_center = self._get_val(row, ['KOSTL', 'CostCenter', 'Cost_Center'])

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
                reasons.append("Missing unit")

            normalized_unit, normalized_value = self.normalize_unit(raw_unit, raw_value)

            reporting_date = self.parse_date(date_str)
            if not reporting_date:
                is_suspicious = True
                reasons.append("Invalid or missing date")
                reporting_date = datetime.now().date()

            ef = self._guess_fuel_factor(material_desc)
            co2 = None
            if ef and normalized_value > 0 and normalized_unit == 'L':
                co2 = round(normalized_value * ef, 2)

            if plant and cost_center:
                category = f"{material_desc or material_num} [{plant}/{cost_center}]"
            elif plant:
                category = f"{material_desc or material_num} [{plant}]"
            else:
                category = material_desc or material_num or "Unknown Material"

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
