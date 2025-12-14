from django.contrib import admin
from .models import Province, District, Sector

# 1. Define a custom display for the District model
class DistrictAdmin(admin.ModelAdmin):
    # Display these fields in the list view
    list_display = ('name', 'province', 'code', 'sector_count')
    # Add a filter sidebar to quickly filter by Province
    list_filter = ('province',)
    # Add a search bar to search by name or code
    search_fields = ('name', 'code')

    # Custom method to count sectors within a district
    def sector_count(self, obj):
        # We use obj.sector_set.count() because the Sector model has a ForeignKey to District
        return obj.sector_set.count()
    sector_count.short_description = 'Sectors in District'

# 2. Define a custom display for the Sector model
class SectorAdmin(admin.ModelAdmin):
    list_display = ('name', 'district', 'code')
    # Filter by District, and by the District's parent Province (for better navigation)
    list_filter = ('district__province', 'district')
    search_fields = ('name', 'code', 'district__name')

# 3. Register the models
admin.site.register(Province)
admin.site.register(District, DistrictAdmin)
admin.site.register(Sector, SectorAdmin)