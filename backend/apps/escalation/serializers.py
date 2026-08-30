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
