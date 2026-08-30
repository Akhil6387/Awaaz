from django.db import models
from apps.core.models import TimeStampedModel
from apps.config_engine.models import AreaType

class State(TimeStampedModel):
    code = models.CharField(max_length=10, unique=True)
    name_en = models.CharField(max_length=100)
    name_hi = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name_en} ({self.name_hi})"

class District(TimeStampedModel):
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='districts')
    code = models.CharField(max_length=20)
    name_en = models.CharField(max_length=100)
    name_hi = models.CharField(max_length=100)

    class Meta:
        unique_together = ('state', 'code')

    def __str__(self):
        return f"{self.name_en} - {self.state.name_en}"

class AdministrativeUnit(TimeStampedModel):
    UNIT_TYPE_CHOICES = (
        ('MUNICIPAL_CORP', 'Municipal Corporation (Nagar Nigam)'),
        ('ZONE', 'Zone / Division'),
        ('WARD', 'Ward / Mohalla'),
        ('NAGAR_PANCHAYAT', 'Nagar Panchayat / Palika Parishad'),
        ('BLOCK', 'Block / Tehsil / Janpad'),
        ('GRAM_PANCHAYAT', 'Gram Panchayat'),
        ('VILLAGE', 'Village / Gaon / Mauza'),
    )
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='admin_units')
    area_type = models.ForeignKey(AreaType, on_delete=models.CASCADE, related_name='admin_units')
    unit_type = models.CharField(max_length=30, choices=UNIT_TYPE_CHOICES)
    name_en = models.CharField(max_length=150)
    name_hi = models.CharField(max_length=150)
    ward_number = models.CharField(max_length=20, blank=True, null=True)
    parent_unit = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='sub_units')
    helpline_number = models.CharField(max_length=50, blank=True)
    official_portal_url = models.URLField(blank=True)
    approx_latitude = models.FloatField(null=True, blank=True)
    approx_longitude = models.FloatField(null=True, blank=True)

    class Meta:
        ordering = ['name_en']

    def __str__(self):
        return f"{self.name_en} ({self.get_unit_type_display()}) - {self.district.name_en}"

class PublicAuthority(TimeStampedModel):
    name_en = models.CharField(max_length=150)
    name_hi = models.CharField(max_length=150)
    designation_en = models.CharField(max_length=150)
    designation_hi = models.CharField(max_length=150)
    administrative_unit = models.ForeignKey(AdministrativeUnit, on_delete=models.CASCADE, related_name='authorities')
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    office_address_en = models.TextField(blank=True)
    office_address_hi = models.TextField(blank=True)
    photo_url = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.designation_en} {self.name_en} ({self.administrative_unit.name_en})"
