from django.db import models


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('upload', 'File Upload'),
        ('review_approved', 'Review Approved'),
        ('review_rejected', 'Review Rejected'),
    ]

    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    target_type = models.CharField(max_length=50)
    target_id = models.PositiveIntegerField()
    details = models.JSONField(default=dict, blank=True)
    performed_by = models.CharField(max_length=100, blank=True, default='system')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.action} on {self.target_type}#{self.target_id}"
