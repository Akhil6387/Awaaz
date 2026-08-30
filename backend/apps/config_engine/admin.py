from django.contrib import admin
from .models import ComplaintCategory, AreaType, DurationOption, PriorChannelOption, PlatformConfig

@admin.register(ComplaintCategory)
class ComplaintCategoryAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'name_hi', 'slug', 'icon', 'requires_strict_moderation', 'order', 'is_active')
    list_editable = ('order', 'is_active', 'requires_strict_moderation')
    search_fields = ('name_en', 'name_hi', 'slug')
    prepopulated_fields = {'slug': ('name_en',)}

@admin.register(AreaType)
class AreaTypeAdmin(admin.ModelAdmin):
    list_display = ('code', 'name_en', 'name_hi', 'order')
    list_editable = ('order',)

@admin.register(DurationOption)
class DurationOptionAdmin(admin.ModelAdmin):
    list_display = ('code', 'label_en', 'label_hi', 'order')
    list_editable = ('order',)

@admin.register(PriorChannelOption)
class PriorChannelOptionAdmin(admin.ModelAdmin):
    list_display = ('code', 'label_en', 'label_hi', 'order')
    list_editable = ('order',)

@admin.register(PlatformConfig)
class PlatformConfigAdmin(admin.ModelAdmin):
    list_display = ('key', 'value', 'description')
