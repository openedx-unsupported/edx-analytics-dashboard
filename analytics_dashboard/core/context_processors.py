from django.conf import settings


def common(_request):
    return {
        'support_email': settings.SUPPORT_EMAIL,
        'full_application_name': settings.FULL_APPLICATION_NAME,
        'platform_name': settings.PLATFORM_NAME,
        'application_name': settings.APPLICATION_NAME,
        'footer_links': settings.FOOTER_LINKS,
    }
