from django.db import models

class Company(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class EmissionRecord(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='emissions')
    source_type = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    raw_value = models.FloatField()
    normalized_value = models.FloatField(null=True, blank=True)
    raw_unit = models.CharField(max_length=50)
    normalized_unit = models.CharField(max_length=50, null=True, blank=True)
    reporting_date = models.DateField()
    is_suspicious = models.BooleanField(default=False)
    suspicious_reason = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.source_type} - {self.reporting_date}"
