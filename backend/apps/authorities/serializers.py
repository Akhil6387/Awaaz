from rest_framework import serializers
from .models import State, District, AdministrativeUnit, PublicAuthority

class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['id', 'code', 'name_en', 'name_hi']

class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = ['id', 'state', 'code', 'name_en', 'name_hi']

class PublicAuthoritySerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicAuthority
        fields = ['id', 'name_en', 'name_hi', 'designation_en', 'designation_hi', 'contact_email', 'contact_phone', 'office_address_en', 'office_address_hi', 'photo_url']

class AdministrativeUnitSerializer(serializers.ModelSerializer):
    authorities = PublicAuthoritySerializer(many=True, read_only=True)
    district_name = serializers.CharField(source='district.name_en', read_only=True)
    area_type_code = serializers.CharField(source='area_type.code', read_only=True)

    class Meta:
        model = AdministrativeUnit
        fields = [
            'id', 'district', 'district_name', 'area_type', 'area_type_code', 'unit_type',
            'name_en', 'name_hi', 'ward_number', 'helpline_number', 'official_portal_url',
            'approx_latitude', 'approx_longitude', 'authorities'
        ]
