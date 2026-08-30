from django.db import models
from apps.core.models import TimeStampedModel
from apps.complaints.models import Complaint

class EscalationTemplate(TimeStampedModel):
    TEMPLATE_TYPE_CHOICES = (
        ('GRIEVANCE_LETTER', 'Formal Public Grievance Letter (औपचारिक जन शिकायत पत्र)'),
        ('RTI_APPLICATION', 'Right to Information (RTI / सूचना का अधिकार आवेदन)'),
        ('PRESS_DOSSIER', 'Media & Press Accountability Dossier'),
    )
    template_type = models.CharField(max_length=40, choices=TEMPLATE_TYPE_CHOICES)
    language = models.CharField(max_length=10, default='hi', choices=(('hi', 'Hindi'), ('en', 'English')))
    title_format = models.CharField(max_length=255)
    body_template = models.TextField()

    def __str__(self):
        return f"{self.get_template_type_display()} ({self.language})"

class GeneratedEscalation(TimeStampedModel):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='escalations')
    template_type = models.CharField(max_length=40)
    language = models.CharField(max_length=10, default='hi')
    addressed_to = models.CharField(max_length=255)
    content = models.TextField()
    corroboration_count_at_generation = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.template_type} for {self.complaint.public_id}"
