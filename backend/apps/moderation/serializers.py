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
