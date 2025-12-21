from django.contrib import admin
from .models import Province, District, Sector

@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'district_count')
    search_fields = ('name', 'code')

    def district_count(self, obj):
        # Uses related_name='districts' from your District model
        return obj.districts.count()
    district_count.short_description = 'Number of Districts'

@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ('name', 'province', 'sector_count', 'code')
    list_filter = ('province',)
    search_fields = ('name', 'code')

    def sector_count(self, obj):
        # FIX: Uses related_name='sectors' from your Sector model
        return obj.sectors.count()
    sector_count.short_description = 'Number of Sectors'

@admin.register(Sector)
class SectorAdmin(admin.ModelAdmin):
    list_display = ('name', 'district', 'get_province', 'code')
    list_filter = ('district__province', 'district')
    search_fields = ('name', 'code')

    def get_province(self, obj):
        return obj.district.province.name
    get_province.short_description = 'Province'