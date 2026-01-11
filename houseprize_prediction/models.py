from django.db import models

class register(models.Model):
    name=models.CharField(max_length=150)
    email=models.CharField(max_length=150)
    phone=models.CharField(max_length=120)
    password=models.CharField(max_length=120)

class Owner(models.Model):
    name = models.CharField(max_length=150)
    email = models.CharField(max_length=150, unique=True)
    phone = models.CharField(max_length=120)
    password = models.CharField(max_length=120)
    # Add any additional fields specific to owners, e.g., address, license, etc.
    address = models.TextField(blank=True)
    license_number = models.CharField(max_length=100, blank=True)

class Property(models.Model):
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    area_type = models.CharField(max_length=50)
    total_sqft = models.FloatField()
    bath = models.IntegerField()
    balcony = models.IntegerField()
    BHK = models.IntegerField()
    HALL_KITCHEN = models.CharField(max_length=50)
    location_new = models.CharField(max_length=100)
    # Additional fields if needed
    price = models.FloatField(blank=True, null=True)  # Optional, can be predicted later
    availability = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
