from rest_framework.views import APIView
from rest_framework.response import Response
from .models import ComplaintCategory, AreaType, DurationOption, PriorChannelOption
from .serializers import ComplaintCategorySerializer, AreaTypeSerializer, DurationOptionSerializer, PriorChannelOptionSerializer

class ConfigBootstrapView(APIView):
    """Return all dynamic form choices in a single high-performance call."""
    def get(self, request):
        categories = ComplaintCategory.objects.filter(is_active=True).order_by('order')
        area_types = AreaType.objects.all().order_by('order')
        durations = DurationOption.objects.all().order_by('order')
        prior_channels = PriorChannelOption.objects.all().order_by('order')

        return Response({
            'categories': ComplaintCategorySerializer(categories, many=True).data,
            'area_types': AreaTypeSerializer(area_types, many=True).data,
            'duration_options': DurationOptionSerializer(durations, many=True).data,
            'prior_channels': PriorChannelOptionSerializer(prior_channels, many=True).data,
        })
