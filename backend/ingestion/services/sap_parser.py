import csv
import io
from datetime import datetime
from emissions.models import EmissionRecord, Company

class SAPParserService:
    def __init__(self, file_obj, company_id):
        self.file_obj = file_obj
        self.company_id = company_id

    def process(self):
        content = self.file_obj.read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(content))
        
        company = Company.objects.get(id=self.company_id)
        records_to_create = []

        for row in reader:
            parsed_data = self._parse_row(row)
            validated_data = self._validate_and_normalize(parsed_data)
            
            record = EmissionRecord(
                company=company,
                source_type=validated_data.get('source_type', ''),
                category=validated_data.get('category', ''),
                raw_value=validated_data.get('raw_value', 0),
                normalized_value=validated_data.get('normalized_value'),
                raw_unit=validated_data.get('raw_unit', ''),
                normalized_unit=validated_data.get('normalized_unit'),
                reporting_date=validated_data.get('reporting_date'),
                is_suspicious=validated_data.get('is_suspicious', False),
                suspicious_reason=validated_data.get('suspicious_reason', '')
            )
            records_to_create.append(record)

        EmissionRecord.objects.bulk_create(records_to_create)
        return len(records_to_create)

    def _parse_row(self, row):
        return {
            'source_type': row.get('source_type', '').strip(),
            'category': row.get('category', '').strip(),
            'raw_value': row.get('quantity', '').strip(),
            'raw_unit': row.get('unit', '').strip(),
            'reporting_date': row.get('date', '').strip(),
        }

    def _validate_and_normalize(self, data):
        is_suspicious = False
        suspicious_reasons = []

        try:
            raw_value = float(data['raw_value']) if data['raw_value'] else 0.0
        except ValueError:
            raw_value = 0.0
            is_suspicious = True
            suspicious_reasons.append("Invalid quantity format")

        if raw_value < 0:
            is_suspicious = True
            suspicious_reasons.append("Negative quantity")

        raw_unit = data['raw_unit']
        normalized_unit = raw_unit
        normalized_value = raw_value

        if not raw_unit:
            is_suspicious = True
            suspicious_reasons.append("Missing unit")
        else:
            unit_lower = raw_unit.lower()
            if unit_lower in ['ltr', 'liters', 'liter', 'l']:
                normalized_unit = 'L'
            elif unit_lower in ['kl', 'kiloliters']:
                normalized_unit = 'L'
                normalized_value = raw_value * 1000
            else:
                normalized_unit = raw_unit

        reporting_date = None
        date_str = data['reporting_date']
        if date_str:
            for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y'):
                try:
                    reporting_date = datetime.strptime(date_str, fmt).date()
                    break
                except ValueError:
                    pass
            
        if not reporting_date:
            is_suspicious = True
            suspicious_reasons.append("Invalid or missing date")
            reporting_date = datetime.now().date()

        return {
            'source_type': data['source_type'],
            'category': data['category'],
            'raw_value': raw_value,
            'normalized_value': normalized_value,
            'raw_unit': raw_unit,
            'normalized_unit': normalized_unit,
            'reporting_date': reporting_date,
            'is_suspicious': is_suspicious,
            'suspicious_reason': "; ".join(suspicious_reasons) if is_suspicious else ""
        }
