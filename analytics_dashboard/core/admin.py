from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from analytics_dashboard.core.models import User


@admin.register(User)
class AnalyticsDashboardUserAdmin(UserAdmin):
    pass
