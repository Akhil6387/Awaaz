"""
Awaaz Complete Backend Builder Script
Generates all apps, models, serializers, views, admin interfaces, and seeders.
"""
import os
import sys
from pathlib import Path

def write_file(rel_path: str, content: str):
    p = Path(rel_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, 'w', encoding='utf-8') as f:
        f.write(content.strip() + '\n')
    print(f"Created: {rel_path}")

# -------------------------------------------------------------
# 1. apps/core
# -------------------------------------------------------------
write_file("apps/core/models.py", """
from django.db import models

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
""")

write_file("apps/core/utils.py", """
import hashlib
import math
import random
import string
from django.utils import timezone

def compute_sha256(file_obj_or_bytes):
    \"Compute SHA-256 hash of file content or bytes for tamper-evidence.\"
    sha256 = hashlib.sha256()
    if isinstance(file_obj_or_bytes, bytes):
        sha256.update(file_obj_or_bytes)
    elif hasattr(file_obj_or_bytes, 'read'):
        current_pos = file_obj_or_bytes.tell() if hasattr(file_obj_or_bytes, 'tell') else 0
        for chunk in getattr(file_obj_or_bytes, 'chunks', lambda: iter(lambda: file_obj_or_bytes.read(4096), b''))():
            sha256.update(chunk)
        if hasattr(file_obj_or_bytes, 'seek'):
            file_obj_or_bytes.seek(current_pos)
    return sha256.hexdigest()

def hash_session_id(session_id: str) -> str:
    \"Anonymously hash client session UUID for privacy.\"
    if not session_id:
        return ''
    salt = 'awaaz_anon_salt_2026'
    return hashlib.sha256(f'{salt}:{session_id}'.encode('utf-8')).hexdigest()[:32]

def generate_public_id() -> str:
    \"Generate public tracking identifier e.g. AWZ-2026-8941.\"
    year = timezone.now().year
    digits = ''.join(random.choices(string.digits, k=4))
    return f'AWZ-{year}-{digits}'

def haversine_distance_meters(lat1, lon1, lat2, lon2) -> float:
    \"Calculate geodesic distance between two points in meters.\"
    if None in (lat1, lon1, lat2, lon2):
        return float('inf')
    R = 6371000
    phi1 = math.radians(float(lat1))
    phi2 = math.radians(float(lat2))
    delta_phi = math.radians(float(lat2) - float(lat1))
    delta_lambda = math.radians(float(lon2) - float(lon1))

    a = (math.sin(delta_phi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

def bounding_box(lat, lon, radius_meters=1000):
    \"Return (min_lat, max_lat, min_lon, max_lon) for quick DB filtering.\"
    lat = float(lat)
    lon = float(lon)
    lat_delta = radius_meters / 111000.0
    lon_delta = radius_meters / (111000.0 * math.cos(math.radians(lat)))
    return (lat - lat_delta, lat + lat_delta, lon - lon_delta, lon + lon_delta)
""")

# -------------------------------------------------------------
# 2. apps/config_engine
# -------------------------------------------------------------
write_file("apps/config_engine/models.py", """
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
""")

write_file("apps/config_engine/serializers.py", """
from rest_framework import serializers
from .models import ComplaintCategory, AreaType, DurationOption, PriorChannelOption, PlatformConfig

class ComplaintCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplaintCategory
        fields = ['id', 'slug', 'name_en', 'name_hi', 'icon', 'description_en', 'description_hi', 'requires_strict_moderation', 'order']

class AreaTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AreaType
        fields = ['id', 'code', 'name_en', 'name_hi', 'description_en', 'description_hi', 'order']

class DurationOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DurationOption
        fields = ['id', 'code', 'label_en', 'label_hi', 'order']

class PriorChannelOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriorChannelOption
        fields = ['id', 'code', 'label_en', 'label_hi', 'order']
""")

write_file("apps/config_engine/views.py", """
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import ComplaintCategory, AreaType, DurationOption, PriorChannelOption
from .serializers import ComplaintCategorySerializer, AreaTypeSerializer, DurationOptionSerializer, PriorChannelOptionSerializer

class ConfigBootstrapView(APIView):
    \"\"\"Return all dynamic form choices in a single high-performance call.\"\"\"
    def get(self, request):
        categories = ComplaintCategory.objects.filter(is_active=True).order_by('order')
        area_types = AreaType.objects.all().order_by('order')
        durations = DurationOption.objects.all().order_by('order')
        prior_channels = PriorChannelOption.objects.all().order_by('order')

        return Response({
            'categories': ComplaintCategorySerializer(categories, many=True).data,
            'area_types': AreaTypeSerializer(area_types, many=True).data,
            'duration_options': DurationOptionSerializer(durations, many=True).data,
            'prior_channels': PriorChannelOptionSerializer(prior_channels, many=True).data,
        })
""")

write_file("apps/config_engine/admin.py", """
from django.contrib import admin
from .models import ComplaintCategory, AreaType, DurationOption, PriorChannelOption, PlatformConfig

@admin.register(ComplaintCategory)
class ComplaintCategoryAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'name_hi', 'slug', 'icon', 'requires_strict_moderation', 'order', 'is_active')
    list_editable = ('order', 'is_active', 'requires_strict_moderation')
    search_fields = ('name_en', 'name_hi', 'slug')
    prepopulated_fields = {'slug': ('name_en',)}

@admin.register(AreaType)
class AreaTypeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name_en', 'name_hi', 'order')
    list_editable = ('order',)

@admin.register(DurationOption)
class DurationOptionAdmin(admin.ModelAdmin):
    list_display = ('code', 'label_en', 'label_hi', 'order')
    list_editable = ('order',)

@admin.register(PriorChannelOption)
class PriorChannelOptionAdmin(admin.ModelAdmin):
    list_display = ('code', 'label_en', 'label_hi', 'order')
    list_editable = ('order',)

@admin.register(PlatformConfig)
class PlatformConfigAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'description')
""")

# -------------------------------------------------------------
# 3. apps/authorities
# -------------------------------------------------------------
write_file("apps/authorities/models.py", """
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
""")

write_file("apps/authorities/serializers.py", """
from rest_framework import serializers
from .models import State, District, AdministrativeUnit, PublicAuthority

class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['id', 'code', 'name_en', 'name_hi']

class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ['id', 'state', 'code', 'name_en', 'name_hi']

class PublicAuthoritySerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicAuthority
        fields = ['id', 'name_en', 'name_hi', 'designation_en', 'designation_hi', 'contact_email', 'contact_phone', 'office_address_en', 'office_address_hi', 'photo_url']

class AdministrativeUnitSerializer(serializers.ModelSerializer):
    authorities = PublicAuthoritySerializer(many=True, read_only=True)
    district_name = serializers.CharField(source='district.name_en', read_only=True)
    area_type_code = serializers.CharField(source='area_type.code', read_only=True)

    class Meta:
        model = AdministrativeUnit
        fields = [
            'id', 'district', 'district_name', 'area_type', 'area_type_code', 'unit_type',
            'name_en', 'name_hi', 'ward_number', 'helpline_number', 'official_portal_url',
            'approx_latitude', 'approx_longitude', 'authorities'
        ]
""")

write_file("apps/authorities/views.py", """
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import State, District, AdministrativeUnit, PublicAuthority
from .serializers import StateSerializer, DistrictSerializer, AdministrativeUnitSerializer, PublicAuthoritySerializer
from apps.core.utils import haversine_distance_meters, bounding_box

class AdministrativeUnitViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AdministrativeUnit.objects.all().select_related('district', 'area_type').prefetch_related('authorities')
    serializer_class = AdministrativeUnitSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        area_type = self.request.query_params.get('area_type')
        district_id = self.request.query_params.get('district_id')
        unit_type = self.request.query_params.get('unit_type')
        search = self.request.query_params.get('search')

        if area_type:
            qs = qs.filter(area_type__code=area_type)
        if district_id:
            qs = qs.filter(district_id=district_id)
        if unit_type:
            qs = qs.filter(unit_type=unit_type)
        if search:
            qs = qs.filter(name_en__icontains=search) | qs.filter(name_hi__icontains=search) | qs.filter(ward_number__icontains=search)
        return qs

    @action(detail=False, methods=['get'])
    def suggest_by_coords(self, request):
        \"\"\"Suggest closest administrative unit based on GPS pin.\"\"\"
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        area_type = request.query_params.get('area_type')

        if not lat or not lng:
            return Response({'suggested': None, 'message': 'Coordinates missing'})

        lat, lng = float(lat), float(lng)
        qs = self.get_queryset()
        if area_type:
            qs = qs.filter(area_type__code=area_type)

        units_with_coords = [u for u in qs if u.approx_latitude and u.approx_longitude]
        if not units_with_coords:
            return Response({'suggested': None})

        # Calculate nearest
        closest_unit = min(
            units_with_coords,
            key=lambda u: haversine_distance_meters(lat, lng, u.approx_latitude, u.approx_longitude)
        )
        distance = haversine_distance_meters(lat, lng, closest_unit.approx_latitude, closest_unit.approx_longitude)
        serializer = self.get_serializer(closest_unit)
        return Response({
            'suggested': serializer.data,
            'distance_meters': round(distance, 1)
        })

class StateDistrictViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = State.objects.all().prefetch_related('districts')
    serializer_class = StateSerializer

    @action(detail=False, methods=['get'])
    def hierarchy(self, request):
        states = State.objects.all()
        data = []
        for s in states:
            districts = DistrictSerializer(s.districts.all(), many=True).data
            data.append({
                'id': s.id,
                'code': s.code,
                'name_en': s.name_en,
                'name_hi': s.name_hi,
                'districts': districts
            })
        return Response(data)
""")

write_file("apps/authorities/admin.py", """
from django.contrib import admin
from .models import State, District, AdministrativeUnit, PublicAuthority

class DistrictInline(admin.TabularInline):
    model = District
    extra = 1

@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'name_hi', 'code')
    inlines = [DistrictInline]

@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'name_hi', 'code', 'state')
    list_filter = ('state',)

class PublicAuthorityInline(admin.StackedInline):
    model = PublicAuthority
    extra = 1

@admin.register(AdministrativeUnit)
class AdministrativeUnitAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'name_hi', 'unit_type', 'ward_number', 'area_type', 'district')
    list_filter = ('area_type', 'unit_type', 'district')
    search_fields = ('name_en', 'name_hi', 'ward_number')
    inlines = [PublicAuthorityInline]

@admin.register(PublicAuthority)
class PublicAuthorityAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'designation_en', 'administrative_unit', 'contact_phone', 'contact_email')
    search_fields = ('name_en', 'name_hi', 'designation_en', 'administrative_unit__name_en')
""")

# -------------------------------------------------------------
# 4. apps/complaints
# -------------------------------------------------------------
write_file("apps/complaints/models.py", """
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
""")

write_file("apps/complaints/serializers.py", """
from rest_framework import serializers
from .models import Complaint, ComplaintEvidence, ComplaintCoSign, StatusAuditLog
from apps.config_engine.serializers import ComplaintCategorySerializer, AreaTypeSerializer, DurationOptionSerializer, PriorChannelOptionSerializer
from apps.authorities.serializers import AdministrativeUnitSerializer

class ComplaintEvidenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplaintEvidence
        fields = [
            'id', 'media_type', 'file', 'file_url', 'sha256_hash',
            'capture_timestamp', 'server_timestamp', 'capture_latitude',
            'capture_longitude', 'is_live_captured'
        ]

class StatusAuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusAuditLog
        fields = ['id', 'from_status', 'to_status', 'actor_type', 'actor_label', 'notes', 'created_at']

class ComplaintListSerializer(serializers.ModelSerializer):
    category = ComplaintCategorySerializer(read_only=True)
    area_type = AreaTypeSerializer(read_only=True)
    duration = DurationOptionSerializer(read_only=True)
    evidence = ComplaintEvidenceSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Complaint
        fields = [
            'id', 'public_id', 'title', 'description', 'category', 'area_type',
            'duration', 'sub_location', 'status', 'status_display',
            'latitude', 'longitude', 'co_sign_count', 'evidence',
            'is_official_conduct', 'moderation_status', 'created_at'
        ]

class ComplaintDetailSerializer(serializers.ModelSerializer):
    category = ComplaintCategorySerializer(read_only=True)
    area_type = AreaTypeSerializer(read_only=True)
    duration = DurationOptionSerializer(read_only=True)
    prior_channel = PriorChannelOptionSerializer(read_only=True)
    administrative_unit = AdministrativeUnitSerializer(read_only=True)
    evidence = ComplaintEvidenceSerializer(many=True, read_only=True)
    audit_trail = StatusAuditLogSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    moderation_status_display = serializers.CharField(source='get_moderation_status_display', read_only=True)

    class Meta:
        model = Complaint
        fields = [
            'id', 'public_id', 'title', 'description', 'revealed_identity', 'filer_name', 'filer_phone',
            'category', 'area_type', 'duration', 'people_affected_type', 'people_affected_count',
            'prior_attempts_count', 'prior_channel', 'prior_reference_number',
            'sub_location', 'authority_name_override', 'authority_designation',
            'administrative_unit', 'latitude', 'longitude', 'gps_accuracy_meters', 'manual_address_text',
            'status', 'status_display', 'moderation_status', 'moderation_status_display',
            'is_official_conduct', 'co_sign_count', 'flag_count',
            'evidence', 'audit_trail', 'created_at', 'updated_at'
        ]

class ComplaintCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = [
            'anonymous_session_hash', 'revealed_identity', 'filer_name', 'filer_phone',
            'area_type', 'category', 'duration', 'title', 'description',
            'people_affected_type', 'people_affected_count',
            'prior_attempts_count', 'prior_channel', 'prior_reference_number',
            'administrative_unit', 'sub_location', 'authority_name_override', 'authority_designation',
            'latitude', 'longitude', 'gps_accuracy_meters', 'manual_address_text',
            'is_official_conduct'
        ]

    def validate_description(self, value):
        if len(value.strip()) < 30:
            raise serializers.ValidationError('Description must be at least 30 characters to ensure verifiable details.')
        return value
""")

write_file("apps/complaints/views.py", """
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from .models import Complaint, ComplaintEvidence, ComplaintCoSign, StatusAuditLog
from .serializers import (
    ComplaintListSerializer, ComplaintDetailSerializer, ComplaintCreateSerializer,
    ComplaintEvidenceSerializer, StatusAuditLogSerializer
)
from apps.core.utils import compute_sha256, hash_session_id, haversine_distance_meters, bounding_box

class ComplaintViewSet(viewsets.ModelViewSet):
    queryset = Complaint.objects.all().select_related(
        'category', 'area_type', 'duration', 'prior_channel', 'administrative_unit'
    ).prefetch_related('evidence', 'audit_trail')

    def get_serializer_class(self):
        if self.action == 'list':
            return ComplaintListSerializer
        elif self.action == 'retrieve':
            return ComplaintDetailSerializer
        elif self.action == 'create':
            return ComplaintCreateSerializer
        return ComplaintDetailSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        # Default public feed filters out rejected complaints
        show_all = self.request.query_params.get('include_all')
        if not show_all:
            # Public view shows approved or under review (unless explicitly rejected)
            qs = qs.exclude(moderation_status='REJECTED')

        # Filters
        category_slug = self.request.query_params.get('category')
        area_type = self.request.query_params.get('area_type')
        status_filter = self.request.query_params.get('status')
        duration = self.request.query_params.get('duration')
        search = self.request.query_params.get('search')
        session_id = self.request.query_params.get('my_session_id')

        if category_slug:
            qs = qs.filter(category__slug=category_slug)
        if area_type:
            qs = qs.filter(area_type__code=area_type)
        if status_filter:
            qs = qs.filter(status=status_filter)
        if duration:
            qs = qs.filter(duration__code=duration)
        if search:
            qs = qs.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(sub_location__icontains=search) |
                Q(public_id__icontains=search)
            )
        if session_id:
            s_hash = hash_session_id(session_id)
            qs = qs.filter(anonymous_session_hash=s_hash)

        return qs

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        raw_session = data.get('anonymous_session_id')
        data['anonymous_session_hash'] = hash_session_id(raw_session)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        complaint = serializer.save()

        # Handle uploaded evidence files if provided
        files = request.FILES.getlist('evidence_files')
        media_types = request.data.getlist('media_types')
        file_urls = request.data.getlist('file_urls')
        
        for idx, f in enumerate(files):
            m_type = media_types[idx] if idx < len(media_types) else 'PHOTO'
            content = f.read()
            sha256_val = compute_sha256(content)
            f.seek(0)
            ComplaintEvidence.objects.create(
                complaint=complaint,
                media_type=m_type,
                file=f,
                sha256_hash=sha256_val,
                capture_latitude=complaint.latitude,
                capture_longitude=complaint.longitude,
                is_live_captured=True
            )

        # Handle base64 / captured data URLs if sent as text
        for idx, f_url in enumerate(file_urls):
            m_type = media_types[idx] if idx < len(media_types) else 'PHOTO'
            ComplaintEvidence.objects.create(
                complaint=complaint,
                media_type=m_type,
                file_url=f_url,
                sha256_hash=compute_sha256(f_url.encode('utf-8')),
                capture_latitude=complaint.latitude,
                capture_longitude=complaint.longitude,
                is_live_captured=True
            )

        response_serializer = ComplaintDetailSerializer(complaint)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def check_duplicates(self, request):
        \"\"\"Near-duplicate detection: Geo-proximity + Category match.\"\"\"
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        category_id = request.query_params.get('category_id')
        radius_meters = float(request.query_params.get('radius', 500))

        if not lat or not lng:
            return Response({'duplicates': [], 'count': 0})

        lat, lng = float(lat), float(lng)
        min_lat, max_lat, min_lon, max_lon = bounding_box(lat, lng, radius_meters)

        candidates = Complaint.objects.filter(
            latitude__gte=min_lat, latitude__lte=max_lat,
            longitude__gte=min_lon, longitude__lte=max_lon
        ).exclude(moderation_status='REJECTED')

        if category_id:
            candidates = candidates.filter(category_id=category_id)

        matching = []
        for c in candidates:
            dist = haversine_distance_meters(lat, lng, c.latitude, c.longitude)
            if dist <= radius_meters:
                item = ComplaintListSerializer(c).data
                item['distance_meters'] = round(dist, 1)
                matching.append(item)

        matching.sort(key=lambda x: x['distance_meters'])
        return Response({
            'duplicates': matching,
            'count': len(matching),
            'radius_meters': radius_meters
        })

    @action(detail=True, methods=['post'])
    def co_sign(self, request, pk=None):
        \"\"\"Anonymous Co-sign / 'I face this too'.\"\"\"
        complaint = self.get_object()
        session_id = request.data.get('anonymous_session_id')
        comment = request.data.get('comment', '')

        if not session_id:
            return Response({'error': 'Anonymous session identifier required'}, status=status.HTTP_400_BAD_REQUEST)

        s_hash = hash_session_id(session_id)
        ip = request.META.get('REMOTE_ADDR', '')
        ip_hash = hash_session_id(ip)

        existing = ComplaintCoSign.objects.filter(complaint=complaint, anonymous_session_hash=s_hash).first()
        if existing:
            return Response({
                'message': 'You have already co-signed this complaint.',
                'co_sign_count': complaint.co_sign_count,
                'already_cosigned': True
            })

        ComplaintCoSign.objects.create(
            complaint=complaint,
            anonymous_session_hash=s_hash,
            ip_hash=ip_hash,
            comment=comment
        )
        complaint.refresh_from_db()
        return Response({
            'message': 'Successfully co-signed! Your voice has been added to this public complaint.',
            'co_sign_count': complaint.co_sign_count,
            'already_cosigned': False
        }, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def my_cosigns(self, request):
        \"\"\"List complaints co-signed by current session.\"\"\"
        session_id = request.query_params.get('anonymous_session_id')
        if not session_id:
            return Response([])
        s_hash = hash_session_id(session_id)
        complaint_ids = ComplaintCoSign.objects.filter(anonymous_session_hash=s_hash).values_list('complaint_id', flat=True)
        complaints = Complaint.objects.filter(id__in=complaint_ids)
        return Response(ComplaintListSerializer(complaints, many=True).data)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        \"\"\"Update complaint status with immutable audit logging.\"\"\"
        complaint = self.get_object()
        new_status = request.data.get('status')
        actor_type = request.data.get('actor_type', 'MODERATOR')
        actor_label = request.data.get('actor_label', 'Public Grievance Desk')
        notes = request.data.get('notes', '')

        if new_status not in dict(Complaint.STATUS_CHOICES):
            return Response({'error': 'Invalid status choice'}, status=status.HTTP_400_BAD_REQUEST)

        old_status = complaint.status
        complaint.status = new_status
        complaint.save()

        StatusAuditLog.objects.create(
            complaint=complaint,
            from_status=old_status,
            to_status=new_status,
            actor_type=actor_type,
            actor_label=actor_label,
            notes=notes or f"Status changed from {old_status} to {new_status}."
        )

        return Response(ComplaintDetailSerializer(complaint).data)
""")

write_file("apps/complaints/admin.py", """
from django.contrib import admin
from .models import Complaint, ComplaintEvidence, ComplaintCoSign, StatusAuditLog

class ComplaintEvidenceInline(admin.TabularInline):
    model = ComplaintEvidence
    extra = 0
    readonly_fields = ('sha256_hash', 'capture_timestamp', 'server_timestamp', 'is_live_captured')

class StatusAuditLogInline(admin.TabularInline):
    model = StatusAuditLog
    extra = 0
    readonly_fields = ('created_at',)

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = (
        'public_id', 'title', 'category', 'area_type', 'sub_location',
        'status', 'moderation_status', 'co_sign_count', 'created_at'
    )
    list_filter = ('area_type', 'status', 'moderation_status', 'category', 'is_official_conduct')
    search_fields = ('public_id', 'title', 'description', 'sub_location')
    inlines = [ComplaintEvidenceInline, StatusAuditLogInline]
    readonly_fields = ('public_id', 'anonymous_session_hash', 'created_at', 'updated_at')

@admin.register(ComplaintEvidence)
class ComplaintEvidenceAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'media_type', 'sha256_hash', 'capture_timestamp', 'is_live_captured')
    list_filter = ('media_type', 'is_live_captured')

@admin.register(ComplaintCoSign)
class ComplaintCoSignAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'anonymous_session_hash', 'created_at')

@admin.register(StatusAuditLog)
class StatusAuditLogAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'from_status', 'to_status', 'actor_type', 'actor_label', 'created_at')
    list_filter = ('actor_type', 'to_status')
""")

# -------------------------------------------------------------
# 5. apps/moderation
# -------------------------------------------------------------
write_file("apps/moderation/models.py", """
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
""")

write_file("apps/moderation/serializers.py", """
from rest_framework import serializers
from .models import ComplaintFlag, ModerationReview
from apps.complaints.serializers import ComplaintDetailSerializer

class ComplaintFlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComplaintFlag
        fields = ['id', 'complaint', 'reason', 'explanation', 'created_at']

class ModerationReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModerationReview
        fields = ['id', 'complaint', 'action', 'moderator_name', 'notes', 'created_at']
""")

write_file("apps/moderation/views.py", """
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ComplaintFlag, ModerationReview
from .serializers import ComplaintFlagSerializer, ModerationReviewSerializer
from apps.complaints.models import Complaint, StatusAuditLog
from apps.complaints.serializers import ComplaintDetailSerializer
from apps.core.utils import hash_session_id

class ModerationViewSet(viewsets.ViewSet):
    \"\"\"Moderation Queue & Community Flagging API.\"\"\"

    @action(detail=False, methods=['get'])
    def queue(self, request):
        \"\"\"List complaints awaiting moderation review.\"\"\"
        status_filter = request.query_params.get('status', 'PENDING')
        qs = Complaint.objects.filter(moderation_status=status_filter).order_by('-created_at')
        return Response(ComplaintDetailSerializer(qs, many=True).data)

    @action(detail=False, methods=['post'])
    def flag_complaint(self, request):
        \"\"\"Submit community flag against a complaint.\"\"\"
        complaint_id = request.data.get('complaint_id')
        reason = request.data.get('reason')
        explanation = request.data.get('explanation', '')
        session_id = request.data.get('anonymous_session_id')

        try:
            complaint = Complaint.objects.get(id=complaint_id)
        except Complaint.DoesNotExist:
            return Response({'error': 'Complaint not found'}, status=status.HTTP_404_NOT_FOUND)

        s_hash = hash_session_id(session_id)
        flag = ComplaintFlag.objects.create(
            complaint=complaint,
            reason=reason,
            explanation=explanation,
            anonymous_session_hash=s_hash
        )
        return Response({'message': 'Thank you for reporting. Our moderation desk will review this complaint.', 'flag_id': flag.id}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def review_action(self, request, pk=None):
        \"\"\"Moderator decision to Approve/Reject/Flag.\"\"\"
        try:
            complaint = Complaint.objects.get(id=pk)
        except Complaint.DoesNotExist:
            return Response({'error': 'Complaint not found'}, status=status.HTTP_404_NOT_FOUND)

        act = request.data.get('action') # APPROVE, REJECT, FLAGGED
        notes = request.data.get('notes', '')
        moderator = request.data.get('moderator_name', 'Public Desk Moderator')

        if act == 'APPROVE':
            complaint.moderation_status = 'APPROVED'
            if complaint.status == 'UNDER_REVIEW':
                complaint.status = 'ACKNOWLEDGED'
        elif act == 'REJECT':
            complaint.moderation_status = 'REJECTED'
            complaint.status = 'CLOSED_UNRESOLVED'
        elif act == 'FLAG':
            complaint.moderation_status = 'FLAGGED'

        complaint.save()

        ModerationReview.objects.create(
            complaint=complaint,
            action=act,
            moderator_name=moderator,
            notes=notes
        )

        StatusAuditLog.objects.create(
            complaint=complaint,
            from_status='UNDER_REVIEW',
            to_status=complaint.status,
            actor_type='MODERATOR',
            actor_label=f'Moderation Desk ({moderator})',
            notes=f"Moderation decision: {act}. Note: {notes}"
        )

        return Response(ComplaintDetailSerializer(complaint).data)
""")

write_file("apps/moderation/admin.py", """
from django.contrib import admin
from .models import ComplaintFlag, ModerationReview

@admin.register(ComplaintFlag)
class ComplaintFlagAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'reason', 'created_at')
    list_filter = ('reason',)

@admin.register(ModerationReview)
class ModerationReviewAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'action', 'moderator_name', 'created_at')
    list_filter = ('action',)
""")

# -------------------------------------------------------------
# 6. apps/escalation
# -------------------------------------------------------------
write_file("apps/escalation/models.py", """
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
""")

write_file("apps/escalation/generators.py", """
from django.utils import timezone
from apps.complaints.models import Complaint

def generate_formal_letter(complaint: Complaint, language: str = 'hi') -> dict:
    \"\"\"Auto-generate formatted formal grievance or RTI letter addressed to designated civic authority.\"\"\"
    today_str = timezone.now().strftime('%d-%m-%Y')
    
    # Identify authority
    if complaint.administrative_unit and complaint.administrative_unit.authorities.exists():
        auth = complaint.administrative_unit.authorities.first()
        auth_title = auth.name_hi if language == 'hi' else auth.name_en
        auth_desig = auth.designation_hi if language == 'hi' else auth.designation_en
        office = auth.office_address_hi if language == 'hi' else auth.office_address_en
    else:
        auth_title = complaint.authority_name_override or ("श्रीमान सक्षम अधिकारी महोदय" if language == 'hi' else "The Competent Authority")
        auth_desig = complaint.authority_designation or ("विभागीय प्रमुख" if language == 'hi' else "Head of Department")
        office = complaint.sub_location

    loc = complaint.sub_location
    admin_name = complaint.administrative_unit.name_hi if complaint.administrative_unit else loc
    co_sign = complaint.co_sign_count
    duration_label = complaint.duration.label_hi if (complaint.duration and language == 'hi') else (complaint.duration.label_en if complaint.duration else 'काफी समय')

    evidence_hashes = "\\n".join([f"- साक्ष्य #{i+1} [{e.media_type}] SHA-256: {e.sha256_hash}" for i, e in enumerate(complaint.evidence.all())]) or "- लाइव वेबकैम/माइक्रोफोन द्वारा जियो-टैग्ड साक्ष्य संलग्न।"

    if language == 'hi':
        subject = f"जनहित याचिका / औपचारिक शिकायत: {complaint.category.name_hi} - {loc} ({complaint.public_id})"
        content = f\"\"\"दिनांक: {today_str}

सेवा में,
{auth_desig} / {auth_title}
{office}, {admin_name}

विषय: {subject}

महोदय/महोदया,

आवाज़ (Awaaz) नागरिक जन-उत्तरदायित्व मंच के माध्यम से आपको अवगत कराया जाता है कि {loc} क्षेत्र में नागरिक निम्नलिखित गंभीर समस्या से {duration_label} से जूझ रहे हैं:

समस्या का विवरण:
{complaint.description}

सार्वजनिक साक्ष्य एवं जन-समर्थन विवरण:
1. आवाज़ ट्रैकिंग आईडी: {complaint.public_id}
2. प्रभावित नागरिकों की सह-पुष्टि (Co-Signs): {co_sign} नागरिकों ने इस समस्या की पुष्टि करते हुए मंच पर आवाज़ उठाई है।
3. समस्या की अवधि: {duration_label}
4. सटीक जीपीएस निर्देशांक (GPS): Latitude {complaint.latitude}, Longitude {complaint.longitude}
5. पूर्व में की गई शिकायतें: {complaint.prior_attempts_count} बार ({complaint.prior_channel.label_hi if complaint.prior_channel else 'स्थानीय स्तर पर'})

डिजिटल साक्ष्य की सत्यता (Tamper-Evident SHA-256 Hash):
{evidence_hashes}

अतः आपसे सविनय अनुरोध है कि जनहित में इस समस्या की त्वरित जांच करवाकर संबंधित एजेंसी को नियमानुसार समयबद्ध समाधान कराने का आदेश जारी करने की कृपा करें।

सादर,
नागरिक प्रतिनिधिमंडल ({loc})
प्रमाणित प्रति: आवाज़ (Awaaz) नागरिक साक्ष्य मंच
URL: https://awaaz.civic.in/complaint/{complaint.public_id}
\"\"\"
    else:
        subject = f"Formal Grievance Petition: {complaint.category.name_en} at {loc} ({complaint.public_id})"
        content = f\"\"\"Date: {today_str}

To,
{auth_desig} / {auth_title}
{office}, {admin_name}

Subject: {subject}

Respected Authority,

This formal grievance is submitted on behalf of local residents of {loc} through the Awaaz Civic Accountability Layer. The community has been severely affected by the following grievance for {duration_label}:

Description of Grievance:
{complaint.description}

Public Evidence & Community Corroboration:
1. Awaaz Public Docket ID: {complaint.public_id}
2. Corroborated Citizens Count (Co-Signs): {co_sign} verified residents
3. Duration of Problem: {duration_label}
4. Verified GPS Coordinates: Latitude {complaint.latitude}, Longitude {complaint.longitude}
5. Prior Grievance Reference: {complaint.prior_attempts_count} attempt(s) ({complaint.prior_channel.label_en if complaint.prior_channel else 'Departmental channel'})

Tamper-Evident Media Integrity (SHA-256 Hashes):
{evidence_hashes}

We formally request the department to inspect the site and initiate resolution within the statutory grievance redressal timeframe.

Yours sincerely,
Citizens of {loc}
Public Docket: Awaaz Civic Accountability Platform
Web Record: https://awaaz.civic.in/complaint/{complaint.public_id}
\"\"\"

    return {
        'subject': subject,
        'content': content,
        'addressed_to': f"{auth_desig}, {office}",
        'language': language,
        'public_id': complaint.public_id,
        'corroboration_count': co_sign
    }
""")

write_file("apps/escalation/serializers.py", """
from rest_framework import serializers
from .models import EscalationTemplate, GeneratedEscalation

class EscalationTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EscalationTemplate
        fields = ['id', 'template_type', 'language', 'title_format', 'body_template']

class GeneratedEscalationSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedEscalation
        fields = ['id', 'complaint', 'template_type', 'language', 'addressed_to', 'content', 'corroboration_count_at_generation', 'created_at']
""")

write_file("apps/escalation/views.py", """
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import GeneratedEscalation
from .serializers import GeneratedEscalationSerializer
from .generators import generate_formal_letter
from apps.complaints.models import Complaint

class EscalationViewSet(viewsets.ViewSet):
    \"\"\"Generate formal grievance documents and RTI letters.\"\"\"

    @action(detail=False, methods=['get'])
    def generate_letter(self, request):
        complaint_id = request.query_params.get('complaint_id')
        language = request.query_params.get('lang', 'hi')
        
        if not complaint_id:
            return Response({'error': 'Complaint ID required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            complaint = Complaint.objects.get(id=complaint_id)
        except Complaint.DoesNotExist:
            return Response({'error': 'Complaint not found'}, status=status.HTTP_404_NOT_FOUND)

        doc = generate_formal_letter(complaint, language=language)
        return Response(doc)
""")

write_file("apps/escalation/admin.py", """
from django.contrib import admin
from .models import EscalationTemplate, GeneratedEscalation

@admin.register(EscalationTemplate)
class EscalationTemplateAdmin(admin.ModelAdmin):
    list_display = ('template_type', 'language', 'title_format')

@admin.register(GeneratedEscalation)
class GeneratedEscalationAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'template_type', 'language', 'addressed_to', 'created_at')
""")

# -------------------------------------------------------------
# 7. Seed Data Management Command (Realistic Pilot)
# -------------------------------------------------------------
write_file("apps/seed/management/commands/seed_awaaz_data.py", """
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.config_engine.models import ComplaintCategory, AreaType, DurationOption, PriorChannelOption
from apps.authorities.models import State, District, AdministrativeUnit, PublicAuthority
from apps.complaints.models import Complaint, ComplaintEvidence, ComplaintCoSign, StatusAuditLog
from apps.core.utils import compute_sha256, hash_session_id

class Command(BaseCommand):
    help = 'Seed initial config categories, pilot authority directory, and sample complaints'

    def handle(self, *args, **options):
        self.stdout.write('Seeding Awaaz platform data...')

        # 1. Area Types
        village_at, _ = AreaType.objects.get_or_create(
            code='VILLAGE',
            defaults={
                'name_en': 'Village / Gram Panchayat',
                'name_hi': 'ग्रामीण / ग्राम पंचायत',
                'description_en': 'Rural areas governed by Gram Panchayat, Sarpanch, and Janpad Panchayat.',
                'description_hi': 'ग्राम पंचायत, सरपंच एवं सचिव द्वारा प्रशासित ग्रामीण क्षेत्र।',
                'order': 1
            }
        )

        town_at, _ = AreaType.objects.get_or_create(
            code='TOWN',
            defaults={
                'name_en': 'Town / Nagar Panchayat',
                'name_hi': 'कस्बा / नगर पंचायत व पालिका',
                'description_en': 'Semi-urban localities governed by Nagar Palika Parishad or Nagar Panchayat.',
                'description_hi': 'नगर पालिका परिषद अथवा नगर पंचायत द्वारा प्रशासित कस्बाई क्षेत्र।',
                'order': 2
            }
        )

        city_at, _ = AreaType.objects.get_or_create(
            code='CITY',
            defaults={
                'name_en': 'City / Nagar Nigam',
                'name_hi': 'शहर / नगर निगम',
                'description_en': 'Urban cities divided into Municipal Wards and governed by Nagar Nigam.',
                'description_hi': 'नगर निगम एवं वार्ड पार्षदों द्वारा प्रशासित शहरी क्षेत्र।',
                'order': 3
            }
        )

        # 2. Complaint Categories
        categories_data = [
            ('roads', 'Roads & Potholes', 'सड़क एवं गड्ढे', 'Construction', False, 1),
            ('water-supply', 'Water Supply & Quality', 'पेयजल आपूर्ति व गुणवत्ता', 'Droplets', False, 2),
            ('drainage', 'Drainage & Waterlogging', 'जलभराव एवं नाली जाम', 'Waves', False, 3),
            ('garbage', 'Garbage & Waste Disposal', 'कचरा प्रबंधन व सफाई', 'Trash2', False, 4),
            ('electricity', 'Electricity & Power Outage', 'बिजली आपूर्ति व खंभे', 'Zap', False, 5),
            ('street-lights', 'Street Lighting', 'स्ट्रीट लाइट / पथ प्रकाश', 'Lightbulb', False, 6),
            ('school-condition', 'Government School Condition', 'सरकारी स्कूल की दुर्दशा', 'GraduationCap', False, 7),
            ('health-center', 'Primary Health Center (PHC)', 'प्राथमिक स्वास्थ्य केंद्र (अस्पताल)', 'Cross', False, 8),
            ('sanitation', 'Public Toilets & Sanitation', 'सार्वजनिक शौचालय व स्वच्छता', 'Sparkles', False, 9),
            ('encroachment', 'Illegal Construction / Encroachment', 'अवैध निर्माण एवं अतिक्रमण', 'Home', False, 10),
            ('stray-animals', 'Stray Animals Menace', 'आवारा मवेशी एवं पशु समस्या', 'Dog', False, 11),
            ('public-transport', 'Public Transport & Bus Stand', 'सार्वजनिक परिवहन व बस स्टैंड', 'Bus', False, 12),
            ('official-conduct', 'Local Official Conduct & Bribes', 'अधिकारी/कर्मचारी का आचरण व रिश्वत', 'ShieldAlert', True, 13),
            ('other', 'Other Civic Grievance', 'अन्य स्थानीय जन समस्या', 'HelpCircle', False, 14),
        ]

        for slug, name_en, name_hi, icon, strict, order in categories_data:
            ComplaintCategory.objects.update_or_create(
                slug=slug,
                defaults={
                    'name_en': name_en,
                    'name_hi': name_hi,
                    'icon': icon,
                    'requires_strict_moderation': strict,
                    'order': order,
                    'is_active': True
                }
            )

        # 3. Durations
        durations_data = [
            ('LESS_1_MONTH', 'Less than 1 month', '1 माह से कम', 1),
            ('1_TO_6_MONTHS', '1 to 6 months', '1 से 6 महीने', 2),
            ('6_TO_12_MONTHS', '6 to 12 months', '6 से 12 महीने', 3),
            ('MORE_1_YEAR', 'More than 1 year', '1 वर्ष से अधिक', 4),
        ]
        for code, en, hi, order in durations_data:
            DurationOption.objects.update_or_create(
                code=code,
                defaults={'label_en': en, 'label_hi': hi, 'order': order}
            )

        # 4. Prior Channels
        channels_data = [
            ('CM_HELPLINE', 'CM Helpline (181 / Portal)', 'सीएम हेल्पलाइन (181)', 1),
            ('MUNICIPAL_APP', 'Nagar Nigam 311 / Citizen App', 'नगर निगम 311 ऐप', 2),
            ('PANCHAYAT_LETTER', 'Gram Panchayat Written Application', 'ग्राम पंचायत लिखित आवेदन', 3),
            ('DELEGATION', 'In-Person Delegation to Official', 'अधिकारी को व्यक्तिगत रूप से मिलकर', 4),
            ('RTI_QUERY', 'RTI (Right to Information) Request', 'सूचना का अधिकार (RTI) याचिका', 5),
            ('NONE_FIRST_TIME', 'First Time Reporting on Awaaz', 'पहली बार आवाज़ पर दर्ज', 6),
        ]
        for code, en, hi, order in channels_data:
            PriorChannelOption.objects.update_or_create(
                code=code,
                defaults={'label_en': en, 'label_hi': hi, 'order': order}
            )

        # 5. Pilot Authority Directory (Bhopal & Sehore Region - Urban + Rural)
        mp_state, _ = State.objects.get_or_create(code='MP', defaults={'name_en': 'Madhya Pradesh', 'name_hi': 'मध्य प्रदेश'})
        bhopal_dist, _ = District.objects.get_or_create(state=mp_state, code='BHO', defaults={'name_en': 'Bhopal', 'name_hi': 'भोपाल'})
        sehore_dist, _ = District.objects.get_or_create(state=mp_state, code='SEH', defaults={'name_en': 'Sehore', 'name_hi': 'सीहोर'})

        # Urban Units (Bhopal Wards)
        ward45, _ = AdministrativeUnit.objects.get_or_create(
            district=bhopal_dist,
            area_type=city_at,
            name_en='Ward 45 - MP Nagar & Zone 1',
            defaults={
                'name_hi': 'वार्ड 45 - एमपी नगर व ज़ोन 1',
                'unit_type': 'WARD',
                'ward_number': '45',
                'helpline_number': '0755-2701222',
                'official_portal_url': 'https://bhopalmc.mp.gov.in',
                'approx_latitude': 23.2332,
                'approx_longitude': 77.4350,
            }
        )
        PublicAuthority.objects.get_or_create(
            administrative_unit=ward45,
            name_en='Rajesh Sharma',
            defaults={
                'name_hi': 'राजेश शर्मा',
                'designation_en': 'Ward Corporator / Parshad',
                'designation_hi': 'वार्ड पार्षद',
                'contact_phone': '+91 98260 11234',
                'contact_email': 'parshad.ward45@bhopalmc.org',
                'office_address_en': 'Zone Office 10, Near Jyoti Talkies, MP Nagar, Bhopal',
                'office_address_hi': 'ज़ोन कार्यालय 10, ज्योति टॉकीज़ के पास, एमपी नगर, भोपाल',
            }
        )

        ward28, _ = AdministrativeUnit.objects.get_or_create(
            district=bhopal_dist,
            area_type=city_at,
            name_en='Ward 28 - Kolar Road & Sarvadharma',
            defaults={
                'name_hi': 'वार्ड 28 - कोलार रोड व सर्वधर्म',
                'unit_type': 'WARD',
                'ward_number': '28',
                'helpline_number': '0755-2701222',
                'approx_latitude': 23.1780,
                'approx_longitude': 77.4180,
            }
        )
        PublicAuthority.objects.get_or_create(
            administrative_unit=ward28,
            name_en='Sunita Malviya',
            defaults={
                'name_hi': 'सुनीता मालवीय',
                'designation_en': 'Ward Corporator',
                'designation_hi': 'वार्ड पार्षद',
                'contact_phone': '+91 94250 88901',
                'contact_email': 'ward28@bhopalmc.org',
                'office_address_en': 'Kolar Nagar Palika Bhavan, Kolar Road, Bhopal',
                'office_address_hi': 'कोलार पालिका भवन, कोलार रोड, भोपाल',
            }
        )

        # Rural Units (Sehore Gram Panchayats)
        bilkisganj_gp, _ = AdministrativeUnit.objects.get_or_create(
            district=sehore_dist,
            area_type=village_at,
            name_en='Bilkisganj Gram Panchayat',
            defaults={
                'name_hi': 'बिलकिसगंज ग्राम पंचायत',
                'unit_type': 'GRAM_PANCHAYAT',
                'helpline_number': '07562-224100',
                'approx_latitude': 23.0850,
                'approx_longitude': 77.2340,
            }
        )
        PublicAuthority.objects.get_or_create(
            administrative_unit=bilkisganj_gp,
            name_en='Rameshwar Patel',
            defaults={
                'name_hi': 'रामेश्वर पटेल',
                'designation_en': 'Sarpanch (Pradhan)',
                'designation_hi': 'ग्राम प्रधान / सरपंच',
                'contact_phone': '+91 97531 44520',
                'office_address_en': 'Panchayat Bhavan, Main Bazaar, Bilkisganj, Sehore',
                'office_address_hi': 'पंचायत भवन, मुख्य बाज़ार, बिलकिसगंज, सीहोर',
            }
        )

        dora_gp, _ = AdministrativeUnit.objects.get_or_create(
            district=sehore_dist,
            area_type=village_at,
            name_en='Dora Gram Panchayat',
            defaults={
                'name_hi': 'डोरा ग्राम पंचायत',
                'unit_type': 'GRAM_PANCHAYAT',
                'helpline_number': '07562-224100',
                'approx_latitude': 23.1120,
                'approx_longitude': 77.1980,
            }
        )
        PublicAuthority.objects.get_or_create(
            administrative_unit=dora_gp,
            name_en='Kamla Bai',
            defaults={
                'name_hi': 'कमला बाई',
                'designation_en': 'Sarpanch',
                'designation_hi': 'सरपंच',
                'contact_phone': '+91 98930 22314',
                'office_address_en': 'Panchayat Bhavan, Dora, Sehore',
                'office_address_hi': 'पंचायत भवन, डोरा, सीहोर',
            }
        )

        # Semi-Urban Town (Sehore Town Nagar Palika)
        sehore_town, _ = AdministrativeUnit.objects.get_or_create(
            district=sehore_dist,
            area_type=town_at,
            name_en='Sehore Nagar Palika Parishad - Ward 12',
            defaults={
                'name_hi': 'सीहोर नगर पालिका परिषद - वार्ड 12',
                'unit_type': 'NAGAR_PANCHAYAT',
                'ward_number': '12',
                'helpline_number': '07562-222333',
                'approx_latitude': 23.2000,
                'approx_longitude': 77.0850,
            }
        )
        PublicAuthority.objects.get_or_create(
            administrative_unit=sehore_town,
            name_en='Pradeep Singh',
            defaults={
                'name_hi': 'प्रदीप सिंह',
                'designation_en': 'Nagar Palika Chairman',
                'designation_hi': 'नगर पालिका अध्यक्ष',
                'contact_phone': '+91 94251 77112',
                'office_address_en': 'Nagar Palika Office, Main Chauraha, Sehore',
                'office_address_hi': 'नगर पालिका कार्यालय, मुख्य चौराहा, सीहोर',
            }
        )

        # 6. Sample Live Pilot Complaints
        cat_roads = ComplaintCategory.objects.get(slug='roads')
        cat_water = ComplaintCategory.objects.get(slug='water-supply')
        cat_school = ComplaintCategory.objects.get(slug='school-condition')
        cat_garbage = ComplaintCategory.objects.get(slug='garbage')
        cat_drainage = ComplaintCategory.objects.get(slug='drainage')

        dur_6_12 = DurationOption.objects.get(code='6_TO_12_MONTHS')
        dur_more_1 = DurationOption.objects.get(code='MORE_1_YEAR')
        dur_1_6 = DurationOption.objects.get(code='1_TO_6_MONTHS')

        chan_cm = PriorChannelOption.objects.get(code='CM_HELPLINE')
        chan_app = PriorChannelOption.objects.get(code='MUNICIPAL_APP')
        chan_panch = PriorChannelOption.objects.get(code='PANCHAYAT_LETTER')

        # Complaint 1: Urban Road Pothole in MP Nagar
        c1, created = Complaint.objects.get_or_create(
            public_id='AWZ-2026-8941',
            defaults={
                'anonymous_session_hash': hash_session_id('pilot_user_1'),
                'area_type': city_at,
                'category': cat_roads,
                'duration': dur_6_12,
                'title': 'Dangerous 2-foot Deep Trench & Broken Road near Jyoti Talkies Crossroad',
                'description': 'The main connecting road between Zone 1 and Jyoti Talkies has been dug up for pipeline laying and left unpaved for 8 months. Two-wheelers crash daily during nighttime due to lack of barricading and street lighting. Over 10,000 commuters pass here every day.',
                'people_affected_type': 'ENTIRE_WARD',
                'people_affected_count': 12000,
                'prior_attempts_count': 3,
                'prior_channel': chan_app,
                'prior_reference_number': 'BMC-311-884912',
                'state': mp_state,
                'district': bhopal_dist,
                'administrative_unit': ward45,
                'sub_location': 'MP Nagar Zone 1, Near Jyoti Talkies',
                'authority_name_override': 'Rajesh Sharma (Ward Corporator)',
                'authority_designation': 'Ward 45 Corporator & Executive Engineer PWD',
                'latitude': 23.2335,
                'longitude': 77.4355,
                'gps_accuracy_meters': 4.2,
                'manual_address_text': 'Opposite Hotel Surendra Vilas, Zone 1, MP Nagar, Bhopal',
                'status': 'IN_PROGRESS',
                'moderation_status': 'APPROVED',
                'co_sign_count': 38,
            }
        )
        if created:
            ComplaintEvidence.objects.create(
                complaint=c1,
                media_type='PHOTO',
                file_url='https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?auto=format&fit=crop&w=800&q=80',
                sha256_hash='8f4b12a5e921d7b32814c02998a12e3445fb678832c199876543210fedcba987',
                capture_latitude=23.2335,
                capture_longitude=77.4355,
                is_live_captured=True
            )
            StatusAuditLog.objects.create(
                complaint=c1,
                from_status='UNDER_REVIEW',
                to_status='ACKNOWLEDGED',
                actor_type='AUTHORITY',
                actor_label='Nagar Nigam Zone 10 Engineer',
                notes='Site inspection conducted. Repair tender issued under Ward development fund.'
            )
            StatusAuditLog.objects.create(
                complaint=c1,
                from_status='ACKNOWLEDGED',
                to_status='IN_PROGRESS',
                actor_type='AUTHORITY',
                actor_label='PWD Sub-Division Bhopal',
                notes='Patchwork and bituminous concrete re-carpeting started on 24-Aug-2026.'
            )

        # Complaint 2: Rural Non-functional Government School Roof in Bilkisganj
        c2, created = Complaint.objects.get_or_create(
            public_id='AWZ-2026-3104',
            defaults={
                'anonymous_session_hash': hash_session_id('pilot_user_2'),
                'area_type': village_at,
                'category': cat_school,
                'duration': dur_more_1,
                'title': 'Leaking Roof and Collapsed Boundary Wall at Govt Primary School Bilkisganj',
                'description': 'During heavy rains, water drips directly onto students desks in classrooms 1 to 4. Plaster from the ceiling fell twice near the blackboard. There are no functional girl toilets, forcing 45 village girls to skip school during monsoon. The Sarpanch has ignored 4 written requests.',
                'people_affected_type': 'ENTIRE_VILLAGE',
                'people_affected_count': 320,
                'prior_attempts_count': 4,
                'prior_channel': chan_panch,
                'prior_reference_number': 'GP-BILKIS-2025/44',
                'state': mp_state,
                'district': sehore_dist,
                'administrative_unit': bilkisganj_gp,
                'sub_location': 'Govt Primary School, Bilkisganj Gram',
                'authority_name_override': 'Rameshwar Patel (Sarpanch)',
                'authority_designation': 'Gram Sarpanch & Block Education Officer (BEO)',
                'latitude': 23.0862,
                'longitude': 77.2348,
                'gps_accuracy_meters': 6.1,
                'manual_address_text': 'Near Village Pond, Bilkisganj Tehsil, Sehore',
                'status': 'ACKNOWLEDGED',
                'moderation_status': 'APPROVED',
                'co_sign_count': 64,
            }
        )
        if created:
            ComplaintEvidence.objects.create(
                complaint=c2,
                media_type='PHOTO',
                file_url='https://images.unsplash.com/photo-1580582932707-520aed937b7b?auto=format&fit=crop&w=800&q=80',
                sha256_hash='3a7e4b90f12c58e7789a44b3c0021e549887cd4a321efcba9876543210fedcba',
                capture_latitude=23.0862,
                capture_longitude=77.2348,
                is_live_captured=True
            )
            StatusAuditLog.objects.create(
                complaint=c2,
                from_status='UNDER_REVIEW',
                to_status='ACKNOWLEDGED',
                actor_type='AUTHORITY',
                actor_label='District Collectorate Grievance Portal',
                notes='Complaint escalated with 64 citizen corroborations. BEO Sehore assigned for physical verification.'
            )

        # Complaint 3: Urban Garbage Dump near Kolar Road Ward 28
        c3, created = Complaint.objects.get_or_create(
            public_id='AWZ-2026-5520',
            defaults={
                'anonymous_session_hash': hash_session_id('pilot_user_3'),
                'area_type': city_at,
                'category': cat_garbage,
                'duration': dur_1_6,
                'title': 'Overflowing Garbage Open Dump creating Health Hazard near Mandakini Chauraha',
                'description': 'Municipal waste collection bin was removed 3 months ago and replaced by an open dump. Stray cattle, dogs, and toxic stench make it impossible for 800+ families in the adjacent residential societies to open their windows. Vector-borne disease outbreak risk.',
                'people_affected_type': 'ENTIRE_WARD',
                'people_affected_count': 4500,
                'prior_attempts_count': 2,
                'prior_channel': chan_cm,
                'prior_reference_number': 'CM-181-499201',
                'state': mp_state,
                'district': bhopal_dist,
                'administrative_unit': ward28,
                'sub_location': 'Mandakini Colony, Kolar Road',
                'authority_name_override': 'Sunita Malviya (Ward Corporator)',
                'authority_designation': 'Ward 28 Corporator & Health Officer Zone 18',
                'latitude': 23.1795,
                'longitude': 77.4192,
                'gps_accuracy_meters': 3.5,
                'manual_address_text': 'Corner of Mandakini Colony Main Gate, Kolar Road, Bhopal',
                'status': 'RESOLVED',
                'moderation_status': 'APPROVED',
                'co_sign_count': 21,
            }
        )
        if created:
            ComplaintEvidence.objects.create(
                complaint=c3,
                media_type='PHOTO',
                file_url='https://images.unsplash.com/photo-1530587191325-3db32d826c18?auto=format&fit=crop&w=800&q=80',
                sha256_hash='1b994c48a12e3456789abcdef0123456789abcdef0123456789abcdef0123456',
                capture_latitude=23.1795,
                capture_longitude=77.4192,
                is_live_captured=True
            )
            StatusAuditLog.objects.create(
                complaint=c3,
                from_status='IN_PROGRESS',
                to_status='RESOLVED',
                actor_type='AUTHORITY',
                actor_label='Sanitation Department BMC',
                notes='Waste cleared with JCB excavator, area sanitized with lime powder, 2 enclosed green waste bins installed.'
            )

        # Complaint 4: Rural Contaminated Borewell Water in Dora Village
        c4, created = Complaint.objects.get_or_create(
            public_id='AWZ-2026-9012',
            defaults={
                'anonymous_session_hash': hash_session_id('pilot_user_4'),
                'area_type': village_at,
                'category': cat_water,
                'duration': dur_1_6,
                'title': 'Yellow Muddy Water with Foul Odor from Govt Borewell Pump',
                'description': 'The sole public borewell in Harijan Mohalla has been discharging rusty, contaminated yellow water for 2 months. 14 children have developed gastrointestinal illness. Women are forced to walk 2.5 km to agricultural tube wells to fetch drinking water.',
                'people_affected_type': 'ENTIRE_VILLAGE',
                'people_affected_count': 500,
                'prior_attempts_count': 1,
                'prior_channel': chan_panch,
                'prior_reference_number': '',
                'state': mp_state,
                'district': sehore_dist,
                'administrative_unit': dora_gp,
                'sub_location': 'Harijan Mohalla, Dora Gaon',
                'authority_name_override': 'Kamla Bai (Sarpanch)',
                'authority_designation': 'Gram Sarpanch & PHE Department Executive Engineer',
                'latitude': 23.1130,
                'longitude': 77.1995,
                'gps_accuracy_meters': 5.0,
                'manual_address_text': 'Near Community Handpump, Dora Village, Sehore',
                'status': 'UNDER_REVIEW',
                'moderation_status': 'APPROVED',
                'co_sign_count': 19,
            }
        )
        if created:
            ComplaintEvidence.objects.create(
                complaint=c4,
                media_type='PHOTO',
                file_url='https://images.unsplash.com/photo-1584467735815-f778f274e296?auto=format&fit=crop&w=800&q=80',
                sha256_hash='7c9e01f23456789abcdef0123456789abcdef0123456789abcdef0123456789a',
                capture_latitude=23.1130,
                capture_longitude=77.1995,
                is_live_captured=True
            )

        # Complaint 5: Near-duplicate Road complaint in MP Nagar Zone 1 (to demonstrate duplicate detection)
        c5, created = Complaint.objects.get_or_create(
            public_id='AWZ-2026-8955',
            defaults={
                'anonymous_session_hash': hash_session_id('pilot_user_5'),
                'area_type': city_at,
                'category': cat_roads,
                'duration': dur_1_6,
                'title': 'Caved-in Manhole and Damaged Asphalt opposite Surendra Vilas',
                'description': 'The asphalt has completely eroded around the storm drain manhole creating a hazardous obstacle right at the intersection. Immediate hot-mix asphalt filling needed.',
                'people_affected_type': 'ENTIRE_WARD',
                'people_affected_count': 8000,
                'prior_attempts_count': 1,
                'prior_channel': chan_app,
                'prior_reference_number': 'BMC-311-901844',
                'state': mp_state,
                'district': bhopal_dist,
                'administrative_unit': ward45,
                'sub_location': 'MP Nagar Zone 1',
                'authority_name_override': 'Rajesh Sharma',
                'authority_designation': 'Ward 45 Corporator',
                'latitude': 23.2340,
                'longitude': 77.4360,
                'gps_accuracy_meters': 4.0,
                'manual_address_text': 'Zone 1, MP Nagar, Bhopal',
                'status': 'ACKNOWLEDGED',
                'moderation_status': 'APPROVED',
                'co_sign_count': 14,
            }
        )
        if created:
            ComplaintEvidence.objects.create(
                complaint=c5,
                media_type='PHOTO',
                file_url='https://images.unsplash.com/photo-1515162816999-a0c47dc192f7?auto=format&fit=crop&w=800&q=80',
                sha256_hash='4d88e01f23456789abcdef0123456789abcdef0123456789abcdef0123456789b',
                capture_latitude=23.2340,
                capture_longitude=77.4360,
                is_live_captured=True
            )

        self.stdout.write(self.style.SUCCESS('Successfully seeded Awaaz platform with categories, authorities, and realistic pilot data!'))
""")

# -------------------------------------------------------------
# 8. Settings & Root URLs
# -------------------------------------------------------------
write_file("awaaz_backend/settings.py", """
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-awaaz-civic-accountability-2026-production-ready'

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third party
    'corsheaders',
    'rest_framework',
    # Awaaz Modules
    'apps.core',
    'apps.config_engine',
    'apps.authorities',
    'apps.complaints',
    'apps.moderation',
    'apps.escalation',
    'apps.seed',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'awaaz_backend.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'awaaz_backend.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Kolkata'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': None,
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}
""")

write_file("awaaz_backend/urls.py", """
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

from apps.config_engine.views import ConfigBootstrapView
from apps.authorities.views import StateDistrictViewSet, AdministrativeUnitViewSet
from apps.complaints.views import ComplaintViewSet
from apps.moderation.views import ModerationViewSet
from apps.escalation.views import EscalationViewSet

router = DefaultRouter()
router.register(r'states', StateDistrictViewSet, basename='states')
router.register(r'admin-units', AdministrativeUnitViewSet, basename='admin-units')
router.register(r'complaints', ComplaintViewSet, basename='complaints')
router.register(r'moderation', ModerationViewSet, basename='moderation')
router.register(r'escalation', EscalationViewSet, basename='escalation')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/config/bootstrap/', ConfigBootstrapView.as_view(), name='config-bootstrap'),
    path('api/v1/', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
""")

print("All backend code generated successfully!")

