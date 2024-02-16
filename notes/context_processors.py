from django.conf import settings

def constants(request):
    return {
        "website_name": settings.WEBSITE_NAME,
        "contact_email": settings.CONTACT_EMAIL,
    }