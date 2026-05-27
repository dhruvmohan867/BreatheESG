from datetime import datetime
from emissions.models import EmissionRecord
from .base_parser import BaseParserService, EMISSION_FACTORS


class UtilityParserService(BaseParserService):
    def process(self):
        rows = self.read_csv()
        records = []
        values_for_spike = []

        for row in rows:
            val, _ = self.parse_float(row.get('kwh_consumed', '').strip())
            if val > 0:
                values_for_spike.append(val)

        median_val = sorted(values_for_spike)[len(values_for_spike) // 2] if values_for_spike else 0

        for idx, row in enumerate(rows, start=1):
            account = row.get('account_number', '').strip()
            meter_id = row.get('meter_id', '').strip()
            provider = row.get('provider', '').strip()
            facility = row.get('facility', '').strip()
            raw_unit = row.get('unit', '').strip() or 'kWh'
            date_str = row.get('reading_date', '').strip()
            quantity_str = row.get('kwh_consumed', '').strip()
            billing_start = row.get('billing_period_start', '').strip()
            billing_end = row.get('billing_period_end', '').strip()

            is_suspicious = False
            reasons = []

            raw_value, bad_number = self.parse_float(quantity_str)
            if bad_number:
                is_suspicious = True
                reasons.append("Invalid consumption value")

            if raw_value < 0:
                is_suspicious = True
                reasons.append("Negative consumption")

            if raw_value == 0 and not bad_number:
                is_suspicious = True
                reasons.append("Zero consumption reading")

            if median_val > 0 and raw_value > median_val * 10:
                is_suspicious = True
                reasons.append(f"Usage spike: {raw_value} vs median {median_val}")

            if not meter_id:
                is_suspicious = True
                reasons.append("Missing meter ID")

            normalized_unit, normalized_value = self.normalize_unit(raw_unit, raw_value)

            reporting_date = self.parse_date(date_str)
            if not reporting_date:
                reporting_date = self.parse_date(billing_end)
            if not reporting_date:
                is_suspicious = True
                reasons.append("Invalid or missing date")
                reporting_date = datetime.now().date()

            ef = EMISSION_FACTORS['electricity_india']
            co2 = None
            if normalized_value > 0 and normalized_unit == 'kWh':
                co2 = round(normalized_value * ef, 2)

            parts = [p for p in [facility, provider, meter_id] if p]
            category = " | ".join(parts) if parts else "Unknown"

            records.append(EmissionRecord(
                company=self.upload.company,
                upload=self.upload,
                row_number=idx,
                source_type='utility',
                scope=2,
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
