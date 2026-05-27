from django.contrib import admin
from .models import Company, EmissionRecord

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)

@admin.register(EmissionRecord)
class EmissionRecordAdmin(admin.ModelAdmin):
    list_display = (
        'source_type', 'category', 'reporting_date',
        'raw_value', 'raw_unit', 'is_suspicious', 'status'
    )
    list_filter = ('is_suspicious', 'status', 'source_type', 'category', 'company')
    search_fields = ('source_type', 'category', 'suspicious_reason')
