from django.db import models
from apps.core.models import TimeStampedModel

class ComplaintCategory(TimeStampedModel):
    slug = models.SlugField(unique=True, max_length=100)
    name_en = models.CharField(max_length=150)
    name_hi = models.CharField(max_length=150)
    icon = models.CharField(max_length=50, default='AlertCircle', help_text='Lucide icon name')
    description_en = models.TextField(blank=True)
    description_hi = models.TextField(blank=True)
    requires_strict_moderation = models.BooleanField(default=False, help_text='E.g. Official Conduct requires corroboration threshold')
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order', 'name_en']
        verbose_name_plural = 'Complaint Categories'

    def __str__(self):
        return f"{self.name_en} ({self.name_hi})"

class AreaType(TimeStampedModel):
    CODE_CHOICES = (
        ('VILLAGE', 'Village / Gram Panchayat (ग्रामीण)'),
        ('TOWN', 'Town / Nagar Panchayat (कस्बा/नगर पंचायत)'),
        ('CITY', 'City / Nagar Nigam (शहर/नगर निगम)'),
    )
    code = models.CharField(max_length=20, unique=True, choices=CODE_CHOICES)
    name_en = models.CharField(max_length=100)
    name_hi = models.CharField(max_length=100)
    description_en = models.TextField(blank=True)
    description_hi = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.name_en} - {self.name_hi}"

class DurationOption(TimeStampedModel):
    code = models.CharField(max_length=30, unique=True)
    label_en = models.CharField(max_length=100)
    label_hi = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.label_en} / {self.label_hi}"

class PriorChannelOption(TimeStampedModel):
    code = models.CharField(max_length=50, unique=True)
    label_en = models.CharField(max_length=150)
    label_hi = models.CharField(max_length=150)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.label_en} / {self.label_hi}"

class PlatformConfig(TimeStampedModel):
    key = models.CharField(max_length=100, unique=True)
    value = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.key}: {self.value}"
