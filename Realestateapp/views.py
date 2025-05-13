
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Property, PropertyType, City, Amenity
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Property, City, PropertyType, Amenity, ContactMessage
from django.http import Http404

def Home(request):

    return render(request,'Homepage.html')
def About(request):
    return render(request,'About.html')
def Contact(request):
    return render(request,'contact.html')
def SignIn(request):
    return render(request,'signin.html')
def SignUp(request):
    return render(request, 'signup.html')


def property_page(request):
    """View function for displaying all properties with filters."""

    # Get all properties by default (we'll apply filters later)
    properties = Property.objects.all()

    # Get all property types, cities, and amenities for filter dropdowns
    property_types = PropertyType.objects.all()
    cities = City.objects.all()
    amenities = Amenity.objects.all()

    # Process filter parameters
    if request.method == 'GET':
        # Property Type filter
        property_type = request.GET.get('property_type')
        if property_type and property_type != '':
            properties = properties.filter(property_type__id=property_type)

        # City filter
        city = request.GET.get('city')
        if city and city != '':
            properties = properties.filter(city__id=city)

        # Status filter (for sale/for rent)
        status = request.GET.get('status')
        if status and status != '':
            properties = properties.filter(status=status)

        # Price Range filter
        price_range = request.GET.get('price_range')
        if price_range and price_range != '':
            price_min, price_max = price_range.split('-')
            if price_max:
                properties = properties.filter(price__gte=float(price_min), price__lte=float(price_max))
            else:
                properties = properties.filter(price__gte=float(price_min))

        # Bedrooms filter
        bedrooms = request.GET.get('bedrooms')
        if bedrooms and bedrooms != '':
            properties = properties.filter(bedrooms__gte=int(bedrooms))

        # Bathrooms filter
        bathrooms = request.GET.get('bathrooms')
        if bathrooms and bathrooms != '':
            properties = properties.filter(bathrooms__gte=float(bathrooms))

        # Area filter
        area_range = request.GET.get('area')
        if area_range and area_range != '':
            area_min, area_max = area_range.split('-')
            if area_max:
                properties = properties.filter(area__gte=float(area_min), area__lte=float(area_max))
            else:
                properties = properties.filter(area__gte=float(area_min))

        # Sort by filter
        sort_by = request.GET.get('sort_by', 'newest')
        if sort_by == 'price_low_high':
            properties = properties.order_by('price')
        elif sort_by == 'price_high_low':
            properties = properties.order_by('-price')
        elif sort_by == 'newest':
            properties = properties.order_by('-created_at')

    # Pagination
    from django.core.paginator import Paginator
    page = request.GET.get('page', 1)
    paginator = Paginator(properties, 6)  # 6 properties per page (as shown in the template)
    properties_paginated = paginator.get_page(page)

    context = {
        'properties': properties_paginated,
        'property_types': property_types,
        'cities': cities,
        'amenities': amenities,
        'filter_parameters': request.GET,  # Pass the GET parameters back to maintain filters
    }

    return render(request, 'property_list.html', context)


def property_detail_view(request, slug):
    """
    View to display property details based on slug
    Also handles contact form submission from the property detail page
    """
    try:
        # Get the property by slug
        property = get_object_or_404(Property, slug=slug)

        # Get related properties (same property type, same city, exclude current)
        related_properties = Property.objects.filter(
            property_type=property.property_type,
            city=property.city
        ).exclude(id=property.id).order_by('-featured', '-created_at')[:3]

        # Get main image
        main_image = property.images.filter(is_main=True).first()
        if not main_image:
            main_image = property.images.first()

        # Get other images
        other_images = property.images.all()

        # Handle contact form submission
        if request.method == 'POST':
            name = request.POST.get('name')
            email = request.POST.get('email')
            phone = request.POST.get('phone')
            message_text = request.POST.get('message')

            # Create and save contact message
            if name and email and message_text:
                contact = ContactMessage(
                    name=name,
                    email=email,
                    phone=phone,
                    subject=f"Inquiry about {property.title}",
                    message=message_text,
                    property=property
                )
                contact.save()
                messages.success(request, "Your message has been sent successfully. We'll contact you soon.")
                return redirect('property_detail', slug=slug)
            else:
                messages.error(request, "Please complete all required fields.")

        # Prepare context for template
        context = {
            'property': property,
            'main_image': main_image,
            'other_images': other_images,
            'related_properties': related_properties,
            'agent': property.agent,
        }

        return render(request, 'property_detail.html', context)

    except Http404:
        # Handle case when property is not found
        return render(request, '404.html', status=404)



