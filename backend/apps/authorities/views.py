from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import State, District, AdministrativeUnit, PublicAuthority
from .serializers import StateSerializer, DistrictSerializer, AdministrativeUnitSerializer, PublicAuthoritySerializer
from apps.core.utils import haversine_distance_meters, bounding_box

class AdministrativeUnitViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AdministrativeUnit.objects.all().select_related('district', 'area_type').prefetch_related('authorities')
    serializer_class = AdministrativeUnitSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        area_type = self.request.query_params.get('area_type')
        district_id = self.request.query_params.get('district_id')
        unit_type = self.request.query_params.get('unit_type')
        search = self.request.query_params.get('search')

        if area_type:
            qs = qs.filter(area_type__code=area_type)
        if district_id:
            qs = qs.filter(district_id=district_id)
        if unit_type:
            qs = qs.filter(unit_type=unit_type)
        if search:
            qs = qs.filter(name_en__icontains=search) | qs.filter(name_hi__icontains=search) | qs.filter(ward_number__icontains=search)
        return qs

    @action(detail=False, methods=['get'])
    def suggest_by_coords(self, request):
        """Suggest closest administrative unit based on GPS pin."""
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        area_type = request.query_params.get('area_type')

        if not lat or not lng:
            return Response({'suggested': None, 'message': 'Coordinates missing'})

        lat, lng = float(lat), float(lng)
        qs = self.get_queryset()
        if area_type:
            qs = qs.filter(area_type__code=area_type)

        units_with_coords = [u for u in qs if u.approx_latitude and u.approx_longitude]
        if not units_with_coords:
            return Response({'suggested': None})

        # Calculate nearest
        closest_unit = min(
            units_with_coords,
            key=lambda u: haversine_distance_meters(lat, lng, u.approx_latitude, u.approx_longitude)
        )
        distance = haversine_distance_meters(lat, lng, closest_unit.approx_latitude, closest_unit.approx_longitude)
        serializer = self.get_serializer(closest_unit)
        return Response({
            'suggested': serializer.data,
            'distance_meters': round(distance, 1)
        })

class StateDistrictViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = State.objects.all().prefetch_related('districts')
    serializer_class = StateSerializer

    @action(detail=False, methods=['get'])
    def hierarchy(self, request):
        states = State.objects.all()
        data = []
        for s in states:
            districts = DistrictSerializer(s.districts.all(), many=True).data
            data.append({
                'id': s.id,
                'code': s.code,
                'name_en': s.name_en,
                'name_hi': s.name_hi,
                'districts': districts
            })
        return Response(data)
