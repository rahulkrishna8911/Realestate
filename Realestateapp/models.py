from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class PropertyType(models.Model):
    """Model for different property types (Apartment, House, Commercial, etc.)"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Property Types"


class City(models.Model):
    """Model for cities where properties are located"""
    name = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, default="United States")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Cities"


class Amenity(models.Model):
    """Model for amenities that properties can have"""
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True, null=True)  # For FontAwesome or similar icon names

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Amenities"


class Property(models.Model):
    """Main property model"""
    STATUS_CHOICES = (
        ('for_sale', 'For Sale'),
        ('for_rent', 'For Rent'),
        ('sold', 'Sold'),
        ('rented', 'Rented'),
    )

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='for_sale')
    property_type = models.ForeignKey(PropertyType, on_delete=models.CASCADE)
    bedrooms = models.PositiveIntegerField(default=0)
    bathrooms = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    area = models.DecimalField(max_digits=10, decimal_places=2, help_text="Area in square feet")

    # Location details
    address = models.CharField(max_length=255)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    zip_code = models.CharField(max_length=20)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)

    # Features and amenities
    amenities = models.ManyToManyField(Amenity, blank=True)
    featured = models.BooleanField(default=False)
    year_built = models.PositiveIntegerField(blank=True, null=True)

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(Property, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name_plural = "Properties"
        ordering = ['-created_at']


class PropertyImage(models.Model):
    """Model for property images"""
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='properties/')
    is_main = models.BooleanField(default=False)
    alt_text = models.CharField(max_length=100, blank=True)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Image for {self.property.title}"

    class Meta:
        ordering = ['order']


class ContactMessage(models.Model):
    """Model for contact form submissions"""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    property = models.ForeignKey(Property, on_delete=models.SET_NULL, null=True, blank=True, related_name='inquiries')
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Message from {self.name} - {self.subject}"

    class Meta:
        ordering = ['-created_at']


