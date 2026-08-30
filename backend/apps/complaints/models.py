from django.db import models
from django.utils import timezone
from apps.core.models import TimeStampedModel
from apps.config_engine.models import ComplaintCategory, AreaType, DurationOption, PriorChannelOption
from apps.authorities.models import State, District, AdministrativeUnit
from apps.core.utils import generate_public_id

class Complaint(TimeStampedModel):
    STATUS_CHOICES = (
        ('FILED', 'Filed (दर्ज किया गया)'),
        ('UNDER_REVIEW', 'Under Review (समीक्षा में)'),
        ('ACKNOWLEDGED', 'Acknowledged (संज्ञान लिया)'),
        ('IN_PROGRESS', 'In Progress (कार्य प्रगति पर)'),
        ('RESOLVED', 'Resolved (निस्तारित)'),
        ('CLOSED_UNRESOLVED', 'Closed Unresolved (अनिस्तारित बंद)'),
    )

    MODERATION_STATUS_CHOICES = (
        ('PENDING', 'Pending Review'),
        ('APPROVED', 'Approved / Public'),
        ('REJECTED', 'Rejected'),
        ('FLAGGED', 'Flagged for Concern'),
    )

    PEOPLE_AFFECTED_CHOICES = (
        ('ESTIMATE', 'Specific Count'),
        ('ENTIRE_VILLAGE', 'Entire Village / Gram (संपूर्ण गांव)'),
        ('ENTIRE_WARD', 'Entire Ward / Mohalla (संपूर्ण वार्ड)'),
        ('ENTIRE_STREET', 'Entire Street / Gali (पूरी गली)'),
    )

    # Identifiers
    public_id = models.CharField(max_length=30, unique=True, default=generate_public_id, db_index=True)
    anonymous_session_hash = models.CharField(max_length=64, db_index=True)
    
    # Optional Reveal Identity
    revealed_identity = models.BooleanField(default=False)
    filer_name = models.CharField(max_length=150, blank=True, null=True)
    filer_phone = models.CharField(max_length=30, blank=True, null=True)

    # Classification (Config-Driven)
    area_type = models.ForeignKey(AreaType, on_delete=models.PROTECT, related_name='complaints')
    category = models.ForeignKey(ComplaintCategory, on_delete=models.PROTECT, related_name='complaints')
    duration = models.ForeignKey(DurationOption, on_delete=models.PROTECT, related_name='complaints', null=True, blank=True)
    
    title = models.CharField(max_length=200)
    description = models.TextField(help_text='Detailed description of the issue (min 30 chars)')
    
    people_affected_type = models.CharField(max_length=30, choices=PEOPLE_AFFECTED_CHOICES, default='ESTIMATE')
    people_affected_count = models.PositiveIntegerField(null=True, blank=True)

    # Prior attempts (escalation context)
    prior_attempts_count = models.PositiveIntegerField(default=0)
    prior_channel = models.ForeignKey(PriorChannelOption, on_delete=models.SET_NULL, null=True, blank=True)
    prior_reference_number = models.CharField(max_length=100, blank=True, null=True)

    # Location & Administration
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True, blank=True)
    district = models.ForeignKey(District, on_delete=models.SET_NULL, null=True, blank=True)
    administrative_unit = models.ForeignKey(AdministrativeUnit, on_delete=models.SET_NULL, null=True, blank=True, related_name='complaints')
    sub_location = models.CharField(max_length=200, help_text='Village / Hamlet / Ward name / Landmark')
    
    # Authority details (branched by area type)
    authority_name_override = models.CharField(max_length=150, blank=True, null=True)
    authority_designation = models.CharField(max_length=150, blank=True, null=True)

    # GPS coordinates
    latitude = models.FloatField(db_index=True)
    longitude = models.FloatField(db_index=True)
    gps_accuracy_meters = models.FloatField(null=True, blank=True)
    manual_address_text = models.TextField(blank=True)

    # Status & Moderation
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='UNDER_REVIEW', db_index=True)
    moderation_status = models.CharField(max_length=30, choices=MODERATION_STATUS_CHOICES, default='PENDING', db_index=True)
    is_official_conduct = models.BooleanField(default=False, help_text='Direct complaint on named official conduct')
    
    co_sign_count = models.PositiveIntegerField(default=0, db_index=True)
    flag_count = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.public_id}] {self.title} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            # Create initial audit log
            StatusAuditLog.objects.create(
                complaint=self,
                from_status='',
                to_status=self.status,
                actor_type='SYSTEM',
                actor_label='Awaaz Filing Gateway',
                notes='Complaint filed via anonymous live-capture engine.'
            )

class ComplaintEvidence(TimeStampedModel):
    MEDIA_TYPE_CHOICES = (
        ('PHOTO', 'Live Photo Snapshot'),
        ('VIDEO', 'Live Video Stream (30s)'),
        ('AUDIO_NOTE', 'Live Audio Voice-Note (60s)'),
    )

    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='evidence')
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPE_CHOICES)
    file = models.FileField(upload_to='evidence/%Y/%m/', blank=True, null=True)
    file_url = models.CharField(max_length=500, blank=True)
    sha256_hash = models.CharField(max_length=64, help_text='Tamper-evident SHA-256 hash of media file')
    
    capture_timestamp = models.DateTimeField(default=timezone.now)
    server_timestamp = models.DateTimeField(auto_now_add=True)
    
    capture_latitude = models.FloatField(null=True, blank=True)
    capture_longitude = models.FloatField(null=True, blank=True)
    is_live_captured = models.BooleanField(default=True, help_text='Captured via getUserMedia (no gallery picker)')

    def __str__(self):
        return f"{self.media_type} for {self.complaint.public_id} [{self.sha256_hash[:10]}...]"

class ComplaintCoSign(TimeStampedModel):
    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='co_signs')
    anonymous_session_hash = models.CharField(max_length=64, db_index=True)
    ip_hash = models.CharField(max_length=64, blank=True)
    comment = models.CharField(max_length=250, blank=True)

    class Meta:
        unique_together = ('complaint', 'anonymous_session_hash')

    def __str__(self):
        return f"Co-Sign on {self.complaint.public_id} ({self.anonymous_session_hash[:8]})"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            Complaint.objects.filter(id=self.complaint_id).update(
                co_sign_count=models.F('co_sign_count') + 1
            )
            # Log audit step if threshold reached
            comp = Complaint.objects.get(id=self.complaint_id)
            if comp.co_sign_count in (5, 15, 50, 100):
                StatusAuditLog.objects.create(
                    complaint=comp,
                    from_status=comp.status,
                    to_status=comp.status,
                    actor_type='CITIZEN',
                    actor_label=f'Community Escalation ({comp.co_sign_count} citizens co-signed)',
                    notes=f'{comp.co_sign_count} citizens have corroborated facing this exact issue.'
                )

class StatusAuditLog(TimeStampedModel):
    ACTOR_TYPE_CHOICES = (
        ('SYSTEM', 'Awaaz System Engine'),
        ('MODERATOR', 'Public Moderator'),
        ('AUTHORITY', 'Civic Authority / Official'),
        ('CITIZEN', 'Citizen Community'),
    )

    complaint = models.ForeignKey(Complaint, on_delete=models.CASCADE, related_name='audit_trail')
    from_status = models.CharField(max_length=30, blank=True)
    to_status = models.CharField(max_length=30)
    actor_type = models.CharField(max_length=20, choices=ACTOR_TYPE_CHOICES, default='SYSTEM')
    actor_label = models.CharField(max_length=150)
    notes = models.TextField()

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.complaint.public_id}: {self.from_status} -> {self.to_status} by {self.actor_label}"
