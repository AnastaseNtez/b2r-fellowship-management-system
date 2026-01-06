from django.db import models

# --- 1. Province Model ---
class Province(models.Model):
    """Represents the highest administrative division in Rwanda."""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, blank=True, null=True, 
                            help_text="Administrative code (optional).")

    class Meta:
        ordering = ['name']
        verbose_name_plural = "Provinces"

    def __str__(self):
        return self.name

# --- 2. District Model ---
class District(models.Model):
    """Represents the second-level administrative division."""
    # FK1 (ForeignKey1): Link to Province
    province = models.ForeignKey(
        Province, 
        on_delete=models.CASCADE, 
        related_name='districts'
    )
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        # Ensures that a District name is unique within a Province
        unique_together = ('name', 'province')
        ordering = ['province__name', 'name']

    def __str__(self):
        return f"{self.name} ({self.province.name})"

# --- 3. Sector Model ---
class Sector(models.Model):
    """Represents the third-level administrative division, where Fellows are stationed."""
    # FK1: Link to District
    district = models.ForeignKey(
        District, 
        on_delete=models.CASCADE, 
        related_name='sectors'
    )
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        # Ensures that a Sector name is unique within a District
        unique_together = ('name', 'district')
        ordering = ['district__province__name', 'district__name', 'name']

    def __str__(self):
        return f"{self.name} Sector"
    
class Village(models.Model):
    """Represents the fourth-level administrative division within a Sector."""
    sector = models.ForeignKey(
        Sector, 
        on_delete=models.CASCADE, 
        related_name='villages'
    )
    name = models.CharField(max_length=100)
    
    class Meta:
        # Ensures village names are unique within a specific Sector
        unique_together = ('name', 'sector')
        ordering = ['sector__name', 'name']

    def __str__(self):
        return f"{self.name} Village ({self.sector.name})"