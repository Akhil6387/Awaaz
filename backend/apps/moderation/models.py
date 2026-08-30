from django.db import models
from apps.core.models import TimeStampedModel
from apps.complaints.models import Complaint

class ComplaintFlag(TimeStampedModel):
    REASON_CHOICES = (
        ('HATE_SPEECH', 'Hate Speech / Discriminatory Language'),
        ('UNVERIFIED_DEFAMATION', 'Unverified Personal Defamation against Individual'),
        ('SPAM', 'Spam / Advertisement / Irrelevant Content'),
        ('FALSE_LOCATION', 'Fabricated / False GPS Location'),
        ('PERSONAL_DATA_LEAK', 'Unauthorized Leak of Private Citizen Data / Phone Numbers'),
        ('OTHER', 'Other Violation of Community Guidelines'),
    )

    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='flags')
    reason = models.CharField(max_length=40, choices=REASON_CHOICES)
    explanation = models.TextField()
    anonymous_session_hash = models.CharField(max_length=64)
    ip_hash = models.CharField(max_length=64, blank=True)

    def __str__(self):
        return f"Flag on {self.complaint.public_id} ({self.reason})"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            Complaint.objects.filter(id=self.complaint_id).update(
                flag_count=models.F('flag_count') + 1
            )
            # Auto-flag status if flags exceed threshold
            comp = Complaint.objects.get(id=self.complaint_id)
            if comp.flag_count >= 3 and comp.moderation_status != 'FLAGGED':
                comp.moderation_status = 'FLAGGED'
                comp.save(update_fields=['moderation_status'])

class ModerationReview(TimeStampedModel):
    ACTION_CHOICES = (
        ('APPROVE', 'Approve for Public Feed'),
        ('REJECT', 'Reject Submission (Spam/Defamation)'),
        ('FLAG', 'Mark for Strict Verification'),
        ('REQUEST_REVISION', 'Request Redaction of Named Individual'),
    )

    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='moderation_reviews')
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    moderator_name = models.CharField(max_length=100, default='Community Moderator')
    notes = models.TextField()

    def __str__(self):
        return f"{self.action} on {self.complaint.public_id} by {self.moderator_name}"
