# fellows/forms.py

from django import forms
from .models import Fellow
from locations.models import Province, District, Sector

class FellowRegistrationForm(forms.ModelForm):
    # --- Custom Fields for User Creation (NOT on Fellow Model) ---
    email = forms.EmailField(
        required=True,
        label='Fellow Email (Used for Login)',
        help_text="Must be unique."
    )
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)

    # --- Custom Fields for Cascading Locations (NOT on Fellow Model) ---
    province = forms.ModelChoiceField(
        queryset=Province.objects.all().order_by('name'),
        required=True,
        label='Assigned Province',
        empty_label="--- Select Province ---"
    )

    district = forms.ModelChoiceField(
        queryset=District.objects.none(),
        required=True,
        label='Assigned District',
        empty_label="--- Select District ---"
    )
    
    class Meta:
        model = Fellow
        # CRITICAL: Only include fields that exist DIRECTLY on the Fellow model.
        # All custom fields are defined above and handled manually in the view.
        fields = (
            'university', 
            'degree_field', 
            'graduation_year', 
            'assigned_sector', 
            'status', 
            'training_completed',
            'fellowship_start_date', 
            'fellowship_end_date'
        )
        widgets = {
            'fellowship_start_date': forms.DateInput(attrs={'type': 'date'}),
            'fellowship_end_date': forms.DateInput(attrs={'type': 'date'}),
        }


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Base initialization for all location fields
        self.fields['province'].queryset = Province.objects.all().order_by('name')
        self.fields['district'].queryset = District.objects.none()
        self.fields['assigned_sector'].queryset = Sector.objects.none()

        # CRITICAL: Restore querysets and selections on failed validation (POST)
        if self.data:
            try:
                # 1. Restore District Queryset
                province_id = self.data.get('province')
                if province_id:
                    self.fields['district'].queryset = District.objects.filter(
                        province_id=province_id
                    ).order_by('name')
                
                # 2. Restore Sector Queryset
                district_id = self.data.get('district')
                if district_id:
                    self.fields['assigned_sector'].queryset = Sector.objects.filter(
                        district_id=district_id
                    ).order_by('name')

            except (ValueError, TypeError):
                # Handles cases where submitted IDs are invalid integers
                pass
        
        # Handle initialization when EDITING an existing instance (for Admin forms, etc.)
        if self.instance.pk:
            if self.instance.assigned_sector:
                sector = self.instance.assigned_sector
                district = sector.district
                province = district.province

                # Populate querysets for existing instance
                self.fields['province'].queryset = Province.objects.all()
                self.fields['district'].queryset = District.objects.filter(province=province)
                self.fields['assigned_sector'].queryset = Sector.objects.filter(district=district)
                
                # Set initial values for the custom fields
                self.initial['province'] = province.pk
                self.initial['district'] = district.pk
            
            if self.instance.user:
                 self.initial['email'] = self.instance.user.email
                 self.initial['first_name'] = self.instance.user.first_name
                 self.initial['last_name'] = self.instance.user.last_name
    
    def clean(self):
        cleaned_data = super().clean()
        assigned_sector = cleaned_data.get('assigned_sector')
        district = cleaned_data.get('district')
        
        # Optional: Add cross-field validation check
        if assigned_sector and district and assigned_sector.district != district:
            self.add_error('assigned_sector', "The selected sector does not belong to the selected district.")
        
        return cleaned_data