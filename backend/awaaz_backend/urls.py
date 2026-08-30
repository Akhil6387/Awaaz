from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter

from apps.config_engine.views import ConfigBootstrapView
from apps.authorities.views import StateDistrictViewSet, AdministrativeUnitViewSet
from apps.complaints.views import ComplaintViewSet
from apps.moderation.views import ModerationViewSet
from apps.escalation.views import EscalationViewSet

router = DefaultRouter()
router.register(r'states', StateDistrictViewSet, basename='states')
router.register(r'admin-units', AdministrativeUnitViewSet, basename='admin-units')
router.register(r'complaints', ComplaintViewSet, basename='complaints')
router.register(r'moderation', ModerationViewSet, basename='moderation')
router.register(r'escalation', EscalationViewSet, basename='escalation')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/config/bootstrap/', ConfigBootstrapView.as_view(), name='config-bootstrap'),
    path('api/v1/', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
