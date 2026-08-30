from django.contrib import admin
from .models import EscalationTemplate, GeneratedEscalation

@admin.register(EscalationTemplate)
class EscalationTemplateAdmin(admin.ModelAdmin):
    list_display = ('template_type', 'language', 'title_format')

@admin.register(GeneratedEscalation)
class GeneratedEscalationAdmin(admin.ModelAdmin):
    list_display = ('complaint', 'template_type', 'language', 'addressed_to', 'created_at')
