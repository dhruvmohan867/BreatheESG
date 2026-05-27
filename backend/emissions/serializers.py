from rest_framework import serializers
from .models import EmissionRecord, Company
from ingestion.models import Upload


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'


class UploadSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)

    class Meta:
        model = Upload
        fields = [
            'id', 'company', 'company_name', 'source_type',
            'file_name', 'row_count', 'suspicious_count',
            'status', 'created_at',
        ]


class EmissionRecordSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name', read_only=True)
    upload_file = serializers.CharField(source='upload.file_name', read_only=True, default=None)

    class Meta:
        model = EmissionRecord
        fields = [
            'id', 'company', 'company_name', 'upload', 'upload_file',
            'row_number', 'source_type', 'scope', 'category',
            'raw_value', 'normalized_value', 'raw_unit', 'normalized_unit',
            'emission_factor', 'co2_kg',
            'reporting_date', 'is_suspicious', 'suspicious_reason',
            'status', 'created_at',
        ]
