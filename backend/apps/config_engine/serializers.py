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
