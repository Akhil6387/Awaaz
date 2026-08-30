from pathlib import Path

content = '''from rest_framework import viewsets, status
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
        show_all = self.request.query_params.get('include_all')
        if not show_all:
            qs = qs.exclude(moderation_status='REJECTED')

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
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        raw_session = data.get('anonymous_session_id')
        data['anonymous_session_hash'] = hash_session_id(raw_session)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        complaint = serializer.save()

        # Handle uploaded evidence files if provided
        files = request.FILES.getlist('evidence_files') if hasattr(request.FILES, 'getlist') else []
        
        if hasattr(request.data, 'getlist'):
            media_types = request.data.getlist('media_types')
            file_urls = request.data.getlist('file_urls')
        else:
            media_types = request.data.get('media_types', [])
            if isinstance(media_types, str):
                media_types = [media_types]
            file_urls = request.data.get('file_urls', [])
            if isinstance(file_urls, str):
                file_urls = [file_urls]
        
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

    @action(detail=False, methods=['get'], url_path='check-duplicates')
    def check_duplicates(self, request):
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
        session_id = request.query_params.get('anonymous_session_id')
        if not session_id:
            return Response([])
        s_hash = hash_session_id(session_id)
        complaint_ids = ComplaintCoSign.objects.filter(anonymous_session_hash=s_hash).values_list('complaint_id', flat=True)
        complaints = Complaint.objects.filter(id__in=complaint_ids)
        return Response(ComplaintListSerializer(complaints, many=True).data)

    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
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
'''

Path('apps/complaints/views.py').write_text(content, encoding='utf-8')
print('Updated apps/complaints/views.py')
