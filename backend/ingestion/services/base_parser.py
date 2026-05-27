import csv
import io
from datetime import datetime


EMISSION_FACTORS = {
    'diesel': 2.68,
    'petrol': 2.31,
    'lpg': 1.51,
    'natural_gas': 2.04,
    'furnace_oil': 3.15,
    'electricity_india': 0.82,
    'flight_domestic': 0.255,
    'flight_international': 0.195,
    'flight_business': 0.39,
}


class BaseParserService:
    UNIT_MAP = {
        'ltr': ('L', 1),
        'liters': ('L', 1),
        'liter': ('L', 1),
        'l': ('L', 1),
        'kl': ('L', 1000),
        'kiloliters': ('L', 1000),
        'kiloliter': ('L', 1000),
        'gal': ('L', 3.78541),
        'gallon': ('L', 3.78541),
        'gallons': ('L', 3.78541),
        'kwh': ('kWh', 1),
        'mwh': ('kWh', 1000),
        'gwh': ('kWh', 1000000),
        'km': ('km', 1),
        'mi': ('km', 1.60934),
        'miles': ('km', 1.60934),
        'scm': ('SCM', 1),
    }

    DATE_FORMATS = [
        '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%d-%m-%Y',
        '%d.%m.%Y', '%Y/%m/%d', '%d-%b-%Y'
    ]

    def __init__(self, file_obj, upload):
        self.file_obj = file_obj
        self.upload = upload

    def read_csv(self):
        content = self.file_obj.read().decode('utf-8')
        return list(csv.DictReader(io.StringIO(content)))

    def normalize_unit(self, raw_unit, raw_value):
        if not raw_unit:
            return raw_unit, raw_value
        key = raw_unit.strip().lower()
        if key in self.UNIT_MAP:
            norm_unit, factor = self.UNIT_MAP[key]
            return norm_unit, raw_value * factor
        return raw_unit, raw_value

    def parse_date(self, date_str):
        if not date_str:
            return None
        date_str = date_str.strip()
        for fmt in self.DATE_FORMATS:
            try:
                return datetime.strptime(date_str, fmt).date()
            except ValueError:
                continue
        return None

    def parse_float(self, value_str):
        if not value_str:
            return 0.0, False
        try:
            return float(value_str.strip()), False
        except ValueError:
            return 0.0, True

    def process(self):
        raise NotImplementedError

    def finalize_upload(self, records):
        suspicious_count = sum(1 for r in records if r.is_suspicious)
        self.upload.row_count = len(records)
        self.upload.suspicious_count = suspicious_count
        self.upload.status = 'completed'
        self.upload.save()
        return len(records)
