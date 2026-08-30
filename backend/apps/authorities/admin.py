from django.contrib import admin
from .models import State, District, AdministrativeUnit, PublicAuthority

class DistrictInline(admin.TabularInline):
    model = District
    extra = 1

@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'name_hi', 'code')
    inlines = [DistrictInline]

@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'name_hi', 'code', 'state')
    list_filter = ('state',)

class PublicAuthorityInline(admin.StackedInline):
    model = PublicAuthority
    extra = 1

@admin.register(AdministrativeUnit)
class AdministrativeUnitAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'name_hi', 'unit_type', 'ward_number', 'area_type', 'district')
    list_filter = ('area_type', 'unit_type', 'district')
    search_fields = ('name_en', 'name_hi', 'ward_number')
    inlines = [PublicAuthorityInline]

@admin.register(PublicAuthority)
class PublicAuthorityAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'designation_en', 'administrative_unit', 'contact_phone', 'contact_email')
    search_fields = ('name_en', 'name_hi', 'designation_en', 'administrative_unit__name_en')
