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
