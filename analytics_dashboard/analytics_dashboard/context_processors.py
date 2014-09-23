from django.conf import settings


def common(_request):
    return {
        'help_url': settings.HELP_URL,
        'feedback_email': settings.FEEDBACK_EMAIL,
        'support_url': settings.SUPPORT_URL,
        'terms_of_service_url': settings.TERMS_OF_SERVICE_URL,
        'privacy_policy_url': settings.PRIVACY_POLICY_URL,
        'full_application_name': settings.FULL_APPLICATION_NAME,
        'platform_name': settings.PLATFORM_NAME,
        'application_name': settings.APPLICATION_NAME
    }
