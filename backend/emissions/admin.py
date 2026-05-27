from django.contrib import admin
from .models import Company, EmissionRecord


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'industry', 'created_at')
    search_fields = ('name',)


@admin.register(EmissionRecord)
class EmissionRecordAdmin(admin.ModelAdmin):
    list_display = (
        'source_type', 'scope', 'category', 'reporting_date',
        'raw_value', 'raw_unit', 'co2_kg',
        'is_suspicious', 'status', 'upload',
    )
    list_filter = ('is_suspicious', 'status', 'source_type', 'scope', 'company')
    search_fields = ('category', 'suspicious_reason')
