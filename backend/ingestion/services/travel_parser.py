from datetime import datetime
from emissions.models import EmissionRecord
from .base_parser import BaseParserService, EMISSION_FACTORS


class TravelParserService(BaseParserService):
    MAX_REASONABLE_DISTANCE_KM = 20000

    def _get_flight_factor(self, distance_km, travel_class):
        tc = travel_class.lower() if travel_class else ''
        if tc in ('business', 'first'):
            return EMISSION_FACTORS['flight_business']
        if distance_km > 3500:
            return EMISSION_FACTORS['flight_international']
        return EMISSION_FACTORS['flight_domestic']

    def process(self):
        rows = self.read_csv()
        records = []

        for idx, row in enumerate(rows, start=1):
            booking_ref = row.get('booking_ref', '').strip()
            employee_id = row.get('employee_id', '').strip()
            origin = row.get('departure_iata', '').strip()
            destination = row.get('arrival_iata', '').strip()
            travel_class = row.get('travel_class', '').strip()
            expense_cat = row.get('expense_category', '').strip()
            vendor = row.get('vendor', '').strip()
            date_str = row.get('trip_date', '').strip()
            distance_str = row.get('distance_km', '').strip()
            raw_unit = row.get('unit', '').strip() or 'km'

            is_suspicious = False
            reasons = []

            raw_value, bad_number = self.parse_float(distance_str)
            if bad_number:
                is_suspicious = True
                reasons.append("Invalid distance value")

            if raw_value < 0:
                is_suspicious = True
                reasons.append("Negative distance")

            if raw_value > self.MAX_REASONABLE_DISTANCE_KM:
                is_suspicious = True
                reasons.append(f"Unrealistic distance: {raw_value} km")

            if not origin:
                is_suspicious = True
                reasons.append("Missing departure IATA code")

            if not destination:
                is_suspicious = True
                reasons.append("Missing arrival IATA code")

            normalized_unit, normalized_value = self.normalize_unit(raw_unit, raw_value)

            reporting_date = self.parse_date(date_str)
            if not reporting_date:
                is_suspicious = True
                reasons.append("Invalid or missing date")
                reporting_date = datetime.now().date()

            ef = self._get_flight_factor(raw_value, travel_class)
            co2 = None
            if normalized_value > 0 and normalized_unit == 'km':
                co2 = round(normalized_value * ef, 2)

            route = f"{origin or '???'}-{destination or '???'}"
            category = f"{expense_cat}: {route} ({travel_class})" if expense_cat else route

            records.append(EmissionRecord(
                company=self.upload.company,
                upload=self.upload,
                row_number=idx,
                source_type='travel',
                scope=3,
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
