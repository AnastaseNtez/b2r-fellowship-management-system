# locations/views.py

from django.shortcuts import render
from django.http import JsonResponse
from .models import Province, District, Sector

# NOTE: The render view below is generally not needed if you use this for AJAX, 
# but including it for completeness if you had a locations landing page.
# def locations_home(request):
# return render(request, 'locations/home.html') 

def load_districts(request):
    """
    AJAX endpoint to load districts based on the selected province ID.
    Returns JSON: {district_id: district_name, ...}
    """
    province_id = request.GET.get('province_id')
    
    # 1. Filter districts based on the province ID
    districts = District.objects.filter(province_id=province_id).order_by('name')
    
    # 2. Serialize the data into the format expected by the JavaScript: {id: name}
    data = {district.pk: district.name for district in districts}
    
    # 3. Return the data as a JSON response
    return JsonResponse(data)

def load_sectors(request):
    """
    AJAX endpoint to load sectors based on the selected district ID.
    Returns JSON: {sector_id: sector_name, ...}
    """
    district_id = request.GET.get('district_id')
    
    # 1. Filter sectors based on the district ID
    sectors = Sector.objects.filter(district_id=district_id).order_by('name')

    # 2. Serialize the data into the format expected by the JavaScript: {id: name}
    data = {sector.pk: sector.name for sector in sectors}
    
    # 3. Return the data as a JSON response
    return JsonResponse(data)