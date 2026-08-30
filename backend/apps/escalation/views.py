from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import GeneratedEscalation
from .serializers import GeneratedEscalationSerializer
from .generators import generate_formal_letter
from apps.complaints.models import Complaint

class EscalationViewSet(viewsets.ViewSet):
    """Generate formal grievance documents and RTI letters."""

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
