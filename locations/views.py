from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Sum, Count

from .models import Province, District, Sector
from activities.models import TrainingActivity
from rest_framework.reverse import reverse
from rest_framework.decorators import api_view, permission_classes

# --- 1. Province API ---
class ProvinceListView(APIView):
    """GET /api/locations/provinces/ - List all provinces."""
    permission_classes = [AllowAny]

    def get(self, request):
        provinces = Province.objects.all().values('id', 'name', 'code')
        return Response(list(provinces))

# --- 2. District API ---
class DistrictListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # This checks both DRF query_params AND standard GET params
        province_id = request.query_params.get('province_id') or request.GET.get('province_id')
        districts = District.objects.all()
        
        if province_id:
            districts = districts.filter(province_id=province_id)
            
        data = districts.values('id', 'name', 'province_id', 'province__name')
        return Response(list(data))

# --- 3. Sector API ---
class SectorListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # This checks both DRF query_params AND standard GET params
        district_id = request.query_params.get('district_id') or request.GET.get('district_id')
        sectors = Sector.objects.all()
        
        if district_id:
            sectors = sectors.filter(district_id=district_id)
            
        data = sectors.values('id', 'name', 'district_id', 'district__name')
        return Response(list(data))

# --- 4. Sector Coverage API ---
class SectorCoverageAPIView(APIView):
    """
    GET /api/locations/sectors/{id}/coverage/
    Aggregates approved training impact data for a specific sector.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        sector = get_object_or_404(Sector, id=id)
        
        # Calculate impact from the TrainingActivity model
        impact_stats = TrainingActivity.objects.filter(
            sector=sector, 
            status='APPROVED'
        ).aggregate(
            total_farmers=Sum('number_of_farmers_trained'),
            total_sessions=Count('id')
        )

        return Response({
            "sector_id": sector.id,
            "sector_name": sector.name,
            "district": sector.district.name,
            "province": sector.district.province.name,
            "total_farmers_trained": impact_stats['total_farmers'] or 0,
            "total_sessions": impact_stats['total_sessions'] or 0,
            # Calculated coverage metric for B2R stakeholders
            "coverage_level": "High" if (impact_stats['total_farmers'] or 0) > 100 else "Active"
        })

# API/ endpoints listing

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root_view(request, format=None):
    """
    B2R Fellowship Management System API Root.
    This entry point provides a structured map of all available endpoints.
    """
    return Response({
        # Geographical Hierarchy
        'provinces': reverse('api-provinces', request=request, format=format),
        'districts': reverse('api-districts', request=request, format=format),
        'sectors': reverse('api-sectors', request=request, format=format),
        
        # Specific Analytics/Coverage
        # Note: This is a detail endpoint, so we use a dummy ID (like 1) 
        # just to show the structure to recruiters.
        'sector-coverage-example': reverse('api-sector-coverage', kwargs={'id': 1}, request=request, format=format),
    })



# Aliases to support existing AJAX calls in the forms
load_districts = DistrictListView.as_view()
load_sectors = SectorListView.as_view()