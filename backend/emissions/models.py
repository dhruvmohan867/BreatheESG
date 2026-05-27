from django.db import models


class Company(models.Model):
    name = models.CharField(max_length=255, unique=True)
    industry = models.CharField(max_length=100, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'companies'

    def __str__(self):
        return self.name


class EmissionRecord(models.Model):
    SOURCE_TYPES = [
        ('sap_fuel', 'SAP Fuel/Procurement'),
        ('utility', 'Utility Electricity'),
        ('travel', 'Travel Platform'),
    ]

    SCOPE_CHOICES = [
        (1, 'Scope 1 — Direct Emissions'),
        (2, 'Scope 2 — Purchased Energy'),
        (3, 'Scope 3 — Indirect / Value Chain'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='emissions')
    upload = models.ForeignKey(
        'ingestion.Upload',
        on_delete=models.CASCADE,
        related_name='records',
        null=True,
        blank=True,
    )
    row_number = models.PositiveIntegerField(null=True, blank=True)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES)
    scope = models.PositiveSmallIntegerField(choices=SCOPE_CHOICES, default=1)
    category = models.CharField(max_length=200)
    raw_value = models.FloatField()
    normalized_value = models.FloatField(null=True, blank=True)
    raw_unit = models.CharField(max_length=50, blank=True, default='')
    normalized_unit = models.CharField(max_length=50, blank=True, default='')
    emission_factor = models.FloatField(null=True, blank=True)
    co2_kg = models.FloatField(null=True, blank=True)
    reporting_date = models.DateField()
    is_suspicious = models.BooleanField(default=False)
    suspicious_reason = models.TextField(blank=True, default='')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Scope {self.scope} | {self.source_type} | {self.reporting_date}"
