"""
This script uses standard Python and Django functions to read data and create records. Since the actual, 
comprehensive list of Rwanda's 30 districts and 416 sectors is quite long, 
we will use a simplified example structure within the script.
"""

# locations/management/commands/load_rwanda_locations.py

import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from locations.models import Province, District, Sector
from django.db import transaction

class Command(BaseCommand):
    help = 'Loads Rwanda administrative divisions (Provinces, Districts, Sectors) from a JSON fixture file.'

    # 1. Define the file path relative to the project base
    def get_file_path(self):
        # Assumes the file is named rwanda_locations.json and is in the locations app directory
        return os.path.join(settings.BASE_DIR, 'locations', 'rwanda_locations.json')

    def handle(self, *args, **options):
        file_path = self.get_file_path()
        
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'Error: Geographic data file not found at {file_path}'))
            return

        self.stdout.write(self.style.NOTICE('Starting geographic data loading from JSON fixture...'))
        
        try:
            # 2. Open and load the JSON data
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR('Error decoding JSON file. Check file syntax.'))
            return
        
        total_provinces = 0
        total_districts = 0
        total_sectors = 0

        # Using a transaction ensures that all database operations succeed together, 
        # or none of them do, maintaining data integrity.
        with transaction.atomic():
            for p_data in data:
                # 3. Create/Get Province (Top Level)
                province, created = Province.objects.get_or_create(
                    code=p_data['code'],
                    defaults={'name': p_data['province']} 
                )
                if created:
                    total_provinces += 1
                    # self.stdout.write(f'Created Province: {province.name}') # Optional: too verbose
    
                for d_data in p_data.get('districts', []):
                    # 4. Create/Get District (Middle Level)
                    district, created = District.objects.get_or_create(
                        code=d_data['code'],
                        province=province, # Link to the parent Province object
                        defaults={'name': d_data['name']}
                    )
                    if created:
                        total_districts += 1
                        # self.stdout.write(f'  Created District: {district.name}') # Optional: too verbose
    
                    for s_data in d_data.get('sectors', []):
                        # 5. Create/Get Sector (Bottom Level)
                        sector, created = Sector.objects.get_or_create(
                            code=s_data['code'],
                            district=district, # Link to the parent District object
                            defaults={'name': s_data['name']}
                        )
                        if created:
                            total_sectors += 1
        
        self.stdout.write(self.style.SUCCESS(f'\n--- Data Load Complete ---'))
        self.stdout.write(self.style.SUCCESS(f'New Provinces Created: {total_provinces}'))
        self.stdout.write(self.style.SUCCESS(f'New Districts Created: {total_districts}'))
        self.stdout.write(self.style.SUCCESS(f'New Sectors Created: {total_sectors}'))
        self.stdout.write(self.style.SUCCESS(f'Total Locations Loaded: {Province.objects.count()} Provinces, {District.objects.count()} Districts, {Sector.objects.count()} Sectors'))