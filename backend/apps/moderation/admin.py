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
