from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ComplaintFlag, ModerationReview
from .serializers import ComplaintFlagSerializer, ModerationReviewSerializer
from apps.complaints.models import Complaint, StatusAuditLog
from apps.complaints.serializers import ComplaintDetailSerializer
from apps.core.utils import hash_session_id

class ModerationViewSet(viewsets.ViewSet):
    """Moderation Queue & Community Flagging API."""

    @action(detail=False, methods=['get'])
    def queue(self, request):
        """List complaints awaiting moderation review."""
        status_filter = request.query_params.get('status', 'PENDING')
        qs = Complaint.objects.filter(moderation_status=status_filter).order_by('-created_at')
        return Response(ComplaintDetailSerializer(qs, many=True).data)

    @action(detail=False, methods=['post'])
    def flag_complaint(self, request):
        """Submit community flag against a complaint."""
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
        """Moderator decision to Approve/Reject/Flag."""
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
