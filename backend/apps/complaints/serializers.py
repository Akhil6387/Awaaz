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
